"""
Controlador para digitalización de documentos
Maneja el flujo: Upload → MinIO → BD → OCR/HTR → Resultados
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import asyncio
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.services.digitalizacion_service import DigitalizacionService
from app.dto.digitalizacion_dto import (
    UploadDocumentRequest, UploadDocumentResponse, 
    ProcessingStatusResponse, DocumentListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/digitalizacion",
    tags=["Digitalización"]
)

# Instancia del servicio
digitalizacion_service = DigitalizacionService()

@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(
    archivo: UploadFile = File(..., description="Archivo JPG, PNG o PDF"),
    libro_id: int = Form(..., description="ID del libro"),
    tipo_sacramento: int = Form(..., description="Tipo de sacramento (1=bautizo, 2=confirmacion, etc.)"),
    institucion_id: int = Form(1, description="ID de la institución/parroquia"),
    procesar_automaticamente: bool = Form(True, description="Procesar con OCR/HTR automáticamente"),
    modelo_procesamiento: str = Form('ocr', description="Modelo de procesamiento: 'ocr' (texto impreso) o 'htr' (texto manuscrito)"),
    db: Session = Depends(get_db)
):
    """
    Sube un documento y opcionalmente lo procesa con OCR o HTR
    
    Flujo:
    1. Valida el archivo
    2. Sube a MinIO
    3. Guarda metadata en BD (documento_digitalizado)
    4. Si procesar_automaticamente=True, llama al OCR o HTR service
    5. Guarda resultados en BD (ocr_resultado)
    """
    
    try:
        logger.info(f"Iniciando upload de documento: {archivo.filename} (modelo: {modelo_procesamiento})")
        
        # Validar modelo_procesamiento
        if modelo_procesamiento not in ['ocr', 'htr']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="modelo_procesamiento debe ser 'ocr' o 'htr'"
            )
        
        # Validar tipo de archivo
        if not archivo.content_type or not any([
            archivo.content_type.startswith('image/'),
            archivo.content_type == 'application/pdf'
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de archivo no soportado. Solo JPG, PNG y PDF."
            )
        
        # Validar tamaño (máx 50MB)
        MAX_SIZE = 50 * 1024 * 1024  # 50MB
        archivo_bytes = await archivo.read()
        
        if len(archivo_bytes) > MAX_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo demasiado grande. Máximo 50MB."
            )
        
        if len(archivo_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo vacío."
            )
        
        logger.info(f"Archivo validado: {len(archivo_bytes)} bytes")
        
        # Procesar documento usando el servicio
        resultado = await digitalizacion_service.procesar_documento(
            archivo_bytes=archivo_bytes,
            archivo_nombre=archivo.filename,
            content_type=archivo.content_type,
            libro_id=libro_id,
            tipo_sacramento=tipo_sacramento,
            institucion_id=institucion_id,
            procesar_ocr=procesar_automaticamente,
            modelo_procesamiento=modelo_procesamiento,
            db=db
        )
        
        logger.info(f"Documento procesado exitosamente. ID: {resultado.documento_id}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
        
        # Procesar documento usando el servicio
        resultado = await digitalizacion_service.procesar_documento(
            archivo_bytes=archivo_bytes,
            archivo_nombre=archivo.filename,
            content_type=archivo.content_type,
            libro_id=libro_id,
            tipo_sacramento=tipo_sacramento,
            institucion_id=institucion_id,
            procesar_ocr=procesar_automaticamente,
            db=db
        )
        
        logger.info(f"Documento procesado exitosamente. ID: {resultado.documento_id}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/progreso/{documento_id}")
async def get_progreso_procesamiento(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el progreso de procesamiento leyendo los logs de Docker
    del contenedor OCR o HTR según corresponda
    """
    try:
        from sqlalchemy import text
        import subprocess
        import re
        
        # Obtener modelo_procesamiento del documento
        query = text("""
            SELECT modelo_procesamiento 
            FROM documento_digitalizado 
            WHERE id_documento = :doc_id
        """)
        result = db.execute(query, {"doc_id": documento_id}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {documento_id} no encontrado"
            )
        
        modelo = result[0] or 'ocr'
        
        # Determinar nombre del contenedor según modelo
        if modelo == 'htr':
            container_name = "sacra360_htr_service"
            modelo_upper = "HTR"
        else:
            container_name = "sacra360_ocr_service"
            modelo_upper = "OCR"
        
        try:
            # Leer logs del contenedor (últimas 200 líneas)
            cmd = ["docker", "logs", container_name, "--tail", "200"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            all_logs = result.stdout + result.stderr
            
            # CRÍTICO: Extraer solo las líneas del documento específico
            # Buscar desde "Procesando documento ... ID=X" hasta el próximo "Procesando documento" o final
            # Soporta ambos formatos: OCR usa "desde BD: ID=X" y HTR usa "con HTR: ID=X"
            doc_start_pattern = rf"Procesando documento.+ID={documento_id}\b"
            lines = all_logs.split('\n')
            
            doc_lines = []
            capturing = False
            for line in lines:
                if re.search(doc_start_pattern, line, re.IGNORECASE):
                    capturing = True
                    doc_lines = [line]  # Reiniciar captura
                elif capturing:
                    # Detener si empieza otro documento (cualquier ID diferente)
                    other_doc_match = re.search(r'Procesando documento.+ID=(\d+)', line, re.IGNORECASE)
                    if other_doc_match and int(other_doc_match.group(1)) != documento_id:
                        break
                    doc_lines.append(line)
            
            # Si no se encontraron logs del documento, está pendiente
            if not doc_lines:
                return {
                    "estado": "pendiente",
                    "progreso": 0,
                    "mensaje": f"Esperando inicio de procesamiento {modelo_upper}...",
                    "etapa": "pendiente"
                }
            
            # Trabajar solo con los logs del documento específico
            logs = '\n'.join(doc_lines)
            
            # Parsear logs para extraer progreso
            estado = "procesando"
            progreso = 0
            mensaje = f"Procesando con {modelo_upper}..."
            
            # Para HTR: buscar filas procesadas
            if modelo == 'htr':
                # Buscar "✅ COMPLETADO: X filas válidas extraídas"
                completado_match = re.search(r'✅ COMPLETADO:\s*(\d+)\s*filas válidas', logs)
                if completado_match:
                    return {
                        "estado": "completado",
                        "progreso": 100,
                        "mensaje": f"HTR completado: {completado_match.group(1)} filas extraídas",
                        "etapa": "completado"
                    }
                
                # Contar TODAS las filas procesadas (válidas + saltadas por ruido)
                filas_validas = len(re.findall(r'✅ VÁLIDA', logs))
                filas_saltadas = len(re.findall(r'⏭️.*SALTADA|Fila.*SALTADA', logs))
                total_procesadas = filas_validas + filas_saltadas
                
                # Buscar total estimado de filas detectadas
                filas_detectadas_match = re.search(r'📍 Filas detectadas:\s*(\d+)', logs)
                total_filas = int(filas_detectadas_match.group(1)) if filas_detectadas_match else 10
                
                if total_procesadas > 0:
                    # Progreso basado en filas procesadas (válidas + ruido)
                    progreso = min(int((total_procesadas / total_filas) * 85), 85)  # Max 85% durante procesamiento
                    mensaje = f"HTR: {total_procesadas}/{total_filas} filas procesadas ({filas_validas} válidas)"
                    estado = "procesando_htr"
                elif "Detectando estructura" in logs:
                    progreso = 10
                    mensaje = "HTR: Detectando estructura de tabla..."
                    estado = "procesando_htr"
                elif "Convirtiendo PDF" in logs:
                    progreso = 5
                    mensaje = "HTR: Convirtiendo PDF a imagen..."
                    estado = "procesando_htr"
                else:
                    progreso = 2
                    mensaje = "HTR: Iniciando procesamiento..."
                    estado = "procesando_htr"
                    
            # Para OCR: buscar progreso de EasyOCR
            else:
                # Buscar completado - DEBE ser mensaje final específico
                if re.search(r'✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE|✅ OCR completado:', logs):
                    return {
                        "estado": "completado",
                        "progreso": 100,
                        "mensaje": "OCR completado exitosamente",
                        "etapa": "completado"
                    }
                
                # Buscar progreso de lectura de celdas en logs de EasyOCR
                # Patrón: "📊 Procesadas X/Y celdas" - ÚNICO indicador válido para evitar saltos
                # Usar findall para encontrar TODAS las coincidencias y tomar la ÚLTIMA
                ocr_cells_matches = re.findall(r'📊 Procesadas (\d+)/(\d+) celdas', logs)
                
                if ocr_cells_matches:
                    # Tomar la ÚLTIMA coincidencia (progreso más reciente)
                    procesadas, total = ocr_cells_matches[-1]
                    procesadas = int(procesadas)
                    total = int(total)
                    # Progreso 0-95% basado en celdas procesadas
                    progreso = min(int((procesadas / total) * 95), 95)
                    mensaje = f"OCR: Leyendo {procesadas}/{total} celdas..."
                    estado = "procesando_ocr"
                else:
                    # Antes de empezar a leer celdas, mantener en 0%
                    progreso = 0
                    mensaje = "OCR: Preparando documento..."
                    estado = "procesando_ocr"
            
            # Buscar errores
            if re.search(r'ERROR|Exception|Traceback|Failed', logs, re.IGNORECASE):
                error_match = re.search(r'(ERROR|Exception):\s*(.+)', logs)
                error_msg = error_match.group(2) if error_match else "Error en procesamiento"
                return {
                    "estado": "error",
                    "progreso": 0,
                    "mensaje": f"Error: {error_msg[:100]}",
                    "etapa": "error"
                }
            
            return {
                "estado": estado,
                "progreso": progreso,
                "mensaje": mensaje,
                "etapa": modelo
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout leyendo logs de {container_name}")
            return {
                "estado": "error",
                "progreso": 0,
                "mensaje": "Timeout consultando logs del contenedor"
            }
        except Exception as e:
            logger.error(f"Error leyendo logs de Docker: {e}")
            return {
                "estado": "procesando",
                "progreso": 10,
                "mensaje": f"Procesando con {modelo_upper}... (sin acceso a logs)"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo progreso: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo progreso: {str(e)}"
        )

@router.get("/status/{documento_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de procesamiento de un documento
    """
    try:
        status_info = await digitalizacion_service.obtener_estado_procesamiento(
            documento_id=documento_id,
            db=db
        )
        
        return status_info
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado: {str(e)}"
        )

@router.get("/documentos", response_model=DocumentListResponse)
async def list_documents(
    libro_id: Optional[int] = None,
    tipo_sacramento: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Lista documentos con filtros opcionales
    """
    try:
        documentos = await digitalizacion_service.listar_documentos(
            libro_id=libro_id,
            tipo_sacramento=tipo_sacramento,
            skip=skip,
            limit=limit,
            db=db
        )
        
        return documentos
        
    except Exception as e:
        logger.error(f"Error listando documentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando documentos: {str(e)}"
        )

@router.get("/documentos-pendientes")
async def get_documentos_pendientes(db: Session = Depends(get_db)):
    """
    Obtiene documentos con tuplas OCR pendientes de validación
    """
    try:
        from sqlalchemy import text
        
        query = text("""
            SELECT DISTINCT 
                d.id_documento,
                d.nombre_archivo,
                d.libros_id,
                d.tipo_sacramento,
                d.imagen_url,
                d.fecha_procesamiento,
                d.modelo_procesamiento,
                d.modelo_fuente,
                COUNT(o.id_ocr) as total_tuplas,
                SUM(CASE WHEN o.estado_validacion = 'pendiente' THEN 1 ELSE 0 END) as tuplas_pendientes,
                SUM(CASE WHEN o.estado_validacion = 'validado' THEN 1 ELSE 0 END) as tuplas_validadas,
                o.fuente_modelo
            FROM documento_digitalizado d
            INNER JOIN ocr_resultado o ON d.id_documento = o.documento_id
            WHERE o.estado_validacion = 'pendiente'
            GROUP BY d.id_documento, d.nombre_archivo, d.libros_id, d.tipo_sacramento, 
                     d.imagen_url, d.fecha_procesamiento, d.modelo_procesamiento, d.modelo_fuente, o.fuente_modelo
            ORDER BY d.fecha_procesamiento DESC
        """)
        
        result = db.execute(query)
        documentos = []
        
        for row in result:
            documentos.append({
                "id": row[0],  # id en lugar de id_documento para el frontend
                "id_documento": row[0],
                "nombre_archivo": row[1] or f"Documento_{row[0]}",
                "libro_id": row[2],
                "tipo_sacramento": row[3],
                "imagen_url": row[4],
                "fecha_procesamiento": row[5].isoformat() if row[5] else None,
                "fecha_subida": row[5].strftime("%Y-%m-%d %H:%M") if row[5] else None,
                "modelo_procesamiento": row[6] or 'ocr',  # 'ocr' o 'htr'
                "modelo_fuente": row[7] or 'Desconocido',  # 'EasyOCR V2' o 'HTR_Sacra360'
                "total_tuplas": row[8],
                "tuplas_pendientes": row[9],
                "tuplas_validadas": row[10],
                "fuente_modelo": row[11] or 'Desconocido',  # de ocr_resultado
                "progreso": int((row[10] / row[8] * 100)) if row[8] > 0 else 0
            })
        
        return documentos
        
    except Exception as e:
        logger.error(f"Error obteniendo documentos pendientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@router.post("/procesar/{documento_id}")
async def process_existing_document(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Procesa con OCR un documento ya subido
    """
    try:
        resultado = await digitalizacion_service.procesar_ocr_documento_existente(
            documento_id=documento_id,
            db=db
        )
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error procesando documento existente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando documento: {str(e)}"
        )

@router.put("/modelo/{documento_id}")
async def update_modelo_procesamiento(
    documento_id: int,
    modelo_procesamiento: str = Form(..., description="Modelo de procesamiento: 'ocr' o 'htr'"),
    db: Session = Depends(get_db)
):
    """
    Cambia el modelo de procesamiento de un documento existente y lo reprocesa
    """
    try:
        # Validar modelo
        if modelo_procesamiento not in ['ocr', 'htr']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="modelo_procesamiento debe ser 'ocr' o 'htr'"
            )
        
        # Verificar que el documento existe
        query = text("SELECT id_documento, modelo_procesamiento FROM documento_digitalizado WHERE id_documento = :doc_id")
        result = db.execute(query, {"doc_id": documento_id}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {documento_id} no encontrado"
            )
        
        modelo_actual = result[1]
        
        if modelo_actual == modelo_procesamiento:
            return {
                "mensaje": f"El documento ya está configurado con modelo '{modelo_procesamiento}'",
                "documento_id": documento_id,
                "modelo_procesamiento": modelo_procesamiento
            }
        
        # Actualizar modelo y resetear estado
        update_query = text("""
            UPDATE documento_digitalizado 
            SET modelo_procesamiento = :modelo,
                estado_procesamiento = 'pendiente',
                progreso_ocr = 0,
                modelo_fuente = ''
            WHERE id_documento = :doc_id
        """)
        
        db.execute(update_query, {
            "modelo": modelo_procesamiento,
            "doc_id": documento_id
        })
        
        # Limpiar resultados anteriores
        delete_query = text("DELETE FROM ocr_resultado WHERE documento_id = :doc_id")
        db.execute(delete_query, {"doc_id": documento_id})
        
        db.commit()
        
        logger.info(f"Modelo actualizado de '{modelo_actual}' a '{modelo_procesamiento}' para documento {documento_id}")
        
        # Obtener info del documento para reprocesar
        doc_query = text("""
            SELECT imagen_url, nombre_archivo, libros_id, tipo_sacramento 
            FROM documento_digitalizado 
            WHERE id_documento = :doc_id
        """)
        doc_info = db.execute(doc_query, {"doc_id": documento_id}).fetchone()
        
        # Disparar procesamiento asíncrono
        import threading
        import requests
        
        def _reprocesar():
            try:
                servicio_nombre = "HTR" if modelo_procesamiento == 'htr' else "OCR"
                service_url = digitalizacion_service.htr_service_url if modelo_procesamiento == 'htr' else digitalizacion_service.ocr_service_url
                endpoint = f"{service_url}/api/v1/{modelo_procesamiento}/procesar-desde-bd/{documento_id}"
                
                logger.info(f"🔄 Reprocesando documento {documento_id} con {servicio_nombre}: {endpoint}")
                response = requests.post(endpoint, timeout=600)
                
                if response.status_code == 200:
                    logger.info(f"✅ Reprocesamiento {servicio_nombre} completado para documento {documento_id}")
                else:
                    logger.error(f"❌ Reprocesamiento {servicio_nombre} falló HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error reprocesando documento {documento_id}: {e}")
        
        thread = threading.Thread(target=_reprocesar, daemon=True)
        thread.start()
        
        return {
            "mensaje": f"Modelo cambiado de '{modelo_actual}' a '{modelo_procesamiento}'. Reprocesando en background...",
            "documento_id": documento_id,
            "modelo_anterior": modelo_actual,
            "modelo_nuevo": modelo_procesamiento,
            "estado": "procesando"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando modelo de procesamiento: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
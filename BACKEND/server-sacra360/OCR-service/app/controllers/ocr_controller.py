"""
OCR Controller - Lógica de negocio para procesamiento OCR
"""

from fastapi import UploadFile, HTTPException
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import io
import requests

from ..services.ocr_v2_processor import OcrV2Processor
from ..services.database_service import DatabaseService
from ..services.minio_service import MinioService

logger = logging.getLogger(__name__)

# Diccionario global para tracking de progreso
progress_tracker = {}


class OcrController:
    """Controlador para procesamiento de documentos con OCR V2"""
    
    def __init__(self, db):
        """
        Inicializa el controlador
        
        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.db_service = DatabaseService(db)
        self.minio_service = MinioService()
        self.ocr_processor = OcrV2Processor()
    
    async def procesar_documento(self, file: UploadFile) -> Dict[str, Any]:
        """
        Procesa un documento con OCR V2
        
        Args:
            file: Archivo subido (PDF o imagen)
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            logger.info("=" * 70)
            logger.info(f"📄 Procesando documento: {file.filename}")
            logger.info("=" * 70)
            
            # 1. Validar tipo de archivo
            es_pdf = file.filename.lower().endswith('.pdf')
            if not es_pdf and not any(file.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                raise HTTPException(
                    status_code=400,
                    detail="Formato no soportado. Use PDF, JPG o PNG"
                )
            
            # 2. Leer archivo
            contenido = await file.read()
            logger.info(f"📦 Archivo leído: {len(contenido)} bytes")
            
            # 3. Procesar con OCR V2
            logger.info("🔍 Iniciando procesamiento OCR V2...")
            resultado_ocr = self.ocr_processor.procesar_documento_completo(
                archivo_bytes=contenido,
                es_pdf=es_pdf
            )
            
            if resultado_ocr['estado'] != 'success':
                logger.error(f"❌ Error en OCR: {resultado_ocr.get('mensaje', 'Error desconocido')}")
                return {
                    'estado': 'error',
                    'mensaje': resultado_ocr.get('mensaje', 'Error en procesamiento OCR'),
                    'total_tuplas': 0
                }
            
            logger.info(f"✅ OCR completado: {resultado_ocr['total_tuplas']} tuplas extraídas")
            
            # 4. Subir archivo a MinIO
            logger.info("☁️  Subiendo archivo a MinIO...")
            resultado_minio = self.minio_service.upload_file(
                file_data=contenido,
                file_name=file.filename,
                content_type=file.content_type
            )
            archivo_url = resultado_minio.get('object_url') or resultado_minio.get('url')
            logger.info(f"✅ Archivo subido: {archivo_url}")
            
            # 5. Guardar en base de datos
            logger.info("💾 Guardando resultados en PostgreSQL...")
            documento_id = self.db_service.guardar_documento_completo(
                archivo_nombre=file.filename,
                archivo_url=archivo_url,
                tuplas=resultado_ocr['tuplas'],
                total_tuplas=resultado_ocr['total_tuplas']
            )
            logger.info(f"✅ Documento guardado con ID: {documento_id}")
            
            logger.info("=" * 70)
            logger.info("✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
            logger.info("=" * 70)
            
            return {
                'documento_id': documento_id,
                'estado': 'success',
                'total_tuplas': resultado_ocr['total_tuplas'],
                'archivo_url': archivo_url,
                'archivo_nombre': file.filename,
                'fecha_procesamiento': datetime.now().isoformat()
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error en procesamiento: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar documento: {str(e)}"
            )
    
    async def obtener_resultados(self, documento_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los resultados de un documento procesado
        
        Args:
            documento_id: ID del documento
            
        Returns:
            Dict con resultados o None si no existe
        """
        try:
            logger.info(f"🔍 Buscando resultados de documento ID: {documento_id}")
            
            resultado = self.db_service.obtener_resultado_por_id(documento_id)
            
            if resultado:
                logger.info(f"✅ Documento encontrado: {resultado.get('archivo_nombre', 'N/A')}")
            else:
                logger.warning(f"⚠️  Documento {documento_id} no encontrado")
            
            return resultado
        
        except Exception as e:
            logger.error(f"❌ Error al obtener resultados: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener resultados: {str(e)}"
            )
    
    async def procesar_desde_bd(self, documento_id: int) -> Dict[str, Any]:
        """
        Procesa un documento que ya está guardado en BD y MinIO
        
        Args:
            documento_id: ID del documento en la tabla documento_digitalizado
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            logger.info("=" * 70)
            logger.info(f"📄 Procesando documento desde BD: ID={documento_id}")
            logger.info("=" * 70)
            
            # Actualizar progreso: iniciando
            progress_tracker[documento_id] = {
                'estado': 'iniciando',
                'progreso': 5,
                'mensaje': 'Iniciando procesamiento...',
                'etapa': 'init'
            }
            
            # 1. Obtener documento de BD
            from sqlalchemy import text
            query = text("""
                SELECT id_documento, nombre_archivo, imagen_url, tipo_sacramento
                FROM documento_digitalizado
                WHERE id_documento = :doc_id
            """)
            result = self.db.execute(query, {"doc_id": documento_id}).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"Documento {documento_id} no encontrado en BD")
            
            doc_id, nombre_archivo, archivo_url, tipo_sacramento = result
            logger.info(f"📄 Documento encontrado: {nombre_archivo}")
            
            # Actualizar progreso: descargando
            progress_tracker[documento_id] = {
                'estado': 'descargando',
                'progreso': 15,
                'mensaje': 'Descargando archivo desde MinIO...',
                'etapa': 'download'
            }
            
            # 2. Descargar archivo de MinIO
            logger.info(f"☁️  Descargando desde: {archivo_url}")
            contenido = self.minio_service.download_file_by_url(archivo_url)
            logger.info(f"✅ Archivo descargado: {len(contenido)} bytes")
            
            # Actualizar progreso: procesando OCR
            progress_tracker[documento_id] = {
                'estado': 'procesando_ocr',
                'progreso': 25,
                'mensaje': 'Extrayendo texto con OCR V2... (esto puede tardar varios minutos)',
                'etapa': 'ocr'
            }
            
            # 3. Determinar tipo de archivo
            es_pdf = nombre_archivo.lower().endswith('.pdf')
            
            # 4. Procesar con OCR V2 con callback de progreso
            logger.info("🔍 Iniciando procesamiento OCR V2...")
            
            def actualizar_progreso_ocr(celda_actual, total_celdas):
                """Callback para actualizar progreso durante OCR"""
                # Progreso entre 25% y 80% basado en celdas procesadas
                progreso_ocr = 25 + int((celda_actual / total_celdas) * 55)
                mensaje = f'Procesadas {celda_actual}/{total_celdas} celdas'
                
                # Actualizar en memoria
                progress_tracker[documento_id] = {
                    'estado': 'procesando_ocr',
                    'progreso': progreso_ocr,
                    'mensaje': mensaje,
                    'etapa': 'ocr'
                }
                
                # Actualizar en BD para persistencia
                try:
                    update_query = text("""
                        UPDATE documento_digitalizado
                        SET progreso_ocr = :progreso,
                            mensaje_progreso = :mensaje
                        WHERE id_documento = :doc_id
                    """)
                    self.db.execute(update_query, {
                        'doc_id': documento_id,
                        'progreso': progreso_ocr,
                        'mensaje': mensaje
                    })
                    self.db.commit()
                    logger.info(f"💾 Progreso guardado en BD: {progreso_ocr}% - {mensaje}")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo guardar progreso en BD: {e}")
            
            resultado_ocr = self.ocr_processor.procesar_documento_completo(
                archivo_bytes=contenido,
                es_pdf=es_pdf,
                progress_callback=actualizar_progreso_ocr
            )
            
            if resultado_ocr['estado'] != 'success':
                progress_tracker[documento_id] = {
                    'estado': 'error',
                    'progreso': 100,
                    'mensaje': f"Error en OCR: {resultado_ocr.get('mensaje', 'Error desconocido')}",
                    'etapa': 'error'
                }
                logger.error(f"❌ Error en OCR: {resultado_ocr.get('mensaje')}")
                return {
                    'estado': 'error',
                    'mensaje': resultado_ocr.get('mensaje', 'Error en procesamiento OCR'),
                    'total_tuplas': 0
                }
            
            logger.info(f"✅ OCR completado: {resultado_ocr['total_tuplas']} tuplas extraídas")
            
            # Actualizar progreso: guardando
            progress_tracker[documento_id] = {
                'estado': 'guardando',
                'progreso': 85,
                'mensaje': f'Guardando {resultado_ocr["total_tuplas"]} tuplas en base de datos...',
                'etapa': 'save'
            }
            
            # 5. Actualizar BD con resultados OCR
            logger.info("💾 Guardando resultados en PostgreSQL...")
            
            # Guardar tuplas en ocr_resultado
            import json
            for idx, tupla in enumerate(resultado_ocr['tuplas'], start=1):
                # tupla es una lista simple: ['val1', 'val2', 'val3', ...]
                # Convertir a formato JSONB con nombres de columnas
                datos_ocr = {
                    f"col_{i}": valor 
                    for i, valor in enumerate(tupla)
                }
                
                insert_query = text("""
                    INSERT INTO ocr_resultado 
                    (documento_id, tupla_numero, datos_ocr, confianza, fuente_modelo, validado, estado_validacion)
                    VALUES 
                    (:doc_id, :tupla_num, CAST(:datos AS jsonb), :confianza, :modelo, false, 'pendiente')
                """)
                
                self.db.execute(insert_query, {
                    "doc_id": documento_id,
                    "tupla_num": idx,
                    "datos": json.dumps(datos_ocr),
                    "confianza": 0.85,  # Confianza promedio de EasyOCR
                    "modelo": 'OCR_V2_EasyOCR'
                })
            
            # Actualizar estado del documento
            update_query = text("""
                UPDATE documento_digitalizado
                SET estado_procesamiento = 'ocr_completado',
                    fecha_procesamiento = NOW()
                WHERE id_documento = :doc_id
            """)
            self.db.execute(update_query, {"doc_id": documento_id})
            
            self.db.commit()
            logger.info(f"✅ Resultados guardados en BD")
            
            # Actualizar progreso: completado
            progress_tracker[documento_id] = {
                'estado': 'completado',
                'progreso': 100,
                'mensaje': f'Procesamiento completado: {resultado_ocr["total_tuplas"]} tuplas extraídas',
                'etapa': 'completed'
            }
            
            logger.info("=" * 70)
            logger.info("✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
            logger.info("=" * 70)
            
            return {
                'documento_id': documento_id,
                'estado': 'success',
                'total_tuplas': resultado_ocr['total_tuplas'],
                'archivo_nombre': nombre_archivo,
                'fecha_procesamiento': datetime.now().isoformat()
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error en procesamiento desde BD: {e}")
            import traceback
            traceback.print_exc()
            
            # Actualizar progreso: error
            progress_tracker[documento_id] = {
                'estado': 'error',
                'progreso': 100,
                'mensaje': f'Error: {str(e)}',
                'etapa': 'error'
            }
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar documento: {str(e)}"
            )
    
    def obtener_progreso(self, documento_id: int) -> Dict[str, Any]:
        """
        Obtiene el progreso actual del procesamiento de un documento.
        Primero intenta leer de BD (más confiable), luego de memoria.
        
        Args:
            documento_id: ID del documento
            
        Returns:
            Dict con información de progreso
        """
        # Primero verificar en BD (fuente de verdad)
        from sqlalchemy import text
        query = text("""
            SELECT estado_procesamiento, progreso_ocr, mensaje_progreso
            FROM documento_digitalizado
            WHERE id_documento = :doc_id
        """)
        result = self.db.execute(query, {"doc_id": documento_id}).fetchone()
            
        if not result:
            return {
                'estado': 'no_encontrado',
                'progreso': 0,
                'mensaje': 'Documento no encontrado',
                'etapa': 'none'
            }
        
        estado_bd, progreso_bd, mensaje_bd = result[0], result[1] or 0, result[2] or ''
        
        logger.info(f"📊 Consultando progreso doc {documento_id}: estado_bd={estado_bd}, progreso={progreso_bd}, mensaje='{mensaje_bd}'")
        
        # Si está en procesamiento y tiene progreso, devolverlo
        if estado_bd == 'procesando' and progreso_bd > 0:
            respuesta = {
                'estado': 'procesando_ocr',
                'progreso': progreso_bd,
                'mensaje': mensaje_bd or f'Procesando OCR: {progreso_bd}%',
                'etapa': 'ocr'
            }
            logger.info(f"✅ Devolviendo progreso desde BD: {respuesta}")
            return respuesta
        
        # Si hay info en memoria, usarla
        if documento_id in progress_tracker:
            logger.info(f"✅ Devolviendo progreso desde memoria")
            return progress_tracker[documento_id]
        
        # Mapear estado de BD a respuesta
        if estado_bd == 'ocr_completado':
            return {
                'estado': 'completado',
                'progreso': 100,
                'mensaje': 'Procesamiento completado',
                'etapa': 'completed'
            }
        else:
            return {
                'estado': 'pendiente',
                'progreso': 0,
                'mensaje': 'Esperando procesamiento',
                'etapa': 'pending'
            }


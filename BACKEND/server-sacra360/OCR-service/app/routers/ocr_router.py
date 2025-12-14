"""
Router OCR - Endpoints para procesamiento de documentos
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Optional
import logging

from ..controllers.ocr_controller import OcrController
from ..services.database_service import get_database

logger = logging.getLogger(__name__)

# Router API
api_router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])


@api_router.post("/procesar", summary="Procesar documento con OCR V2")
async def procesar_documento(
    file: UploadFile = File(..., description="Archivo PDF o imagen para procesar"),
    db = Depends(get_database)
):
    """
    Procesa un documento (PDF o imagen) con OCR V2 y guarda los resultados.
    
    **Flujo**:
    1. Valida el archivo subido
    2. Extrae tuplas usando OCR V2 (EasyOCR)
    3. Guarda el archivo en MinIO
    4. Guarda resultados en PostgreSQL
    5. Retorna resumen de procesamiento
    
    **Formatos soportados**: PDF, JPG, PNG
    
    **Respuesta**:
    - `documento_id`: ID del documento en base de datos
    - `estado`: Estado del procesamiento
    - `total_tuplas`: Número de tuplas extraídas
    - `archivo_url`: URL del archivo en MinIO
    """
    try:
        controller = OcrController(db)
        resultado = await controller.procesar_documento(file)
        return resultado
    
    except Exception as e:
        logger.error(f"❌ Error en endpoint /procesar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar documento: {str(e)}"
        )


@api_router.get("/resultados/{documento_id}", summary="Obtener resultados de un documento")
async def obtener_resultados(
    documento_id: int,
    db = Depends(get_database)
):
    """
    Obtiene los resultados de OCR de un documento procesado.
    
    **Parámetros**:
    - `documento_id`: ID del documento en base de datos
    
    **Respuesta**:
    - Tuplas extraídas
    - Metadatos del procesamiento
    - URL del archivo original
    """
    try:
        controller = OcrController(db)
        resultado = await controller.obtener_resultados(documento_id)
        
        if not resultado:
            raise HTTPException(
                status_code=404,
                detail=f"Documento {documento_id} no encontrado"
            )
        
        return resultado
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en endpoint /resultados: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resultados: {str(e)}"
        )


@api_router.post("/procesar-desde-bd/{documento_id}", summary="Procesar documento que ya está en BD/MinIO")
async def procesar_desde_bd(
    documento_id: int,
    db = Depends(get_database)
):
    """
    Procesa un documento que ya fue subido a la base de datos y MinIO.
    Este endpoint es llamado por Documents-service después de guardar el archivo.
    
    **Flujo**:
    1. Obtiene la información del documento desde BD
    2. Descarga el archivo desde MinIO
    3. Procesa con OCR V2
    4. Guarda resultados en ocr_resultado
    5. Actualiza el estado del documento
    
    **Parámetros**:
    - `documento_id`: ID del documento en documento_digitalizado
    
    **Respuesta**:
    - Estado del procesamiento
    - Total de tuplas extraídas
    - Información del documento
    """
    try:
        controller = OcrController(db)
        resultado = await controller.procesar_desde_bd(documento_id)
        return resultado
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en endpoint /procesar-desde-bd: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar documento: {str(e)}"
        )


@api_router.get("/progreso/{documento_id}", summary="Obtener progreso de procesamiento")
async def obtener_progreso(
    documento_id: int,
    db = Depends(get_database)
):
    """
    Obtiene el progreso actual del procesamiento OCR de un documento.
    
    **Parámetros**:
    - `documento_id`: ID del documento
    
    **Respuesta**:
    - `estado`: Estado actual (iniciando, descargando, procesando_ocr, guardando, completado, error)
    - `progreso`: Porcentaje de avance (0-100)
    - `mensaje`: Descripción del estado actual
    - `etapa`: Etapa técnica del proceso
    
    **Estados posibles**:
    - `iniciando` (5%): Iniciando procesamiento
    - `descargando` (15%): Descargando archivo desde MinIO
    - `procesando_ocr` (25-80%): Ejecutando OCR V2 (puede tardar varios minutos)
    - `guardando` (85%): Guardando resultados en base de datos
    - `completado` (100%): Proceso finalizado exitosamente
    - `error` (100%): Error en el proceso
    """
    try:
        controller = OcrController(db)
        progreso = controller.obtener_progreso(documento_id)
        return progreso
    
    except Exception as e:
        logger.error(f"❌ Error en endpoint /progreso: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener progreso: {str(e)}"
        )


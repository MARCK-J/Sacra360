"""
Controlador para digitalización de documentos
Maneja el flujo: Upload → MinIO → BD → OCR → Resultados
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
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
    procesar_automaticamente: bool = Form(True, description="Procesar con OCR automáticamente"),
    db: Session = Depends(get_db)
):
    """
    Sube un documento y opcionalmente lo procesa con OCR
    
    Flujo:
    1. Valida el archivo
    2. Sube a MinIO
    3. Guarda metadata en BD (documento_digitalizado)
    4. Si procesar_automaticamente=True, llama al OCR service
    5. Guarda resultados OCR en BD (ocr_resultado)
    """
    
    try:
        logger.info(f"Iniciando upload de documento: {archivo.filename}")
        
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
                COUNT(o.id_ocr) as total_tuplas,
                SUM(CASE WHEN o.estado_validacion = 'pendiente' THEN 1 ELSE 0 END) as tuplas_pendientes,
                SUM(CASE WHEN o.estado_validacion = 'validado' THEN 1 ELSE 0 END) as tuplas_validadas
            FROM documento_digitalizado d
            INNER JOIN ocr_resultado o ON d.id_documento = o.documento_id
            WHERE o.estado_validacion = 'pendiente'
            GROUP BY d.id_documento, d.nombre_archivo, d.libros_id, d.tipo_sacramento, 
                     d.imagen_url, d.fecha_procesamiento
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
                "fecha": row[5].strftime("%Y-%m-%d %H:%M") if row[5] else None,
                "total_tuplas": row[6],
                "tuplas_pendientes": row[7],
                "tuplas_validadas": row[8],
                "progreso": int((row[8] / row[6] * 100)) if row[6] > 0 else 0
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
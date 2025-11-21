from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
import asyncio
from datetime import datetime

from ..dto.ocr_dto import (
    OcrProcessRequest, OcrProcessResponse, HealthCheckResponse
)
from ..services.ocr_service import OcrService
from ..services.database_service import DatabaseService, get_database
from ..services.minio_service import minio_service

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/ocr",
    tags=["OCR"]
)

# Instancia global del servicio OCR
ocr_service = OcrService()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check del servicio OCR"""
    try:
        # Verificar dependencias básicas
        dependencies = {
            "tesseract": "available",
            "opencv": "available", 
            "database": "available",
            "minio": "available"
        }
        
        return HealthCheckResponse(
            service="OCR Service - Sacra360",
            version="1.0.0",
            status="healthy",
            timestamp=datetime.utcnow(),
            dependencies=dependencies
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Service unhealthy: {str(e)}"
        )

@router.post("/procesar", response_model=OcrProcessResponse)
async def procesar_imagen_ocr(
    archivo: UploadFile = File(..., description="Imagen o PDF a procesar"),
    libros_id: int = Form(..., description="ID del libro al que pertenece"),
    tipo_sacramento: int = Form(2, description="Tipo de sacramento (1=bautizo, 2=confirmacion, etc.)"),
    guardar_en_bd: bool = Form(True, description="Si guardar en base de datos"),
    db: Session = Depends(get_database)
):
    """
    Procesa una imagen o PDF con OCR para extraer registros de confirmación
    
    - **archivo**: Imagen (JPG, PNG) o PDF a procesar
    - **libros_id**: ID del libro en la base de datos
    - **tipo_sacramento**: Tipo de sacramento (por defecto confirmación = 2)
    - **guardar_en_bd**: Si guardar los resultados en base de datos
    
    Retorna los registros extraídos con información de calidad y métricas.
    """
    
    try:
        logger.info(f"Iniciando procesamiento OCR para archivo: {archivo.filename}")
        
        # Validar tipo de archivo
        if not archivo.content_type or not any([
            archivo.content_type.startswith('image/'),
            archivo.content_type == 'application/pdf'
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de archivo no soportado. Solo se aceptan imágenes (JPG, PNG) y PDFs."
            )
        
        # Leer contenido del archivo
        contenido_archivo = await archivo.read()
        
        if len(contenido_archivo) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío"
            )
        
        logger.info(f"Archivo leído: {len(contenido_archivo)} bytes")
        
        # Subir archivo a Minio
        try:
            minio_result = minio_service.upload_file(
                file_data=contenido_archivo,
                file_name=archivo.filename,
                content_type=archivo.content_type
            )
            logger.info(f"Archivo subido a Minio: {minio_result['object_name']}")
        except Exception as e:
            logger.error(f"Error subiendo archivo a Minio: {str(e)}")
            # Continuar sin Minio si falla (modo degradado)
            minio_result = None
        
        # Configurar servicio de base de datos
        db_service = DatabaseService(db) if guardar_en_bd else None
        
        # Procesar imagen con OCR
        resultado = ocr_service.procesar_imagen(
            imagen_bytes=contenido_archivo,
            libros_id=libros_id,
            tipo_sacramento=tipo_sacramento,
            guardar_en_bd=guardar_en_bd,
            db_service=db_service,
            minio_info=minio_result  # Pasar información de Minio
        )
        
        logger.info(f"Procesamiento completado. Tuplas extraídas: {resultado.total_tuplas}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error durante procesamiento OCR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el procesamiento: {str(e)}"
        )

@router.post("/procesar-interno", response_model=OcrProcessResponse)
async def procesar_imagen_ocr_interno(
    archivo: UploadFile = File(..., description="Imagen o PDF a procesar"),
    libros_id: int = Form(..., description="ID del libro al que pertenece"),
    tipo_sacramento: int = Form(2, description="Tipo de sacramento (1=bautizo, 2=confirmacion, etc.)"),
    documento_id: int = Form(..., description="ID del documento ya creado en BD"),
    db: Session = Depends(get_database)
):
    """
    Procesa OCR de una imagen sin subir a MinIO (para uso interno desde Documents-service)
    
    Este endpoint asume que el archivo ya fue subido a MinIO y registrado en BD.
    Solo procesa el OCR y actualiza los resultados.
    
    - **archivo**: Imagen (JPG, PNG) o PDF a procesar
    - **libros_id**: ID del libro en la base de datos
    - **tipo_sacramento**: Tipo de sacramento (por defecto confirmación = 2)
    - **documento_id**: ID del documento ya existente en documento_digitalizado
    
    Retorna los registros extraídos con información de calidad y métricas.
    """
    
    try:
        logger.info(f"Iniciando procesamiento OCR interno para documento ID: {documento_id}")
        
        # Validar tipo de archivo
        if not archivo.content_type or not any([
            archivo.content_type.startswith('image/'),
            archivo.content_type == 'application/pdf'
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de archivo no soportado. Solo se aceptan imágenes (JPG, PNG) y PDFs."
            )
        
        # Leer contenido del archivo
        contenido_archivo = await archivo.read()
        
        if len(contenido_archivo) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío"
            )
        
        logger.info(f"Archivo leído para OCR: {len(contenido_archivo)} bytes")
        
        # Configurar servicio de base de datos
        db_service = DatabaseService(db)
        
        # Procesar imagen con OCR (sin subir a MinIO)
        resultado = ocr_service.procesar_imagen_interno(
            imagen_bytes=contenido_archivo,
            documento_id=documento_id,
            libros_id=libros_id,
            tipo_sacramento=tipo_sacramento,
            db_service=db_service
        )
        
        logger.info(f"Procesamiento OCR interno completado. Tuplas extraídas: {resultado.total_tuplas}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error durante procesamiento OCR interno: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el procesamiento OCR: {str(e)}"
        )

@router.get("/documento/{documento_id}", response_model=dict)
async def obtener_documento_ocr(
    documento_id: int,
    db: Session = Depends(get_database)
):
    """
    Obtiene un documento procesado y sus resultados OCR
    """
    try:
        db_service = DatabaseService(db)
        
        # Obtener documento
        documento = db_service.obtener_documento(documento_id)
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento con ID {documento_id} no encontrado"
            )
        
        # Obtener resultados OCR
        resultados_ocr = db_service.obtener_resultados_ocr(documento_id)
        
        return {
            "documento": {
                "id_documento": documento.id_documento,
                "libros_id": documento.libros_id,
                "tipo_sacramento": documento.tipo_sacramento,
                "imagen_url": documento.imagen_url,
                "modelo_fuente": documento.modelo_fuente,
                "confianza": float(documento.confianza),
                "fecha_procesamiento": documento.fecha_procesamiento
            },
            "resultados_ocr": [
                {
                    "id_ocr": resultado.id_ocr,
                    "campo": resultado.campo,
                    "valor_extraido": resultado.valor_extraido,
                    "confianza": float(resultado.confianza),
                    "fuente_modelo": resultado.fuente_modelo,
                    "validado": resultado.validado
                } for resultado in resultados_ocr
            ],
            "total_campos": len(resultados_ocr)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.patch("/validar-campo/{ocr_id}")
async def validar_campo_ocr(
    ocr_id: int,
    db: Session = Depends(get_database)
):
    """
    Marca un campo OCR como validado
    """
    try:
        db_service = DatabaseService(db)
        
        resultado = db_service.validar_campo_ocr(ocr_id)
        
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campo OCR con ID {ocr_id} no encontrado"
            )
        
        return {
            "success": True,
            "message": f"Campo OCR {ocr_id} marcado como validado"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al validar campo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.post("/procesar-desde-bd/{documento_id}", response_model=OcrProcessResponse)
async def procesar_documento_desde_bd(
    documento_id: int,
    db: Session = Depends(get_database)
):
    """
    Procesa OCR de un documento que ya está en la base de datos y MinIO
    
    - **documento_id**: ID del documento existente en documento_digitalizado
    
    Este endpoint:
    1. Busca el documento en la BD
    2. Descarga el archivo desde MinIO usando la imagen_url
    3. Procesa el OCR
    4. Guarda los resultados en ocr_resultado
    """
    
    try:
        logger.info(f"Iniciando procesamiento OCR desde BD para documento ID: {documento_id}")
        
        # Obtener documento de la BD
        db_service = DatabaseService(db)
        documento = db_service.obtener_documento(documento_id)
        
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento con ID {documento_id} no encontrado"
            )
        
        # Descargar archivo desde MinIO usando el cliente MinIO
        try:
            from ..services.minio_service import minio_service
            from io import BytesIO
            
            # Extraer object_name de la URL: http://minio:9000/bucket/object_path
            url_parts = documento.imagen_url.split('/')
            object_name = '/'.join(url_parts[-2:])  # documents/filename.png
            
            logger.info(f"Descargando archivo desde MinIO - object: {object_name}")
            
            # Usar el cliente MinIO para descargar el archivo
            file_data = minio_service.download_file(object_name)
            archivo_bytes = file_data
            archivo_nombre = url_parts[-1]  # filename.png
            
        except Exception as e:
            logger.error(f"Error descargando archivo desde MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error descargando archivo: {str(e)}"
            )
        
        # Procesar OCR usando el método correcto para documentos existentes
        resultado = ocr_service.procesar_imagen_interno(
            imagen_bytes=archivo_bytes,
            documento_id=documento_id,
            libros_id=documento.libros_id,
            tipo_sacramento=documento.tipo_sacramento,
            db_service=db_service
        )
        
        logger.info(f"Procesamiento OCR completado para documento {documento_id}. Tuplas extraídas: {resultado.total_tuplas}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error durante procesamiento OCR desde BD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el procesamiento OCR: {str(e)}"
        )

@router.get("/test")
async def test_endpoint():
    """
    Endpoint de prueba para verificar que el servicio funciona
    """
    return {
        "message": "OCR Service funcionando correctamente",
        "timestamp": datetime.utcnow(),
        "service": "OCR-service",
        "version": "1.0.0"
    }
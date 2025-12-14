"""
OCR Service - Sacra360
Microservicio especializado en reconocimiento óptico de caracteres (OCR)
Puerto: 8003
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime

# Importar configuración y routers
from .utils.config import settings
from .routers.ocr_router import api_router

# Configuración de logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title=settings.service_name,
    description="Microservicio especializado en reconocimiento óptico de caracteres para documentos sacramentales. "
               "Procesa imágenes de registros de confirmación, bautizo y otros sacramentos, "
               "extrayendo información estructurada con alta precisión.",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "OCR",
            "description": "Endpoints para procesamiento de imágenes con OCR"
        },
        {
            "name": "Health",
            "description": "Endpoints de monitoreo y salud del servicio"
        }
    ]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router)

@app.get("/")
async def root():
    """Endpoint raíz del servicio"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "port": settings.service_port,
        "description": "Microservicio especializado en reconocimiento óptico de caracteres para documentos sacramentales",
        "timestamp": datetime.utcnow(),
        "docs_url": "/docs",
        "health_check": "/health",
        "endpoints": {
            "procesar": "/api/v1/ocr/procesar",
            "resultados": "/api/v1/ocr/resultados/{documento_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check para Docker"""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "timestamp": datetime.utcnow()
    }

@app.get("/status")
async def service_status():
    """Status detallado del servicio"""
    try:
        return {
            "service": settings.service_name,
            "version": settings.service_version,
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "config": {
                "ocr_language": settings.ocr_language,
                "max_file_size_mb": settings.max_file_size // (1024 * 1024),
                "supported_file_types": settings.allowed_file_types
            },
            "capabilities": [
                "OCR de registros de confirmación",
                "Extracción de tuplas estructuradas", 
                "Correcciones automáticas de errores comunes",
                "Métricas de calidad automáticas",
                "Almacenamiento en base de datos",
                "Validación de campos extraídos"
            ]
        }
    except Exception as e:
        logger.error(f"Error en status check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

# Manejo de errores globales
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejo global de excepciones"""
    logger.error(f"Error no manejado: {str(exc)}")
    return {
        "error": "Error interno del servidor",
        "detail": str(exc),
        "timestamp": datetime.utcnow(),
        "service": settings.service_name
    }

if __name__ == "__main__":
    logger.info(f"Iniciando {settings.service_name} v{settings.service_version}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=settings.service_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
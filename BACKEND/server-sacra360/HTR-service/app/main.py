"""
HTR Service - Sacra360
Microservicio especializado en reconocimiento de texto manuscrito (HTR)
Puerto: 8004
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from typing import Optional, List
import logging
from datetime import datetime

# Importar configuración centralizada
try:
    from .utils.config import settings
except ImportError:
    from utils.config import settings

# Configuración de logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title=settings.service_name,
    description="Microservicio especializado en reconocimiento de texto manuscrito para documentos sacramentales. "
               "Procesa imágenes de registros manuscritos históricos usando deep learning y redes neuronales "
               "especializadas (HTR_Sacra360).",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "HTR",
            "description": "Endpoints para procesamiento de texto manuscrito con HTR"
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

# Security
security = HTTPBearer()

# Variable global para HTR Processor (se inicializa una sola vez)
htr_processor_instance = None

@app.on_event("startup")
async def startup_event():
    """Inicializar recursos al arrancar el servicio"""
    global htr_processor_instance
    logger.info("🚀 Iniciando HTR Service...")
    logger.info("📦 Inicializando HTR Processor (esto puede tomar varios minutos)...")
    
    try:
        from services.htr_processor import HTRProcessor
        htr_processor_instance = HTRProcessor()
        logger.info("✅ HTR Processor inicializado correctamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar HTR Processor: {str(e)}")
        raise

def get_htr_processor():
    """Dependency para obtener instancia del HTR Processor"""
    if htr_processor_instance is None:
        raise HTTPException(status_code=503, detail="HTR Processor no inicializado")
    return htr_processor_instance

# Importar routers
try:
    from routers import htr_router
except ImportError:
    from .routers import htr_router

# Registrar routers
app.include_router(htr_router.router)

@app.get("/")
async def root():
    """Endpoint raíz del servicio"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "port": settings.service_port,
        "description": "Microservicio especializado en reconocimiento de texto manuscrito (HTR_Sacra360)",
        "timestamp": datetime.utcnow(),
        "docs_url": "/docs",
        "health_check": "/health",
        "model": "HTR_Sacra360 con alternancia inteligente",
        "endpoints": {
            "procesar": "/api/v1/htr/procesar",
            "resultados": "/api/v1/htr/resultados/{documento_id}"
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
                "htr_model_path": settings.htr_model_path,
                "confidence_threshold": settings.htr_confidence_threshold,
                "max_file_size_mb": settings.max_file_size // (1024 * 1024),
                "supported_file_types": settings.allowed_file_types
            },
            "capabilities": [
                "HTR de registros manuscritos",
                "Extracción de tuplas estructuradas",
                "Procesamiento de documentos históricos",
                "Soporte para múltiples sacramentos"
            ]
        }
    except Exception as e:
        logger.error(f"Error al obtener status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
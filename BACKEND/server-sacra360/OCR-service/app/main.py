"""
OCR Service - Sacra360
Microservicio especializado en reconocimiento óptico de caracteres (OCR)
Puerto: 8003
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from typing import Optional, List
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="OCR Service - Sacra360",
    description="Microservicio especializado en reconocimiento óptico de caracteres para documentos sacramentales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Importar routers (se crearán posteriormente)
# from .routers import ocr_router

@app.get("/")
async def root():
    """Endpoint raíz del servicio"""
    return {
        "service": "OCR Service",
        "version": "1.0.0",
        "status": "running",
        "port": 8003,
        "description": "Microservicio especializado en reconocimiento óptico de caracteres",
        "capabilities": [
            "text_extraction",
            "image_preprocessing",
            "document_analysis", 
            "multiple_languages",
            "batch_processing"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check del servicio"""
    return {
        "status": "healthy",
        "service": "ocr-service",
        "timestamp": "2024-01-01T00:00:00Z",
        "dependencies": {
            "tesseract": "available",
            "opencv": "available",
            "pillow": "available"
        }
    }

@app.get("/capabilities")
async def get_capabilities():
    """Obtener capacidades del servicio OCR"""
    return {
        "supported_formats": ["pdf", "jpg", "jpeg", "png", "tiff", "bmp"],
        "supported_languages": ["spa", "eng", "lat"],  # Español, Inglés, Latín
        "max_file_size": "10MB",
        "batch_limit": 50,
        "preprocessing_options": [
            "deskew",
            "noise_removal", 
            "contrast_enhancement",
            "binarization"
        ]
    }

# Incluir routers cuando se implementen
# app.include_router(ocr_router.router, prefix="/api/v1/ocr", tags=["OCR"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
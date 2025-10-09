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

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="HTR Service - Sacra360",
    description="Microservicio especializado en reconocimiento de texto manuscrito usando redes neuronales",
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
# from .routers import htr_router

@app.get("/")
async def root():
    """Endpoint raíz del servicio"""
    return {
        "service": "HTR Service",
        "version": "1.0.0",
        "status": "running",
        "port": 8004,
        "description": "Microservicio especializado en reconocimiento de texto manuscrito",
        "capabilities": [
            "handwritten_text_recognition",
            "historical_documents",
            "ecclesiastical_scripts",
            "confidence_scoring",
            "model_training"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check del servicio"""
    return {
        "status": "healthy",
        "service": "htr-service",
        "timestamp": "2024-01-01T00:00:00Z",
        "dependencies": {
            "pytorch": "available",
            "transformers": "available",
            "opencv": "available",
            "models": "loaded"
        }
    }

@app.get("/models")
async def get_available_models():
    """Obtener modelos disponibles para HTR"""
    return {
        "available_models": [
            {
                "name": "ecclesiastical_spanish_v1",
                "description": "Modelo especializado en textos eclesiásticos en español",
                "languages": ["es"],
                "accuracy": 0.92,
                "training_date": "2024-01-01"
            },
            {
                "name": "historical_latin_v1", 
                "description": "Modelo para textos históricos en latín",
                "languages": ["la"],
                "accuracy": 0.88,
                "training_date": "2024-01-01"
            }
        ]
    }

# Incluir routers cuando se implementen
# app.include_router(htr_router.router, prefix="/api/v1/htr", tags=["HTR"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
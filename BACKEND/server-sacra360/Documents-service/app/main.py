"""
Documents Service - Sacra360
Microservicio para gestión de documentos sacramentales
Puerto: 8002
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from typing import Optional
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Documents Service - Sacra360",
    description="Microservicio para gestión de documentos sacramentales del Arzobispado",
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
# from .routers import documents_router, sacraments_router

@app.get("/")
async def root():
    """Endpoint raíz del servicio"""
    return {
        "service": "Documents Service",
        "version": "1.0.0",
        "status": "running",
        "port": 8002,
        "description": "Microservicio para gestión de documentos sacramentales"
    }

@app.get("/health")
async def health_check():
    """Health check del servicio"""
    return {
        "status": "healthy",
        "service": "documents-service",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Incluir routers cuando se implementen
# app.include_router(documents_router.router, prefix="/api/v1/documents", tags=["Documents"])
# app.include_router(sacraments_router.router, prefix="/api/v1/sacraments", tags=["Sacraments"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
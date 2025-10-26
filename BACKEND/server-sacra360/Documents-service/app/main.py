"""
Documents Service - Sacra360
Microservicio para gestión de documentos sacramentales
Puerto: 8002
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os

# Importar routers
from app.controllers.persona_controller import router as persona_router
from app.controllers.libro_controller import router as libro_router

# Importar configuración de base de datos y modelos
from app.database import engine, Base
from app.models import PersonaModel, LibroModel

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear las tablas al inicializar
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas exitosamente")
except Exception as e:
    logger.error(f"Error al crear tablas: {e}")

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
    try:
        # Verificar conexión a base de datos
        from app.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "service": "documents-service",
            "version": "1.0.0",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Incluir routers
app.include_router(persona_router, prefix="/api/v1")
app.include_router(libro_router, prefix="/api/v1")

# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8002))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
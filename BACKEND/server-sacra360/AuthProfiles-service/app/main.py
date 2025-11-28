"""
AuthProfiles Service - Microservicio de Autenticación y Perfiles
Sistema Sacra360 - Gestión de Archivos Sacramentales

Puerto: 8004
Responsabilidades:
- Autenticación de usuarios (JWT)
- Gestión de perfiles de usuario
- Control de roles y permisos
- Sesiones y tokens JWT
- Auditoría de accesos
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.routers.auth_router_adapted import router as auth_router
from app.routers.profiles_router import router as profiles_router
from app.database import init_db

# Función para verificar conexión DB
def check_db_connection():
    """Verificar conexión a la base de datos"""
    try:
        from app.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Error conectando a BD: {e}")
        return False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida del servicio"""
    # Startup
    logger.info("🔐 AuthProfiles Service iniciando...")
    
    # Verificar conexión a la base de datos
    if check_db_connection():
        logger.info("✅ Conexión a BD exitosa")
        # Inicializar tablas si no existen
        try:
            init_db()
            logger.info("✅ Tablas de BD inicializadas")
        except Exception as e:
            logger.error(f"❌ Error al inicializar tablas: {e}")
    else:
        logger.error("❌ No se pudo conectar a la base de datos")
    
    logger.info("🚀 AuthProfiles Service iniciado correctamente")
    
    yield
    
    # Shutdown
    logger.info("👋 AuthProfiles Service detenido")


app = FastAPI(
    title="AuthProfiles API - Sacra360",
    description="Microservicio de autenticación y gestión de perfiles para el sistema de archivos sacramentales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8002",
        "http://localhost:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router, tags=["Autenticación"])
app.include_router(profiles_router, prefix="/api/v1/profiles", tags=["Perfiles"])


@app.get("/")
async def root():
    """Endpoint raíz del servicio"""
    return {
        "service": "AuthProfiles Service",
        "version": "1.0.0",
        "status": "active",
        "port": 8001,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {
        "service": "AuthProfiles",
        "status": "healthy",
        "port": 8001,
        "database": "connected"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
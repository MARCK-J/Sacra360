"""
AuthProfiles Service - Microservicio de Autenticación y Perfiles
Sistema Sacra360 - Gestión de Archivos Sacramentales

Puerto: 8001
Responsabilidades:
- Autenticación de usuarios (sacerdotes, administrativos)
- Gestión de perfiles de usuario
- Control de roles y permisos eclesiásticos
- Sesiones y tokens JWT
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.routers.auth_router import router as auth_router
from app.routers.profiles_router import router as profiles_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida del servicio"""
    # Startup
    print("🔐 AuthProfiles Service iniciado")
    yield
    # Shutdown
    print("👋 AuthProfiles Service detenido")


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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profiles_router, prefix="/api/profiles", tags=["Profiles"])


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
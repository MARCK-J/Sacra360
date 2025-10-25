from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from .core.config import settings
from .api import usuarios, personas, sacramentos, documentos, auditoria, instituciones

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    logger.info("🚀 Iniciando Sacra360 API...")
    logger.info(f"🌍 Entorno: {'Desarrollo' if settings.debug else 'Producción'}")
    logger.info(f"🔧 Versión: {settings.version}")
    
    yield
    
    logger.info("🛑 Cerrando Sacra360 API...")


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de hosts confiables (opcional)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )


# Middleware personalizado para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requests"""
    start_time = time.time()
    
    # Log del request entrante
    logger.info(f"📥 {request.method} {request.url}")
    
    # Procesar el request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log del response
        logger.info(
            f"📤 {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        # Agregar header de tiempo de procesamiento
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.4f}s"
        )
        raise


# Manejadores de excepciones globales
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para 404"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Recurso no encontrado",
            "detail": "La URL solicitada no existe en el servidor",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Manejador personalizado para errores internos"""
    logger.error(f"Error interno del servidor: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detail": "Ha ocurrido un error inesperado. Por favor, inténtalo más tarde.",
            "request_id": id(request)
        }
    )


# Incluir routers - Sistema Sacra360
app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(personas.router, prefix="/api/v1")
app.include_router(sacramentos.router, prefix="/api/v1")
app.include_router(documentos.router, prefix="/api/v1")
app.include_router(auditoria.router, prefix="/api/v1")
app.include_router(instituciones.router, prefix="/api/v1")


# Endpoint de salud
@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint para verificar el estado de la API.
    
    Útil para health checks y monitoreo.
    """
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": "2024-01-01T00:00:00",  # Reemplazar con datetime.utcnow()
        "environment": "development" if settings.debug else "production"
    }


# Endpoint de información de la API
@app.get("/", tags=["Sistema"])
async def root():
    """
    Endpoint raíz de la API.
    
    Proporciona información básica sobre la API.
    """
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.version,
        "description": settings.description,
        "docs_url": "/docs" if settings.debug else "Documentación no disponible en producción",
        "status": "operational"
    }


# Endpoint para obtener información de la API
@app.get("/api/v1/info", tags=["Sistema"])
async def api_info():
    """
    Información detallada de la API.
    """
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": settings.description,
        "endpoints": {
            "authentication": "/api/v1/usuarios/login",
            "registration": "/api/v1/usuarios/register",
            "usuarios": "/api/v1/usuarios/",
            "personas": "/api/v1/personas/",
            "sacramentos": "/api/v1/sacramentos/",
            "instituciones": "/api/v1/instituciones/",
            "documentos": "/api/v1/documentos/",
            "auditoria": "/api/v1/auditoria/",
            "health": "/health",
            "docs": "/docs" if settings.debug else None
        },
        "features": [
            "Gestión de usuarios con roles parroquiales",
            "Registro y administración de personas",
            "Gestión completa de sacramentos (bautizo, confirmación, matrimonio)",
            "Administración de instituciones parroquiales",
            "Digitalización y procesamiento OCR de documentos",
            "Sistema de auditoría y trazabilidad",
            "Autenticación JWT con roles",
            "Validación con Pydantic v2",
            "Documentación automática",
            "Manejo de errores personalizado",
            "CORS configurado",
            "Logging detallado de requests",
            "Paginación y filtros avanzados",
            "Búsquedas específicas por tipo de sacramento"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Iniciando servidor en {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
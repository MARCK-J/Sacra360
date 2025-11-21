from fastapi import APIRouter
from ..controllers.ocr_controller import router as ocr_controller

# Router principal que incluye todos los endpoints de OCR
api_router = APIRouter()

# Incluir el controlador de OCR
api_router.include_router(ocr_controller)

# Router de salud general del servicio
health_router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@health_router.get("/")
async def service_health():
    """Health check general del servicio"""
    return {
        "service": "OCR Service - Sacra360",
        "status": "running",
        "version": "1.0.0",
        "description": "Microservicio especializado en reconocimiento óptico de caracteres para documentos sacramentales"
    }

# Incluir health router en el router principal
api_router.include_router(health_router)
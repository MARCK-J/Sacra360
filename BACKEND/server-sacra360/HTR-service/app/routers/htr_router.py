"""
HTR Router - Endpoints HTTP para el servicio HTR
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from controllers.htr_controller import HTRController
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/htr", tags=["HTR"])

# Importar la función get_htr_processor desde main
# Se hace lazy import para evitar circular dependency
def get_htr_processor_dependency():
    from main import get_htr_processor
    return get_htr_processor()


@router.post("/procesar-desde-bd/{documento_id}")
async def procesar_documento_desde_bd(
    documento_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Procesa un documento almacenado en BD usando HTR
    
    Args:
        documento_id: ID del documento en documento_digitalizado
        
    Returns:
        Estado del procesamiento
    """
    htr_processor = get_htr_processor_dependency()
    controller = HTRController(db, htr_processor)
    return await controller.procesar_desde_bd(documento_id)


@router.get("/progreso/{documento_id}")
async def obtener_progreso(
    documento_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtiene el progreso actual del procesamiento HTR de un documento
    
    Args:
        documento_id: ID del documento
        
    Returns:
        Información de progreso
    """
    htr_processor = get_htr_processor_dependency()
    controller = HTRController(db, htr_processor)
    return controller.obtener_progreso(documento_id)


@router.get("/health")
async def health_check():
    """Health check del servicio HTR"""
    return {
        "status": "healthy",
        "service": "HTR-service",
        "model": "HTR_Sacra360"
    }

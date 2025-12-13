"""
Controller para registro de Bautizos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dto.bautizo_dto import BautizoCreateDTO, BautizoResponseDTO
from app.services.bautizo_service import BautizoService

router = APIRouter(prefix="/bautizos", tags=["Bautizos"])


@router.post("/",
             response_model=BautizoResponseDTO,
             status_code=status.HTTP_201_CREATED,
             summary="Registrar nuevo bautizo",
             description="Crea un nuevo registro de bautizo con persona y sacramento")
def crear_bautizo(
    dto: BautizoCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo bautizo.
    
    Crea:
    - 1 registro en tabla `personas` (bautizado)
    - 1 registro en tabla `sacramentos` (tipo_id=1)
    
    Returns:
        BautizoResponseDTO con persona_id y sacramento_id generados
    
    Raises:
        - 400 BAD REQUEST: Si hay error de validación
        - 500 INTERNAL SERVER ERROR: Si hay error en BD
    """
    service = BautizoService(db)
    
    try:
        resultado = service.crear_bautizo(dto)
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

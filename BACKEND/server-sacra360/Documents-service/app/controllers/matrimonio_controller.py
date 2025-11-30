"""
Controller para registro de Matrimonios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dto.matrimonio_dto import MatrimonioCreateDTO, MatrimonioResponseDTO
from app.services.matrimonio_service import MatrimonioService

router = APIRouter(prefix="/matrimonios", tags=["Matrimonios"])


@router.post("/",
             response_model=MatrimonioResponseDTO,
             status_code=status.HTTP_201_CREATED,
             summary="Registrar nuevo matrimonio",
             description="Crea un nuevo registro de matrimonio con ambos cónyuges y datos específicos")
def crear_matrimonio(
    dto: MatrimonioCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo matrimonio.
    
    Crea:
    - 2 registros en tabla `personas` (esposo y esposa)
    - 1 registro en tabla `sacramentos` (tipo_id=3)
    - 1 registro en tabla `matrimonios` (con testigos y padres)
    
    Returns:
        MatrimonioResponseDTO con esposo_id, esposa_id, sacramento_id y matrimonio_id generados
    
    Raises:
        - 400 BAD REQUEST: Si hay error de validación
        - 500 INTERNAL SERVER ERROR: Si hay error en BD
    """
    service = MatrimonioService(db)
    
    try:
        resultado = service.crear_matrimonio(dto)
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

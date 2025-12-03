"""
Controller para registro de Matrimonios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.dto.matrimonio_dto import MatrimonioCreateDTO, MatrimonioResponseDTO
from app.services.matrimonio_service import MatrimonioService
from app.models.matrimonio_model import MatrimonioModel

router = APIRouter(prefix="/matrimonios", tags=["Matrimonios"])


class MatrimonioRegistroDTO(BaseModel):
    """DTO para crear solo el registro en tabla matrimonios (cuando personas ya existen)"""
    sacramento_id: int
    esposo_id: int
    esposa_id: int
    nombre_padre_esposo: str
    nombre_madre_esposo: str
    nombre_padre_esposa: str
    nombre_madre_esposa: str
    testigos: str


@router.post("/registro",
             status_code=status.HTTP_201_CREATED,
             summary="Crear solo registro de matrimonio",
             description="Inserta registro en tabla matrimonios cuando personas ya existen")
def crear_registro_matrimonio(
    dto: MatrimonioRegistroDTO,
    db: Session = Depends(get_db)
):
    """
    Crea solo el registro en tabla matrimonios.
    
    Usa este endpoint cuando las personas (esposo/esposa) ya existen en BD.
    
    Returns:
        dict con id_matrimonio generado
    """
    try:
        nuevo_matrimonio = MatrimonioModel(
            sacramento_id=dto.sacramento_id,
            esposo_id=dto.esposo_id,
            esposa_id=dto.esposa_id,
            nombre_padre_esposo=dto.nombre_padre_esposo,
            nombre_madre_esposo=dto.nombre_madre_esposo,
            nombre_padre_esposa=dto.nombre_padre_esposa,
            nombre_madre_esposa=dto.nombre_madre_esposa,
            testigos=dto.testigos
        )
        
        db.add(nuevo_matrimonio)
        db.commit()
        db.refresh(nuevo_matrimonio)
        
        return {
            "id_matrimonio": nuevo_matrimonio.id_matrimonio,
            "mensaje": "Matrimonio registrado exitosamente"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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

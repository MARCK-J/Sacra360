"""
Controller para gestión de sacramentos
Endpoints para registrar y validar sacramentos
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.dto.sacramento_dto import SacramentoCreateDTO, SacramentoResponseDTO
from app.services.sacramento_service import SacramentoService

router = APIRouter(prefix="/sacramentos", tags=["Sacramentos"])


@router.get("/check-duplicate",
             response_model=dict,
             status_code=status.HTTP_200_OK,
             summary="Verificar si existe sacramento duplicado",
             description="Valida si una persona ya tiene registrado este sacramento")
def check_duplicate_sacramento(
    persona_id: int = Query(..., description="ID de la persona", gt=0),
    tipo_id: int = Query(..., description="ID del tipo de sacramento", gt=0),
    libro_id: int = Query(..., description="ID del libro", gt=0),
    fecha_sacramento: date = Query(..., description="Fecha del sacramento (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Verifica si ya existe un sacramento para esta persona.
    
    Evita registrar:
    - Dos bautizos para la misma persona
    - Dos confirmaciones en el mismo libro
    - Dos matrimonios en la misma fecha
    
    Returns:
        - **exists**: true si ya existe, false si no existe
        - **sacramento**: datos del sacramento existente (si existe)
    """
    service = SacramentoService(db)
    resultado = service.check_duplicate(
        persona_id=persona_id,
        tipo_id=tipo_id,
        libro_id=libro_id,
        fecha_sacramento=fecha_sacramento
    )
    
    return resultado


@router.post("/",
             response_model=SacramentoResponseDTO,
             status_code=status.HTTP_201_CREATED,
             summary="Registrar nuevo sacramento",
             description="Crea un nuevo registro de sacramento con validación de duplicados")
def create_sacramento(
    dto: SacramentoCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo sacramento.
    
    Validaciones:
    - La persona no debe tener el mismo sacramento ya registrado
    - La fecha del sacramento no puede ser futura
    - Todas las FK deben existir (persona, tipo, usuario, institución, libro)
    
    Returns:
        Sacramento creado con su ID asignado
    
    Raises:
        - 409 CONFLICT: Si el sacramento ya existe
        - 400 BAD REQUEST: Si hay error de validación
    """
    service = SacramentoService(db)
    
    try:
        sacramento = service.create(
            persona_id=dto.persona_id,
            tipo_id=dto.tipo_id,
            usuario_id=dto.usuario_id,
            institucion_id=dto.institucion_id,
            libro_id=dto.libro_id,
            fecha_sacramento=dto.fecha_sacramento
        )
        
        return SacramentoResponseDTO.model_validate(sacramento)
        
    except ValueError as e:
        # Sacramento duplicado
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear sacramento: {str(e)}"
        )


@router.get("/{sacramento_id}",
            response_model=SacramentoResponseDTO,
            summary="Obtener sacramento por ID",
            description="Obtiene un sacramento específico por su ID")
def get_sacramento(
    sacramento_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un sacramento específico por su ID"""
    service = SacramentoService(db)
    sacramento = service.get_by_id(sacramento_id)
    
    if not sacramento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sacramento con ID {sacramento_id} no encontrado"
        )
    
    return SacramentoResponseDTO.model_validate(sacramento)


@router.get("/persona/{persona_id}",
            response_model=List[dict],
            summary="Obtener sacramentos de una persona",
            description="Lista todos los sacramentos registrados para una persona")
def get_sacramentos_by_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener historial de sacramentos de una persona.
    
    Útil para ver qué sacramentos ha recibido una persona:
    - Bautizo
    - Confirmación
    - Matrimonio
    """
    service = SacramentoService(db)
    sacramentos = service.get_by_persona(persona_id)
    
    return sacramentos


@router.get("/",
            response_model=List[SacramentoResponseDTO],
            summary="Listar sacramentos",
            description="Lista todos los sacramentos con paginación")
def list_sacramentos(
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: Session = Depends(get_db)
):
    """Listar todos los sacramentos con paginación"""
    service = SacramentoService(db)
    sacramentos = service.list_all(skip=skip, limit=limit)
    
    return [SacramentoResponseDTO.model_validate(s) for s in sacramentos]


@router.get("/list/details",
            response_model=List[dict],
            summary="Listar sacramentos con detalles",
            description="Lista sacramentos con información completa de personas, tipo e institución")
def list_sacramentos_with_details(
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Listar sacramentos con datos completos para visualización.
    Incluye nombres de personas, tipo de sacramento e institución.
    """
    service = SacramentoService(db)
    sacramentos = service.list_with_details(skip=skip, limit=limit)
    
    return sacramentos

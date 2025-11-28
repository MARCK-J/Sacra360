from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.dto.persona_dto import PersonaCreateDTO, PersonaUpdateDTO, PersonaResponseDTO
from app.services.persona_service import PersonaService

router = APIRouter(prefix="/personas", tags=["Personas"])

@router.get("/search",
             response_model=List[PersonaResponseDTO],
             status_code=status.HTTP_200_OK,
             summary="Buscar personas por similitud",
             description="Busca personas que coincidan con los criterios proporcionados")
def search_personas(
    nombres: Optional[str] = Query(None, description="Nombres de la persona"),
    apellido_paterno: Optional[str] = Query(None, description="Apellido paterno"),
    apellido_materno: Optional[str] = Query(None, description="Apellido materno"),
    fecha_nacimiento: Optional[date] = Query(None, description="Fecha de nacimiento (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Busca personas que coincidan con los criterios de búsqueda.
    
    Útil para encontrar si una persona ya existe antes de crear un sacramento.
    
    Returns:
        Lista de personas que coinciden con los criterios
    """
    personas = PersonaService.search(
        db=db,
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        fecha_nacimiento=fecha_nacimiento
    )
    
    return [PersonaResponseDTO.model_validate(p) for p in personas]

@router.post("/", 
             response_model=PersonaResponseDTO, 
             status_code=status.HTTP_201_CREATED,
             summary="Crear nueva persona",
             description="Crea una nueva persona con validaciones completas")
def create_persona(
    dto: PersonaCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva persona.
    
    - **nombres**: Nombres de la persona (solo letras, espacios y acentos)
    - **apellidos**: Apellidos de la persona (solo letras, espacios y acentos)
    - **fecha_nacimiento**: Fecha de nacimiento (no puede ser futura)
    - **lugar_nacimiento**: Lugar donde nació (opcional)
    - **estado_civil**: Estado civil (soltero, casado, viudo, divorciado)
    - **ocupacion**: Ocupación o profesión (opcional)
    """
    persona = PersonaService.create(db, dto)
    return PersonaResponseDTO.model_validate(persona)

@router.get("/{persona_id}", 
            response_model=PersonaResponseDTO,
            summary="Obtener persona por ID",
            description="Obtiene una persona específica por su ID")
def get_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una persona específica por su ID"""
    persona = PersonaService.get(db, persona_id)
    return PersonaResponseDTO.model_validate(persona)

@router.get("/", 
            response_model=List[PersonaResponseDTO],
            summary="Listar personas",
            description="Lista personas con filtros opcionales y paginación")
def list_personas(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar"),
    nombres: Optional[str] = Query(None, description="Filtrar por nombres (búsqueda parcial)"),
    apellido_paterno: Optional[str] = Query(None, description="Filtrar por apellido paterno"),
    apellido_materno: Optional[str] = Query(None, description="Filtrar por apellido materno"),
    db: Session = Depends(get_db)
):
    """
    Listar personas con filtros opcionales.
    
    Soporta paginación y múltiples filtros de búsqueda.
    """
    personas = PersonaService.list(
        db=db,
        skip=skip,
        limit=limit,
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno
    )
    return [PersonaResponseDTO.model_validate(p) for p in personas]

@router.get("/count/total",
            response_model=dict,
            summary="Contar personas",
            description="Cuenta el total de personas que coinciden con los filtros")
def count_personas(
    solo_activos: bool = Query(True, description="Solo contar personas activas"),
    nombres: Optional[str] = Query(None, description="Filtrar por nombres"),
    apellidos: Optional[str] = Query(None, description="Filtrar por apellidos"),
    estado_civil: Optional[str] = Query(None, description="Filtrar por estado civil"),
    fecha_desde: Optional[date] = Query(None, description="Fecha de nacimiento desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha de nacimiento hasta"),
    db: Session = Depends(get_db)
):
    """Contar personas que coinciden con los filtros especificados"""
    total = PersonaService.count(
        db=db,
        solo_activos=solo_activos,
        nombres=nombres,
        apellidos=apellidos,
        estado_civil=estado_civil,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    return {"total": total}

@router.put("/{persona_id}", 
            response_model=PersonaResponseDTO,
            summary="Actualizar persona",
            description="Actualiza los datos de una persona existente")
def update_persona(
    persona_id: int,
    dto: PersonaUpdateDTO,
    db: Session = Depends(get_db)
):
    """
    Actualizar una persona existente.
    
    Solo se actualizarán los campos proporcionados en el DTO.
    """
    persona = PersonaService.update(db, persona_id, dto)
    return PersonaResponseDTO.model_validate(persona)

@router.delete("/{persona_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Desactivar persona",
               description="Desactiva una persona (soft delete)")
def delete_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """
    Desactivar una persona (soft delete).
    
    La persona no se elimina físicamente, solo se marca como inactiva.
    """
    PersonaService.soft_delete(db, persona_id)
    return

@router.get("/search/by-name",
            response_model=List[PersonaResponseDTO],
            summary="Buscar personas por nombre",
            description="Búsqueda específica por nombres y/o apellidos")
def search_personas_by_name(
    nombres: Optional[str] = Query(None, description="Nombres a buscar"),
    apellidos: Optional[str] = Query(None, description="Apellidos a buscar"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros"),
    solo_activos: bool = Query(True, description="Solo personas activas"),
    db: Session = Depends(get_db)
):
    """Búsqueda específica por nombres y/o apellidos con coincidencia parcial"""
    personas = PersonaService.search_by_name(
        db=db,
        nombres=nombres,
        apellidos=apellidos,
        skip=skip,
        limit=limit,
        solo_activos=solo_activos
    )
    return [PersonaResponseDTO.model_validate(p) for p in personas]

@router.get("/filter/estado-civil/{estado_civil}",
            response_model=List[PersonaResponseDTO],
            summary="Filtrar por estado civil",
            description="Obtiene personas por estado civil específico")
def filter_by_estado_civil(
    estado_civil: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    solo_activos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Filtrar personas por estado civil específico"""
    personas = PersonaService.list(
        db=db,
        skip=skip,
        limit=limit,
        solo_activos=solo_activos,
        estado_civil=estado_civil
    )
    return [PersonaResponseDTO.model_validate(p) for p in personas]


@router.get("/{persona_id}/sacramentos", summary="Obtener sacramentos de una persona")
def get_sacramentos_de_persona(persona_id: int, db: Session = Depends(get_db)):
    """Devuelve la lista de sacramentos asociados a una persona"""
    try:
        sql = "SELECT s.*, ts.nombre as tipo_nombre FROM sacramentos s LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id WHERE s.persona_id = :pid ORDER BY s.fecha_sacramento DESC"
        res = db.execute(sql, {"pid": persona_id})
        rows = [dict(r._mapping) for r in res.fetchall()]
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
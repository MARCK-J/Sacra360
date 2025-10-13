"""
Endpoints para gestión de personas en el Sistema Sacra360
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date

from ..schemas.sacra360_schemas import (
    PersonaCreate, PersonaResponse, PersonaUpdate, 
    MessageResponse, BusquedaPersona
)
from .usuarios import get_current_user

# Configuración del router
router = APIRouter(prefix="/personas", tags=["Personas"])

# Simulación de base de datos en memoria
fake_personas_db = {}
persona_id_counter = 1


@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    persona_data: PersonaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Registra una nueva persona en el sistema.
    
    - **nombres**: Nombres de la persona (requerido)
    - **apellido_paterno**: Apellido paterno
    - **apellido_materno**: Apellido materno
    - **fecha_nacimiento**: Fecha de nacimiento
    - **lugar_nacimiento**: Lugar de nacimiento
    - **nombre_padre**: Nombre del padre
    - **nombre_madre**: Nombre de la madre
    """
    global persona_id_counter
    
    # Verificar si ya existe una persona similar (nombres + apellidos + fecha nacimiento)
    for persona in fake_personas_db.values():
        if (persona["nombres"].lower() == persona_data.nombres.lower() and
            persona.get("apellido_paterno", "").lower() == (persona_data.apellido_paterno or "").lower() and
            persona.get("apellido_materno", "").lower() == (persona_data.apellido_materno or "").lower() and
            persona.get("fecha_nacimiento") == persona_data.fecha_nacimiento):
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una persona con los mismos datos personales"
            )
    
    # Crear la persona
    nueva_persona = {
        "id_persona": persona_id_counter,
        "nombres": persona_data.nombres,
        "apellido_paterno": persona_data.apellido_paterno,
        "apellido_materno": persona_data.apellido_materno,
        "fecha_nacimiento": persona_data.fecha_nacimiento,
        "lugar_nacimiento": persona_data.lugar_nacimiento,
        "nombre_padre": persona_data.nombre_padre,
        "nombre_madre": persona_data.nombre_madre
    }
    
    fake_personas_db[persona_id_counter] = nueva_persona
    persona_id_counter += 1
    
    return PersonaResponse(**nueva_persona)


@router.get("/", response_model=List[PersonaResponse])
async def get_personas(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Elementos por página"),
    nombres: Optional[str] = Query(None, description="Filtrar por nombres"),
    apellido_paterno: Optional[str] = Query(None, description="Filtrar por apellido paterno"),
    apellido_materno: Optional[str] = Query(None, description="Filtrar por apellido materno"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de personas.
    
    Permite filtrar por nombres y apellidos.
    """
    # Filtrar personas
    filtered_personas = list(fake_personas_db.values())
    
    if nombres:
        nombres_lower = nombres.lower()
        filtered_personas = [
            p for p in filtered_personas 
            if nombres_lower in p["nombres"].lower()
        ]
    
    if apellido_paterno:
        apellido_lower = apellido_paterno.lower()
        filtered_personas = [
            p for p in filtered_personas 
            if p.get("apellido_paterno") and apellido_lower in p["apellido_paterno"].lower()
        ]
        
    if apellido_materno:
        apellido_lower = apellido_materno.lower()
        filtered_personas = [
            p for p in filtered_personas 
            if p.get("apellido_materno") and apellido_lower in p["apellido_materno"].lower()
        ]
    
    # Paginación
    start = (page - 1) * limit
    end = start + limit
    paginated_personas = filtered_personas[start:end]
    
    return [PersonaResponse(**persona) for persona in paginated_personas]


@router.post("/buscar", response_model=List[PersonaResponse])
async def buscar_personas(
    busqueda: BusquedaPersona,
    current_user: dict = Depends(get_current_user)
):
    """
    Búsqueda avanzada de personas.
    
    Permite combinar múltiples criterios de búsqueda.
    """
    filtered_personas = list(fake_personas_db.values())
    
    # Aplicar filtros
    if busqueda.nombres:
        nombres_lower = busqueda.nombres.lower()
        filtered_personas = [
            p for p in filtered_personas 
            if nombres_lower in p["nombres"].lower()
        ]
    
    if busqueda.apellido_paterno:
        apellido_lower = busqueda.apellido_paterno.lower()
        filtered_personas = [
            p for p in filtered_personas 
            if p.get("apellido_paterno") and apellido_lower in p["apellido_paterno"].lower()
        ]
        
    if busqueda.apellido_materno:
        apellido_lower = busqueda.apellido_materno.lower()
        filtered_personas = [
            p for p in filtered_personas 
            if p.get("apellido_materno") and apellido_lower in p["apellido_materno"].lower()
        ]
    
    if busqueda.fecha_nacimiento_desde:
        filtered_personas = [
            p for p in filtered_personas 
            if p.get("fecha_nacimiento") and p["fecha_nacimiento"] >= busqueda.fecha_nacimiento_desde
        ]
        
    if busqueda.fecha_nacimiento_hasta:
        filtered_personas = [
            p for p in filtered_personas 
            if p.get("fecha_nacimiento") and p["fecha_nacimiento"] <= busqueda.fecha_nacimiento_hasta
        ]
    
    return [PersonaResponse(**persona) for persona in filtered_personas]


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona_by_id(
    persona_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una persona por su ID.
    """
    persona = fake_personas_db.get(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona no encontrada"
        )
    
    return PersonaResponse(**persona)


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    persona_update: PersonaUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza la información de una persona.
    
    Requiere permisos de sacerdote, secretario o administrador.
    """
    # Verificar permisos
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote", "secretario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar personas"
        )
    
    persona = fake_personas_db.get(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona no encontrada"
        )
    
    # Obtener datos a actualizar
    update_data = persona_update.model_dump(exclude_unset=True)
    
    # Actualizar campos
    for field, value in update_data.items():
        persona[field] = value
    
    return PersonaResponse(**persona)


@router.delete("/{persona_id}", response_model=MessageResponse)
async def delete_persona(
    persona_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina una persona del sistema.
    
    Solo administradores pueden eliminar personas.
    NOTA: Verificar que no tenga sacramentos asociados antes de eliminar.
    """
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar personas"
        )
    
    if persona_id not in fake_personas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona no encontrada"
        )
    
    # TODO: Verificar que no tenga sacramentos asociados
    # En una implementación real, hacer una consulta a la tabla sacramentos
    
    del fake_personas_db[persona_id]
    
    return MessageResponse(
        message="Persona eliminada exitosamente",
        success=True
    )


@router.get("/{persona_id}/sacramentos")
async def get_sacramentos_persona(
    persona_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todos los sacramentos de una persona.
    
    Endpoint placeholder - se implementará cuando se creen los endpoints de sacramentos.
    """
    persona = fake_personas_db.get(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona no encontrada"
        )
    
    # TODO: Implementar consulta real a sacramentos
    return {
        "persona_id": persona_id,
        "sacramentos": [],
        "message": "Endpoint en desarrollo - se conectará con la tabla de sacramentos"
    }
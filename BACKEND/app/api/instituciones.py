"""
Endpoints para gestión de instituciones parroquiales en el Sistema Sacra360
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from ..schemas.sacra360_schemas import (
    InstitucionCreate, InstitucionResponse, InstitucionUpdate,
    MessageResponse
)
from .usuarios import get_current_user

# Configuración del router
router = APIRouter(prefix="/instituciones", tags=["Instituciones Parroquiales"])

# Simulación de base de datos en memoria (reemplazar por base de datos real)
fake_instituciones_db = {}
institucion_id_counter = 1

# Datos iniciales para demostración
fake_instituciones_db[1] = {
    "id_institucion": 1,
    "nombre": "Parroquia San José",
    "direccion": "Av. Principal 123, La Paz",
    "telefono": "+591-2-2234567",
    "email": "info@parroquiasanjose.bo"
}
fake_instituciones_db[2] = {
    "id_institucion": 2,
    "nombre": "Catedral Metropolitana",
    "direccion": "Plaza Murillo S/N, La Paz",
    "telefono": "+591-2-2280123",
    "email": "catedral@iglesia.bo"
}
institucion_id_counter = 3


@router.post("/", response_model=InstitucionResponse, status_code=status.HTTP_201_CREATED)
async def create_institucion(
    institucion_data: InstitucionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Registra una nueva institución parroquial.
    
    Requiere permisos de administrador.
    """
    # Verificar permisos - solo administradores pueden crear instituciones
    user_role = current_user.get("rol")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden registrar instituciones"
        )
    
    global institucion_id_counter
    
    # Verificar que no exista una institución con el mismo nombre
    for inst in fake_instituciones_db.values():
        if inst["nombre"].lower() == institucion_data.nombre.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una institución con el nombre '{institucion_data.nombre}'"
            )
    
    # Crear nueva institución
    nueva_institucion = {
        "id_institucion": institucion_id_counter,
        **institucion_data.model_dump()
    }
    
    fake_instituciones_db[institucion_id_counter] = nueva_institucion
    institucion_id_counter += 1
    
    return InstitucionResponse(**nueva_institucion)


@router.get("/", response_model=List[InstitucionResponse])
async def list_instituciones(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre de institución"),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todas las instituciones parroquiales con filtros opcionales.
    
    Todos los usuarios autenticados pueden ver las instituciones.
    """
    instituciones = list(fake_instituciones_db.values())
    
    # Aplicar filtro por nombre si se proporciona
    if nombre:
        instituciones = [
            inst for inst in instituciones 
            if nombre.lower() in inst["nombre"].lower()
        ]
    
    # Aplicar paginación
    total = len(instituciones)
    instituciones = instituciones[skip:skip + limit]
    
    return [InstitucionResponse(**inst) for inst in instituciones]


@router.get("/{institucion_id}", response_model=InstitucionResponse)
async def get_institucion(
    institucion_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una institución específica por ID.
    
    Todos los usuarios autenticados pueden ver las instituciones.
    """
    if institucion_id not in fake_instituciones_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institución con ID {institucion_id} no encontrada"
        )
    
    institucion = fake_instituciones_db[institucion_id]
    return InstitucionResponse(**institucion)


@router.put("/{institucion_id}", response_model=InstitucionResponse)
async def update_institucion(
    institucion_id: int,
    institucion_update: InstitucionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza una institución existente.
    
    Requiere permisos de administrador.
    """
    # Verificar permisos - solo administradores pueden actualizar instituciones
    user_role = current_user.get("rol")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar instituciones"
        )
    
    if institucion_id not in fake_instituciones_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institución con ID {institucion_id} no encontrada"
        )
    
    # Verificar nombre único si se está actualizando
    update_data = institucion_update.model_dump(exclude_unset=True)
    if "nombre" in update_data:
        for inst_id, inst in fake_instituciones_db.items():
            if (inst_id != institucion_id and 
                inst["nombre"].lower() == update_data["nombre"].lower()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe una institución con el nombre '{update_data['nombre']}'"
                )
    
    # Actualizar la institución
    institucion_actual = fake_instituciones_db[institucion_id]
    institucion_actual.update(update_data)
    
    return InstitucionResponse(**institucion_actual)


@router.delete("/{institucion_id}", response_model=MessageResponse)
async def delete_institucion(
    institucion_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina una institución.
    
    Requiere permisos de administrador.
    """
    # Verificar permisos - solo administradores pueden eliminar instituciones
    user_role = current_user.get("rol")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar instituciones"
        )
    
    if institucion_id not in fake_instituciones_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institución con ID {institucion_id} no encontrada"
        )
    
    # TODO: Verificar que no haya sacramentos asociados a esta institución
    # antes de eliminarla (implementar cuando se conecte a base de datos)
    
    del fake_instituciones_db[institucion_id]
    
    return MessageResponse(
        message=f"Institución con ID {institucion_id} eliminada exitosamente"
    )


@router.get("/search/by-name", response_model=List[InstitucionResponse])
async def search_instituciones_by_name(
    q: str = Query(..., min_length=2, description="Término de búsqueda en el nombre"),
    current_user: dict = Depends(get_current_user)
):
    """
    Busca instituciones por nombre con coincidencia parcial.
    
    Útil para autocompletado en formularios.
    """
    instituciones = list(fake_instituciones_db.values())
    
    # Búsqueda case-insensitive en el nombre
    resultados = [
        inst for inst in instituciones 
        if q.lower() in inst["nombre"].lower()
    ]
    
    return [InstitucionResponse(**inst) for inst in resultados]


@router.get("/stats/summary")
async def get_instituciones_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estadísticas básicas de las instituciones.
    
    Accesible por administradores y sacerdotes.
    """
    user_role = current_user.get("rol")
    if user_role not in ["admin", "sacerdote"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas estadísticas"
        )
    
    total_instituciones = len(fake_instituciones_db)
    con_telefono = sum(1 for inst in fake_instituciones_db.values() if inst.get("telefono"))
    con_email = sum(1 for inst in fake_instituciones_db.values() if inst.get("email"))
    
    return {
        "total_instituciones": total_instituciones,
        "con_telefono": con_telefono,
        "con_email": con_email,
        "porcentaje_contacto_completo": round((con_telefono + con_email) / (total_instituciones * 2) * 100, 2) if total_instituciones > 0 else 0
    }
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from ..schemas import (
    ResourceCreate, ResourceResponse, ResourceUpdate, 
    MessageResponse, PaginationParams
)
from ..api.users import get_current_user

# Router para recursos generales
router = APIRouter(prefix="/resources", tags=["Recursos"])

# Simulación de base de datos en memoria
fake_resources_db = {}
resource_id_counter = 1


@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crea un nuevo recurso en el sistema.
    
    - **name**: Nombre del recurso (requerido)
    - **description**: Descripción del recurso (opcional)
    - **status**: Estado del recurso (activo por defecto)
    """
    global resource_id_counter
    
    # Verificar si ya existe un recurso con el mismo nombre
    for resource in fake_resources_db.values():
        if resource["name"].lower() == resource_data.name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un recurso con este nombre"
            )
    
    # Crear el recurso
    new_resource = {
        "id": resource_id_counter,
        "name": resource_data.name,
        "description": resource_data.description,
        "status": resource_data.status,
        "created_at": "2024-01-01T00:00:00",  # Reemplazar con datetime.utcnow()
        "updated_at": None,
        "created_by": current_user["id"]
    }
    
    fake_resources_db[resource_id_counter] = new_resource
    resource_id_counter += 1
    
    return ResourceResponse(**new_resource)


@router.get("/", response_model=List[ResourceResponse])
async def get_resources(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de recursos.
    
    Permite filtrar por nombre y estado.
    """
    # Filtrar recursos
    filtered_resources = list(fake_resources_db.values())
    
    if search:
        filtered_resources = [
            r for r in filtered_resources 
            if search.lower() in r["name"].lower() or 
               (r["description"] and search.lower() in r["description"].lower())
        ]
    
    if status_filter:
        filtered_resources = [r for r in filtered_resources if r["status"] == status_filter]
    
    # Paginación
    total = len(filtered_resources)
    start = (page - 1) * limit
    end = start + limit
    paginated_resources = filtered_resources[start:end]
    
    return [ResourceResponse(**resource) for resource in paginated_resources]


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource_by_id(
    resource_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un recurso específico por su ID.
    """
    resource = fake_resources_db.get(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    return ResourceResponse(**resource)


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza un recurso existente.
    
    Solo el creador del recurso o un administrador puede actualizarlo.
    """
    resource = fake_resources_db.get(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    # Verificar permisos
    if current_user["role"] != "admin" and resource["created_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este recurso"
        )
    
    # Verificar unicidad del nombre si se está actualizando
    update_data = resource_update.dict(exclude_unset=True)
    
    if "name" in update_data:
        for rid, r in fake_resources_db.items():
            if rid != resource_id and r["name"].lower() == update_data["name"].lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un recurso con este nombre"
                )
    
    # Actualizar campos
    for field, value in update_data.items():
        resource[field] = value
    
    resource["updated_at"] = "2024-01-01T00:00:00"  # Reemplazar con datetime.utcnow()
    
    return ResourceResponse(**resource)


@router.delete("/{resource_id}", response_model=MessageResponse)
async def delete_resource(
    resource_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un recurso del sistema.
    
    Solo el creador del recurso o un administrador puede eliminarlo.
    """
    resource = fake_resources_db.get(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    # Verificar permisos
    if current_user["role"] != "admin" and resource["created_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este recurso"
        )
    
    del fake_resources_db[resource_id]
    
    return MessageResponse(
        message="Recurso eliminado exitosamente",
        success=True
)
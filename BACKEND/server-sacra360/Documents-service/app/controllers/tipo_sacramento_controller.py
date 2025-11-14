"""
Controlador REST para Tipos de Sacramentos
Maneja las peticiones HTTP y coordina con el servicio
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Importar dependencias
from app.database import get_db
from app.services.tipo_sacramento_service import TipoSacramentoService
from app.dto.tipo_sacramento_dto import (
    TipoSacramentoCreateDTO,
    TipoSacramentoUpdateDTO,
    TipoSacramentoResponseDTO,
    TipoSacramentoListResponseDTO
)

import logging

logger = logging.getLogger(__name__)

# Crear el router
router = APIRouter(
    prefix="/tipos-sacramentos",
    tags=["tipos-sacramentos"],
    responses={404: {"description": "Tipo de sacramento no encontrado"}}
)


@router.post(
    "/",
    response_model=TipoSacramentoResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo tipo de sacramento",
    description="Crea un nuevo tipo de sacramento en el sistema"
)
async def create_tipo_sacramento(
    tipo_sacramento: TipoSacramentoCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo tipo de sacramento.
    
    - **nombre**: Nombre del tipo de sacramento (único, requerido)
    - **descripcion**: Descripción opcional del tipo de sacramento
    """
    try:
        logger.info(f"Creando tipo de sacramento: {tipo_sacramento.nombre}")
        
        # Crear el tipo de sacramento usando el servicio
        nuevo_tipo = TipoSacramentoService.create(db, tipo_sacramento)
        
        # Convertir a DTO de respuesta
        response = TipoSacramentoResponseDTO(
            id_tipo=nuevo_tipo.id_tipo,
            nombre=nuevo_tipo.nombre,
            descripcion=nuevo_tipo.descripcion
        )
        
        logger.info(f"Tipo de sacramento creado exitosamente con ID: {nuevo_tipo.id_tipo}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al crear tipo de sacramento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/",
    response_model=TipoSacramentoListResponseDTO,
    summary="Listar tipos de sacramentos",
    description="Obtiene una lista paginada de tipos de sacramentos con filtros opcionales"
)
async def list_tipos_sacramentos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre (búsqueda parcial)"),
    db: Session = Depends(get_db)
):
    """
    Listar tipos de sacramentos con paginación y filtros opcionales.
    
    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros a retornar (máximo 100)
    - **nombre**: Filtro opcional por nombre (búsqueda parcial)
    """
    try:
        logger.info(f"Listando tipos de sacramentos - skip: {skip}, limit: {limit}, nombre: {nombre}")
        
        # Obtener tipos de sacramentos usando el servicio
        tipos_sacramentos, total = TipoSacramentoService.list(
            db=db,
            skip=skip,
            limit=limit,
            nombre=nombre
        )
        
        # Convertir a DTOs de respuesta
        tipos_response = []
        for tipo in tipos_sacramentos:
            tipos_response.append(TipoSacramentoResponseDTO(
                id_tipo=tipo.id_tipo,
                nombre=tipo.nombre,
                descripcion=tipo.descripcion
            ))
        
        response = TipoSacramentoListResponseDTO(
            tipos_sacramentos=tipos_response,
            total=total
        )
        
        logger.info(f"Se encontraron {total} tipos de sacramentos")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al listar tipos de sacramentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/{tipo_id}",
    response_model=TipoSacramentoResponseDTO,
    summary="Obtener tipo de sacramento por ID",
    description="Obtiene un tipo de sacramento específico por su ID"
)
async def get_tipo_sacramento(
    tipo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un tipo de sacramento específico por su ID.
    
    - **tipo_id**: ID único del tipo de sacramento
    """
    try:
        logger.info(f"Obteniendo tipo de sacramento con ID: {tipo_id}")
        
        # Obtener el tipo de sacramento usando el servicio
        tipo_sacramento = TipoSacramentoService.get_by_id(db, tipo_id)
        
        # Convertir a DTO de respuesta
        response = TipoSacramentoResponseDTO(
            id_tipo=tipo_sacramento.id_tipo,
            nombre=tipo_sacramento.nombre,
            descripcion=tipo_sacramento.descripcion
        )
        
        logger.info(f"Tipo de sacramento encontrado: {tipo_sacramento.nombre}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener tipo de sacramento {tipo_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put(
    "/{tipo_id}",
    response_model=TipoSacramentoResponseDTO,
    summary="Actualizar tipo de sacramento",
    description="Actualiza un tipo de sacramento existente"
)
async def update_tipo_sacramento(
    tipo_id: int,
    tipo_sacramento: TipoSacramentoUpdateDTO,
    db: Session = Depends(get_db)
):
    """
    Actualizar un tipo de sacramento existente.
    
    - **tipo_id**: ID único del tipo de sacramento a actualizar
    - **nombre**: Nuevo nombre del tipo de sacramento (opcional)
    - **descripcion**: Nueva descripción del tipo de sacramento (opcional)
    """
    try:
        logger.info(f"Actualizando tipo de sacramento con ID: {tipo_id}")
        
        # Actualizar el tipo de sacramento usando el servicio
        tipo_actualizado = TipoSacramentoService.update(db, tipo_id, tipo_sacramento)
        
        # Convertir a DTO de respuesta
        response = TipoSacramentoResponseDTO(
            id_tipo=tipo_actualizado.id_tipo,
            nombre=tipo_actualizado.nombre,
            descripcion=tipo_actualizado.descripcion
        )
        
        logger.info(f"Tipo de sacramento actualizado exitosamente: {tipo_actualizado.nombre}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al actualizar tipo de sacramento {tipo_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete(
    "/{tipo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tipo de sacramento",
    description="Elimina un tipo de sacramento del sistema"
)
async def delete_tipo_sacramento(
    tipo_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un tipo de sacramento del sistema.
    
    - **tipo_id**: ID único del tipo de sacramento a eliminar
    """
    try:
        logger.info(f"Eliminando tipo de sacramento con ID: {tipo_id}")
        
        # Eliminar el tipo de sacramento usando el servicio
        TipoSacramentoService.delete(db, tipo_id)
        
        logger.info(f"Tipo de sacramento con ID {tipo_id} eliminado exitosamente")
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al eliminar tipo de sacramento {tipo_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/search/by-name",
    response_model=List[TipoSacramentoResponseDTO],
    summary="Buscar tipos de sacramentos por nombre",
    description="Busca tipos de sacramentos que contengan el nombre especificado"
)
async def search_tipos_sacramentos_by_name(
    nombre: str = Query(..., min_length=1, description="Nombre a buscar"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """
    Buscar tipos de sacramentos por nombre.
    
    - **nombre**: Nombre a buscar (búsqueda parcial)
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    """
    try:
        logger.info(f"Buscando tipos de sacramentos por nombre: {nombre}")
        
        # Buscar tipos de sacramentos usando el servicio
        tipos_sacramentos = TipoSacramentoService.search_by_name(
            db=db,
            nombre=nombre,
            skip=skip,
            limit=limit
        )
        
        # Convertir a DTOs de respuesta
        response = []
        for tipo in tipos_sacramentos:
            response.append(TipoSacramentoResponseDTO(
                id_tipo=tipo.id_tipo,
                nombre=tipo.nombre,
                descripcion=tipo.descripcion
            ))
        
        logger.info(f"Se encontraron {len(response)} tipos de sacramentos con nombre '{nombre}'")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al buscar tipos de sacramentos por nombre '{nombre}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
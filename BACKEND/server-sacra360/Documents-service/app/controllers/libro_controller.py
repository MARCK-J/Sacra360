from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.dto.libro_dto import LibroCreateDTO, LibroUpdateDTO, LibroResponseDTO
from app.services.libro_service import LibroService

router = APIRouter(prefix="/libros", tags=["Libros"])

@router.post("/", 
             response_model=LibroResponseDTO, 
             status_code=status.HTTP_201_CREATED,
             summary="Crear nuevo libro",
             description="Crea un nuevo libro con validaciones completas")
def create_libro(
    dto: LibroCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo libro.
    
    - **nombre**: Nombre del libro (obligatorio, máximo 200 caracteres)
    - **fecha_inicio**: Fecha de inicio de registros (debe ser anterior a fecha_fin)
    - **fecha_fin**: Fecha de fin de registros (debe ser posterior a fecha_inicio)
    - **observaciones**: Observaciones adicionales (opcional, máximo 500 caracteres)
    """
    libro = LibroService.create(db, dto)
    return LibroResponseDTO.model_validate(libro)

@router.get("/{libro_id}", 
            response_model=LibroResponseDTO,
            summary="Obtener libro por ID",
            description="Obtiene un libro específico por su ID")
def get_libro(
    libro_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un libro específico por su ID"""
    libro = LibroService.get_by_id(db, libro_id)
    return LibroResponseDTO.model_validate(libro)

@router.get("/", 
            response_model=List[LibroResponseDTO],
            summary="Listar libros",
            description="Lista libros con filtros opcionales y paginación")
def list_libros(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre (búsqueda parcial)"),
    db: Session = Depends(get_db)
):
    """
    Listar libros con filtros opcionales.
    
    Soporta paginación y filtro de búsqueda por nombre.
    """
    libros, total = LibroService.list(
        db=db,
        skip=skip,
        limit=limit,
        nombre=nombre
    )
    
    response_data = []
    for libro in libros:
        response_data.append(LibroResponseDTO(
            id_libro=libro.id_libro,
            nombre=libro.nombre,
            fecha_inicio=libro.fecha_inicio,
            fecha_fin=libro.fecha_fin,
            observaciones=libro.observaciones
        ))
    
    return response_data

@router.get("/count/total",
            response_model=dict,
            summary="Contar libros",
            description="Cuenta el total de libros que coinciden con los filtros")
def count_libros(
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    db: Session = Depends(get_db)
):
    """Contar libros que coinciden con los filtros especificados"""
    total = LibroService.count(
        db=db,
        nombre=nombre
    )
    return {"total": total}

@router.put("/{libro_id}", 
            response_model=LibroResponseDTO,
            summary="Actualizar libro",
            description="Actualiza los datos de un libro existente")
def update_libro(
    libro_id: int,
    dto: LibroUpdateDTO,
    db: Session = Depends(get_db)
):
    """
    Actualizar un libro existente.
    
    Solo se actualizarán los campos proporcionados en el DTO.
    """
    libro = LibroService.update(db, libro_id, dto)
    return LibroResponseDTO.model_validate(libro)

@router.delete("/{libro_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar libro",
               description="Elimina un libro de forma permanente")
def delete_libro(
    libro_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un libro de forma permanente.
    
    El libro se elimina físicamente de la base de datos.
    """
    LibroService.delete(db, libro_id)
    return

@router.get("/search/by-name",
            response_model=List[LibroResponseDTO],
            summary="Buscar libros por nombre",
            description="Búsqueda específica por nombre del libro")
def search_libros_by_name(
    nombre: str = Query(..., description="Nombre del libro a buscar"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros"),
    solo_activos: bool = Query(True, description="Solo libros activos"),
    db: Session = Depends(get_db)
):
    """Búsqueda específica por nombre del libro con coincidencia parcial"""
    libros = LibroService.search_by_name(
        db=db,
        nombre=nombre,
        skip=skip,
        limit=limit,
        solo_activos=solo_activos
    )
    return [LibroResponseDTO.model_validate(l) for l in libros]

@router.get("/filter/date-range",
            response_model=List[LibroResponseDTO],
            summary="Filtrar por rango de fechas",
            description="Obtiene libros dentro de un rango de fechas específico")
def filter_by_date_range(
    fecha_desde: Optional[date] = Query(None, description="Fecha de inicio desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha de fin hasta"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    solo_activos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Filtrar libros por rango de fechas específico"""
    libros = LibroService.list_by_date_range(
        db=db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        skip=skip,
        limit=limit,
        solo_activos=solo_activos
    )
    return [LibroResponseDTO.model_validate(l) for l in libros]

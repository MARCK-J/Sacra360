from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from datetime import date

from app.models import LibroModel
from app.entities.libro import Libro
from app.dto.libro_dto import LibroCreateDTO, LibroUpdateDTO

class LibroService:
    @staticmethod
    def create(db: Session, dto: LibroCreateDTO) -> Libro:
        """Crear un nuevo libro"""
        try:
            # Crear el modelo SQLAlchemy
            db_libro = LibroModel(
                nombre=dto.nombre,
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
                observaciones=dto.observaciones,
                active=dto.active
            )
            
            # Guardar en base de datos
            db.add(db_libro)
            db.commit()
            db.refresh(db_libro)
            
            # Convertir a entidad
            return Libro.from_orm(db_libro)
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear libro: {str(e)}"
            )

    @staticmethod
    def get(db: Session, libro_id: int) -> Libro:
        """Obtener un libro por ID"""
        db_libro = db.query(LibroModel).filter(
            LibroModel.id_libro == libro_id,
            LibroModel.active == True
        ).first()
        
        if not db_libro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Libro con ID {libro_id} no encontrado"
            )
        
        return Libro.from_orm(db_libro)

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        solo_activos: bool = True,
        nombre: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[Libro]:
        """Listar libros con filtros opcionales"""
        query = db.query(LibroModel)
        
        # Filtrar por estado activo
        if solo_activos:
            query = query.filter(LibroModel.active == True)
        
        # Filtros de búsqueda
        if nombre:
            query = query.filter(LibroModel.nombre.ilike(f"%{nombre}%"))
        
        if fecha_desde:
            query = query.filter(LibroModel.fecha_inicio >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(LibroModel.fecha_fin <= fecha_hasta)
        
        # Aplicar paginación y orden
        db_libros = query.order_by(LibroModel.fecha_inicio.desc(), LibroModel.nombre)\
                         .offset(skip)\
                         .limit(limit)\
                         .all()
        
        return [Libro.from_orm(l) for l in db_libros]

    @staticmethod
    def count(
        db: Session,
        solo_activos: bool = True,
        nombre: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> int:
        """Contar libros que coinciden con los filtros"""
        query = db.query(LibroModel)
        
        if solo_activos:
            query = query.filter(LibroModel.active == True)
        
        if nombre:
            query = query.filter(LibroModel.nombre.ilike(f"%{nombre}%"))
        
        if fecha_desde:
            query = query.filter(LibroModel.fecha_inicio >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(LibroModel.fecha_fin <= fecha_hasta)
        
        return query.count()

    @staticmethod
    def update(db: Session, libro_id: int, dto: LibroUpdateDTO) -> Libro:
        """Actualizar un libro"""
        try:
            # Buscar el libro
            db_libro = db.query(LibroModel).filter(
                LibroModel.id_libro == libro_id,
                LibroModel.active == True
            ).first()
            
            if not db_libro:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Libro con ID {libro_id} no encontrado"
                )
            
            # Actualizar solo los campos proporcionados
            update_data = dto.dict(exclude_unset=True, exclude_none=True)
            for field, value in update_data.items():
                setattr(db_libro, field, value)
            
            # Guardar cambios
            db.commit()
            db.refresh(db_libro)
            
            return Libro.from_orm(db_libro)
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar libro: {str(e)}"
            )

    @staticmethod
    def soft_delete(db: Session, libro_id: int) -> bool:
        """Desactivar un libro (soft delete)"""
        try:
            db_libro = db.query(LibroModel).filter(
                LibroModel.id_libro == libro_id,
                LibroModel.active == True
            ).first()
            
            if not db_libro:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Libro con ID {libro_id} no encontrado"
                )
            
            # Marcar como inactivo
            db_libro.active = False
            db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al desactivar libro: {str(e)}"
            )

    @staticmethod
    def search_by_name(
        db: Session,
        nombre: str,
        skip: int = 0,
        limit: int = 20,
        solo_activos: bool = True
    ) -> List[Libro]:
        """Búsqueda específica por nombre del libro"""
        return LibroService.list(
            db=db,
            skip=skip,
            limit=limit,
            solo_activos=solo_activos,
            nombre=nombre
        )

    @staticmethod
    def list_by_date_range(
        db: Session,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
        solo_activos: bool = True
    ) -> List[Libro]:
        """Listar libros por rango de fechas"""
        return LibroService.list(
            db=db,
            skip=skip,
            limit=limit,
            solo_activos=solo_activos,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
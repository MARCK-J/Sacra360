"""
Servicio para la gestión de Libros
Contiene la lógica de negocio para operaciones CRUD
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from datetime import date

from app.models import LibroModel
from app.entities.libro import Libro
from app.dto.libro_dto import LibroCreateDTO, LibroUpdateDTO

import logging

logger = logging.getLogger(__name__)


class LibroService:
    """Servicio para la gestión de libros"""

    @staticmethod
    def create(db: Session, dto: LibroCreateDTO) -> Libro:
        """Crear un nuevo libro"""
        try:
            # Crear el modelo SQLAlchemy
            db_libro = LibroModel(
                nombre=dto.nombre,
                fecha_inicio=dto.fecha_inicio,
                fecha_fin=dto.fecha_fin,
                observaciones=dto.observaciones
            )
            
            # Guardar en base de datos
            db.add(db_libro)
            db.commit()
            db.refresh(db_libro)
            
            # Convertir a entidad
            return Libro(
                id_libro=db_libro.id_libro,
                nombre=db_libro.nombre,
                fecha_inicio=db_libro.fecha_inicio,
                fecha_fin=db_libro.fecha_fin,
                observaciones=db_libro.observaciones
            )
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al crear libro: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear libro: {str(e)}"
            )

    @staticmethod
    def get_by_id(db: Session, libro_id: int) -> Libro:
        """Obtener un libro por ID"""
        try:
            db_libro = db.query(LibroModel).filter(
                LibroModel.id_libro == libro_id
            ).first()
            
            if not db_libro:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Libro con ID {libro_id} no encontrado"
                )
            
            return Libro(
                id_libro=db_libro.id_libro,
                nombre=db_libro.nombre,
                fecha_inicio=db_libro.fecha_inicio,
                fecha_fin=db_libro.fecha_fin,
                observaciones=db_libro.observaciones
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener libro: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        nombre: Optional[str] = None
    ) -> tuple[List[Libro], int]:
        """Listar libros con paginación y filtros opcionales"""
        try:
            query = db.query(LibroModel)
            
            # Filtro por nombre si se proporciona
            if nombre:
                query = query.filter(LibroModel.nombre.ilike(f"%{nombre}%"))
            
            # Obtener el total
            total = query.count()
            
            # Aplicar paginación y orden
            libros_db = query.order_by(LibroModel.fecha_inicio.desc())\
                             .offset(skip)\
                             .limit(limit)\
                             .all()
            
            # Convertir a entidades
            libros = []
            for libro_db in libros_db:
                libros.append(Libro(
                    id_libro=libro_db.id_libro,
                    nombre=libro_db.nombre,
                    fecha_inicio=libro_db.fecha_inicio,
                    fecha_fin=libro_db.fecha_fin,
                    observaciones=libro_db.observaciones
                ))
            
            return libros, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error al listar libros: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    @staticmethod
    def update(db: Session, libro_id: int, dto: LibroUpdateDTO) -> Libro:
        """Actualizar un libro"""
        try:
            # Buscar el libro
            db_libro = db.query(LibroModel).filter(
                LibroModel.id_libro == libro_id
            ).first()
            
            if not db_libro:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Libro con ID {libro_id} no encontrado"
                )
            
            # Actualizar solo los campos proporcionados
            if dto.nombre is not None:
                db_libro.nombre = dto.nombre
            if dto.fecha_inicio is not None:
                db_libro.fecha_inicio = dto.fecha_inicio
            if dto.fecha_fin is not None:
                db_libro.fecha_fin = dto.fecha_fin
            if dto.observaciones is not None:
                db_libro.observaciones = dto.observaciones
            
            # Guardar cambios
            db.commit()
            db.refresh(db_libro)
            
            return Libro(
                id_libro=db_libro.id_libro,
                nombre=db_libro.nombre,
                fecha_inicio=db_libro.fecha_inicio,
                fecha_fin=db_libro.fecha_fin,
                observaciones=db_libro.observaciones
            )
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al actualizar libro: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar libro: {str(e)}"
            )

    @staticmethod
    def delete(db: Session, libro_id: int) -> bool:
        """Eliminar un libro"""
        try:
            db_libro = db.query(LibroModel).filter(
                LibroModel.id_libro == libro_id
            ).first()
            
            if not db_libro:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Libro con ID {libro_id} no encontrado"
                )
            
            # Eliminar registro
            db.delete(db_libro)
            db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al eliminar libro: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar libro: {str(e)}"
            )

    @staticmethod
    def search_by_name(
        db: Session,
        nombre: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Libro]:
        """Búsqueda específica por nombre del libro"""
        libros, _ = LibroService.list(
            db=db,
            skip=skip,
            limit=limit,
            nombre=nombre
        )
        return libros

    @staticmethod
    def count(db: Session, nombre: Optional[str] = None) -> int:
        """Contar libros que coinciden con los filtros"""
        try:
            query = db.query(LibroModel)
            
            if nombre:
                query = query.filter(LibroModel.nombre.ilike(f"%{nombre}%"))
            
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al contar libros: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
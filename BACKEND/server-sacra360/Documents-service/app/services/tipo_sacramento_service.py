"""
Servicio para la gestión de Tipos de Sacramentos
Contiene la lógica de negocio para operaciones CRUD
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

# Importar modelos y entidades
from app.models import TipoSacramentoModel
from app.entities.tipo_sacramento import TipoSacramento
from app.dto.tipo_sacramento_dto import TipoSacramentoCreateDTO, TipoSacramentoUpdateDTO

import logging

logger = logging.getLogger(__name__)


class TipoSacramentoService:
    """Servicio para la gestión de tipos de sacramentos"""

    @staticmethod
    def create(db: Session, tipo_sacramento_data: TipoSacramentoCreateDTO) -> TipoSacramento:
        """Crear un nuevo tipo de sacramento"""
        try:
            # Verificar si ya existe un tipo de sacramento con el mismo nombre
            existing = db.query(TipoSacramentoModel).filter(
                TipoSacramentoModel.nombre.ilike(tipo_sacramento_data.nombre.strip())
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un tipo de sacramento con el nombre '{tipo_sacramento_data.nombre}'"
                )

            # Crear el modelo de SQLAlchemy
            db_tipo_sacramento = TipoSacramentoModel(
                nombre=tipo_sacramento_data.nombre.strip().title(),
                descripcion=tipo_sacramento_data.descripcion.strip() if tipo_sacramento_data.descripcion else None
            )
            
            # Guardar en la base de datos
            db.add(db_tipo_sacramento)
            db.commit()
            db.refresh(db_tipo_sacramento)
            
            # Convertir a entidad de dominio
            return TipoSacramento(
                id_tipo=db_tipo_sacramento.id_tipo,
                nombre=db_tipo_sacramento.nombre,
                descripcion=db_tipo_sacramento.descripcion
            )
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad al crear tipo de sacramento: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre del tipo de sacramento debe ser único"
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error de base de datos al crear tipo de sacramento: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al crear tipo de sacramento"
            )

    @staticmethod
    def get_by_id(db: Session, tipo_id: int) -> TipoSacramento:
        """Obtener un tipo de sacramento por su ID"""
        try:
            db_tipo_sacramento = db.query(TipoSacramentoModel).filter(
                TipoSacramentoModel.id_tipo == tipo_id
            ).first()
            
            if not db_tipo_sacramento:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tipo de sacramento con ID {tipo_id} no encontrado"
                )
            
            return TipoSacramento(
                id_tipo=db_tipo_sacramento.id_tipo,
                nombre=db_tipo_sacramento.nombre,
                descripcion=db_tipo_sacramento.descripcion
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener tipo de sacramento por ID {tipo_id}: {e}")
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
    ) -> tuple[List[TipoSacramento], int]:
        """Listar tipos de sacramentos con paginación y filtros opcionales"""
        try:
            query = db.query(TipoSacramentoModel)
            
            # Aplicar filtro por nombre si se proporciona
            if nombre:
                query = query.filter(
                    TipoSacramentoModel.nombre.ilike(f"%{nombre}%")
                )
            
            # Obtener el total de registros (antes de aplicar paginación)
            total = query.count()
            
            # Aplicar paginación y ordenación
            tipos_sacramentos_db = query.order_by(
                TipoSacramentoModel.nombre
            ).offset(skip).limit(limit).all()
            
            # Convertir a entidades de dominio
            tipos_sacramentos = []
            for tipo_db in tipos_sacramentos_db:
                tipos_sacramentos.append(TipoSacramento(
                    id_tipo=tipo_db.id_tipo,
                    nombre=tipo_db.nombre,
                    descripcion=tipo_db.descripcion
                ))
            
            return tipos_sacramentos, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error al listar tipos de sacramentos: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    @staticmethod
    def update(db: Session, tipo_id: int, tipo_sacramento_data: TipoSacramentoUpdateDTO) -> TipoSacramento:
        """Actualizar un tipo de sacramento existente"""
        try:
            # Buscar el tipo de sacramento
            db_tipo_sacramento = db.query(TipoSacramentoModel).filter(
                TipoSacramentoModel.id_tipo == tipo_id
            ).first()
            
            if not db_tipo_sacramento:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tipo de sacramento con ID {tipo_id} no encontrado"
                )
            
            # Actualizar campos si se proporcionan
            if tipo_sacramento_data.nombre is not None:
                nombre_normalizado = tipo_sacramento_data.nombre.strip().title()
                
                # Verificar que no exista otro tipo con el mismo nombre
                existing = db.query(TipoSacramentoModel).filter(
                    TipoSacramentoModel.nombre.ilike(nombre_normalizado),
                    TipoSacramentoModel.id_tipo != tipo_id
                ).first()
                
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe otro tipo de sacramento con el nombre '{nombre_normalizado}'"
                    )
                
                db_tipo_sacramento.nombre = nombre_normalizado
            
            if tipo_sacramento_data.descripcion is not None:
                db_tipo_sacramento.descripcion = tipo_sacramento_data.descripcion.strip() if tipo_sacramento_data.descripcion else None
            
            # Guardar cambios
            db.commit()
            db.refresh(db_tipo_sacramento)
            
            # Convertir a entidad de dominio
            return TipoSacramento(
                id_tipo=db_tipo_sacramento.id_tipo,
                nombre=db_tipo_sacramento.nombre,
                descripcion=db_tipo_sacramento.descripcion
            )
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad al actualizar tipo de sacramento: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad de datos"
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al actualizar tipo de sacramento: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    @staticmethod
    def delete(db: Session, tipo_id: int) -> bool:
        """Eliminar un tipo de sacramento"""
        try:
            db_tipo_sacramento = db.query(TipoSacramentoModel).filter(
                TipoSacramentoModel.id_tipo == tipo_id
            ).first()
            
            if not db_tipo_sacramento:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tipo de sacramento con ID {tipo_id} no encontrado"
                )
            
            # Eliminar registro
            db.delete(db_tipo_sacramento)
            db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al eliminar tipo de sacramento: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al eliminar tipo de sacramento"
            )

    @staticmethod
    def search_by_name(
        db: Session,
        nombre: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[TipoSacramento]:
        """Búsqueda específica por nombre"""
        tipos_sacramentos, _ = TipoSacramentoService.list(
            db=db,
            skip=skip,
            limit=limit,
            nombre=nombre
        )
        return tipos_sacramentos

    @staticmethod
    def count(db: Session, nombre: Optional[str] = None) -> int:
        """Contar tipos de sacramentos que coinciden con los filtros"""
        try:
            query = db.query(TipoSacramentoModel)
            
            if nombre:
                query = query.filter(TipoSacramentoModel.nombre.ilike(f"%{nombre}%"))
            
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al contar tipos de sacramentos: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
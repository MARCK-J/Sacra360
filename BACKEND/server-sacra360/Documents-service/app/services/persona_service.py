from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models import PersonaModel
from app.entities.persona import Persona
from app.dto.persona_dto import PersonaCreateDTO, PersonaUpdateDTO

class PersonaService:
    @staticmethod
    def create(db: Session, dto: PersonaCreateDTO) -> Persona:
        """Crear una nueva persona"""
        try:
            # Crear el modelo SQLAlchemy
            db_persona = PersonaModel(
                nombres=dto.nombres,
                apellido_paterno=dto.apellido_paterno,
                apellido_materno=dto.apellido_materno,
                fecha_nacimiento=dto.fecha_nacimiento,
                lugar_nacimiento=dto.lugar_nacimiento,
                nombre_padre=dto.nombre_padre,
                nombre_madre=dto.nombre_madre
            )
            
            # Guardar en base de datos
            db.add(db_persona)
            db.commit()
            db.refresh(db_persona)
            
            # Convertir a entidad
            return Persona.from_orm(db_persona)
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear persona: {str(e)}"
            )

    @staticmethod
    def get(db: Session, persona_id: int) -> Persona:
        """Obtener una persona por ID"""
        db_persona = db.query(PersonaModel).filter(
            PersonaModel.id_persona == persona_id
        ).first()
        
        if not db_persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona con ID {persona_id} no encontrada"
            )
        
        return Persona.from_orm(db_persona)

    @staticmethod
    def list(
        db: Session, 
        skip: int = 0, 
        limit: int = 20, 
        nombres: Optional[str] = None,
        apellido_paterno: Optional[str] = None,
        apellido_materno: Optional[str] = None
    ) -> List[Persona]:
        """Listar personas con filtros opcionales"""
        query = db.query(PersonaModel)
        
        # Filtros de búsqueda
        if nombres:
            query = query.filter(PersonaModel.nombres.ilike(f"%{nombres}%"))
        if apellido_paterno:
            query = query.filter(PersonaModel.apellido_paterno.ilike(f"%{apellido_paterno}%"))
        if apellido_materno:
            query = query.filter(PersonaModel.apellido_materno.ilike(f"%{apellido_materno}%"))
        
        # Aplicar paginación y orden
        db_personas = query.order_by(PersonaModel.apellido_paterno, PersonaModel.apellido_materno, PersonaModel.nombres)\
                          .offset(skip)\
                          .limit(limit)\
                          .all()
        
        return [Persona.from_orm(p) for p in db_personas]

    @staticmethod
    def count(
        db: Session, 
        solo_activos: bool = True,
        nombres: Optional[str] = None,
        apellido_paterno: Optional[str] = None,
        apellido_materno: Optional[str] = None
    ) -> int:
        """Contar personas que coinciden con los filtros"""
        query = db.query(PersonaModel)
        
        # Comentado: El campo 'active' no existe en la tabla personas
        # if solo_activos:
        #     query = query.filter(PersonaModel.active == True)
        
        if nombres:
            query = query.filter(PersonaModel.nombres.ilike(f"%{nombres}%"))
        if apellido_paterno:
            query = query.filter(PersonaModel.apellido_paterno.ilike(f"%{apellido_paterno}%"))
        if apellido_materno:
            query = query.filter(PersonaModel.apellido_materno.ilike(f"%{apellido_materno}%"))
        
        return query.count()

    @staticmethod
    def update(db: Session, persona_id: int, dto: PersonaUpdateDTO) -> Persona:
        """Actualizar una persona"""
        try:
            # Buscar la persona
            db_persona = db.query(PersonaModel).filter(
                PersonaModel.id_persona == persona_id
            ).first()
            
            if not db_persona:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Persona con ID {persona_id} no encontrada"
                )
            
            # Actualizar solo los campos proporcionados
            update_data = dto.dict(exclude_unset=True, exclude_none=True)
            for field, value in update_data.items():
                setattr(db_persona, field, value)
            
            # Guardar cambios
            db.commit()
            db.refresh(db_persona)
            
            return Persona.from_orm(db_persona)
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar persona: {str(e)}"
            )

    @staticmethod
    def soft_delete(db: Session, persona_id: int) -> bool:
        """Eliminar una persona (eliminación física ya que no hay campo active)"""
        try:
            db_persona = db.query(PersonaModel).filter(
                PersonaModel.id_persona == persona_id
            ).first()
            
            if not db_persona:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Persona con ID {persona_id} no encontrada"
                )
            
            # Eliminar registro (eliminación física)
            db.delete(db_persona)
            db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al desactivar persona: {str(e)}"
            )

    @staticmethod
    def search_by_name(
        db: Session,
        nombres: Optional[str] = None,
        apellido_paterno: Optional[str] = None,
        apellido_materno: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        solo_activos: bool = True
    ) -> List[Persona]:
        """Búsqueda específica por nombres y apellidos"""
        return PersonaService.list(
            db=db,
            skip=skip,
            limit=limit,
            solo_activos=solo_activos,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno
        )

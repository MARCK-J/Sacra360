"""
Servicio para gestionar sacramentos en el sistema Sacra360
Incluye validación de duplicados y operaciones CRUD
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from app.models.sacramento_model import SacramentoModel
from app.models.persona_model import PersonaModel
from app.models.tipo_sacramento_model import TipoSacramentoModel
from app.models.institucion_model import InstitucionModel
from app.entities.sacramento import Sacramento


class SacramentoService:
    """Servicio para gestionar sacramentos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_duplicate(
        self,
        persona_id: int,
        tipo_id: int,
        libro_id: int = None,
        fecha_sacramento: date = None
    ) -> Dict[str, Any]:
        """
        Verifica si existe un sacramento duplicado.
        Una persona NO puede tener DOS sacramentos del mismo tipo (ej: dos bautizos).
        
        Args:
            persona_id: ID de la persona
            tipo_id: ID del tipo de sacramento
            libro_id: ID del libro (opcional, para contexto)
            fecha_sacramento: Fecha del sacramento (opcional, para contexto)
            
        Returns:
            Dict con 'exists' (bool) y 'sacramento' (dict si existe)
        """
        # Verificar si la persona ya tiene un sacramento de este tipo
        sacramento = self.db.query(SacramentoModel).filter(
            and_(
                SacramentoModel.persona_id == persona_id,
                SacramentoModel.tipo_id == tipo_id
            )
        ).first()
        
        if sacramento:
            # Obtener información adicional
            persona = self.db.query(PersonaModel).filter(PersonaModel.id_persona == persona_id).first()
            tipo = self.db.query(TipoSacramentoModel).filter(TipoSacramentoModel.id_tipo == tipo_id).first()
            
            return {
                "exists": True,
                "sacramento": {
                    "id_sacramento": sacramento.id_sacramento,
                    "persona": {
                        "id_persona": persona.id_persona,
                        "nombres": persona.nombres,
                        "apellido_paterno": persona.apellido_paterno,
                        "apellido_materno": persona.apellido_materno,
                        "fecha_nacimiento": persona.fecha_nacimiento.isoformat()
                    } if persona else None,
                    "tipo": {
                        "id_tipo": tipo.id_tipo,
                        "nombre": tipo.nombre
                    } if tipo else None,
                    "fecha_sacramento": sacramento.fecha_sacramento.isoformat(),
                    "fecha_registro": sacramento.fecha_registro.isoformat()
                }
            }
        
        return {"exists": False, "sacramento": None}
    
    def create(
        self,
        persona_id: int,
        tipo_id: int,
        usuario_id: int,
        institucion_id: int,
        libro_id: int,
        fecha_sacramento: date
    ) -> Sacramento:
        """
        Crea un nuevo sacramento con validación de duplicados
        
        Raises:
            ValueError: Si el sacramento ya existe (duplicado)
            IntegrityError: Si hay error de integridad en la BD
        """
        # Validar duplicado (solo por persona_id + tipo_id)
        duplicado = self.check_duplicate(persona_id, tipo_id)
        if duplicado["exists"]:
            tipo = self.db.query(TipoSacramentoModel).filter(TipoSacramentoModel.id_tipo == tipo_id).first()
            nombre_tipo = tipo.nombre if tipo else f"tipo {tipo_id}"
            raise ValueError(
                f"Esta persona ya tiene el sacramento de {nombre_tipo} registrado. "
                f"Una persona no puede tener el mismo sacramento dos veces. "
                f"ID sacramento existente: {duplicado['sacramento']['id_sacramento']}"
            )
        
        # Crear sacramento
        try:
            now = datetime.utcnow()
            nuevo_sacramento = SacramentoModel(
                persona_id=persona_id,
                tipo_id=tipo_id,
                usuario_id=usuario_id,
                institucion_id=institucion_id,
                libro_id=libro_id,
                fecha_sacramento=fecha_sacramento,
                fecha_registro=now,
                fecha_actualizacion=now
            )
            
            self.db.add(nuevo_sacramento)
            self.db.commit()
            self.db.refresh(nuevo_sacramento)
            
            return Sacramento.from_orm(nuevo_sacramento)
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Error al crear sacramento: {str(e)}")
    
    def get_by_id(self, sacramento_id: int) -> Optional[Sacramento]:
        """Obtiene un sacramento por su ID"""
        sacramento = self.db.query(SacramentoModel).filter(
            SacramentoModel.id_sacramento == sacramento_id
        ).first()
        
        if sacramento:
            return Sacramento.from_orm(sacramento)
        return None
    
    def get_by_persona(self, persona_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los sacramentos de una persona
        
        Returns:
            Lista de sacramentos con información completa
        """
        sacramentos = self.db.query(SacramentoModel).filter(
            SacramentoModel.persona_id == persona_id
        ).all()
        
        resultado = []
        for sacramento in sacramentos:
            tipo = self.db.query(TipoSacramentoModel).filter(
                TipoSacramentoModel.id_tipo == sacramento.tipo_id
            ).first()
            
            institucion = self.db.query(InstitucionModel).filter(
                InstitucionModel.id_institucion == sacramento.institucion_id
            ).first()
            
            resultado.append({
                "id_sacramento": sacramento.id_sacramento,
                "tipo": {
                    "id_tipo": tipo.id_tipo,
                    "nombre": tipo.nombre
                } if tipo else None,
                "institucion": {
                    "id_institucion": institucion.id_institucion,
                    "nombre": institucion.nombre
                } if institucion else None,
                "libro_id": sacramento.libro_id,
                "fecha_sacramento": sacramento.fecha_sacramento.isoformat(),
                "fecha_registro": sacramento.fecha_registro.isoformat()
            })
        
        return resultado
    
    def list_all(self, skip: int = 0, limit: int = 100) -> List[Sacramento]:
        """Lista todos los sacramentos con paginación"""
        sacramentos = self.db.query(SacramentoModel).offset(skip).limit(limit).all()
        return [Sacramento.from_orm(s) for s in sacramentos]

"""
Entidad Sacramento para el sistema Sacra360
Representa un sacramento registrado para una persona
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime


@dataclass
class Sacramento:
    """
    Entidad que representa un sacramento registrado
    
    Attributes:
        id_sacramento: ID único del sacramento
        persona_id: ID de la persona que recibió el sacramento
        tipo_id: ID del tipo de sacramento (1=Bautizo, 2=Confirmación, 3=Matrimonio)
        usuario_id: ID del usuario que registró el sacramento
        institucion_id: ID de la institución/parroquia donde se realizó
        libro_id: ID del libro donde está registrado
        fecha_sacramento: Fecha en que se realizó el sacramento
        fecha_registro: Fecha en que se registró en el sistema
        fecha_actualizacion: Fecha de última actualización
    """
    persona_id: int
    tipo_id: int
    usuario_id: int
    institucion_id: int
    libro_id: int
    fecha_sacramento: date
    fecha_registro: datetime
    fecha_actualizacion: datetime
    id_sacramento: Optional[int] = None

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            "id_sacramento": self.id_sacramento,
            "persona_id": self.persona_id,
            "tipo_id": self.tipo_id,
            "usuario_id": self.usuario_id,
            "institucion_id": self.institucion_id,
            "libro_id": self.libro_id,
            "fecha_sacramento": self.fecha_sacramento.isoformat() if isinstance(self.fecha_sacramento, date) else self.fecha_sacramento,
            "fecha_registro": self.fecha_registro.isoformat() if isinstance(self.fecha_registro, datetime) else self.fecha_registro,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if isinstance(self.fecha_actualizacion, datetime) else self.fecha_actualizacion
        }

    @classmethod
    def from_orm(cls, orm_obj):
        """Crear instancia desde modelo SQLAlchemy"""
        return cls(
            id_sacramento=orm_obj.id_sacramento,
            persona_id=orm_obj.persona_id,
            tipo_id=orm_obj.tipo_id,
            usuario_id=orm_obj.usuario_id,
            institucion_id=orm_obj.institucion_id,
            libro_id=orm_obj.libro_id,
            fecha_sacramento=orm_obj.fecha_sacramento,
            fecha_registro=orm_obj.fecha_registro,
            fecha_actualizacion=orm_obj.fecha_actualizacion
        )

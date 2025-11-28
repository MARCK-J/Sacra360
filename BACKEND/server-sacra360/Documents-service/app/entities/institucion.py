"""
Entidad Institucion para el sistema Sacra360
Representa una parroquia o institución religiosa
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Institucion:
    """
    Entidad que representa una institución/parroquia
    
    Attributes:
        id_institucion: ID único de la institución
        nombre: Nombre de la institución/parroquia
        direccion: Dirección física (opcional)
        telefono: Número de teléfono (opcional)
        email: Correo electrónico (opcional)
    """
    id_institucion: int
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            "id_institucion": self.id_institucion,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "email": self.email
        }

    @classmethod
    def from_orm(cls, orm_obj):
        """Crear instancia desde modelo SQLAlchemy"""
        return cls(
            id_institucion=orm_obj.id_institucion,
            nombre=orm_obj.nombre,
            direccion=orm_obj.direccion,
            telefono=orm_obj.telefono,
            email=orm_obj.email
        )

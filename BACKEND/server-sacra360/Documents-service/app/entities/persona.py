from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class Persona:
    id_persona: int
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: date
    lugar_nacimiento: str
    nombre_padre: str
    nombre_madre: str
    
    @classmethod
    def from_orm(cls, orm_obj):
        """Crear instancia desde modelo SQLAlchemy"""
        return cls(
            id_persona=orm_obj.id_persona,
            nombres=orm_obj.nombres,
            apellido_paterno=orm_obj.apellido_paterno,
            apellido_materno=orm_obj.apellido_materno,
            fecha_nacimiento=orm_obj.fecha_nacimiento,
            lugar_nacimiento=orm_obj.lugar_nacimiento,
            nombre_padre=orm_obj.nombre_padre,
            nombre_madre=orm_obj.nombre_madre
        )
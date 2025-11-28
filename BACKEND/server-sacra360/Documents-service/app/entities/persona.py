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
    fecha_bautismo: date
    nombre_padre_nombre_madre: str
    nombre_padrino_nombre_madrina: str
    
    @classmethod
    def from_orm(cls, orm_obj):
        """Crear instancia desde modelo SQLAlchemy"""
        return cls(
            id_persona=orm_obj.id_persona,
            nombres=orm_obj.nombres,
            apellido_paterno=orm_obj.apellido_paterno,
            apellido_materno=orm_obj.apellido_materno,
            fecha_nacimiento=orm_obj.fecha_nacimiento,
            fecha_bautismo=orm_obj.fecha_bautismo,
            nombre_padre_nombre_madre=orm_obj.nombre_padre_nombre_madre,
            nombre_padrino_nombre_madrina=orm_obj.nombre_padrino_nombre_madrina
        )
from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class Libro:
    id_libro: int
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    observaciones: Optional[str] = None
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, orm_obj):
        """Crear instancia desde modelo SQLAlchemy"""
        return cls(
            id_libro=orm_obj.id_libro,
            nombre=orm_obj.nombre,
            fecha_inicio=orm_obj.fecha_inicio,
            fecha_fin=orm_obj.fecha_fin,
            observaciones=orm_obj.observaciones,
            active=orm_obj.active,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at
        )
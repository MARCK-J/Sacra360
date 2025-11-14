from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import date
import re

class LibroCreateDTO(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del libro")
    fecha_inicio: date = Field(..., description="Fecha de inicio del libro")
    fecha_fin: date = Field(..., description="Fecha de fin del libro")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones del libro")

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        """Validar el nombre del libro"""
        if not v or not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

    @field_validator('fecha_fin')
    @classmethod
    def validate_fecha_fin(cls, v, info):
        """Validar que fecha_fin sea posterior a fecha_inicio"""
        # En Pydantic V2, necesitamos usar info para acceder a otros campos
        if 'fecha_inicio' in info.data and v <= info.data['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

    @field_validator('observaciones')
    @classmethod
    def validate_observaciones(cls, v):
        """Validar observaciones opcionales"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            return v
        return v

class LibroUpdateDTO(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    observaciones: Optional[str] = Field(None, max_length=500)

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El nombre no puede estar vacío')
            return v.strip()
        return v

    @field_validator('observaciones')
    @classmethod
    def validate_observaciones(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
            return v
        return v

class LibroResponseDTO(BaseModel):
    id_libro: int
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    observaciones: Optional[str]
    active: bool
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def from_orm(cls, obj):
        """Método de compatibilidad para crear desde objeto ORM"""
        return cls.model_validate(obj)
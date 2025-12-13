"""
DTOs (Data Transfer Objects) para registro de Bautizo
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional


class BautizoCreateDTO(BaseModel):
    """DTO para registrar un nuevo bautizo"""
    # Datos del libro e institución
    libro_id: int = Field(..., description="ID del libro donde se registra", gt=0)
    institucion_id: int = Field(..., description="ID de la parroquia/institución", gt=0)
    fecha_sacramento: date = Field(..., description="Fecha del bautizo")
    
    # Datos de la persona bautizada
    nombres: str = Field(..., min_length=1, max_length=100, description="Nombres de la persona bautizada")
    apellido_paterno: str = Field(..., min_length=1, max_length=50, description="Apellido paterno")
    apellido_materno: str = Field(..., min_length=1, max_length=50, description="Apellido materno")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    fecha_bautismo: date = Field(..., description="Fecha del bautismo (puede ser igual a fecha_sacramento)")
    
    # Padres y padrinos
    nombre_padre_nombre_madre: str = Field(..., max_length=200, description="Nombres completos del padre y madre")
    nombre_padrino_nombre_madrina: str = Field(..., max_length=200, description="Nombres completos del padrino y madrina")
    
    # Usuario que registra
    usuario_id: int = Field(..., description="ID del usuario que registra", gt=0)
    
    @field_validator('fecha_sacramento', 'fecha_nacimiento', 'fecha_bautismo')
    @classmethod
    def validar_fecha(cls, v):
        if v > date.today():
            raise ValueError('La fecha no puede ser futura')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "libro_id": 5,
                "institucion_id": 10,
                "fecha_sacramento": "1995-06-15",
                "nombres": "Juan Carlos",
                "apellido_paterno": "Pérez",
                "apellido_materno": "García",
                "fecha_nacimiento": "1995-05-20",
                "fecha_bautismo": "1995-06-15",
                "nombre_padre_nombre_madre": "Pedro Pérez López - María García Fernández",
                "nombre_padrino_nombre_madrina": "José Torres Ruiz - Ana Sánchez Díaz",
                "usuario_id": 4
            }
        }


class BautizoResponseDTO(BaseModel):
    """DTO para respuesta de bautizo registrado"""
    persona_id: int
    sacramento_id: int
    mensaje: str = "Bautizo registrado exitosamente"
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": 123,
                "sacramento_id": 456,
                "mensaje": "Bautizo registrado exitosamente"
            }
        }

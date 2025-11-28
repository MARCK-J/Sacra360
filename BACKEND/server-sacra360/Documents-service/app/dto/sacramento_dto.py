"""
DTOs (Data Transfer Objects) para Sacramentos
"""
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional


class SacramentoCreateDTO(BaseModel):
    """DTO para crear un nuevo sacramento"""
    persona_id: int = Field(..., description="ID de la persona que recibe el sacramento", gt=0)
    tipo_id: int = Field(..., description="ID del tipo de sacramento (1=Bautizo, 2=Confirmación, 3=Matrimonio)", gt=0)
    usuario_id: int = Field(..., description="ID del usuario que registra", gt=0)
    institucion_id: int = Field(..., description="ID de la parroquia/institución", gt=0)
    libro_id: int = Field(..., description="ID del libro donde se registra", gt=0)
    fecha_sacramento: date = Field(..., description="Fecha en que se realizó el sacramento")
    
    @validator('fecha_sacramento')
    def validar_fecha(cls, v):
        if v > date.today():
            raise ValueError('La fecha del sacramento no puede ser futura')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": 1,
                "tipo_id": 1,
                "usuario_id": 1,
                "institucion_id": 1,
                "libro_id": 5,
                "fecha_sacramento": "1995-05-20"
            }
        }


class SacramentoResponseDTO(BaseModel):
    """DTO para respuesta de sacramento"""
    id_sacramento: int
    persona_id: int
    tipo_id: int
    usuario_id: int
    institucion_id: int
    libro_id: int
    fecha_sacramento: date
    fecha_registro: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_sacramento": 1,
                "persona_id": 1,
                "tipo_id": 1,
                "usuario_id": 1,
                "institucion_id": 1,
                "libro_id": 5,
                "fecha_sacramento": "1995-05-20",
                "fecha_registro": "2024-11-28T10:30:00",
                "fecha_actualizacion": "2024-11-28T10:30:00"
            }
        }


class SacramentoCheckDTO(BaseModel):
    """DTO para verificar duplicados de sacramento"""
    persona_id: int = Field(..., gt=0)
    tipo_id: int = Field(..., gt=0)
    libro_id: int = Field(..., gt=0)
    fecha_sacramento: date

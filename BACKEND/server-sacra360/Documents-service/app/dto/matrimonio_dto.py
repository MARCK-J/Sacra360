"""
DTOs (Data Transfer Objects) para registro de Matrimonio
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional


class MatrimonioCreateDTO(BaseModel):
    """DTO para registrar un nuevo matrimonio"""
    # Datos del libro e institución
    libro_id: int = Field(..., description="ID del libro donde se registra", gt=0)
    institucion_id: int = Field(..., description="ID de la parroquia/institución donde se realizó el matrimonio", gt=0)
    fecha_sacramento: date = Field(..., description="Fecha del matrimonio")
    
    # Datos del esposo
    nombres_esposo: str = Field(..., min_length=1, max_length=100, description="Nombres del esposo")
    apellido_paterno_esposo: str = Field(..., min_length=1, max_length=50, description="Apellido paterno del esposo")
    apellido_materno_esposo: str = Field(..., min_length=1, max_length=50, description="Apellido materno del esposo")
    fecha_nacimiento_esposo: date = Field(..., description="Fecha de nacimiento del esposo")
    fecha_bautismo_esposo: date = Field(..., description="Fecha de bautismo del esposo")
    nombre_padrino_nombre_madrina_esposo: str = Field(..., max_length=200, description="Padrinos del esposo")
    
    # Datos de la esposa
    nombres_esposa: str = Field(..., min_length=1, max_length=100, description="Nombres de la esposa")
    apellido_paterno_esposa: str = Field(..., min_length=1, max_length=50, description="Apellido paterno de la esposa")
    apellido_materno_esposa: str = Field(..., min_length=1, max_length=50, description="Apellido materno de la esposa")
    fecha_nacimiento_esposa: date = Field(..., description="Fecha de nacimiento de la esposa")
    fecha_bautismo_esposa: date = Field(..., description="Fecha de bautismo de la esposa")
    nombre_padrino_nombre_madrina_esposa: str = Field(..., max_length=200, description="Padrinos de la esposa")
    
    # Padres del esposo
    nombre_padre_esposo: str = Field(..., max_length=100, description="Nombre completo del padre del esposo")
    nombre_madre_esposo: str = Field(..., max_length=100, description="Nombre completo de la madre del esposo")
    
    # Padres de la esposa
    nombre_padre_esposa: str = Field(..., max_length=100, description="Nombre completo del padre de la esposa")
    nombre_madre_esposa: str = Field(..., max_length=100, description="Nombre completo de la madre de la esposa")
    
    # Testigos
    testigos: str = Field(..., max_length=200, description="Nombres de los testigos del matrimonio")
    
    # Usuario que registra
    usuario_id: int = Field(..., description="ID del usuario que registra", gt=0)
    
    @field_validator('fecha_sacramento', 'fecha_nacimiento_esposo', 'fecha_nacimiento_esposa', 
               'fecha_bautismo_esposo', 'fecha_bautismo_esposa')
    @classmethod
    def validar_fecha(cls, v):
        if v > date.today():
            raise ValueError('La fecha no puede ser futura')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "libro_id": 8,
                "institucion_id": 15,
                "fecha_sacramento": "2024-08-25",
                "nombres_esposo": "Carlos Alberto",
                "apellido_paterno_esposo": "Rodríguez",
                "apellido_materno_esposo": "Mamani",
                "fecha_nacimiento_esposo": "1992-03-15",
                "fecha_bautismo_esposo": "1992-04-20",
                "nombre_padrino_nombre_madrina_esposo": "Juan Pérez - María López",
                "nombres_esposa": "Ana María",
                "apellido_paterno_esposa": "Flores",
                "apellido_materno_esposa": "Quispe",
                "fecha_nacimiento_esposa": "1994-07-10",
                "fecha_bautismo_esposa": "1994-08-15",
                "nombre_padrino_nombre_madrina_esposa": "Pedro García - Rosa Fernández",
                "nombre_padre_esposo": "Roberto Rodríguez Pérez",
                "nombre_madre_esposo": "Carmen Mamani de Rodríguez",
                "nombre_padre_esposa": "José Flores Torres",
                "nombre_madre_esposa": "Luisa Quispe de Flores",
                "testigos": "Miguel Sánchez Torres - Laura Gutiérrez Vargas",
                "usuario_id": 4
            }
        }


class MatrimonioResponseDTO(BaseModel):
    """DTO para respuesta de matrimonio registrado"""
    esposo_id: int
    esposa_id: int
    sacramento_id: int
    matrimonio_id: int
    mensaje: str = "Matrimonio registrado exitosamente"
    
    class Config:
        json_schema_extra = {
            "example": {
                "esposo_id": 201,
                "esposa_id": 202,
                "sacramento_id": 305,
                "matrimonio_id": 50,
                "mensaje": "Matrimonio registrado exitosamente"
            }
        }

from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import date
import re

class PersonaCreateDTO(BaseModel):
    nombres: str = Field(..., min_length=1, max_length=100, description="Nombres de la persona")
    apellidos: str = Field(..., min_length=1, max_length=100, description="Apellidos de la persona")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    lugar_nacimiento: Optional[str] = Field(None, max_length=100, description="Lugar de nacimiento")
    estado_civil: str = Field(..., description="Estado civil")
    ocupacion: Optional[str] = Field(None, max_length=100, description="Ocupación")

    @field_validator('nombres', 'apellidos')
    @classmethod
    def validate_names(cls, v):
        """Validar que los nombres solo contengan letras, espacios y acentos"""
        if not v or not v.strip():
            raise ValueError('No puede estar vacío')
        
        # Limpiar espacios extra
        v = ' '.join(v.strip().split())
        
        # Validar regex para solo letras, espacios y acentos
        pattern = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s]+$'
        if not re.match(pattern, v):
            raise ValueError('Solo se permiten letras, espacios y acentos')
        
        return v.title()  # Capitalizar

    @field_validator('fecha_nacimiento')
    @classmethod
    def validate_fecha_nacimiento(cls, v):
        """Validar que la fecha de nacimiento no sea futura"""
        if v > date.today():
            raise ValueError('La fecha de nacimiento no puede ser futura')
        return v

    @field_validator('estado_civil')
    @classmethod
    def validate_estado_civil(cls, v):
        """Validar estado civil"""
        estados_validos = ['soltero', 'casado', 'viudo', 'divorciado']
        if v.lower() not in estados_validos:
            raise ValueError(f'Estado civil debe ser uno de: {", ".join(estados_validos)}')
        return v.lower()

    @field_validator('lugar_nacimiento', 'ocupacion')
    @classmethod
    def validate_optional_text(cls, v):
        """Validar campos de texto opcionales"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            return v.title()
        return v

class PersonaUpdateDTO(BaseModel):
    nombres: Optional[str] = Field(None, min_length=1, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=100)
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = Field(None, max_length=100)
    estado_civil: Optional[str] = None
    ocupacion: Optional[str] = Field(None, max_length=100)

    @field_validator('nombres', 'apellidos')
    @classmethod
    def validate_names(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('No puede estar vacío')
            
            v = ' '.join(v.strip().split())
            pattern = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s]+$'
            if not re.match(pattern, v):
                raise ValueError('Solo se permiten letras, espacios y acentos')
            
            return v.title()
        return v

    @field_validator('fecha_nacimiento')
    @classmethod
    def validate_fecha_nacimiento(cls, v):
        if v is not None:
            if v > date.today():
                raise ValueError('La fecha de nacimiento no puede ser futura')
        return v

    @field_validator('estado_civil')
    @classmethod
    def validate_estado_civil(cls, v):
        if v is not None:
            estados_validos = ['soltero', 'casado', 'viudo', 'divorciado']
            if v.lower() not in estados_validos:
                raise ValueError(f'Estado civil debe ser uno de: {", ".join(estados_validos)}')
            return v.lower()
        return v

class PersonaResponseDTO(BaseModel):
    id_persona: int
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    lugar_nacimiento: Optional[str]
    estado_civil: str
    ocupacion: Optional[str]
    active: bool
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def from_orm(cls, obj):
        """Método de compatibilidad para crear desde objeto ORM"""
        return cls.model_validate(obj)
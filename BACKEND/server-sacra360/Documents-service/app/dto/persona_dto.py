from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

class PersonaCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    nombres: str = Field(..., min_length=2, max_length=100)
    apellido_paterno: str = Field(..., min_length=2, max_length=50)
    apellido_materno: str = Field(..., min_length=2, max_length=50)
    fecha_nacimiento: date
    fecha_bautismo: date
    nombre_padre_nombre_madre: str = Field(..., min_length=2, max_length=200)
    nombre_padrino_nombre_madrina: str = Field(..., min_length=2, max_length=200)


class PersonaUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido_paterno: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido_materno: Optional[str] = Field(None, min_length=2, max_length=50)
    fecha_nacimiento: Optional[date] = None
    fecha_bautismo: Optional[date] = None
    nombre_padre_nombre_madre: Optional[str] = Field(None, min_length=2, max_length=200)
    nombre_padrino_nombre_madrina: Optional[str] = Field(None, min_length=2, max_length=200)


class PersonaResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_persona: int
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: date
    fecha_bautismo: date
    nombre_padre_nombre_madre: str
    nombre_padrino_nombre_madrina: str

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    @property
    def apellidos(self) -> str:
        return f"{self.apellido_paterno} {self.apellido_materno}"
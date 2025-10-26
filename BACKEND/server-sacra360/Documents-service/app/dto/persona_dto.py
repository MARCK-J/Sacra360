from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

class PersonaCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    nombres: str = Field(..., min_length=2, max_length=100)
    apellido_paterno: str = Field(..., min_length=2, max_length=50)
    apellido_materno: str = Field(..., min_length=2, max_length=50)
    fecha_nacimiento: date
    lugar_nacimiento: str = Field(..., min_length=2, max_length=100)
    nombre_padre: str = Field(..., min_length=2, max_length=100)
    nombre_madre: str = Field(..., min_length=2, max_length=100)


class PersonaUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido_paterno: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido_materno: Optional[str] = Field(None, min_length=2, max_length=50)
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = Field(None, min_length=2, max_length=100)
    nombre_padre: Optional[str] = Field(None, min_length=2, max_length=100)
    nombre_madre: Optional[str] = Field(None, min_length=2, max_length=100)


class PersonaResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_persona: int
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: date
    lugar_nacimiento: str
    nombre_padre: str
    nombre_madre: str

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    @property
    def apellidos(self) -> str:
        return f"{self.apellido_paterno} {self.apellido_materno}"
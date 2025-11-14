from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

IdPBRegex = r"^[a-z0-9]{15}$"

class ResultadoCreateDTO(BaseModel):
    fecha_realizacion: Optional[date] = None
    puntuacion_total: Optional[int] = Field(default=None, ge=0)
    interpretacion: Optional[str] = None
    comentario: Optional[str] = None
    id_test: Optional[str] = Field(default=None, pattern=IdPBRegex)
    id_paciente: Optional[str] = Field(default=None, pattern=IdPBRegex)
    active: bool = True

class ResultadoUpdateDTO(BaseModel):
    fecha_realizacion: Optional[date] = None
    puntuacion_total: Optional[int] = Field(default=None, ge=0)
    interpretacion: Optional[str] = None
    comentario: Optional[str] = None
    id_test: Optional[str] = Field(default=None, pattern=IdPBRegex)
    id_paciente: Optional[str] = Field(default=None, pattern=IdPBRegex)
    active: Optional[bool] = None

class ResultadoOutDTO(BaseModel):
    id: str
    fecha_realizacion: Optional[str] = None
    puntuacion_total: Optional[int] = None
    interpretacion: Optional[str] = None
    comentario: Optional[str] = None
    id_test: Optional[str] = None
    id_paciente: Optional[str] = None
    active: bool
    created: Optional[str] = None
    updated: Optional[str] = None

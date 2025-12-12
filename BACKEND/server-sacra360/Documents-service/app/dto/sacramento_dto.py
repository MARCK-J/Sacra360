from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import date


class SacramentoCreateDTO(BaseModel):
    model_config = ConfigDict(extra='allow', from_attributes=True)

    tipo_sacramento: Optional[str] = Field(None)
    tipo_id: Optional[int] = Field(None)
    id_persona: Optional[int] = Field(None)
    persona_id: Optional[int] = Field(None)
    person_name: Optional[str] = Field(None)
    fecha_sacramento: Optional[str] = Field(None)
    libro_id: Optional[int] = Field(None)
    institucion_id: Optional[int] = Field(None)
    institucion: Optional[str] = Field(None)
    usuario_registro_id: Optional[int] = Field(None)

    # Detail fields
    ministro: Optional[str] = Field(None)
    padrino: Optional[str] = Field(None)
    foja: Optional[str] = Field(None)
    numero_acta: Optional[str] = Field(None)
    nombre_esposo: Optional[str] = Field(None)
    nombre_esposa: Optional[str] = Field(None)
    reg_civil: Optional[str] = Field(None)


class SacramentoUpdateDTO(BaseModel):
    model_config = ConfigDict(extra='allow', from_attributes=True)

    persona_id: Optional[int] = Field(None)
    tipo_id: Optional[int] = Field(None)
    usuario_id: Optional[int] = Field(None)
    institucion_id: Optional[int] = Field(None)
    libro_id: Optional[int] = Field(None)
    fecha_sacramento: Optional[str] = Field(None)
    ministro: Optional[str] = Field(None)
    padrinos: Optional[str] = Field(None)
    observaciones: Optional[str] = Field(None)
    foja: Optional[str] = Field(None)
    numero_acta: Optional[str] = Field(None)
    pagina: Optional[str] = Field(None)


class SacramentoResponseDTO(BaseModel):
    model_config = ConfigDict(extra='allow', from_attributes=True)

    id_sacramento: Optional[int]
    persona_id: Optional[int]
    tipo_id: Optional[int]
    fecha_sacramento: Optional[date]
    persona_nombre: Optional[str]
    tipo_nombre: Optional[str]
    institucion_nombre: Optional[str]
    libro_id: Optional[int]
    foja: Optional[str]
    numero_acta: Optional[str]
"""
DTOs para Sacramentos (Documents-service)
Usa Pydantic V2 para validación y serialización
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from pydantic import ConfigDict


class SacramentoCreateDTO(BaseModel):
    persona_id: int = Field(..., description="ID de la persona asociada")
    tipo_id: int | str = Field(..., description="ID o nombre del tipo de sacramento")
    libro_id: Optional[int] = Field(None, description="ID del libro donde se registra")
    fecha_sacramento: date = Field(..., description="Fecha del sacramento (YYYY-MM-DD)")
    lugar_sacramento: Optional[str] = Field(None, max_length=200)
    ministro: Optional[str] = Field(None, max_length=150)
    padrinos: Optional[str] = Field(None, max_length=300)
    observaciones: Optional[str] = Field(None, max_length=1000)
    numero_acta: Optional[str] = Field(None, max_length=50)
    folio: Optional[str] = Field(None, max_length=50)
    pagina: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class SacramentoUpdateDTO(BaseModel):
    libro_id: Optional[int]
    fecha_sacramento: Optional[date]
    lugar_sacramento: Optional[str]
    ministro: Optional[str]
    padrinos: Optional[str]
    observaciones: Optional[str]
    numero_acta: Optional[str]
    folio: Optional[str]
    pagina: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SacramentoResponseDTO(BaseModel):
    id_sacramento: int
    persona_id: int
    tipo_id: int
    tipo_nombre: Optional[str]
    libro_id: Optional[int]
    fecha_sacramento: Optional[date]
    lugar_sacramento: Optional[str]
    ministro: Optional[str]
    padrinos: Optional[str]
    observaciones: Optional[str]
    numero_acta: Optional[str]
    folio: Optional[str]
    pagina: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SacramentoListResponseDTO(BaseModel):
    sacramentos: List[SacramentoResponseDTO]
    total: int

    model_config = ConfigDict(from_attributes=True)
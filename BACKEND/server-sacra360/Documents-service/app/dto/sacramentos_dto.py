"""
DTOs para Sacramentos
Modelos Pydantic para creacion y respuesta de sacramentos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SacramentoCreateDTO(BaseModel):
    id_persona: int = Field(...)
    tipo_sacramento: str = Field(...)
    fecha_sacramento: datetime = Field(...)
    lugar_sacramento: Optional[str] = None
    sacerdote_celebrante: Optional[str] = None
    padrino: Optional[str] = None
    madrina: Optional[str] = None
    observaciones: Optional[str] = None
    numero_acta: Optional[str] = None
    libro_registro: Optional[str] = None
    folio: Optional[str] = None
    activo: Optional[bool] = True
    id_persona_conyuge: Optional[int] = None
    testigo_1: Optional[str] = None
    testigo_2: Optional[str] = None


class SacramentoResponseDTO(SacramentoCreateDTO):
    id_sacramento: str

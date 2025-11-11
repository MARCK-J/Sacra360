"""
Entidades de Sacramentos
Modelos de dominio (Pydantic) para sacramentos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SacramentoEntity(BaseModel):
    id_sacramento: str
    id_persona: int
    tipo_sacramento: str
    fecha_sacramento: datetime
    lugar_sacramento: Optional[str] = None
    sacerdote_celebrante: Optional[str] = None
    padrino: Optional[str] = None
    madrina: Optional[str] = None
    observaciones: Optional[str] = None
    numero_acta: Optional[str] = None
    libro_registro: Optional[str] = None
    folio: Optional[str] = None
    activo: bool = True
    id_persona_conyuge: Optional[int] = None
    testigo_1: Optional[str] = None
    testigo_2: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

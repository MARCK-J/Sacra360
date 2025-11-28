"""
DTOs para endpoints de reportes (Documents-service)
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from pydantic import ConfigDict


class CountByTypeItemDTO(BaseModel):
    tipo: str
    total: int

    model_config = ConfigDict(from_attributes=True)


class CountByTypeResponseDTO(BaseModel):
    counts: List[CountByTypeItemDTO]

    model_config = ConfigDict(from_attributes=True)


class SummaryResponseDTO(BaseModel):
    total: int
    by_type: List[CountByTypeItemDTO]

    model_config = ConfigDict(from_attributes=True)
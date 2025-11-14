"""
DTOs (Data Transfer Objects) para TipoSacramento
Utilizando Pydantic V2 para validación y serialización de datos
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TipoSacramentoCreateDTO(BaseModel):
    """DTO para crear un nuevo tipo de sacramento"""
    
    nombre: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Nombre del tipo de sacramento",
        examples=["Bautismo", "Confirmación", "Matrimonio"]
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descripción opcional del tipo de sacramento",
        examples=["Sacramento de iniciación cristiana"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "nombre": "Bautismo",
                "descripcion": "Sacramento de iniciación cristiana que purifica del pecado original"
            }
        }
    )


class TipoSacramentoUpdateDTO(BaseModel):
    """DTO para actualizar un tipo de sacramento existente"""
    
    nombre: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=50,
        description="Nombre del tipo de sacramento"
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descripción del tipo de sacramento"
    )

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "nombre": "Confirmación",
                "descripcion": "Sacramento que confirma y fortalece la fe del bautizado"
            }
        }
    )


class TipoSacramentoResponseDTO(BaseModel):
    """DTO para respuesta con información de tipo de sacramento"""
    
    id_tipo: int = Field(
        ...,
        description="ID único del tipo de sacramento",
        examples=[1, 2, 3]
    )
    nombre: str = Field(
        ...,
        description="Nombre del tipo de sacramento",
        examples=["Bautismo", "Confirmación", "Matrimonio"]
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción del tipo de sacramento"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id_tipo": 1,
                "nombre": "Bautismo",
                "descripcion": "Sacramento de iniciación cristiana que purifica del pecado original"
            }
        }
    )


class TipoSacramentoListResponseDTO(BaseModel):
    """DTO para respuesta de lista de tipos de sacramentos"""
    
    tipos_sacramentos: list[TipoSacramentoResponseDTO] = Field(
        ...,
        description="Lista de tipos de sacramentos"
    )
    total: int = Field(
        ...,
        description="Total de tipos de sacramentos encontrados"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "tipos_sacramentos": [
                    {
                        "id_tipo": 1,
                        "nombre": "Bautismo",
                        "descripcion": "Sacramento de iniciación cristiana"
                    },
                    {
                        "id_tipo": 2,
                        "nombre": "Confirmación", 
                        "descripcion": "Sacramento de fortalecimiento de la fe"
                    }
                ],
                "total": 2
            }
        }
    )
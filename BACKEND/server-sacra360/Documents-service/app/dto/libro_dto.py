from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

class LibroCreateDTO(BaseModel):
    """DTO para crear un nuevo libro"""
    model_config = ConfigDict(from_attributes=True)
    
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre del libro")
    fecha_inicio: date = Field(..., description="Fecha de inicio del libro")
    fecha_fin: date = Field(..., description="Fecha de fin del libro")
    observaciones: Optional[str] = Field(None, max_length=1000, description="Observaciones del libro")


class LibroUpdateDTO(BaseModel):
    """DTO para actualizar un libro existente"""
    model_config = ConfigDict(from_attributes=True)
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=50, description="Nombre del libro")
    fecha_inicio: Optional[date] = Field(None, description="Fecha de inicio del libro")
    fecha_fin: Optional[date] = Field(None, description="Fecha de fin del libro")
    observaciones: Optional[str] = Field(None, max_length=1000, description="Observaciones del libro")


class LibroResponseDTO(BaseModel):
    """DTO para respuesta con información de libro"""
    model_config = ConfigDict(from_attributes=True)
    
    id_libro: int = Field(..., description="ID único del libro")
    nombre: str = Field(..., description="Nombre del libro")
    fecha_inicio: date = Field(..., description="Fecha de inicio del libro")
    fecha_fin: date = Field(..., description="Fecha de fin del libro")
    observaciones: Optional[str] = Field(None, description="Observaciones del libro")


class LibroListResponseDTO(BaseModel):
    """DTO para respuesta de lista de libros"""
    model_config = ConfigDict(from_attributes=True)
    
    libros: list[LibroResponseDTO] = Field(..., description="Lista de libros")
    total: int = Field(..., description="Total de libros encontrados")
    titulo: Optional[str] = None
    tipo_sacramento: Optional[str] = None
    parroquia: Optional[str] = None
    active: Optional[bool] = None
    fecha_inicio_desde: Optional[date] = None
    fecha_inicio_hasta: Optional[date] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    order_by: Optional[str] = Field("id")
    order_direction: Optional[str] = Field("asc")
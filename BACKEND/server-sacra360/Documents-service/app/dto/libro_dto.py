from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

class LibroCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    numero_libro: int = Field(..., ge=1)
    tipo_sacramento: str = Field(..., min_length=1, max_length=50)
    parroquia: str = Field(..., min_length=1, max_length=100)
    archivo_url: Optional[str] = Field(None, max_length=500)
    active: bool = Field(default=True)


class LibroUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    numero_libro: Optional[int] = Field(None, ge=1)
    tipo_sacramento: Optional[str] = Field(None, min_length=1, max_length=50)
    parroquia: Optional[str] = Field(None, min_length=1, max_length=100)
    archivo_url: Optional[str] = Field(None, max_length=500)
    active: Optional[bool] = None


class LibroResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    titulo: str
    descripcion: Optional[str]
    fecha_inicio: date
    fecha_fin: Optional[date]
    numero_libro: int
    tipo_sacramento: str
    parroquia: str
    archivo_url: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime


class LibroListParamsDTO(BaseModel):
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
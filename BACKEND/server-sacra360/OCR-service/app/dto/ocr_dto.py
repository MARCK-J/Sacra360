from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# DTOs para Requests
class OcrProcessRequest(BaseModel):
    """DTO para solicitar procesamiento OCR"""
    libros_id: int = Field(..., description="ID del libro al que pertenece el documento")
    tipo_sacramento: Optional[int] = Field(None, description="Tipo de sacramento (1=bautizo, 2=confirmacion, etc.)")
    guardar_en_bd: bool = Field(True, description="Si guardar o no los resultados en base de datos")

class CampoConfirmacion(BaseModel):
    """DTO para un campo individual de confirmación"""
    campo: str = Field(..., description="Nombre del campo")
    valor: str = Field(..., description="Valor extraído")
    confianza: float = Field(..., ge=0, le=1, description="Nivel de confianza del OCR (0-1)")
    celda_index: int = Field(..., description="Índice de celda en la tupla")

class TuplaConfirmacion(BaseModel):
    """DTO para una tupla completa de confirmación"""
    tupla_numero: int = Field(..., description="Número de tupla")
    nombre_confirmando: str = Field("", description="Nombres completos del confirmando")
    dia_nacimiento: str = Field("", description="Día de nacimiento")
    mes_nacimiento: str = Field("", description="Mes de nacimiento")
    ano_nacimiento: str = Field("", description="Año de nacimiento")
    parroquia_bautismo: str = Field("", description="Parroquia de bautismo")
    dia_bautismo: str = Field("", description="Día de bautismo")
    mes_bautismo: str = Field("", description="Mes de bautismo")
    ano_bautismo: str = Field("", description="Año de bautismo")
    padres: str = Field("", description="Nombres completos de los padres")
    padrinos: str = Field("", description="Nombres completos de los padrinos")
    
    coordenadas: Dict[str, int] = Field(default_factory=dict, description="Coordenadas de la tupla en la imagen")
    calidad_extraccion: float = Field(0.0, description="Calidad general de extracción de la tupla")

# DTOs para Responses
class OcrCampoResponse(BaseModel):
    """Respuesta para un campo individual de OCR"""
    id_ocr: Optional[int] = Field(None, description="ID del registro en BD")
    campo: str = Field(..., description="Nombre del campo")
    valor_extraido: str = Field(..., description="Valor extraído")
    confianza: float = Field(..., description="Nivel de confianza")
    fuente_modelo: str = Field(..., description="Modelo utilizado para OCR")
    validado: bool = Field(False, description="Si el campo ha sido validado")

class OcrTuplaResponse(BaseModel):
    """Respuesta para una tupla completa procesada"""
    tupla_numero: int
    confirmando: OcrCampoResponse
    fecha_nacimiento: OcrCampoResponse
    parroquia_bautismo: OcrCampoResponse
    fecha_bautismo: OcrCampoResponse
    padres: OcrCampoResponse
    padrinos: OcrCampoResponse
    
    calidad_general: float = Field(..., description="Calidad general de la tupla")
    coordenadas: Dict[str, int] = Field(default_factory=dict)

class OcrProcessResponse(BaseModel):
    """Respuesta completa del procesamiento OCR"""
    success: bool = Field(..., description="Si el procesamiento fue exitoso")
    documento_id: Optional[int] = Field(None, description="ID del documento en BD")
    total_tuplas: int = Field(..., description="Total de tuplas procesadas")
    tuplas: List[OcrTuplaResponse] = Field(..., description="Lista de tuplas procesadas")
    
    # Métricas de calidad
    calidad_general: float = Field(..., description="Calidad general del procesamiento")
    tuplas_alta_calidad: int = Field(..., description="Número de tuplas con alta calidad")
    
    # Metadatos
    modelo_utilizado: str = Field(..., description="Modelo OCR utilizado")
    tiempo_procesamiento: float = Field(..., description="Tiempo de procesamiento en segundos")
    fecha_procesamiento: datetime = Field(..., description="Fecha y hora del procesamiento")
    
    message: str = Field("", description="Mensaje adicional")
    error: Optional[str] = Field(None, description="Mensaje de error si aplica")

class HealthCheckResponse(BaseModel):
    """Respuesta del health check"""
    service: str
    version: str
    status: str
    timestamp: datetime
    dependencies: Dict[str, str] = Field(default_factory=dict)
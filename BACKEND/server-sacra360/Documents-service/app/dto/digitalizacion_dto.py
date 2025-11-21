"""
DTOs para el sistema de digitalización
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EstadoProcesamiento(str, Enum):
    SUBIDO = "subido"
    EN_COLA = "en_cola"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"

class UploadDocumentRequest(BaseModel):
    """Request para upload de documento"""
    libro_id: int = Field(..., description="ID del libro")
    tipo_sacramento: int = Field(..., description="Tipo de sacramento")
    institucion_id: int = Field(1, description="ID de la institución")
    procesar_automaticamente: bool = Field(True, description="Procesar con OCR automáticamente")

class UploadDocumentResponse(BaseModel):
    """Respuesta del upload de documento"""
    success: bool
    documento_id: int
    mensaje: str
    archivo_url: str
    estado: EstadoProcesamiento
    tiempo_upload: float
    
    # Información OCR (si se procesó)
    ocr_procesado: bool = False
    ocr_resultado: Optional[Dict[str, Any]] = None
    total_tuplas: Optional[int] = None
    calidad_general: Optional[float] = None
    tiempo_ocr: Optional[float] = None

class ProcessingStatusResponse(BaseModel):
    """Estado de procesamiento de un documento"""
    documento_id: int
    estado: EstadoProcesamiento
    progreso: int = Field(..., description="Porcentaje de progreso (0-100)")
    mensaje: str
    archivo_url: str
    fecha_subida: datetime
    
    # Datos OCR si está completado
    ocr_completado: bool = False
    total_tuplas: Optional[int] = None
    calidad_general: Optional[float] = None
    fecha_procesamiento_ocr: Optional[datetime] = None

class DocumentoInfo(BaseModel):
    """Información de un documento"""
    documento_id: int
    libro_id: int
    tipo_sacramento: int
    archivo_url: str
    estado: EstadoProcesamiento
    fecha_subida: datetime
    nombre_archivo: str
    tamaño_archivo: int
    
    # Información OCR
    ocr_procesado: bool
    total_tuplas: Optional[int] = None
    calidad_general: Optional[float] = None

class DocumentListResponse(BaseModel):
    """Lista de documentos"""
    documentos: List[DocumentoInfo]
    total: int
    skip: int
    limit: int

class OcrResultadoResponse(BaseModel):
    """Resultado de procesamiento OCR"""
    documento_id: int
    total_tuplas: int
    calidad_general: float
    tiempo_procesamiento: float
    tuplas: List[Dict[str, Any]]
    mensaje: str
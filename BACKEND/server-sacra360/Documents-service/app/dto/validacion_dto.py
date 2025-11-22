"""
DTOs para el sistema de validación de tuplas OCR
Define las estructuras de datos para requests y responses del proceso de validación
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class CampoOCRResponse(BaseModel):
    """Representa un campo extraído por OCR con su información"""
    id_ocr: int
    campo: str
    valor_extraido: str
    confianza: float
    validado: bool = False
    sacramento_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class TuplaValidacionResponse(BaseModel):
    """Representa una tupla completa con todos sus campos OCR"""
    documento_id: int
    tupla_numero: int
    campos_ocr: List[CampoOCRResponse]
    estado_validacion: str
    fecha_extraccion: Optional[datetime] = None
    total_tuplas_documento: int
    
    class Config:
        from_attributes = True

class CorreccionCampo(BaseModel):
    """Representa una corrección aplicada a un campo OCR"""
    id_ocr: int
    valor_original: str
    valor_corregido: str
    comentario: Optional[str] = None

class ValidacionRequest(BaseModel):
    """Request para validar una tupla con posibles correcciones"""
    documento_id: int
    tupla_numero: int
    tupla_id_ocr: Optional[int] = None
    usuario_validador_id: int
    institucion_id: Optional[int] = None
    correcciones: List[CorreccionCampo] = []
    datos_validados: Optional[Dict[str, Any]] = None
    observaciones: Optional[str] = None
    accion: str = Field(..., description="'aprobar', 'corregir', 'rechazar'")
    
    class Config:
        schema_extra = {
            "example": {
                "documento_id": 1,
                "tupla_numero": 1,
                "usuario_validador_id": 1,
                "institucion_id": 1,
                "datos_validados": {
                    "nombre_confirmando": "Juan Pérez García",
                    "dia_nacimiento": "15",
                    "mes_nacimiento": "6",
                    "ano_nacimiento": "1990"
                },
                "observaciones": "Registro validado",
                "accion": "aprobar"
            }
        }

class ValidacionStatusResponse(BaseModel):
    """Response del estado de validación"""
    documento_id: int
    tupla_actual: int
    tupla_validada: bool
    siguiente_tupla: Optional[int] = None
    tuplas_pendientes: int
    tuplas_validadas: int
    total_tuplas: int
    completado: bool = False
    mensaje: str
    
    class Config:
        schema_extra = {
            "example": {
                "documento_id": 1,
                "tupla_actual": 1,
                "tupla_validada": True,
                "siguiente_tupla": 2,
                "tuplas_pendientes": 4,
                "tuplas_validadas": 1,
                "total_tuplas": 5,
                "completado": False,
                "mensaje": "Tupla validada exitosamente. Siguiente tupla disponible."
            }
        }

class ValidacionCompleteRequest(BaseModel):
    """Request para completar la validación de un documento"""
    usuario_validador_id: int
    observaciones_finales: Optional[str] = None
    registrar_sacramentos: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "usuario_validador_id": 1,
                "observaciones_finales": "Documento procesado completamente",
                "registrar_sacramentos": True
            }
        }

class EstadoValidacionResponse(BaseModel):
    """Response detallado del estado de validación de un documento"""
    documento_id: int
    nombre_archivo: str
    tipo_sacramento: str
    libro_id: int
    fecha_digitalizacion: datetime
    total_tuplas: int
    tuplas_validadas: int
    tuplas_pendientes: int
    tuplas_rechazadas: int
    estado_general: str
    progreso_porcentaje: float
    tiempo_estimado_restante: Optional[str] = None
    ultima_actividad: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ResumenValidacionResponse(BaseModel):
    """Resumen de la validación para dashboard"""
    documentos_en_validacion: int
    tuplas_pendientes_total: int
    documentos_completados_hoy: int
    tiempo_promedio_validacion: Optional[float] = None
    documentos_por_tipo: Dict[str, int]
    
    class Config:
        schema_extra = {
            "example": {
                "documentos_en_validacion": 3,
                "tuplas_pendientes_total": 45,
                "documentos_completados_hoy": 2,
                "tiempo_promedio_validacion": 12.5,
                "documentos_por_tipo": {
                    "bautismo": 2,
                    "matrimonio": 1
                }
            }
        }

class HistorialValidacionResponse(BaseModel):
    """Historial de validaciones de un usuario"""
    usuario_id: int
    nombre_usuario: str
    validaciones_realizadas: int
    documentos_completados: int
    tiempo_total_validacion: float
    promedio_tiempo_por_tupla: float
    fecha_primera_validacion: Optional[datetime] = None
    fecha_ultima_validacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True
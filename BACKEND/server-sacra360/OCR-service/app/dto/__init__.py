# DTOs Module
from .ocr_dto import (
    OcrProcessRequest, OcrProcessResponse, OcrTuplaResponse, 
    OcrCampoResponse, TuplaConfirmacion, CampoConfirmacion,
    HealthCheckResponse
)

__all__ = [
    "OcrProcessRequest", "OcrProcessResponse", "OcrTuplaResponse",
    "OcrCampoResponse", "TuplaConfirmacion", "CampoConfirmacion", 
    "HealthCheckResponse"
]
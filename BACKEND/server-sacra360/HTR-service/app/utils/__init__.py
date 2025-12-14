"""
Utilidades varias para el servicio HTR
"""

import os
import hashlib
from datetime import datetime
from typing import Optional

def generate_file_hash(file_content: bytes) -> str:
    """Generar hash SHA256 de un archivo"""
    return hashlib.sha256(file_content).hexdigest()

def get_timestamp() -> str:
    """Obtener timestamp actual en formato ISO"""
    return datetime.utcnow().isoformat()

def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Validar extensión de archivo"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

def format_confidence(confidence: float) -> str:
    """Formatear confianza como porcentaje"""
    return f"{confidence * 100:.2f}%"

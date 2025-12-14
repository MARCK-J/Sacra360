import os
from typing import Optional

class Settings:
    """Configuración del servicio OCR - Simplificada"""
    
    def __init__(self):
        # Base de datos
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sacra360")
        
        # Configuración del servicio
        self.service_name = "OCR Service - Sacra360"
        self.service_version = "1.0.0"
        self.service_port = int(os.getenv("SERVICE_PORT", "8003"))
        
        # Configuración de OCR
        self.tesseract_path = os.getenv("TESSERACT_PATH")
        self.ocr_language = "spa"  # Español
        
        # Configuración de archivos
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_file_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        
        # Configuración de logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Configuración CORS
        self.cors_origins = ["*"]  # En producción, especificar dominios permitidos

# Instancia global de configuración
settings = Settings()

# Mapeo de tipos de sacramento
TIPOS_SACRAMENTO = {
    1: "bautizo",
    2: "confirmacion", 
    3: "matrimonio",
    4: "primera_comunion"
}

# Mapeo de campos por tipo de sacramento
CAMPOS_CONFIRMACION = [
    "nombre_confirmando",
    "dia_nacimiento", 
    "mes_nacimiento",
    "ano_nacimiento",
    "parroquia_bautismo",
    "dia_bautismo",
    "mes_bautismo", 
    "ano_bautismo",
    "padres",
    "padrinos"
]

CAMPOS_BAUTIZO = [
    "nombre_bautizado",
    "dia_nacimiento",
    "mes_nacimiento", 
    "ano_nacimiento",
    "lugar_nacimiento",
    "dia_bautizo",
    "mes_bautizo",
    "ano_bautizo",
    "padres",
    "padrinos",
    "ministro"
]
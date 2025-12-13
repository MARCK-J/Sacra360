"""
Configuración centralizada del servicio HTR - Sacra360
"""

import os
from typing import Optional, List

class Settings:
    """Configuración del servicio HTR"""
    
    def __init__(self):
        # Base de datos
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sacra360")
        
        # Configuración del servicio
        self.service_name = "HTR Service - Sacra360"
        self.service_version = "1.0.0"
        self.service_port = int(os.getenv("SERVICE_PORT", "8004"))
        
        # Configuración de HTR
        self.htr_model_path = os.getenv("HTR_MODEL_PATH", "./models/htr_model.pth")
        self.htr_confidence_threshold = float(os.getenv("HTR_CONFIDENCE_THRESHOLD", "0.7"))
        
        # Configuración de archivos
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
        self.allowed_file_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        
        # Configuración de logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Configuración CORS
        cors_origins_str = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        # Configuración MinIO
        self.minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.minio_access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        self.minio_secret_key = os.getenv("MINIO_SECRET_KEY", "password123")
        # HTR usa bucket separado del OCR
        self.minio_htr_bucket = os.getenv("MINIO_HTR_BUCKET", "sacra360-htr")
        self.minio_secure = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Instancia global de configuración
settings = Settings()

# Mapeo de tipos de sacramento
TIPOS_SACRAMENTO = {
    1: "bautizo",
    2: "confirmacion", 
    3: "matrimonio",
    4: "primera_comunion"
}

# Mapeo de campos por tipo de sacramento (para HTR)
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

CAMPOS_MATRIMONIO = [
    "nombre_esposo",
    "nombre_esposa",
    "dia_matrimonio",
    "mes_matrimonio",
    "ano_matrimonio",
    "lugar_matrimonio",
    "testigos",
    "ministro"
]

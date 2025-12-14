from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Database
    database_url: str = "postgresql://usuario:password@localhost:5432/sacra360_documents"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sacra360_documents"
    db_user: str = "usuario"
    db_password: str = "password"
    
    # FastAPI
    debug: bool = True
    secret_key: str = "tu_clave_secreta_muy_segura_aqui"
    
    # JWT
    jwt_secret_key: str = "tu_jwt_secret_key_aqui"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "*"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

def get_settings() -> Settings:
    """Obtener configuración de la aplicación"""
    return settings
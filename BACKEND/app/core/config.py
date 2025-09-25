from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Configuración de la aplicación
    app_name: str = "Sacra360 API"
    version: str = "1.0.0"
    description: str = "API para el sistema Sacra360"
    
    # Seguridad
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Base de datos
    database_url: str
    
    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    model_config = SettingsConfigDict(
        env_file="BACKEND/.env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
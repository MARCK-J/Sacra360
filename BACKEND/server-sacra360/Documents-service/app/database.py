from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL de conexión a PostgreSQL - usar la misma configuración que docker-compose.yml
SQLALCHEMY_DATABASE_URL = os.getenv(
    "POSTGRES_URL", 
    "postgresql://postgres:lolsito101@postgres:5432/sacra360"
)

# Crear el engine de SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Solo mostrar SQL en desarrollo
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    pool_recycle=3600,  # Reciclar conexiones cada hora
    pool_size=10,  # Tamaño del pool de conexiones
    max_overflow=20  # Conexiones adicionales si es necesario
)

# Crear sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
def get_db():
    """
    Dependency que proporciona una sesión de base de datos.
    Se encarga de cerrar la sesión automáticamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
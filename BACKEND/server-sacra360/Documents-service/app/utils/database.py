from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL de conexión a PostgreSQL - usar variable de entorno o valor por defecto
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/sacra360"
)

# Crear el engine de SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Mostrar SQL queries en desarrollo
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    pool_recycle=3600  # Reciclar conexiones cada hora
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
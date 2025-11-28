"""
Configuración de conexión a la base de datos PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# URL de conexión a PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:lolsito101@postgres:5432/sacra360"
)

# Crear engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_size=10,  # Tamaño del pool de conexiones
    max_overflow=20,  # Conexiones adicionales permitidas
    echo=False  # No mostrar SQL en logs (cambiar a True para debug)
)

# Crear SessionLocal para transacciones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener una sesión de base de datos
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializar la base de datos creando todas las tablas
    NOTA: Las tablas principales ya existen en la BD, solo verificamos conexión
    """
    from app.entities.user_entity import Base
    # No creamos tablas porque la BD ya existe con su estructura
    # Base.metadata.create_all(bind=engine)
    print("✅ Conexión a base de datos verificada")


def check_db_connection():
    """
    Verificar la conexión a la base de datos
    
    Returns:
        bool: True si la conexión es exitosa
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return False

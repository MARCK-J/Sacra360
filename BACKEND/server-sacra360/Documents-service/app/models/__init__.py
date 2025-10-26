from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class PersonaModel(Base):
    __tablename__ = "personas"
    
    id_persona = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    lugar_nacimiento = Column(String(100), nullable=False)
    nombre_padre = Column(String(100), nullable=False)
    nombre_madre = Column(String(100), nullable=False)

class LibroModel(Base):
    __tablename__ = "libros"
    
    id_libro = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)  # Aumenté el límite
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    observaciones = Column(Text, nullable=True)
    
    # Campos adicionales para control
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Exportar los modelos para facilitar las importaciones
__all__ = ["PersonaModel", "LibroModel"]
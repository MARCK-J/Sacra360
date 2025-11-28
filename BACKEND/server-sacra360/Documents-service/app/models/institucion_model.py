"""
Modelo SQLAlchemy para la tabla institucionesparroquias
Define la estructura de instituciones/parroquias
"""
from sqlalchemy import Column, Integer, String
from app.database import Base


class InstitucionModel(Base):
    """Modelo para la tabla institucionesparroquias"""
    __tablename__ = "institucionesparroquias"
    
    id_institucion = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(150), nullable=True)
    telefono = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Institucion(id={self.id_institucion}, nombre={self.nombre})>"

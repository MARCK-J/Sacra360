"""
Modelo SQLAlchemy para la tabla libros
Define la estructura de los libros sacramentales
"""
from sqlalchemy import Column, Integer, String, Date, Text
from app.database import Base


class LibroModel(Base):
    """Modelo para la tabla libros"""
    __tablename__ = "libros"
    
    id_libro = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    observaciones = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Libro(id={self.id_libro}, nombre={self.nombre})>"

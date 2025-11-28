"""
Modelo SQLAlchemy para la tabla tipos_sacramentos
Define los tipos de sacramentos disponibles
"""
from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class TipoSacramentoModel(Base):
    """Modelo para la tabla tipos_sacramentos"""
    __tablename__ = "tipos_sacramentos"
    
    id_tipo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TipoSacramento(id={self.id_tipo}, nombre={self.nombre})>"

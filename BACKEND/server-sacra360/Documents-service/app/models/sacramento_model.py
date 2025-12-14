"""
Modelo SQLAlchemy para la tabla sacramentos
Define la estructura de los sacramentos registrados
"""
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from datetime import datetime

from app.database import Base

class SacramentoModel(Base):
    """
    Modelo para la tabla sacramentos
    Almacena los sacramentos registrados en el sistema
    """
    __tablename__ = "sacramentos"
    
    id_sacramento = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos_sacramentos.id_tipo"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    institucion_id = Column(Integer, ForeignKey("institucionesparroquias.id_institucion"), nullable=False)
    libro_id = Column(Integer, ForeignKey("libros.id_libro"), nullable=False)
    fecha_sacramento = Column(Date, nullable=False)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Sacramento(id={self.id_sacramento}, tipo={self.tipo_id}, persona={self.persona_id})>"

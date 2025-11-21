"""
Modelo SQLAlchemy para documento_digitalizado
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentoDigitalizadoModel(Base):
    __tablename__ = "documento_digitalizado"
    
    id_documento = Column(Integer, primary_key=True, autoincrement=True)
    libros_id = Column(Integer, nullable=False)
    tipo_sacramento = Column(Integer, nullable=True)
    imagen_url = Column(Text, nullable=False)
    ocr_texto = Column(Text, nullable=False)
    modelo_fuente = Column(String(100), nullable=False)
    confianza = Column(Numeric(4,3), nullable=False)
    fecha_procesamiento = Column(DateTime, nullable=False, default=datetime.now)
    
    def __repr__(self):
        return f"<DocumentoDigitalizado(id={self.id_documento}, libro={self.libros_id}, url={self.imagen_url})>"
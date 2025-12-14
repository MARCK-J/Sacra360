"""
Modelo SQLAlchemy para documento_digitalizado
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.database import Base

class DocumentoDigitalizado(Base):
    __tablename__ = "documento_digitalizado"
    
    id_documento = Column(Integer, primary_key=True, autoincrement=True)
    libros_id = Column(Integer, nullable=False)
    tipo_sacramento = Column(Integer, nullable=True)
    imagen_url = Column(Text, nullable=False)
    ocr_texto = Column(Text, nullable=False)
    modelo_fuente = Column(String(100), nullable=False)
    modelo_procesamiento = Column(String(20), nullable=False, default='ocr', server_default='ocr')
    confianza = Column(Numeric(4,3), nullable=False)
    fecha_procesamiento = Column(DateTime, nullable=False, default=datetime.now)
    
    # Nuevas columnas agregadas en migración
    nombre_archivo = Column(String(255), nullable=True)
    fecha_subida = Column(DateTime, nullable=True, default=datetime.now)
    estado_procesamiento = Column(String(50), nullable=False, default="pendiente")
    fecha_validacion = Column(DateTime, nullable=True)
    
    # Relaciones simples (comentadas para evitar referencias circulares por ahora)
    # resultados_ocr = relationship("OCRResultado", back_populates="documento")
    # validaciones = relationship("ValidacionTupla", back_populates="documento")
    
    def __repr__(self):
        return f"<DocumentoDigitalizado(id={self.id_documento}, libro={self.libros_id}, url={self.imagen_url})>"

# Alias para compatibilidad
DocumentoDigitalizadoModel = DocumentoDigitalizado
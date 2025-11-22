from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional

Base = declarative_base()

class OcrResultado(Base):
    """Entidad para almacenar resultados del OCR por tupla completa"""
    __tablename__ = "ocr_resultado"
    
    id_ocr = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey('documento_digitalizado.id_documento'), nullable=False)
    tupla_numero = Column(Integer, nullable=False)
    datos_ocr = Column(JSONB, nullable=False)  # JSON con todos los campos de la tupla
    confianza = Column(Numeric(4,3), nullable=False)
    fuente_modelo = Column(String(100), nullable=False)
    validado = Column(Boolean, nullable=False, default=False)
    estado_validacion = Column(String(20), nullable=False, default='pendiente')
    sacramento_id = Column(Integer, nullable=True)
    fecha_validacion = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<OcrResultado(id_ocr={self.id_ocr}, tupla={self.tupla_numero}, documento={self.documento_id})>"

class DocumentoDigitalizado(Base):
    """Entidad para documentos procesados"""
    __tablename__ = "documento_digitalizado"
    
    id_documento = Column(Integer, primary_key=True, autoincrement=True)
    libros_id = Column(Integer, nullable=False)
    tipo_sacramento = Column(Integer, nullable=True)
    imagen_url = Column(Text, nullable=False)
    ocr_texto = Column(Text, nullable=False)
    modelo_fuente = Column(String(100), nullable=False)
    confianza = Column(Numeric(4,3), nullable=False)
    fecha_procesamiento = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación con OCR resultados
    ocr_resultados = relationship("OcrResultado", backref="documento")
    
    def __repr__(self):
        return f"<DocumentoDigitalizado(id_documento={self.id_documento}, imagen_url={self.imagen_url})>"
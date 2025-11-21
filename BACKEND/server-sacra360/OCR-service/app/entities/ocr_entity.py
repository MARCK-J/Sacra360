from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()

class OcrResultado(Base):
    """Entidad para almacenar resultados del OCR por campo individual"""
    __tablename__ = "ocr_resultado"
    
    id_ocr = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey('documento_digitalizado.id_documento'), nullable=False)
    campo = Column(String(50), nullable=False)  # Ej: "nombre_confirmando", "fecha_nacimiento", etc.
    valor_extraido = Column(Text, nullable=False)
    confianza = Column(Numeric(4,3), nullable=False)
    fuente_modelo = Column(String(100), nullable=False)
    validado = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f"<OcrResultado(id_ocr={self.id_ocr}, campo={self.campo}, valor={self.valor_extraido[:30]})>"

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
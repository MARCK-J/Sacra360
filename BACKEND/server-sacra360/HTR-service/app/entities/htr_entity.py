"""
Entidades de base de datos para HTR Service - Sacra360
Usa las mismas tablas que OCR Service pero con campo diferenciador
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional

Base = declarative_base()

class OcrResultado(Base):
    """
    Entidad para almacenar resultados del procesamiento (OCR o HTR) por tupla completa.
    Tabla compartida entre OCR-service y HTR-service.
    Se diferencia por el campo 'fuente_modelo'.
    """
    __tablename__ = "ocr_resultado"
    
    id_ocr = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey('documento_digitalizado.id_documento'), nullable=False)
    tupla_numero = Column(Integer, nullable=False)
    datos_ocr = Column(JSONB, nullable=False)  # JSON con todos los campos de la tupla
    confianza = Column(Numeric(4,3), nullable=False)
    fuente_modelo = Column(String(100), nullable=False)  # "HTR_Sacra360" o "OCRv2_EasyOCR"
    validado = Column(Boolean, nullable=False, default=False)
    estado_validacion = Column(String(20), nullable=False, default='pendiente')
    sacramento_id = Column(Integer, nullable=True)
    fecha_validacion = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<OcrResultado(id_ocr={self.id_ocr}, tupla={self.tupla_numero}, documento={self.documento_id}, fuente={self.fuente_modelo})>"

class DocumentoDigitalizado(Base):
    """
    Entidad para documentos procesados.
    Tabla compartida entre OCR-service y HTR-service.
    Se diferencia por el campo 'modelo_procesamiento'.
    """
    __tablename__ = "documento_digitalizado"
    
    id_documento = Column(Integer, primary_key=True, autoincrement=True)
    libros_id = Column(Integer, nullable=False)
    tipo_sacramento = Column(Integer, nullable=True)
    imagen_url = Column(Text, nullable=False)
    ocr_texto = Column(Text, nullable=False)
    modelo_fuente = Column(String(100), nullable=False)  # "HTR_Sacra360" o "OCRv2_EasyOCR"
    confianza = Column(Numeric(4,3), nullable=False)
    fecha_procesamiento = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Nuevos campos para soporte HTR (Migration_Add_HTR_Support.sql)
    modelo_procesamiento = Column(String(20), nullable=False, default='htr')  # 'ocr' o 'htr'
    progreso_ocr = Column(Integer, nullable=True, default=0)  # Aplica para OCR y HTR
    mensaje_progreso = Column(String(255), nullable=True)
    
    # Relación con resultados de procesamiento
    ocr_resultados = relationship("OcrResultado", backref="documento")
    
    def __repr__(self):
        return f"<DocumentoDigitalizado(id_documento={self.id_documento}, modelo={self.modelo_procesamiento}, imagen_url={self.imagen_url})>"

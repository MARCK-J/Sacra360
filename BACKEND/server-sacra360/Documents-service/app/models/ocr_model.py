"""
Modelo SQLAlchemy para la tabla ocr_resultado
Define la estructura de los resultados OCR
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.database import Base

class OCRResultado(Base):
    """
    Modelo para la tabla ocr_resultado
    Almacena los resultados del procesamiento OCR
    """
    __tablename__ = "ocr_resultado"
    
    id_ocr = Column(Integer, primary_key=True, index=True, name="id_ocr")
    documento_id = Column(Integer, ForeignKey("documento_digitalizado.id_documento"), nullable=False, name="documento_id")
    campo = Column(String(50), nullable=False, name="campo")
    valor_extraido = Column(Text, nullable=False, name="valor_extraido")
    confianza = Column(Numeric(4,3), nullable=False, name="confianza")
    fuente_modelo = Column(String(100), nullable=False, name="fuente_modelo")
    validado = Column(Boolean, nullable=False, default=False, name="validado")
    tupla_numero = Column(Integer, nullable=False, default=1, name="tupla_numero")
    estado_validacion = Column(String(20), nullable=False, default="pendiente", name="estado_validacion")
    sacramento_id = Column(Integer, ForeignKey("sacramentos.id_sacramento"), nullable=True, name="sacramento_id")
    
    # Relaciones simples (comentadas para evitar referencias circulares por ahora)
    # documento = relationship("DocumentoDigitalizado", back_populates="resultados_ocr")
    # sacramento = relationship("Sacramento", foreign_keys=[sacramento_id])
    # correcciones = relationship("CorreccionDocumento", back_populates="ocr_resultado")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<OCRResultado(id={self.id_ocr}, campo='{self.campo}', tupla={self.tupla_numero})>"
    
    @property
    def confianza_porcentaje(self):
        """Devuelve la confianza como porcentaje"""
        return float(self.confianza) * 100 if self.confianza else 0
    
    @property
    def nivel_confianza(self):
        """Clasifica el nivel de confianza"""
        if self.confianza >= 0.9:
            return "alta"
        elif self.confianza >= 0.7:
            return "media"
        else:
            return "baja"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_ocr": self.id_ocr,
            "documento_id": self.documento_id,
            "campo": self.campo,
            "valor_extraido": self.valor_extraido,
            "confianza": float(self.confianza) if self.confianza else None,
            "confianza_porcentaje": self.confianza_porcentaje,
            "nivel_confianza": self.nivel_confianza,
            "fuente_modelo": self.fuente_modelo,
            "validado": self.validado,
            "tupla_numero": self.tupla_numero,
            "estado_validacion": self.estado_validacion,
            "sacramento_id": self.sacramento_id
        }
"""
Modelo SQLAlchemy para la tabla ocr_resultado
Define la estructura de los resultados OCR
ACTUALIZADO para OCR V2 - Soporta datos_ocr JSONB
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.database import Base

class OCRResultado(Base):
    """
    Modelo para la tabla ocr_resultado
    Almacena los resultados del procesamiento OCR en formato JSONB
    
    OCR V2 Format:
    - datos_ocr: JSONB con estructura {"col1": "...", "col2": "...", ..., "col10": "..."}
    - Cada tupla es una fila completa (10 columnas)
    """
    __tablename__ = "ocr_resultado"
    
    id_ocr = Column(Integer, primary_key=True, index=True, name="id_ocr")
    documento_id = Column(Integer, ForeignKey("documento_digitalizado.id_documento"), nullable=False, name="documento_id")
    tupla_numero = Column(Integer, nullable=False, default=1, name="tupla_numero")
    datos_ocr = Column(JSONB, nullable=False, name="datos_ocr")  # ← NUEVO: JSON con col1-col10
    confianza = Column(Numeric(4,3), nullable=False, name="confianza")
    fuente_modelo = Column(String(100), nullable=False, name="fuente_modelo")
    validado = Column(Boolean, nullable=False, default=False, name="validado")
    estado_validacion = Column(String(20), nullable=False, default="pendiente", name="estado_validacion")
    sacramento_id = Column(Integer, ForeignKey("sacramentos.id_sacramento"), nullable=True, name="sacramento_id")
    fecha_validacion = Column(DateTime, nullable=True, name="fecha_validacion")
    
    # Relaciones simples (comentadas para evitar referencias circulares por ahora)
    # documento = relationship("DocumentoDigitalizado", back_populates="resultados_ocr")
    # sacramento = relationship("Sacramento", foreign_keys=[sacramento_id])
    # correcciones = relationship("CorreccionDocumento", back_populates="ocr_resultado")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<OCRResultado(id={self.id_ocr}, tupla={self.tupla_numero}, cols={len(self.datos_ocr or {})})>"
    
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
    
    def get_campo_valor(self, campo_nombre: str) -> str:
        """
        Obtiene el valor de un campo específico desde datos_ocr JSONB
        Mapea nombres de campos a columnas (col1-col10)
        """
        campo_map = {
            'nombre_confirmado': 'col1',
            'dia_nacimiento': 'col2',
            'mes_nacimiento': 'col3',
            'ano_nacimiento': 'col4',
            'parroquia': 'col5',
            'dia_confirmacion': 'col6',
            'mes_confirmacion': 'col7',
            'ano_confirmacion': 'col8',
            'padres': 'col9',
            'padrinos': 'col10'
        }
        col_key = campo_map.get(campo_nombre)
        if col_key and self.datos_ocr:
            return self.datos_ocr.get(col_key, '')
        return ''
    
    def set_campo_valor(self, campo_nombre: str, valor: str):
        """
        Actualiza el valor de un campo específico en datos_ocr JSONB
        """
        campo_map = {
            'nombre_confirmado': 'col1',
            'dia_nacimiento': 'col2',
            'mes_nacimiento': 'col3',
            'ano_nacimiento': 'col4',
            'parroquia': 'col5',
            'dia_confirmacion': 'col6',
            'mes_confirmacion': 'col7',
            'ano_confirmacion': 'col8',
            'padres': 'col9',
            'padrinos': 'col10'
        }
        col_key = campo_map.get(campo_nombre)
        if col_key:
            if not self.datos_ocr:
                self.datos_ocr = {}
            self.datos_ocr[col_key] = valor
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_ocr": self.id_ocr,
            "documento_id": self.documento_id,
            "tupla_numero": self.tupla_numero,
            "datos_ocr": self.datos_ocr,
            "confianza": float(self.confianza) if self.confianza else None,
            "confianza_porcentaje": self.confianza_porcentaje,
            "nivel_confianza": self.nivel_confianza,
            "fuente_modelo": self.fuente_modelo,
            "validado": self.validado,
            "estado_validacion": self.estado_validacion,
            "sacramento_id": self.sacramento_id,
            "fecha_validacion": self.fecha_validacion.isoformat() if self.fecha_validacion else None
        }
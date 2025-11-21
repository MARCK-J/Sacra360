"""
Modelo SQLAlchemy para la tabla de correcciones de documentos OCR
Define la estructura de la tabla correccion_documento
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.database import Base

class CorreccionDocumento(Base):
    """
    Modelo para la tabla correccion_documento
    Gestiona las correcciones aplicadas a los resultados OCR
    """
    __tablename__ = "correccion_documento"
    
    id_correccion = Column(Integer, primary_key=True, index=True, name="id_correccion")
    ocr_resultado_id = Column(Integer, ForeignKey("ocr_resultado.id_ocr"), nullable=False, name="ocr_resultado_id")
    valor_original = Column(Text, nullable=False, name="valor_original")
    valor_corregido = Column(Text, nullable=False, name="valor_corregido")
    razon_correccion = Column(Text, nullable=True, name="razon_correccion")
    usuario_corrector_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, name="usuario_corrector_id")
    fecha_correccion = Column(DateTime, nullable=False, default=datetime.utcnow, name="fecha_correccion")
    tipo_correccion = Column(String(50), nullable=False, default="manual", name="tipo_correccion")
    
    # Relaciones simples (comentadas para evitar referencias circulares por ahora)
    # ocr_resultado = relationship("OCRResultado", back_populates="correcciones")
    # usuario_corrector = relationship("Usuario", foreign_keys=[usuario_corrector_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.fecha_correccion:
            self.fecha_correccion = datetime.utcnow()
    
    def __repr__(self):
        return f"<CorreccionDocumento(id={self.id_correccion}, ocr_id={self.ocr_resultado_id}, tipo='{self.tipo_correccion}')>"
    
    @property
    def diferencia_valor(self):
        """Calcula la diferencia entre valor original y corregido"""
        if self.valor_original == self.valor_corregido:
            return "Sin cambios"
        return f"'{self.valor_original}' → '{self.valor_corregido}'"
    
    @property
    def tiempo_desde_correccion(self):
        """Calcula el tiempo transcurrido desde la corrección"""
        if self.fecha_correccion:
            return datetime.utcnow() - self.fecha_correccion
        return None
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_correccion": self.id_correccion,
            "ocr_resultado_id": self.ocr_resultado_id,
            "valor_original": self.valor_original,
            "valor_corregido": self.valor_corregido,
            "diferencia": self.diferencia_valor,
            "razon_correccion": self.razon_correccion,
            "usuario_corrector_id": self.usuario_corrector_id,
            "fecha_correccion": self.fecha_correccion.isoformat() if self.fecha_correccion else None,
            "tipo_correccion": self.tipo_correccion
        }
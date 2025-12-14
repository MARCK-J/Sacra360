"""
Modelo SQLAlchemy para la tabla de validación de tuplas OCR
Define la estructura de la tabla validacion_tuplas
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.database import Base

class ValidacionTupla(Base):
    """
    Modelo para la tabla validacion_tuplas
    Gestiona el estado de validación de cada tupla OCR
    """
    __tablename__ = "validacion_tuplas"
    
    id_validacion = Column(Integer, primary_key=True, index=True, name="id_validacion")
    documento_id = Column(Integer, ForeignKey("documento_digitalizado.id_documento"), nullable=False, name="documento_id")
    tupla_numero = Column(Integer, nullable=False, name="tupla_numero")
    estado = Column(String(20), nullable=False, default="pendiente", name="estado")
    usuario_validador_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True, name="usuario_validador_id")
    fecha_validacion = Column(DateTime, nullable=True, name="fecha_validacion")
    sacramento_registrado_id = Column(Integer, ForeignKey("sacramentos.id_sacramento"), nullable=True, name="sacramento_registrado_id")
    observaciones = Column(Text, nullable=True, name="observaciones")
    
    # Relaciones simples (comentadas para evitar referencias circulares por ahora)
    # documento = relationship("DocumentoDigitalizado", back_populates="validaciones")
    # usuario_validador = relationship("Usuario", foreign_keys=[usuario_validador_id])
    # sacramento_registrado = relationship("Sacramento", foreign_keys=[sacramento_registrado_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<ValidacionTupla(id={self.id_validacion}, doc={self.documento_id}, tupla={self.tupla_numero}, estado='{self.estado}')>"
    
    @property
    def estado_descripcion(self):
        """Devuelve una descripción legible del estado"""
        estados = {
            "pendiente": "Pendiente de validación",
            "validado": "Validado y aprobado",
            "rechazado": "Rechazado por el validador",
            "en_proceso": "En proceso de validación"
        }
        return estados.get(self.estado, "Estado desconocido")
    
    @property
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la validación"""
        if self.fecha_validacion:
            return datetime.utcnow() - self.fecha_validacion
        return None
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_validacion": self.id_validacion,
            "documento_id": self.documento_id,
            "tupla_numero": self.tupla_numero,
            "estado": self.estado,
            "estado_descripcion": self.estado_descripcion,
            "usuario_validador_id": self.usuario_validador_id,
            "fecha_validacion": self.fecha_validacion.isoformat() if self.fecha_validacion else None,
            "sacramento_registrado_id": self.sacramento_registrado_id,
            "observaciones": self.observaciones
        }
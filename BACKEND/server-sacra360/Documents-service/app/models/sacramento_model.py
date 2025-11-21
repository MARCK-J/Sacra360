"""
Modelo SQLAlchemy para la tabla sacramentos
Define la estructura de los sacramentos registrados
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.database import Base

class Sacramento(Base):
    """
    Modelo para la tabla sacramentos
    Almacena los sacramentos registrados en el sistema
    """
    __tablename__ = "sacramentos"
    
    id_sacramento = Column(Integer, primary_key=True, index=True, name="id_sacramento")
    tipo_sacramento_id = Column(Integer, ForeignKey("tipos_sacramento.id_tipo"), nullable=False, name="tipo_sacramento_id")
    persona_id = Column(Integer, ForeignKey("personas.id_persona"), nullable=False, name="persona_id")
    libro_id = Column(Integer, ForeignKey("libros.id_libro"), nullable=False, name="libro_id")
    numero_acta = Column(String(50), nullable=False, name="numero_acta")
    fecha_sacramento = Column(Date, nullable=False, name="fecha_sacramento")
    lugar_sacramento = Column(String(255), nullable=True, name="lugar_sacramento")
    ministro = Column(String(255), nullable=True, name="ministro")
    padrinos = Column(Text, nullable=True, name="padrinos")
    observaciones = Column(Text, nullable=True, name="observaciones")
    fecha_registro = Column(DateTime, nullable=False, default=datetime.utcnow, name="fecha_registro")
    usuario_registro_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, name="usuario_registro_id")
    folio = Column(String(20), nullable=True, name="folio")
    pagina = Column(Integer, nullable=True, name="pagina")
    
    # Relaciones simples (comentadas para evitar referencias circulares por ahora)
    # tipo_sacramento = relationship("TipoSacramento", foreign_keys=[tipo_sacramento_id])
    # persona = relationship("Persona", foreign_keys=[persona_id])
    # libro = relationship("Libro", foreign_keys=[libro_id])
    # usuario_registro = relationship("Usuario", foreign_keys=[usuario_registro_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.fecha_registro:
            self.fecha_registro = datetime.utcnow()
    
    def __repr__(self):
        return f"<Sacramento(id={self.id_sacramento}, tipo={self.tipo_sacramento_id}, persona={self.persona_id})>"
    
    @property
    def nombre_completo_persona(self):
        """Devuelve el nombre completo de la persona"""
        if self.persona:
            return f"{self.persona.nombres} {self.persona.apellidos}".strip()
        return "Sin información"
    
    @property
    def tipo_sacramento_nombre(self):
        """Devuelve el nombre del tipo de sacramento"""
        if self.tipo_sacramento:
            return self.tipo_sacramento.nombre
        return "Sin tipo"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_sacramento": self.id_sacramento,
            "tipo_sacramento_id": self.tipo_sacramento_id,
            "tipo_sacramento_nombre": self.tipo_sacramento_nombre,
            "persona_id": self.persona_id,
            "nombre_completo": self.nombre_completo_persona,
            "libro_id": self.libro_id,
            "numero_acta": self.numero_acta,
            "fecha_sacramento": self.fecha_sacramento.isoformat() if self.fecha_sacramento else None,
            "lugar_sacramento": self.lugar_sacramento,
            "ministro": self.ministro,
            "padrinos": self.padrinos,
            "observaciones": self.observaciones,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "usuario_registro_id": self.usuario_registro_id,
            "folio": self.folio,
            "pagina": self.pagina
        }
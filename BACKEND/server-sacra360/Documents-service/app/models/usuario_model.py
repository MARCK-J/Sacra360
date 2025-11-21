"""
Modelo SQLAlchemy para la tabla usuarios
Define la estructura de los usuarios del sistema
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.database import Base

class Usuario(Base):
    """
    Modelo para la tabla usuarios
    Gestiona los usuarios del sistema
    """
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True, name="id_usuario")
    nombre_usuario = Column(String(50), nullable=False, unique=True, name="nombre_usuario")
    email = Column(String(100), nullable=False, unique=True, name="email")
    nombres = Column(String(100), nullable=False, name="nombres")
    apellidos = Column(String(100), nullable=False, name="apellidos")
    cargo = Column(String(100), nullable=True, name="cargo")
    activo = Column(Boolean, nullable=False, default=True, name="activo")
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow, name="fecha_creacion")
    ultimo_login = Column(DateTime, nullable=True, name="ultimo_login")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.utcnow()
    
    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, usuario='{self.nombre_usuario}', nombres='{self.nombres}')>"
    
    @property
    def nombre_completo(self):
        """Devuelve el nombre completo del usuario"""
        return f"{self.nombres} {self.apellidos}".strip()
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_usuario": self.id_usuario,
            "nombre_usuario": self.nombre_usuario,
            "email": self.email,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "nombre_completo": self.nombre_completo,
            "cargo": self.cargo,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "ultimo_login": self.ultimo_login.isoformat() if self.ultimo_login else None
        }
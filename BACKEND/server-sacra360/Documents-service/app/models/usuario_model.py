"""
Modelo SQLAlchemy para la tabla usuarios
Define la estructura de los usuarios del sistema
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey
from datetime import datetime, date

from app.database import Base

class UsuarioModel(Base):
    """
    Modelo para la tabla usuarios
    Gestiona los usuarios del sistema
    """
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id_rol"), nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    contrasenia = Column(Text, nullable=False)
    fecha_creacion = Column(Date, nullable=False, default=date.today)
    activo = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, nombre='{self.nombre} {self.apellido_paterno}')>"
    
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
"""
Entidades del dominio para Authentication y Profiles usando la BD existente
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import date

Base = declarative_base()


class Usuario(Base):
    """Entidad Usuario usando la estructura existente de la BD"""
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey('roles.id_rol'), nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    contrasenia = Column(Text, nullable=False)
    fecha_creacion = Column(Date, nullable=False, default=date.today)
    activo = Column(Boolean, nullable=False, default=True)
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    auditorias = relationship("Auditoria", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, email={self.email}, nombre={self.nombre})>"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"


class Rol(Base):
    """Entidad Rol"""
    __tablename__ = "roles"
    
    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="rol")
    
    def __repr__(self):
        return f"<Rol(id={self.id_rol}, nombre={self.nombre})>"


class Auditoria(Base):
    """Entidad Auditoria para tracking de accesos"""
    __tablename__ = "auditoria"
    
    id_auditoria = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario'))
    accion = Column(String(100), nullable=False)
    tabla_afectada = Column(String(50))
    registro_id = Column(Integer)
    fecha = Column(Date, nullable=False, default=date.today)
    detalles = Column(Text)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="auditorias")
    
    def __repr__(self):
        return f"<Auditoria(id={self.id_auditoria}, accion={self.accion})>"
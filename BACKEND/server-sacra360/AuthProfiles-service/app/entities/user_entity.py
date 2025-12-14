from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Rol(Base):
    __tablename__ = 'roles'
    
    id_rol = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    
    usuarios = relationship('Usuario', back_populates='rol')


class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100))
    email = Column(String(255), nullable=False, unique=True)
    contrasenia = Column(Text, nullable=False)
    rol_id = Column(Integer, ForeignKey('roles.id_rol'), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    rol = relationship('Rol', back_populates='usuarios')
    auditorias = relationship('Auditoria', back_populates='usuario')


class Auditoria(Base):
    __tablename__ = 'auditoria'
    
    id_auditoria = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    accion = Column(Text, nullable=False)
    registro_afectado = Column(Text, nullable=False)
    id_registro = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    usuario = relationship('Usuario', back_populates='auditorias')

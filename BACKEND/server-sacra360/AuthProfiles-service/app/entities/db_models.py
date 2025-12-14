"""
Modelos SQLAlchemy para la base de datos PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()


class UsuarioDB(Base):
    """Modelo de Usuario en la base de datos"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    rol = Column(String(20), default='usuario')
    estado = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    perfil = relationship("PerfilDB", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    sesiones = relationship("SesionDB", back_populates="usuario", cascade="all, delete-orphan")
    auditorias = relationship("AuditoriaAccesoDB", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', rol='{self.rol}')>"


class PerfilDB(Base):
    """Modelo de Perfil de Usuario en la base de datos"""
    __tablename__ = "perfiles"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    foto_perfil = Column(String(255), nullable=True)
    biografia = Column(Text, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    genero = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    usuario = relationship("UsuarioDB", back_populates="perfil")
    
    def __repr__(self):
        return f"<Perfil(id={self.id}, usuario_id={self.usuario_id})>"


class SesionDB(Base):
    """Modelo de Sesión de Usuario en la base de datos"""
    __tablename__ = "sesiones"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    usuario = relationship("UsuarioDB", back_populates="sesiones")
    
    def __repr__(self):
        return f"<Sesion(id={self.id}, usuario_id={self.usuario_id}, activo={self.activo})>"


class AuditoriaAccesoDB(Base):
    """Modelo de Auditoría de Accesos en la base de datos"""
    __tablename__ = "auditoria_accesos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    accion = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    exitoso = Column(Boolean, default=True)
    mensaje = Column(Text, nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    usuario = relationship("UsuarioDB", back_populates="auditorias")
    
    def __repr__(self):
        return f"<AuditoriaAcceso(id={self.id}, accion='{self.accion}', exitoso={self.exitoso})>"

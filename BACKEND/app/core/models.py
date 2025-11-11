"""SQLAlchemy models for Sacra360 minimal test DB
Models are lightweight and use Base from app.core.database so tests can create tables.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class Parish(Base):
    __tablename__ = "parishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=True)
    priest_name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Sacramento(Base):
    __tablename__ = "sacramentos"

    id = Column(Integer, primary_key=True, index=True)
    id_persona = Column(Integer, nullable=False)
    tipo_sacramento = Column(String(100), nullable=False)
    fecha_sacramento = Column(DateTime(timezone=True), nullable=False)
    lugar_sacramento = Column(String(500), nullable=True)
    sacerdote_celebrante = Column(String(200), nullable=True)
    padrino = Column(String(200), nullable=True)
    madrina = Column(String(200), nullable=True)
    observaciones = Column(Text, nullable=True)
    numero_acta = Column(String(100), nullable=True)
    libro_registro = Column(String(200), nullable=True)
    folio = Column(String(50), nullable=True)
    activo = Column(Boolean, default=True)
    id_persona_conyuge = Column(Integer, nullable=True)
    testigo_1 = Column(String(200), nullable=True)
    testigo_2 = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

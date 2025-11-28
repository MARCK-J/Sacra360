"""
Modelo SQLAlchemy para la tabla personas
Define la estructura de las personas en el sistema
"""
from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class PersonaModel(Base):
    """Modelo para la tabla personas"""
    __tablename__ = "personas"
    
    id_persona = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    fecha_bautismo = Column(Date, nullable=False)
    nombre_padre_nombre_madre = Column(String(200), nullable=False)
    nombre_padrino_nombre_madrina = Column(String(200), nullable=False)
    
    def __repr__(self):
        return f"<Persona(id={self.id_persona}, nombre={self.nombres} {self.apellido_paterno})>"

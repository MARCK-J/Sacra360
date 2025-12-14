"""
Modelo SQLAlchemy para la tabla matrimonios
Define la estructura de los datos específicos de matrimonios
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class MatrimonioModel(Base):
    """
    Modelo para la tabla matrimonios
    Almacena datos específicos de matrimonios (esposo, esposa, testigos, padres)
    """
    __tablename__ = "matrimonios"
    
    id_matrimonio = Column(Integer, primary_key=True, index=True)
    sacramento_id = Column(Integer, ForeignKey("sacramentos.id_sacramento"), nullable=False, unique=True)
    esposo_id = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    esposa_id = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    nombre_padre_esposo = Column(String(100), nullable=False)
    nombre_madre_esposo = Column(String(100), nullable=False)
    nombre_padre_esposa = Column(String(100), nullable=False)
    nombre_madre_esposa = Column(String(100), nullable=False)
    testigos = Column(String(200), nullable=False)
    
    def __repr__(self):
        return f"<Matrimonio(id={self.id_matrimonio}, sacramento={self.sacramento_id}, esposo={self.esposo_id}, esposa={self.esposa_id})>"

"""
Servicio para gestionar instituciones/parroquias
"""
from typing import List
from sqlalchemy.orm import Session

from app.models.institucion_model import InstitucionModel
from app.entities.institucion import Institucion


class InstitucionService:
    """Servicio para gestionar instituciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_all(self) -> List[Institucion]:
        """Lista todas las instituciones"""
        instituciones = self.db.query(InstitucionModel).order_by(InstitucionModel.nombre).all()
        return [Institucion.from_orm(i) for i in instituciones]
    
    def get_by_id(self, institucion_id: int) -> Institucion:
        """Obtiene una institución por ID"""
        institucion = self.db.query(InstitucionModel).filter(
            InstitucionModel.id_institucion == institucion_id
        ).first()
        
        if institucion:
            return Institucion.from_orm(institucion)
        return None

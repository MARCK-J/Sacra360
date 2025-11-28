"""
Controller para instituciones/parroquias
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.institucion_model import InstitucionModel

router = APIRouter(prefix="/instituciones", tags=["Instituciones/Parroquias"])


@router.get("/",
            response_model=List[dict],
            summary="Listar instituciones/parroquias",
            description="Obtiene la lista de todas las instituciones/parroquias registradas")
def list_instituciones(db: Session = Depends(get_db)):
    """
    Lista todas las instituciones/parroquias donde se realizan sacramentos.
    
    Incluye:
    - Nombre de la parroquia
    - Dirección
    - Datos de contacto
    """
    instituciones = db.query(InstitucionModel).all()
    
    return [
        {
            "id_institucion": i.id_institucion,
            "nombre": i.nombre,
            "direccion": i.direccion,
            "telefono": i.telefono,
            "email": i.email
        }
        for i in instituciones
    ]

"""
Router de Sacramentos
Endpoints para gestión de sacramentos: bautizo, matrimonio, confirmación, etc.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import Sacramento as SacramentoModel
from app.dto.documents_dto import BaseModel as _Base  # noqa: F401

router = APIRouter()


class TipoSacramento(str):
    BAUTIZO = "bautizo"
    MATRIMONIO = "matrimonio"
    CONFIRMACION = "confirmacion"
    PRIMERA_COMUNION = "primera_comunion"


class SacramentoCreateDTO(BaseModel):
    id_persona: int = Field(...)
    tipo_sacramento: str = Field(...)
    fecha_sacramento: datetime = Field(...)
    lugar_sacramento: Optional[str] = None
    sacerdote_celebrante: Optional[str] = None
    padrino: Optional[str] = None
    madrina: Optional[str] = None
    observaciones: Optional[str] = None
    numero_acta: Optional[str] = None
    libro_registro: Optional[str] = None
    folio: Optional[str] = None
    activo: Optional[bool] = True
    # Campos específicos para matrimonio
    id_persona_conyuge: Optional[int] = None
    testigo_1: Optional[str] = None
    testigo_2: Optional[str] = None


class SacramentoResponseDTO(SacramentoCreateDTO):
    id_sacramento: int


def _validate_tipo(tipo: str) -> bool:
    allowed = {TipoSacramento.BAUTIZO, TipoSacramento.MATRIMONIO, TipoSacramento.CONFIRMACION, TipoSacramento.PRIMERA_COMUNION}
    return tipo in allowed


@router.post("/sacramentos", status_code=201)
def create_sacramento(payload: SacramentoCreateDTO, db: Session = Depends(get_db)):
    if not _validate_tipo(payload.tipo_sacramento):
        raise HTTPException(status_code=422, detail="Tipo de sacramento inválido")

    model = SacramentoModel(
        id_persona=payload.id_persona,
        tipo_sacramento=payload.tipo_sacramento,
        fecha_sacramento=payload.fecha_sacramento,
        lugar_sacramento=payload.lugar_sacramento,
        sacerdote_celebrante=payload.sacerdote_celebrante,
        padrino=payload.padrino,
        madrina=payload.madrina,
        observaciones=payload.observaciones,
        numero_acta=payload.numero_acta,
        libro_registro=payload.libro_registro,
        folio=payload.folio,
        activo=payload.activo,
        id_persona_conyuge=payload.id_persona_conyuge,
        testigo_1=payload.testigo_1,
        testigo_2=payload.testigo_2,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return {**payload.dict(), "id_sacramento": model.id}


@router.get("/sacramentos", response_model=List[Dict])
def list_sacramentos(tipo_sacramento: Optional[str] = Query(None), fecha_inicio: Optional[str] = Query(None), fecha_fin: Optional[str] = Query(None), id_persona: Optional[int] = Query(None), page: int = 1, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(SacramentoModel)
    if tipo_sacramento:
        q = q.filter(SacramentoModel.tipo_sacramento == tipo_sacramento)
    if id_persona is not None:
        q = q.filter(SacramentoModel.id_persona == id_persona)
    # filtering by dates if provided
    if fecha_inicio:
        try:
            dt_start = datetime.fromisoformat(fecha_inicio)
            q = q.filter(SacramentoModel.fecha_sacramento >= dt_start)
        except Exception:
            pass
    if fecha_fin:
        try:
            dt_end = datetime.fromisoformat(fecha_fin)
            q = q.filter(SacramentoModel.fecha_sacramento <= dt_end)
        except Exception:
            pass

    total = q.count()
    results = q.offset((page-1)*limit).limit(limit).all()
    out = []
    for r in results:
        out.append({
            "id_sacramento": r.id,
            "id_persona": r.id_persona,
            "tipo_sacramento": r.tipo_sacramento,
            "fecha_sacramento": r.fecha_sacramento.isoformat() if r.fecha_sacramento else None,
            "lugar_sacramento": r.lugar_sacramento,
            "activo": r.activo,
        })
    return out


@router.get("/sacramentos/{id_sacramento}")
def get_sacramento(id_sacramento: int, db: Session = Depends(get_db)):
    record = db.query(SacramentoModel).filter(SacramentoModel.id == id_sacramento).first()
    if not record:
        raise HTTPException(status_code=404, detail="Sacramento no encontrado")
    return {
        "id_sacramento": record.id,
        "id_persona": record.id_persona,
        "tipo_sacramento": record.tipo_sacramento,
        "fecha_sacramento": record.fecha_sacramento.isoformat() if record.fecha_sacramento else None,
        "lugar_sacramento": record.lugar_sacramento,
        "activo": record.activo,
    }


@router.put("/sacramentos/{id_sacramento}")
def update_sacramento(id_sacramento: int, payload: SacramentoCreateDTO, db: Session = Depends(get_db)):
    record = db.query(SacramentoModel).filter(SacramentoModel.id == id_sacramento).first()
    if not record:
        raise HTTPException(status_code=404, detail="Sacramento no encontrado")
    if not _validate_tipo(payload.tipo_sacramento):
        raise HTTPException(status_code=422, detail="Tipo de sacramento inválido")
    for k, v in payload.dict().items():
        setattr(record, k, v)
    record.updated_at = datetime.utcnow()
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "id_sacramento": record.id,
        "id_persona": record.id_persona,
        "tipo_sacramento": record.tipo_sacramento,
        "fecha_sacramento": record.fecha_sacramento.isoformat() if record.fecha_sacramento else None,
        "lugar_sacramento": record.lugar_sacramento,
        "activo": record.activo,
    }


@router.delete("/sacramentos/{id_sacramento}")
def delete_sacramento(id_sacramento: int, db: Session = Depends(get_db)):
    record = db.query(SacramentoModel).filter(SacramentoModel.id == id_sacramento).first()
    if not record:
        raise HTTPException(status_code=404, detail="Sacramento no encontrado")
    db.delete(record)
    db.commit()
    return {"success": True, "id_sacramento": id_sacramento}


# Rutas específicas por tipo (listas y creación especializada)
@router.get("/sacramentos/bautizos", response_model=List[Dict])
def get_bautizos(db: Session = Depends(get_db)):
    rows = db.query(SacramentoModel).filter(SacramentoModel.tipo_sacramento == TipoSacramento.BAUTIZO).all()
    return [{
        "id_sacramento": r.id,
        "tipo_sacramento": r.tipo_sacramento,
        "fecha_sacramento": r.fecha_sacramento.isoformat() if r.fecha_sacramento else None,
    } for r in rows]


@router.post("/sacramentos/bautizos", status_code=201)
def create_bautizo(payload: SacramentoCreateDTO, db: Session = Depends(get_db)):
    payload.tipo_sacramento = TipoSacramento.BAUTIZO
    return create_sacramento(payload, db=db)


@router.get("/sacramentos/matrimonios", response_model=List[Dict])
def get_matrimonios(db: Session = Depends(get_db)):
    rows = db.query(SacramentoModel).filter(SacramentoModel.tipo_sacramento == TipoSacramento.MATRIMONIO).all()
    return [{
        "id_sacramento": r.id,
        "tipo_sacramento": r.tipo_sacramento,
        "fecha_sacramento": r.fecha_sacramento.isoformat() if r.fecha_sacramento else None,
    } for r in rows]


@router.post("/sacramentos/matrimonios", status_code=201)
def create_matrimonio(payload: SacramentoCreateDTO, db: Session = Depends(get_db)):
    payload.tipo_sacramento = TipoSacramento.MATRIMONIO
    return create_sacramento(payload, db=db)


@router.get("/sacramentos/confirmaciones", response_model=List[Dict])
def get_confirmaciones(db: Session = Depends(get_db)):
    rows = db.query(SacramentoModel).filter(SacramentoModel.tipo_sacramento == TipoSacramento.CONFIRMACION).all()
    return [{
        "id_sacramento": r.id,
        "tipo_sacramento": r.tipo_sacramento,
        "fecha_sacramento": r.fecha_sacramento.isoformat() if r.fecha_sacramento else None,
    } for r in rows]


@router.post("/sacramentos/confirmaciones", status_code=201)
def create_confirmacion(payload: SacramentoCreateDTO, db: Session = Depends(get_db)):
    payload.tipo_sacramento = TipoSacramento.CONFIRMACION
    return create_sacramento(payload, db=db)


@router.get("/sacramentos/primeras-comuniones", response_model=List[Dict])
def get_primeras_comuniones(db: Session = Depends(get_db)):
    rows = db.query(SacramentoModel).filter(SacramentoModel.tipo_sacramento == TipoSacramento.PRIMERA_COMUNION).all()
    return [{
        "id_sacramento": r.id,
        "tipo_sacramento": r.tipo_sacramento,
        "fecha_sacramento": r.fecha_sacramento.isoformat() if r.fecha_sacramento else None,
    } for r in rows]

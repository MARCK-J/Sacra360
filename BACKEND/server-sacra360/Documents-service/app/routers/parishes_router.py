"""
Router para Parroquias
Endpoints: list, create, get, update, delete
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.dto.documents_dto import ParishCreateDTO, ParishDTO
from app.core.database import get_db
from app.core.models import Parish as ParishModel

router = APIRouter()


@router.get("/parishes/", response_model=List[ParishDTO])
def list_parishes(db: Session = Depends(get_db)):
    rows = db.query(ParishModel).all()
    result = []
    for r in rows:
        result.append({
            "id": r.id,
            "name": r.name,
            "address": r.address,
            "priest_name": r.priest_name,
            "phone": r.phone,
            "email": r.email,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        })
    return result


@router.post("/parishes/", response_model=ParishDTO)
def create_parish(payload: ParishCreateDTO, db: Session = Depends(get_db)):
    model = ParishModel(
        name=payload.name,
        address=payload.address,
        priest_name=payload.priest_name,
        phone=payload.phone,
        email=payload.email,
        is_active=True,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return {
        "id": model.id,
        "name": model.name,
        "address": model.address,
        "priest_name": model.priest_name,
        "phone": model.phone,
        "email": model.email,
        "is_active": model.is_active,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "updated_at": model.updated_at.isoformat() if model.updated_at else None,
    }


@router.get("/parishes/{parish_id}", response_model=ParishDTO)
def get_parish(parish_id: int, db: Session = Depends(get_db)):
    record = db.query(ParishModel).filter(ParishModel.id == parish_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Parroquia no encontrada")
    return {
        "id": record.id,
        "name": record.name,
        "address": record.address,
        "priest_name": record.priest_name,
        "phone": record.phone,
        "email": record.email,
        "is_active": record.is_active,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


@router.put("/parishes/{parish_id}", response_model=ParishDTO)
def update_parish(parish_id: int, payload: ParishCreateDTO, db: Session = Depends(get_db)):
    record = db.query(ParishModel).filter(ParishModel.id == parish_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Parroquia no encontrada")
    record.name = payload.name
    record.address = payload.address
    record.priest_name = payload.priest_name
    record.phone = payload.phone
    record.email = payload.email
    record.updated_at = datetime.utcnow()
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "name": record.name,
        "address": record.address,
        "priest_name": record.priest_name,
        "phone": record.phone,
        "email": record.email,
        "is_active": record.is_active,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


@router.delete("/parishes/{parish_id}")
def delete_parish(parish_id: int, db: Session = Depends(get_db)):
    record = db.query(ParishModel).filter(ParishModel.id == parish_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Parroquia no encontrada")
    db.delete(record)
    db.commit()
    return {"success": True, "id": parish_id}

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter(prefix="/instituciones", tags=["Instituciones"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_institucion(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Crear una institución/parroquia mínima.
    Espera `nombre` en el payload. Se aceptan campos opcionales y se crearán si la tabla los requiere.
    """
    nombre = payload.get("nombre") or payload.get("nombre_institucion") or payload.get("parroquia")
    if not nombre:
        raise HTTPException(status_code=422, detail="campo 'nombre' requerido")
    try:
        res = db.execute(text("INSERT INTO institucionesparroquias (nombre) VALUES (:n) RETURNING id_institucion"), {"n": nombre})
        idv = res.fetchone()[0]
        db.commit()
        row = db.execute(text("SELECT id_institucion, nombre FROM institucionesparroquias WHERE id_institucion = :id"), {"id": idv}).fetchone()
        return dict(row._mapping)
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Dict[str, Any]])
def list_instituciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    nombre: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar instituciones / parroquias con búsqueda por nombre"""
    try:
        sql = "SELECT id_institucion, nombre FROM institucionesparroquias"
        params: Dict[str, Any] = {}
        if nombre:
            sql += " WHERE nombre ILIKE :n"
            params["n"] = f"%{nombre}%"
        sql += " ORDER BY nombre ASC LIMIT :lim OFFSET :off"
        params["lim"] = limit
        params["off"] = skip
        res = db.execute(text(sql), params)
        rows = [dict(r._mapping) for r in res.fetchall()]
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}")
def get_institucion(id: int, db: Session = Depends(get_db)):
    try:
        row = db.execute(text("SELECT id_institucion, nombre FROM institucionesparroquias WHERE id_institucion = :id"), {"id": id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Institución no encontrada")
        return dict(row._mapping)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id}")
def update_institucion(id: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Actualizar campos simples de institución. Solo `nombre` por ahora."""
    if not payload:
        raise HTTPException(status_code=422, detail="payload vacío")
    allowed = {"nombre"}
    updates = []
    params: Dict[str, Any] = {"id": id}
    for k, v in payload.items():
        if k in allowed:
            updates.append(f"{k} = :{k}")
            params[k] = v
    if not updates:
        raise HTTPException(status_code=422, detail="No hay campos válidos para actualizar")
    try:
        db.execute(text(f"UPDATE institucionesparroquias SET {', '.join(updates)} WHERE id_institucion = :id"), params)
        db.commit()
        row = db.execute(text("SELECT id_institucion, nombre FROM institucionesparroquias WHERE id_institucion = :id"), {"id": id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Institución no encontrada")
        return dict(row._mapping)
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_institucion(id: int, db: Session = Depends(get_db)):
    try:
        db.execute(text("DELETE FROM institucionesparroquias WHERE id_institucion = :id"), {"id": id})
        db.commit()
        return
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

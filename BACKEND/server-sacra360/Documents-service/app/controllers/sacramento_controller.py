from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime

from app.database import get_db

router = APIRouter(prefix="/sacramentos", tags=["Sacramentos"])


def _row_to_dict(row, keys):
    return {k: getattr(row, k) if hasattr(row, k) else row[idx] for idx, k in enumerate(keys)}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_sacramento(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Crear un sacramento. Usa los nombres de columnas que utiliza OCR/validación (tipo_id, persona_id, libro_id, etc.)."""
    try:
        # Validaciones mínimas
        tipo = payload.get("tipo_sacramento") or payload.get("tipo_id") or payload.get("tipo")
        if tipo is None:
            raise HTTPException(status_code=422, detail="tipo_sacramento (id) requerido")
        # aceptar nombre -> resolver a id si se recibe string
        tipo_id = None
        if isinstance(tipo, str):
            # buscar id en tipos_sacramentos
            t = db.execute(text("SELECT id_tipo FROM tipos_sacramentos WHERE lower(nombre)=lower(:n) LIMIT 1"), {"n": tipo}).fetchone()
            if not t:
                raise HTTPException(status_code=400, detail=f"Tipo de sacramento '{tipo}' no encontrado")
            tipo_id = t[0]
        else:
            tipo_id = int(tipo)

        persona_id = payload.get("id_persona") or payload.get("persona_id")
        if not persona_id:
            raise HTTPException(status_code=422, detail="id_persona requerido")

        libro_id = payload.get("libro_id") or payload.get("libro") or payload.get("libro_registro")
        # si libro viene como nombre, intentar resolver
        if libro_id and not isinstance(libro_id, int):
            l = db.execute(text("SELECT id_libro FROM libros WHERE lower(nombre)=lower(:n) LIMIT 1"), {"n": libro_id}).fetchone()
            if l:
                libro_id = l[0]
            else:
                # crear libro mínimo
                res = db.execute(text("INSERT INTO libros (nombre, fecha_inicio, fecha_fin) VALUES (:n, NOW()::date, NOW()::date) RETURNING id_libro"), {"n": libro_id})
                libro_id = res.fetchone()[0]

        usuario_id = payload.get("usuario_registro_id") or payload.get("usuario_id") or 1
        institucion_id = payload.get("institucion_id") or payload.get("institucion") or payload.get("parroquia_id") or 1

        fecha_raw = payload.get("fecha_sacramento")
        if not fecha_raw:
            raise HTTPException(status_code=422, detail="fecha_sacramento requerida")
        try:
            fecha_sac = datetime.fromisoformat(fecha_raw).date() if isinstance(fecha_raw, str) else fecha_raw
        except Exception:
            raise HTTPException(status_code=422, detail="fecha_sacramento inválida")

        # Insertar usando SQL coherente con validacion_service
        insert_sql = text("""
            INSERT INTO sacramentos (
                persona_id, tipo_id, usuario_id, institucion_id, libro_id,
                fecha_sacramento, fecha_registro, fecha_actualizacion
            ) VALUES (
                :persona_id, :tipo_id, :usuario_id, :institucion_id, :libro_id,
                :fecha_sacramento, NOW(), NOW()
            ) RETURNING id_sacramento
        """)

        res = db.execute(insert_sql, {
            "persona_id": persona_id,
            "tipo_id": tipo_id,
            "usuario_id": usuario_id,
            "institucion_id": institucion_id,
            "libro_id": libro_id,
            "fecha_sacramento": fecha_sac
        })
        sac_id = res.fetchone()[0]
        db.commit()

        row = db.execute(text("SELECT * FROM sacramentos WHERE id_sacramento = :id"), {"id": sac_id}).fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Error al crear sacramento")
        # row._mapping is a Mapping of column_name -> value
        return dict(row._mapping)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Dict[str, Any]])
def list_sacramentos(
    tipo_sacramento: Optional[str] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    sacerdote: Optional[str] = Query(None),
    id_persona: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    try:
        sql = "SELECT s.*, ts.nombre as tipo_nombre FROM sacramentos s LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id"
        where = []
        params = {}
        if tipo_sacramento:
            where.append("lower(ts.nombre)=lower(:tipo)")
            params["tipo"] = tipo_sacramento
        if fecha_inicio:
            where.append("s.fecha_sacramento >= :fi")
            params["fi"] = fecha_inicio
        if fecha_fin:
            where.append("s.fecha_sacramento <= :ff")
            params["ff"] = fecha_fin
        if sacerdote:
            where.append("s.ministro ILIKE :sac")
            params["sac"] = f"%{sacerdote}%"
        if id_persona:
            where.append("s.persona_id = :pid")
            params["pid"] = id_persona
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY s.fecha_sacramento DESC"
        sql += " LIMIT :lim OFFSET :off"
        params["lim"] = limit
        params["off"] = (page - 1) * limit

        result = db.execute(text(sql), params)
        rows = [dict(r._mapping) for r in result.fetchall()]
        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bautizos")
def list_bautizos(db: Session = Depends(get_db)):
    return list_sacramentos(tipo_sacramento="bautizo", db=db)


@router.get("/confirmaciones")
def list_confirmaciones(db: Session = Depends(get_db)):
    return list_sacramentos(tipo_sacramento="confirmacion", db=db)


@router.get("/matrimonios")
def list_matrimonios(db: Session = Depends(get_db)):
    return list_sacramentos(tipo_sacramento="matrimonio", db=db)


@router.get("/primeras-comuniones")
def list_primeras_comuniones(db: Session = Depends(get_db)):
    return list_sacramentos(tipo_sacramento="primera comunion", db=db)


@router.get("/{id}")
def get_sacramento(id: int, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT s.*, ts.nombre as tipo_nombre FROM sacramentos s LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id WHERE s.id_sacramento = :id"), {"id": id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sacramento no encontrado")
    return dict(row._mapping)


@router.put("/{id}")
def update_sacramento(id: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
    # Construir SET dinámico permitiendo solo columnas esperadas
    allowed = {"persona_id", "tipo_id", "usuario_id", "institucion_id", "libro_id", "fecha_sacramento", "ministro", "padrinos", "observaciones", "folio", "numero_acta", "pagina"}
    updates = []
    params = {"id": id}
    for k, v in payload.items():
        if k in allowed:
            updates.append(f"{k} = :{k}")
            params[k] = v
    if not updates:
        raise HTTPException(status_code=422, detail="No hay campos válidos para actualizar")
    sql = text(f"UPDATE sacramentos SET {', '.join(updates)}, fecha_actualizacion = NOW() WHERE id_sacramento = :id")
    db.execute(sql, params)
    db.commit()
    return get_sacramento(id, db)


@router.delete("/{id}")
def delete_sacramento(id: int, db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM sacramentos WHERE id_sacramento = :id"), {"id": id})
    db.commit()
    return {"message": "Sacramento eliminado"}
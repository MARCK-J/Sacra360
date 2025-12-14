from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date

from app.database import get_db
from app.controllers.sacramento_controller import list_sacramentos

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/count-by-type")
def count_by_type(fecha_inicio: Optional[date] = Query(None), fecha_fin: Optional[date] = Query(None), db: Session = Depends(get_db)):
    """Retorna el conteo de sacramentos agrupado por tipo dentro del rango de fechas (si se provee)."""
    try:
        sql = "SELECT ts.nombre AS tipo, COUNT(s.id_sacramento) AS total FROM sacramentos s JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id"
        params = {}
        where_clauses = []
        if fecha_inicio:
            where_clauses.append("s.fecha_sacramento >= :fi")
            params['fi'] = fecha_inicio
        if fecha_fin:
            where_clauses.append("s.fecha_sacramento <= :ff")
            params['ff'] = fecha_fin
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " GROUP BY ts.nombre ORDER BY total DESC"

        result = db.execute(text(sql), params)
        rows = [{"tipo": r[0], "total": int(r[1])} for r in result.fetchall()]
        return {"counts": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def summary(fecha_inicio: Optional[date] = Query(None), fecha_fin: Optional[date] = Query(None), db: Session = Depends(get_db)):
    """Resumen general de sacramentos (totales y por tipo)."""
    try:
        # Total
        sql_total = "SELECT COUNT(*) as total FROM sacramentos s"
        params = {}
        where = []
        if fecha_inicio:
            where.append("s.fecha_sacramento >= :fi")
            params['fi'] = fecha_inicio
        if fecha_fin:
            where.append("s.fecha_sacramento <= :ff")
            params['ff'] = fecha_fin
        if where:
            sql_total += " WHERE " + " AND ".join(where)
        total = db.execute(text(sql_total), params).scalar()

        # By type
        by_type = count_by_type(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, db=db)

        return {"total": int(total or 0), "by_type": by_type.get('counts', [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sacramentos")
def sacramentos_for_reportes(
    tipo_sacramento: Optional[str] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    sacerdote: Optional[str] = Query(None),
    id_persona: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Lista de sacramentos para la vista de reportes. Reutiliza la lógica de filtrado de list_sacramentos.
    Esto evita duplicar la lógica tolerante a nombres/códigos y a esquemas antiguos.
    """
    try:
        # Build SQL with filters and pagination
        sql = (
            "SELECT s.id_sacramento, s.fecha_sacramento, s.fecha_registro, s.libro_id, "
            "p.id_persona, p.nombres, p.apellido_paterno, p.apellido_materno, "
            "ts.id_tipo, ts.nombre as tipo_nombre, i.id_institucion, i.nombre as institucion_nombre "
            "FROM sacramentos s "
            "JOIN personas p ON p.id_persona = s.persona_id "
            "JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
            "LEFT JOIN institucionesparroquias i ON i.id_institucion = s.institucion_id "
        )

        where_clauses = []
        params = {}

        if tipo_sacramento:
            # allow matching by name (case-insensitive)
            where_clauses.append("ts.nombre ILIKE :tipo")
            params["tipo"] = f"%{tipo_sacramento}%"

        if fecha_inicio:
            where_clauses.append("s.fecha_sacramento >= :fi")
            params["fi"] = fecha_inicio

        if fecha_fin:
            where_clauses.append("s.fecha_sacramento <= :ff")
            params["ff"] = fecha_fin

        if id_persona:
            where_clauses.append("s.persona_id = :pid")
            params["pid"] = id_persona

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        # Order and pagination
        sql += " ORDER BY s.fecha_sacramento DESC"
        offset = (page - 1) * limit
        sql += " LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        result = db.execute(text(sql), params)
        rows = []
        for r in result.fetchall():
            rows.append({
                "id_sacramento": r[0],
                "fecha_sacramento": r[1].isoformat() if r[1] is not None else None,
                "fecha_registro": r[2].isoformat() if r[2] is not None else None,
                "libro_id": r[3],
                "persona": {
                    "id_persona": r[4],
                    "nombres": r[5],
                    "apellido_paterno": r[6],
                    "apellido_materno": r[7]
                },
                "tipo": {
                    "id_tipo": r[8],
                    "nombre": r[9]
                },
                "institucion": {
                    "id_institucion": r[10],
                    "nombre": r[11]
                } if r[10] is not None else None
            })

        return rows
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
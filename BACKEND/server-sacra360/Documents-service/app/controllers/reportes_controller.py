from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date

from app.database import get_db

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
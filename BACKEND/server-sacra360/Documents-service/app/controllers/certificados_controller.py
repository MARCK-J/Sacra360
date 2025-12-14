from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from app.database import get_db

router = APIRouter(prefix="/certificados", tags=["Certificados"])


@router.get("/{id}")
def get_certificado_ensamblado(id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        # 1) Sacramentos principal
        s = db.execute(text("SELECT * FROM sacramentos WHERE id_sacramento = :id"), {"id": id}).fetchone()
        if not s:
            raise HTTPException(status_code=404, detail="Sacramento no encontrado")
        sac = dict(s._mapping)

        # 2) Tipo
        try:
            t = db.execute(text("SELECT nombre FROM tipos_sacramentos WHERE id_tipo = :id LIMIT 1"), {"id": sac.get("tipo_id")}).fetchone()
            sac["tipo_nombre"] = t[0] if t else None
        except Exception:
            sac["tipo_nombre"] = None

        # 3) Persona
        try:
            p = db.execute(text("SELECT nombres, apellido_paterno, apellido_materno, nombre_padre, nombre_madre FROM personas WHERE id_persona = :id"), {"id": sac.get("persona_id")}).fetchone()
            if p:
                sac["persona_nombre"] = " ".join([v for v in (p[0], p[1], p[2]) if v])
                sac["nombre_padre"] = p[3]
                sac["nombre_madre"] = p[4]
        except Exception:
            pass

        # 4) Institucion
        try:
            ip = db.execute(text("SELECT nombre FROM institucionesparroquias WHERE id_institucion = :id"), {"id": sac.get("institucion_id")}).fetchone()
            sac["institucion_nombre"] = ip[0] if ip else None
        except Exception:
            sac["institucion_nombre"] = None

        # 5) Detalles (intentar leer cada tabla; usar COALESCE manual)
        foja = numero = ministro = None
        try:
            dbt = db.execute(text("SELECT foja, numero, ministro, padrino FROM detalles_bautizo WHERE sacramento_id = :id LIMIT 1"), {"id": id}).fetchone()
            if dbt:
                foja = foja or dbt[0]
                numero = numero or dbt[1]
                ministro = ministro or dbt[2]
                sac["padrino_bautizo"] = dbt[3]
        except Exception:
            pass
        try:
            dcf = db.execute(text("SELECT foja, numero, ministro, padrino FROM detalles_confirmacion WHERE sacramento_id = :id LIMIT 1"), {"id": id}).fetchone()
            if dcf:
                foja = foja or dcf[0]
                numero = numero or dcf[1]
                ministro = ministro or dcf[2]
                sac["padrino_confirmacion"] = dcf[3]
        except Exception:
            pass
        try:
            dmt = db.execute(text("SELECT foja, numero, ministro, nombre_esposo, nombre_esposa FROM detalles_matrimonio WHERE sacramento_id = :id LIMIT 1"), {"id": id}).fetchone()
            if dmt:
                foja = foja or dmt[0]
                numero = numero or dmt[1]
                ministro = ministro or dmt[2]
                sac["nombre_esposo"] = dmt[3]
                sac["nombre_esposa"] = dmt[4]
        except Exception:
            pass

        sac["foja"] = foja
        sac["numero_acta"] = numero
        sac["ministro"] = ministro

        return sac

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
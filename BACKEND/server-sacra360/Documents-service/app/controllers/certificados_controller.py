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

        # 3) Persona (use combined fields present in DB)
        try:
            p = db.execute(text(
                "SELECT nombres, apellido_paterno, apellido_materno, nombre_padre_nombre_madre, nombre_padrino_nombre_madrina FROM personas WHERE id_persona = :id"
            ), {"id": sac.get("persona_id")}).fetchone()
            if p:
                sac["persona_nombre"] = " ".join([v for v in (p[0], p[1], p[2]) if v])
                # personas.nombre_padre_nombre_madre may store both padres in one string
                sac["padres"] = p[3] if p[3] else None
                # persona-level padrinos stored as combined field
                sac["padrinos_persona"] = p[4] if p[4] else None
        except Exception:
            pass

        # 4) Institucion
        try:
            ip = db.execute(text("SELECT nombre FROM institucionesparroquias WHERE id_institucion = :id"), {"id": sac.get("institucion_id")}).fetchone()
            sac["institucion_nombre"] = ip[0] if ip else None
        except Exception:
            sac["institucion_nombre"] = None

        # 4b) Libro: obtener nombre legible del libro
        try:
            lb = db.execute(text("SELECT nombre FROM libros WHERE id_libro = :id"), {"id": sac.get("libro_id")}).fetchone()
            sac["libro_nombre"] = lb[0] if lb else None
        except Exception:
            sac["libro_nombre"] = None

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
            dmt = db.execute(text(
                "SELECT foja, numero, ministro, nombre_esposo, nombre_esposa, nombre_padre_esposo, nombre_madre_esposo, nombre_padre_esposa, nombre_madre_esposa FROM detalles_matrimonio WHERE sacramento_id = :id LIMIT 1"
            ), {"id": id}).fetchone()
            if dmt:
                foja = foja or dmt[0]
                numero = numero or dmt[1]
                ministro = ministro or dmt[2]
                sac["nombre_esposo"] = dmt[3]
                sac["nombre_esposa"] = dmt[4]
                # combine padres de los contrayentes
                padre_esposo = dmt[5] or ''
                madre_esposo = dmt[6] or ''
                padre_esposa = dmt[7] or ''
                madre_esposa = dmt[8] or ''
                partes = []
                if padre_esposo or madre_esposo:
                    partes.append(f"{padre_esposo or '-'} y {madre_esposo or '-'}")
                if padre_esposa or madre_esposa:
                    partes.append(f"{padre_esposa or '-'} y {madre_esposa or '-'}")
                if partes:
                    # prefer existing sac['padres'] from persona if present
                    if not sac.get("padres"):
                        sac["padres"] = ' / '.join(partes)
        except Exception:
            pass

        sac["foja"] = foja
        sac["numero_acta"] = numero
        sac["ministro"] = ministro

        # Normalize padrinos field: prioritize detalle_* padrinos then persona-level combined field
        padrinos = sac.get("padrino_bautizo") or sac.get("padrino_confirmacion") or sac.get("padrinos_persona")
        sac["padrinos"] = padrinos if padrinos else None

        return sac

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
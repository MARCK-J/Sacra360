from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
import traceback
import logging
import json

router = APIRouter(prefix="/sacramentos", tags=["SacramentosAdmin"]) 


@router.put("/{sacramento_id}", status_code=status.HTTP_200_OK, summary="Actualizar sacramento y persona")
async def update_sacramento(
    sacramento_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Actualiza datos del sacramento y (opcionalmente) de la persona asociada.
    Payload esperado (ambos opcionales):
    {
      "persona": { "nombres": "...", "apellido_paterno": "...", "apellido_materno": "...", "fecha_nacimiento": "YYYY-MM-DD", "lugar_nacimiento": "..." },
      "sacramento": { "tipo": "Confirmación" | 2, "institucion": "Catedral", "fecha_sacramento": "YYYY-MM-DD" }
    }
    El endpoint intenta resolver nombres de `tipo` e `institucion` contra catálogos existentes.
    """

    # Verificar existencia del sacramento y obtener persona_id
    sac_row = db.execute(text("SELECT persona_id FROM sacramentos WHERE id_sacramento = :id"), {"id": sacramento_id}).first()
    if not sac_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sacramento {sacramento_id} no encontrado")
    # persona_id from the row mapping
    # Quick stdout debug to ensure logs appear in container output
    try:
        print("DEBUG sac_row raw:", repr(sac_row))
        print("DEBUG sac_row type:", type(sac_row))
        logging.info("sacramento_admin_controller: sac_row repr=%s", repr(sac_row))
        try:
            logging.info("sacramento_admin_controller: sac_row type=%s keys=%s", type(sac_row), list(sac_row.keys()))
        except Exception:
            logging.info("sacramento_admin_controller: sac_row has no keys() method; type=%s", type(sac_row))

        persona_id = None
        try:
            persona_id = sac_row._mapping.get('persona_id')
            logging.info("sacramento_admin_controller: persona_id from _mapping=%s", persona_id)
        except Exception:
            # fallback to dict-like access
            try:
                try:
                    keys = list(sac_row.keys())
                except Exception:
                    keys = None
                print("DEBUG sac_row keys:", keys)
                persona_id = sac_row['persona_id'] if keys and 'persona_id' in keys else None
                logging.info("sacramento_admin_controller: persona_id from keys access=%s", persona_id)
            except Exception as e:
                logging.exception("sacramento_admin_controller: failed extracting persona_id from sac_row: %s", e)
                persona_id = None

    except Exception as e:
        logging.exception("sacramento_admin_controller: unexpected error while inspecting sac_row: %s", e)
        persona_id = None

        # Leer y loguear cuerpo crudo y JSON parseado (debug)
    raw_body = await request.body()
    try:
        raw_text = raw_body.decode('utf-8')
    except Exception:
        raw_text = str(raw_body)
    logging.info("sacramento_admin_controller: raw request body: %s", raw_text[:2000])
    try:
        payload = json.loads(raw_text) if raw_text else {}
    except Exception as e:
        logging.exception("sacramento_admin_controller: failed to parse JSON body")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid JSON body: {str(e)}\nRaw:{raw_text[:500]}")

    logging.info("sacramento_admin_controller: parsed payload keys: %s", list(payload.keys()) if isinstance(payload, dict) else type(payload))
    persona_payload = payload.get("persona") or {}
    sacr_payload = payload.get("sacramento") or {}

    try:
        # Actualizar persona si se envió bloque persona
        if persona_payload:
            update_fields = []
            params = {"id": persona_id}
            if "nombres" in persona_payload:
                update_fields.append("nombres = :nombres")
                params["nombres"] = persona_payload["nombres"]
            if "apellido_paterno" in persona_payload:
                update_fields.append("apellido_paterno = :apellido_paterno")
                params["apellido_paterno"] = persona_payload["apellido_paterno"]
            if "apellido_materno" in persona_payload:
                update_fields.append("apellido_materno = :apellido_materno")
                params["apellido_materno"] = persona_payload["apellido_materno"]
            if "fecha_nacimiento" in persona_payload:
                update_fields.append("fecha_nacimiento = :fecha_nacimiento")
                params["fecha_nacimiento"] = persona_payload["fecha_nacimiento"]
            if "lugar_nacimiento" in persona_payload:
                # columna optional en algunos esquemas; intentar actualizar si existe
                col = db.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name = 'personas' AND column_name = 'lugar_nacimiento'")).first()
                if col:
                    update_fields.append("lugar_nacimiento = :lugar_nacimiento")
                    params["lugar_nacimiento"] = persona_payload["lugar_nacimiento"]
                else:
                    logging.info("sacramento_admin_controller: personas.lugar_nacimiento column not found; skipping update")

            if update_fields:
                sql = f"UPDATE personas SET {', '.join(update_fields)} WHERE id_persona = :id"
                db.execute(text(sql), params)

        # Actualizar sacramento
        if sacr_payload:
            sac_updates = []
            sac_params = {"id": sacramento_id}

            # resolver tipo (acepta id numérico o nombre)
            if "tipo" in sacr_payload and sacr_payload["tipo"] is not None:
                tipo_val = sacr_payload["tipo"]
                tipo_id = None
                if isinstance(tipo_val, int):
                    # verify the provided tipo id exists to avoid FK violations
                    row = db.execute(text("SELECT id_tipo FROM tipos_sacramentos WHERE id_tipo = :id"), {"id": int(tipo_val)}).first()
                    if row:
                        tipo_id = int(tipo_val)
                    else:
                        logging.info("sacramento_admin_controller: provided tipo id %s not found; skipping tipo update", tipo_val)
                else:
                    # buscar por nombre (ilike)
                    logging.info("sacramento_admin_controller: resolving tipo by name='%s'", tipo_val)
                    row = db.execute(text("SELECT id_tipo FROM tipos_sacramentos WHERE lower(nombre) = lower(:n)"), {"n": str(tipo_val)}).first()
                    if not row:
                        # try partial match
                        row = db.execute(text("SELECT id_tipo FROM tipos_sacramentos WHERE lower(nombre) LIKE lower(:n)"), {"n": f"%{tipo_val}%"}).first()
                    logging.info("sacramento_admin_controller: tipo query result=%s", repr(row))
                    if row:
                        try:
                            tipo_id = row._mapping.get('id_tipo')
                        except Exception:
                            try:
                                tipo_id = row['id_tipo'] if 'id_tipo' in row.keys() else None
                            except Exception:
                                try:
                                    tipo_id = row[0]
                                except Exception:
                                    tipo_id = None
                if tipo_id:
                    sac_updates.append("tipo_id = :tipo_id")
                    sac_params["tipo_id"] = tipo_id

            # resolver institucion (acepta id o nombre)
            if "institucion" in sacr_payload and sacr_payload["institucion"] is not None:
                inst_val = sacr_payload["institucion"]
                inst_id = None
                if isinstance(inst_val, int):
                    # verify institucion exists
                    row = db.execute(text("SELECT id_institucion FROM InstitucionesParroquias WHERE id_institucion = :id"), {"id": int(inst_val)}).first()
                    if row:
                        inst_id = int(inst_val)
                    else:
                        logging.info("sacramento_admin_controller: provided institucion id %s not found; skipping institucion update", inst_val)
                else:
                    row = db.execute(text("SELECT id_institucion FROM InstitucionesParroquias WHERE lower(nombre) = lower(:n)"), {"n": str(inst_val)}).first()
                    if not row:
                        row = db.execute(text("SELECT id_institucion FROM InstitucionesParroquias WHERE lower(nombre) LIKE lower(:n)"), {"n": f"%{inst_val}%"}).first()
                    logging.info("sacramento_admin_controller: resolving institucion by value='%s'", inst_val)
                    if row:
                        try:
                            inst_id = row._mapping.get('id_institucion')
                        except Exception:
                            try:
                                inst_id = row['id_institucion'] if 'id_institucion' in row.keys() else None
                            except Exception:
                                try:
                                    inst_id = row[0]
                                except Exception:
                                    inst_id = None
                if inst_id:
                    sac_updates.append("institucion_id = :institucion_id")
                    sac_params["institucion_id"] = inst_id

            # resolver libro (acepta id o nombre)
            if "libro" in sacr_payload and sacr_payload["libro"] is not None:
                libro_val = sacr_payload["libro"]
                libro_id = None
                if isinstance(libro_val, int):
                    # verify libro exists
                    row = db.execute(text("SELECT id_libro FROM libros WHERE id_libro = :id"), {"id": int(libro_val)}).first()
                    if row:
                        libro_id = int(libro_val)
                    else:
                        logging.info("sacramento_admin_controller: provided libro id %s not found; skipping libro update", libro_val)
                else:
                    row = db.execute(text("SELECT id_libro FROM libros WHERE lower(nombre) = lower(:n)"), {"n": str(libro_val)}).first()
                    if not row:
                        row = db.execute(text("SELECT id_libro FROM libros WHERE lower(nombre) LIKE lower(:n)"), {"n": f"%{libro_val}%"}).first()
                    logging.info("sacramento_admin_controller: resolving libro by value='%s'", libro_val)
                    if row:
                        try:
                            libro_id = row._mapping.get('id_libro')
                        except Exception:
                            try:
                                libro_id = row['id_libro'] if 'id_libro' in row.keys() else None
                            except Exception:
                                try:
                                    libro_id = row[0]
                                except Exception:
                                    libro_id = None
                if libro_id:
                    sac_updates.append("libro_id = :libro_id")
                    sac_params["libro_id"] = libro_id

            if "fecha_sacramento" in sacr_payload and sacr_payload["fecha_sacramento"] is not None:
                sac_updates.append("fecha_sacramento = :fecha_sacramento")
                sac_params["fecha_sacramento"] = sacr_payload["fecha_sacramento"]

            if sac_updates:
                sql = f"UPDATE sacramentos SET {', '.join(sac_updates)}, fecha_actualizacion = now() WHERE id_sacramento = :id"
                db.execute(text(sql), sac_params)

        db.commit()

        # Reconstruct the updated sacramento + persona to return to the client
        try:
            row = db.execute(text(
                "SELECT s.id_sacramento, s.persona_id, s.tipo_id, s.institucion_id, s.libro_id, s.fecha_sacramento, "
                "t.id_tipo AS tipo_id, t.nombre AS tipo_nombre, "
                "i.id_institucion AS institucion_id, i.nombre AS institucion_nombre, "
                "l.id_libro AS libro_id, l.nombre AS libro_nombre, "
                "p.nombres AS persona_nombres, p.apellido_paterno AS persona_apellido_paterno, p.apellido_materno AS persona_apellido_materno "
                "FROM sacramentos s "
                "LEFT JOIN tipos_sacramentos t ON t.id_tipo = s.tipo_id "
                "LEFT JOIN InstitucionesParroquias i ON i.id_institucion = s.institucion_id "
                "LEFT JOIN libros l ON l.id_libro = s.libro_id "
                "LEFT JOIN personas p ON p.id_persona = s.persona_id "
                "WHERE s.id_sacramento = :id"
            ), {"id": sacramento_id}).fetchone()
            if row:
                m = None
                try:
                    m = row._mapping
                except Exception:
                    # fallback: try to build from tuple/keys
                    try:
                        keys = list(row.keys())
                        m = {k: row[idx] for idx, k in enumerate(keys)}
                    except Exception:
                        m = None

                sac_obj = {
                    "id_sacramento": m.get("id_sacramento") if m else None,
                    "persona_id": m.get("persona_id") if m else None,
                    "fecha_sacramento": str(m.get("fecha_sacramento")) if m and m.get("fecha_sacramento") is not None else None,
                    "tipo": {
                        "id_tipo": m.get("tipo_id"),
                        "nombre": m.get("tipo_nombre")
                    },
                    "institucion": {
                        "id_institucion": m.get("institucion_id"),
                        "nombre": m.get("institucion_nombre")
                    },
                    "libro": {
                        "id_libro": m.get("libro_id"),
                        "nombre": m.get("libro_nombre")
                    }
                }
                persona_obj = None
                if m and m.get("persona_id"):
                    persona_obj = {
                        "id_persona": m.get("persona_id"),
                        "nombres": m.get("persona_nombres"),
                        "apellido_paterno": m.get("persona_apellido_paterno"),
                        "apellido_materno": m.get("persona_apellido_materno"),
                    }
                return {"updated": True, "sacramento": sac_obj, "persona": persona_obj}
        except Exception:
            logging.exception("sacramento_admin_controller: failed to reconstruct updated sacramento")

        # Fallback simple response
        return {"updated": True, "id_sacramento": sacramento_id}

    except Exception as e:
        db.rollback()
        tb = traceback.format_exc()
        logging.error("sacramento_admin_controller: exception traceback:\n%s", tb)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=tb)


@router.delete("/{sacramento_id}", status_code=status.HTTP_200_OK, summary="Eliminar sacramento (físico)")
def delete_sacramento(sacramento_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente el sacramento y sus datos dependientes (detalles) de la base de datos.
    Se borran filas en tablas de detalles relacionadas antes de eliminar el registro principal.
    """
    try:
        # Verificar existencia
        sac = db.execute(text("SELECT id_sacramento FROM sacramentos WHERE id_sacramento = :id"), {"id": sacramento_id}).first()
        if not sac:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sacramento {sacramento_id} no encontrado")

        # Eliminar registros dependientes en orden seguro
        # detalles_bautizo, detalles_confirmacion, detalles_matrimonio, matrimonios, ocr_resultado, validacion_tuplas
        db.execute(text("DELETE FROM detalles_bautizo WHERE sacramento_id = :id"), {"id": sacramento_id})
        db.execute(text("DELETE FROM detalles_confirmacion WHERE sacramento_id = :id"), {"id": sacramento_id})
        db.execute(text("DELETE FROM detalles_matrimonio WHERE sacramento_id = :id"), {"id": sacramento_id})
        db.execute(text("DELETE FROM matrimonios WHERE sacramento_id = :id"), {"id": sacramento_id})
        db.execute(text("DELETE FROM ocr_resultado WHERE sacramento_id = :id"), {"id": sacramento_id})
        db.execute(text("DELETE FROM validacion_tuplas WHERE sacramento_registrado_id = :id"), {"id": sacramento_id})

        # Finalmente eliminar el sacramento
        db.execute(text("DELETE FROM sacramentos WHERE id_sacramento = :id"), {"id": sacramento_id})

        db.commit()

        return {"deleted": True, "id_sacramento": sacramento_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

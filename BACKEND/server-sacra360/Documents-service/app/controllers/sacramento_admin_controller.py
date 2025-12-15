from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter(prefix="/sacramentos", tags=["SacramentosAdmin"]) 


@router.put("/{sacramento_id}", status_code=status.HTTP_200_OK, summary="Actualizar sacramento y persona")
def update_sacramento(
    sacramento_id: int,
    payload: dict,
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

    # Verificar existencia del sacramento
    sac = db.execute(text("SELECT * FROM sacramentos WHERE id_sacramento = :id"), {"id": sacramento_id}).first()
    if not sac:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sacramento {sacramento_id} no encontrado")

    persona_payload = payload.get("persona") or {}
    sacr_payload = payload.get("sacramento") or {}

    try:
        # Actualizar persona si se envió bloque persona
        if persona_payload:
            update_fields = []
            params = {"id": sac.id_persona}
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
                update_fields.append("lugar_nacimiento = :lugar_nacimiento")
                params["lugar_nacimiento"] = persona_payload["lugar_nacimiento"]

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
                    tipo_id = int(tipo_val)
                else:
                    # buscar por nombre (ilike)
                    row = db.execute(text("SELECT id_tipo FROM tipos_sacramentos WHERE lower(nombre) = lower(:n)") , {"n": str(tipo_val)}).first()
                    if not row:
                        # try partial match
                        row = db.execute(text("SELECT id_tipo FROM tipos_sacramentos WHERE lower(nombre) LIKE lower(:n)") , {"n": f"%{tipo_val}%"}).first()
                    if row:
                        tipo_id = row.id_tipo
                if tipo_id:
                    sac_updates.append("tipo_id = :tipo_id")
                    sac_params["tipo_id"] = tipo_id

            # resolver institucion (acepta id o nombre)
            if "institucion" in sacr_payload and sacr_payload["institucion"] is not None:
                inst_val = sacr_payload["institucion"]
                inst_id = None
                if isinstance(inst_val, int):
                    inst_id = int(inst_val)
                else:
                    row = db.execute(text("SELECT id_institucion FROM InstitucionesParroquias WHERE lower(nombre) = lower(:n)"), {"n": str(inst_val)}).first()
                    if not row:
                        row = db.execute(text("SELECT id_institucion FROM InstitucionesParroquias WHERE lower(nombre) LIKE lower(:n)"), {"n": f"%{inst_val}%"}).first()
                    if row:
                        inst_id = row.id_institucion
                if inst_id:
                    sac_updates.append("institucion_id = :institucion_id")
                    sac_params["institucion_id"] = inst_id

            if "fecha_sacramento" in sacr_payload and sacr_payload["fecha_sacramento"] is not None:
                sac_updates.append("fecha_sacramento = :fecha_sacramento")
                sac_params["fecha_sacramento"] = sacr_payload["fecha_sacramento"]

            if sac_updates:
                sql = f"UPDATE sacramentos SET {', '.join(sac_updates)}, fecha_actualizacion = now() WHERE id_sacramento = :id"
                db.execute(text(sql), sac_params)

        db.commit()

        # Reconstruir el recurso actualizado para devolver
        result = db.execute(text(
            "SELECT s.id_sacramento, s.fecha_sacramento, s.fecha_registro, s.tipo_id, ts.nombre as tipo_nombre, s.institucion_id, ip.nombre as institucion_nombre, p.id_persona, p.nombres, p.apellido_paterno, p.apellido_materno, p.fecha_nacimiento, p.fecha_bautismo, p.nombre_padre_nombre_madre, p.nombre_padrino_nombre_madrina "
            "FROM sacramentos s "
            "LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
            "LEFT JOIN InstitucionesParroquias ip ON ip.id_institucion = s.institucion_id "
            "LEFT JOIN personas p ON p.id_persona = s.persona_id "
            "WHERE s.id_sacramento = :id"
        ), {"id": sacramento_id}).first()

        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al reconstruir recurso updated")

        response = {
            "id_sacramento": result.id_sacramento,
            "fecha_sacramento": str(result.fecha_sacramento) if result.fecha_sacramento else None,
            "fecha_registro": str(result.fecha_registro) if result.fecha_registro else None,
            "tipo": {"id_tipo": result.tipo_id, "nombre": result.tipo_nombre} if result.tipo_id else None,
            "institucion": {"id_institucion": result.institucion_id, "nombre": result.institucion_nombre} if result.institucion_id else None,
            "persona": {
                "id_persona": result.id_persona,
                "nombres": result.nombres,
                "apellido_paterno": result.apellido_paterno,
                "apellido_materno": result.apellido_materno,
                "fecha_nacimiento": str(result.fecha_nacimiento) if result.fecha_nacimiento else None,
                "fecha_bautismo": str(result.fecha_bautismo) if hasattr(result, 'fecha_bautismo') and result.fecha_bautismo else None,
                "nombre_padre_nombre_madre": result.nombre_padre_nombre_madre,
                "nombre_padrino_nombre_madrina": result.nombre_padrino_nombre_madrina
            } if result.id_persona else None
        }

        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{sacramento_id}", status_code=status.HTTP_200_OK, summary="Baja lógica de sacramento")
def deactivate_sacramento(sacramento_id: int, db: Session = Depends(get_db)):
    """
    Realiza una baja lógica del sacramento. Añade la columna `activo` si no existe y la marca como FALSE.
    Esto evita eliminar físicamente el registro y mantiene trazabilidad.
    """
    try:
        # Asegurar columna activo
        db.execute(text("ALTER TABLE sacramentos ADD COLUMN IF NOT EXISTS activo boolean DEFAULT true"))
        # Verificar existencia
        sac = db.execute(text("SELECT id_sacramento FROM sacramentos WHERE id_sacramento = :id"), {"id": sacramento_id}).first()
        if not sac:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sacramento {sacramento_id} no encontrado")

        db.execute(text("UPDATE sacramentos SET activo = false, fecha_actualizacion = now() WHERE id_sacramento = :id"), {"id": sacramento_id})
        db.commit()

        return {"deleted": True, "id_sacramento": sacramento_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

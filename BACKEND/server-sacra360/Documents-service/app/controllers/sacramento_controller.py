from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime

from app.database import get_db
from app.dto.sacramento_dto import SacramentoCreateDTO, SacramentoUpdateDTO
from pydantic import ValidationError

router = APIRouter(prefix="/sacramentos", tags=["Sacramentos"])


def _row_to_dict(row, keys):
    return {k: getattr(row, k) if hasattr(row, k) else row[idx] for idx, k in enumerate(keys)}


def _validate_sacramento_payload(tipo_id: int, payload: Dict[str, Any], db: Optional[Session] = None):
    """Valida campos mínimos y reglas por tipo. Lanza HTTPException(422) con detalle si hay errores.
    Esta función intenta ser tolerante con distintos nombres de campo que provienen del frontend.
    """
    errors = []

    # Persona requerida (id_persona o person_name)
    has_persona = bool(payload.get('id_persona') or payload.get('persona_id') or payload.get('person_name') or payload.get('nombres'))
    if not has_persona:
        errors.append({"field": "person", "message": "id_persona o person_name requerido"})

    # Fecha del sacramento
    fecha_raw = payload.get('fecha_sacramento')
    if not fecha_raw:
        errors.append({"field": "fecha_sacramento", "message": "fecha_sacramento requerida"})
    else:
        try:
            if isinstance(fecha_raw, str):
                datetime.fromisoformat(fecha_raw)
        except Exception:
            errors.append({"field": "fecha_sacramento", "message": "fecha_sacramento inválida, use ISO (YYYY-MM-DD)"})

    # Determinar nombre del tipo si es posible (preferir nombre en catálogo)
    tipo_nombre = None
    try:
        if db is not None:
            r = db.execute(text("SELECT nombre FROM tipos_sacramentos WHERE id_tipo = :id LIMIT 1"), {"id": tipo_id}).fetchone()
            if r:
                tipo_nombre = (r[0] or "").lower()
    except Exception:
        tipo_nombre = None
    # si payload trae el nombre, usarlo como respaldo
    if not tipo_nombre:
        tp = payload.get('tipo_sacramento') or payload.get('tipo')
        if isinstance(tp, str):
            tipo_nombre = tp.lower()

    # Reglas por tipo (comparar por nombre cuando sea posible)
    try:
        t = int(tipo_id)
    except Exception:
        t = None

    # Bautizo: exigir al menos ministro o padrino o datos de libro/acta
    if tipo_nombre == 'bautizo' or t == 1:
        has_ministro = bool(payload.get('ministro') or payload.get('sacrament_minister') or payload.get('sacrament-minister'))
        has_padrino = bool(payload.get('padrino') or payload.get('godparent_1_name') or payload.get('godparent-1-name'))
        has_libro_info = bool(payload.get('folio') or payload.get('folio_number') or payload.get('numero_acta') or payload.get('record_number') or payload.get('book_number'))
        if not (has_ministro or has_padrino or has_libro_info):
            errors.append({"field": "bautizo", "message": "Para bautizo debe incluir ministro, padrino o datos de libro/acta"})

    # Confirmación: reglas similares a bautizo (ministro o padrino o datos de libro/acta)
    if tipo_nombre == 'confirmacion' or t == 2:
        has_ministro = bool(payload.get('ministro') or payload.get('sacrament_minister') or payload.get('sacrament-minister'))
        has_padrino = bool(payload.get('padrino') or payload.get('godparent_1_name') or payload.get('godparent-1-name') or payload.get('padrina') or payload.get('godparent_2_name'))
        has_libro_info = bool(payload.get('folio') or payload.get('folio_number') or payload.get('numero_acta') or payload.get('record_number') or payload.get('book_number'))
        if not (has_ministro or has_padrino or has_libro_info):
            errors.append({"field": "confirmacion", "message": "Para confirmación debe incluir ministro, padrino/madrina o datos de libro/acta"})

    # Matrimonio: requerir dos personas y datos de padres para ambos contrayentes (ser tolerante con nombres de campo)
    if tipo_nombre == 'matrimonio' or tipo_nombre == 'matrimonios' or (t is not None and t == 3):
        # Comprobar presencia de ambos contrayentes
        has_person1 = bool(payload.get('persona_id') or payload.get('id_persona') or payload.get('person_name') or payload.get('nombres'))
        has_person2 = bool(payload.get('persona2_id') or payload.get('id_persona_2') or payload.get('spouse_name') or payload.get('second_person_name') or payload.get('contrayente_2') or payload.get('person2_name'))
        if not (has_person1 and has_person2):
            errors.append({"field": "matrimonio", "message": "Matrimonio requiere datos de ambos contrayentes (persona 1 y persona 2)"})

        # Padres: para cada contrayente esperamos padre y madre (aceptar variantes de nombre)
        def has_parents_for(prefixes):
            # prefixes: list of prefix strings to try, e.g. ['','2','_2','spouse_']
            for p in prefixes:
                padre = payload.get(f'father_name{p}') or payload.get(f'padre{p}') or payload.get(f'padre_nombre{p}')
                madre = payload.get(f'mother_name{p}') or payload.get(f'madre{p}') or payload.get(f'madre_nombre{p}')
                if padre and madre:
                    return True
            return False

        # Try common suffixes/variants for second spouse
        person1_parent_ok = has_parents_for(['', '_1', '1']) or (payload.get('father_name') and payload.get('mother_name'))
        person2_parent_ok = has_parents_for(['2', '_2', '2_name', '_spouse']) or bool(payload.get('father2_name') and payload.get('mother2_name')) or bool(payload.get('spouse_father') and payload.get('spouse_mother'))

        if not person1_parent_ok:
            errors.append({"field": "padres_contrayente_1", "message": "Se requieren nombres de padre y madre para el primer contrayente"})
        if not person2_parent_ok:
            errors.append({"field": "padres_contrayente_2", "message": "Se requieren nombres de padre y madre para el segundo contrayente"})

    if errors:
        raise HTTPException(status_code=422, detail=errors)



@router.post("/", status_code=status.HTTP_201_CREATED)
def create_sacramento(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Crear un sacramento. Usa los nombres de columnas que utiliza OCR/validación (tipo_id, persona_id, libro_id, etc.)."""
    # Run pydantic validation if possible (non-destructive — we don't modify payload)
    try:
        try:
            SacramentoCreateDTO.model_validate(payload)
        except ValidationError as ve:
            # Do not reject the request due to DTO validation errors; log and continue.
            try:
                print('[sacramento_controller] SacramentoCreateDTO validation warning:', ve.errors())
            except Exception:
                pass

        # continue with existing logic
    except HTTPException:
        raise
    except Exception:
        # If validation step unexpectedly fails, log/ignore and continue to avoid breaking behavior
        pass

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

        # Asegurar que el tipo exista en la tabla tipos_sacramentos.
        # Si el id numérico fue provisto pero no existe, intentar crear un tipo usando el nombre provisto
        # en el payload o usando un mapeo por defecto.
        try:
            rcheck = db.execute(text("SELECT id_tipo FROM tipos_sacramentos WHERE id_tipo = :id LIMIT 1"), {"id": tipo_id}).fetchone()
            if not rcheck:
                # intentar obtener nombre desde payload
                tipo_name_payload = payload.get('tipo_sacramento') or payload.get('tipo') or payload.get('tipo_nombre') or payload.get('tipoName')
                if tipo_name_payload:
                    res_t = db.execute(text("INSERT INTO tipos_sacramentos (nombre) VALUES (:n) RETURNING id_tipo"), {"n": tipo_name_payload})
                    tipo_id = res_t.fetchone()[0]
                    db.commit()
                else:
                    # mapping por defecto para ids comunes
                    try:
                        default_map = {1: 'bautizo', 2: 'confirmacion', 3: 'matrimonio', 4: 'defuncion', 5: 'primera comunion'}
                        fallback_name = default_map.get(int(tipo_id), 'desconocido')
                    except Exception:
                        fallback_name = 'desconocido'
                    res_t = db.execute(text("INSERT INTO tipos_sacramentos (nombre) VALUES (:n) RETURNING id_tipo"), {"n": fallback_name})
                    tipo_id = res_t.fetchone()[0]
                    db.commit()
        except Exception:
            # Si por alguna razón falla la creación del tipo, hacer rollback y continuar; el intento de inserción
            # del sacramento fallará con FK si no existe el tipo, por eso preferimos propagar el error más adelante.
            try:
                db.rollback()
            except Exception:
                pass

        # Validar payload básico y reglas por tipo antes de continuar
        try:
            _validate_sacramento_payload(tipo_id, payload, db)
        except HTTPException:
            raise

        persona_id = payload.get("id_persona") or payload.get("persona_id")
        # Si no se proporciona persona_id, permitir crear una persona simple a partir de campos del formulario
        if not persona_id:
            # intentar leer nombre / fecha de nacimiento
            person_name = payload.get("person_name") or payload.get("nombres")
            person_birth = payload.get("person_birthdate") or payload.get("fecha_nacimiento") or payload.get("fecha_nacimiento_persona")
            padre = payload.get("father_name") or payload.get("nombre_padre")
            madre = payload.get("mother_name") or payload.get("nombre_madre")
            if person_name:
                # Insertar persona mínima. Los campos apellido_paterno/materno no son obligatorios en la inserción aquí (se usan valores vacíos si no vienen)
                ap1 = payload.get("apellido_paterno") or ""
                ap2 = payload.get("apellido_materno") or ""
                try:
                    lugar = payload.get("lugar_nacimiento") or payload.get("place_of_birth") or ""
                    res_p = db.execute(text(
                        "INSERT INTO personas (nombres, apellido_paterno, apellido_materno, fecha_nacimiento, lugar_nacimiento, nombre_padre, nombre_madre) VALUES (:n, :ap1, :ap2, :fn, :lugar, :np, :nm) RETURNING id_persona"
                    ), {
                        "n": person_name,
                        "ap1": ap1,
                        "ap2": ap2,
                        "fn": person_birth,
                        "lugar": lugar,
                        "np": padre,
                        "nm": madre
                    })
                    persona_id = res_p.fetchone()[0]
                    db.commit()
                except Exception:
                    db.rollback()
                    raise HTTPException(status_code=500, detail="Error creando persona asociada")
            else:
                raise HTTPException(status_code=422, detail="id_persona o person_name requerido")

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
        institucion_val = payload.get("institucion_id") or payload.get("institucion") or payload.get("parroquia") or payload.get("sacrament_location") or payload.get("sacrament-location")
        institucion_id = None
        # Si se pasó un nombre de institución/parroquia intentar resolver o crear
        if institucion_val:
            try:
                if isinstance(institucion_val, int):
                    institucion_id = institucion_val
                else:
                    r = db.execute(text("SELECT id_institucion FROM institucionesparroquias WHERE lower(nombre)=lower(:n) LIMIT 1"), {"n": institucion_val}).fetchone()
                    if r:
                        institucion_id = r[0]
                    else:
                        ins = db.execute(text("INSERT INTO institucionesparroquias (nombre) VALUES (:n) RETURNING id_institucion"), {"n": institucion_val})
                        institucion_id = ins.fetchone()[0]
                        db.commit()
            except Exception:
                db.rollback()
                institucion_id = 1
        if not institucion_id:
            institucion_id = 1

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

        # Si es bautizo, opcionalmente insertar detalles (ministro, padrino, foja, numero)
        try:
            if tipo_id == 1:  # asumimos id 1 = bautizo en el catálogo
                ministro = payload.get("ministro") or payload.get("sacrament_minister") or payload.get("sacrament-minister")
                padrino = payload.get("padrino") or payload.get("godparent_1_name") or payload.get("godparent-1-name")
                foja = payload.get("folio") or payload.get("folio_number") or payload.get("folio-number")
                numero = payload.get("numero_acta") or payload.get("record-number") or payload.get("record_number")
                fecha_det = fecha_sac
                if any([ministro, padrino, foja, numero]):
                    db.execute(text(
                        "INSERT INTO detalles_bautizo (sacramento_id, padrino, ministro, foja, numero, fecha_bautizo) VALUES (:sid, :pad, :min, :foj, :num, :f)"
                    ), {"sid": sac_id, "pad": padrino, "min": ministro, "foj": foja, "num": numero, "f": fecha_det})
                    db.commit()

        except Exception:
            db.rollback()

        # Resolver nombre del tipo (consulta por si no conocemos el id fijo)
        tipo_nombre_local = None
        try:
            tr = db.execute(text("SELECT nombre FROM tipos_sacramentos WHERE id_tipo = :id LIMIT 1"), {"id": tipo_id}).fetchone()
            if tr:
                tipo_nombre_local = (tr[0] or "").lower()
        except Exception:
            tipo_nombre_local = None

        # Si es confirmación, insertar detalles de confirmación (ministro, padrino/madrina, foja, numero)
        try:
            if tipo_id == 2 or tipo_nombre_local == 'confirmacion' or tipo_nombre_local == 'confirmación':
                ministro = payload.get("ministro") or payload.get("sacrament_minister") or payload.get("sacrament-minister")
                padrino = payload.get("padrino") or payload.get("godparent_1_name") or payload.get("godparent-1-name")
                madrina = payload.get("padrina") or payload.get("godparent_2_name") or payload.get("godparent-2-name")
                foja = payload.get("folio") or payload.get("folio_number") or payload.get("folio-number")
                numero = payload.get("numero_acta") or payload.get("record-number") or payload.get("record_number")
                fecha_det = fecha_sac
                # Insertar solo si hay algo relevante
                if any([ministro, padrino, madrina, foja, numero]):
                    db.execute(text(
                        "INSERT INTO detalles_confirmacion (sacramento_id, ministro, padrino, madrina, foja, numero, fecha_confirmacion) VALUES (:sid, :min, :pad, :mad, :foj, :num, :f)"
                    ), {"sid": sac_id, "min": ministro, "pad": padrino, "mad": madrina, "foj": foja, "num": numero, "f": fecha_det})
                    db.commit()
        except Exception:
            # si la tabla no existe u ocurre error, revertir y continuar (no bloquear registro principal)
            db.rollback()

        # Include detail tables (bautizo/confirmacion/matrimonio) so we can return saved foja/numero/pagina and spouse names
        enriched_sql = text(
            "SELECT s.*, ts.nombre as tipo_nombre, "
            "concat_ws(' ', p.nombres, p.apellido_paterno, p.apellido_materno) AS persona_nombre, "
            "p.nombre_padre AS nombre_padre, p.nombre_madre AS nombre_madre, "
            "ip.nombre AS institucion_nombre, "
            "COALESCE(dbt.foja, dcf.foja, dmt.foja) AS foja, "
            "COALESCE(dbt.numero, dcf.numero, dmt.numero) AS numero_acta, "
            "COALESCE(dbt.ministro, dcf.ministro, dmt.ministro) AS ministro, "
            "dmt.nombre_esposo AS nombre_esposo, dmt.nombre_esposa AS nombre_esposa, "
            "dbt.padrino AS padrino_bautizo, dcf.padrino AS padrino_confirmacion "
            "FROM sacramentos s "
            "LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
            "LEFT JOIN personas p ON p.id_persona = s.persona_id "
            "LEFT JOIN institucionesparroquias ip ON ip.id_institucion = s.institucion_id "
            "LEFT JOIN detalles_bautizo dbt ON dbt.sacramento_id = s.id_sacramento "
            "LEFT JOIN detalles_confirmacion dcf ON dcf.sacramento_id = s.id_sacramento "
            "LEFT JOIN detalles_matrimonio dmt ON dmt.sacramento_id = s.id_sacramento "
            "WHERE s.id_sacramento = :id"
        )
        fallback_sql = text(
            "SELECT s.*, ts.nombre as tipo_nombre, "
            "concat_ws(' ', p.nombres, p.apellido_paterno, p.apellido_materno) AS persona_nombre, "
            "ip.nombre AS institucion_nombre "
            "FROM sacramentos s "
            "LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
            "LEFT JOIN personas p ON p.id_persona = s.persona_id "
            "LEFT JOIN institucionesparroquias ip ON ip.id_institucion = s.institucion_id "
            "WHERE s.id_sacramento = :id"
        )
        try:
            row = db.execute(enriched_sql, {"id": sac_id}).fetchone()
        except Exception:
            # If the enriched query references columns that don't exist, fall back to safe select
            try:
                db.rollback()
            except Exception:
                pass
            row = db.execute(fallback_sql, {"id": sac_id}).fetchone()
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
        sql = (
            "SELECT s.*, ts.nombre as tipo_nombre, "
            "concat_ws(' ', p.nombres, p.apellido_paterno, p.apellido_materno) AS persona_nombre, "
            "p.nombre_padre AS nombre_padre, p.nombre_madre AS nombre_madre, "
            "ip.nombre AS institucion_nombre, "
            "COALESCE(dbt.foja, dcf.foja, dmt.foja) AS foja, "
            "COALESCE(dbt.numero, dcf.numero, dmt.numero) AS numero_acta, "
            "COALESCE(dbt.ministro, dcf.ministro, dmt.ministro) AS ministro, "
            "dmt.nombre_esposo AS nombre_esposo, dmt.nombre_esposa AS nombre_esposa, "
            "dbt.padrino AS padrino_bautizo, dcf.padrino AS padrino_confirmacion "
            "FROM sacramentos s "
                "LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
                "LEFT JOIN personas p ON p.id_persona = s.persona_id "
                "LEFT JOIN institucionesparroquias ip ON ip.id_institucion = s.institucion_id "
                "LEFT JOIN detalles_bautizo dbt ON dbt.sacramento_id = s.id_sacramento "
                "LEFT JOIN detalles_confirmacion dcf ON dcf.sacramento_id = s.id_sacramento "
                "LEFT JOIN detalles_matrimonio dmt ON dmt.sacramento_id = s.id_sacramento"
        )
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
            # detalles_bautizo puede almacenar el ministro; la tabla sacramentos no tiene columna 'ministro'
            # por eso buscamos en detalles_bautizo.ministro y en el nombre completo de la persona
            where.append("(dbt.ministro ILIKE :sac OR concat_ws(' ', p.nombres, p.apellido_paterno, p.apellido_materno) ILIKE :sac)")
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

        try:
            result = db.execute(text(sql), params)
            rows = [dict(r._mapping) for r in result.fetchall()]
            return rows
        except Exception:
            # Fallback: run a safe query without referencing detalle_* columns (older DB schemas)
            try:
                db.rollback()
            except Exception:
                pass
            safe_sql = (
                "SELECT s.*, ts.nombre as tipo_nombre, "
                "concat_ws(' ', p.nombres, p.apellido_paterno, p.apellido_materno) AS persona_nombre, "
                "ip.nombre AS institucion_nombre "
                "FROM sacramentos s "
                "LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
                "LEFT JOIN personas p ON p.id_persona = s.persona_id "
                "LEFT JOIN institucionesparroquias ip ON ip.id_institucion = s.institucion_id"
            )
            result = db.execute(text(safe_sql + " ORDER BY s.fecha_sacramento DESC LIMIT :lim OFFSET :off"), params)
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
    enriched_sql = text(
        "SELECT s.*, ts.nombre as tipo_nombre, "
        "concat_ws(' ', p.nombres, p.apellido_paterno, p.apellido_materno) AS persona_nombre, "
        "p.nombre_padre AS nombre_padre, p.nombre_madre AS nombre_madre, "
        "ip.nombre AS institucion_nombre, "
        "COALESCE(dbt.foja, dcf.foja, dmt.foja) AS foja, "
        "COALESCE(dbt.numero, dcf.numero, dmt.numero) AS numero_acta, "
        "COALESCE(dbt.ministro, dcf.ministro, dmt.ministro) AS ministro, "
        "dmt.nombre_esposo AS nombre_esposo, dmt.nombre_esposa AS nombre_esposa "
        "FROM sacramentos s "
        "LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
        "LEFT JOIN personas p ON p.id_persona = s.persona_id "
        "LEFT JOIN institucionesparroquias ip ON ip.id_institucion = s.institucion_id "
        "LEFT JOIN detalles_bautizo dbt ON dbt.sacramento_id = s.id_sacramento "
        "LEFT JOIN detalles_confirmacion dcf ON dcf.sacramento_id = s.id_sacramento "
        "LEFT JOIN detalles_matrimonio dmt ON dmt.sacramento_id = s.id_sacramento "
        "WHERE s.id_sacramento = :id"
    )
    fallback_sql = text(
        "SELECT s.*, ts.nombre as tipo_nombre, "
        "concat_ws(' ', p.nombres, p.apellido_paterno, p.apellido_materno) AS persona_nombre, "
        "ip.nombre AS institucion_nombre "
        "FROM sacramentos s "
        "LEFT JOIN tipos_sacramentos ts ON ts.id_tipo = s.tipo_id "
        "LEFT JOIN personas p ON p.id_persona = s.persona_id "
        "LEFT JOIN institucionesparroquias ip ON ip.id_institucion = s.institucion_id "
        "WHERE s.id_sacramento = :id"
    )
    try:
        row = db.execute(enriched_sql, {"id": id}).fetchone()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        row = db.execute(fallback_sql, {"id": id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sacramento no encontrado")
    return dict(row._mapping)


@router.put("/{id}")
def update_sacramento(id: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
    # Validate update payload non-destructively using pydantic
    try:
        try:
            SacramentoUpdateDTO.model_validate(payload)
        except ValidationError as ve:
            # Don't reject update requests due to DTO validation errors; log and continue.
            try:
                print('[sacramento_controller] SacramentoUpdateDTO validation warning:', ve.errors())
            except Exception:
                pass
    except HTTPException:
        raise
    except Exception:
        # ignore unexpected validation issues to preserve backward compatibility
        pass

    # If client sent `observaciones` but the DB lacks that column, add it dynamically (safe for development).
    try:
        # Ensure certain optional columns exist in sacramentos table so updates won't fail on older schemas.
        for col in ('observaciones', 'folio', 'numero_acta', 'pagina', 'foja'):
            if col in payload:
                try:
                    db.execute(text(f"ALTER TABLE sacramentos ADD COLUMN IF NOT EXISTS {col} text"))
                    db.commit()
                except Exception:
                    try:
                        db.rollback()
                    except Exception:
                        pass
    except Exception:
        # defensive: ignore any problems while ensuring column exists
        try:
            db.rollback()
        except Exception:
            pass

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
    # After updating sacramentos, also upsert into the appropriate detalles_* table
    try:
        # determine tipo_id (may have been updated)
        tr = db.execute(text("SELECT tipo_id FROM sacramentos WHERE id_sacramento = :id"), {"id": id}).fetchone()
        tipo_id_cur = tr[0] if tr else None
        tipo_nombre_cur = None
        try:
            if tipo_id_cur is not None:
                tn = db.execute(text("SELECT nombre FROM tipos_sacramentos WHERE id_tipo = :id LIMIT 1"), {"id": tipo_id_cur}).fetchone()
                if tn:
                    tipo_nombre_cur = (tn[0] or '').lower()
        except Exception:
            tipo_nombre_cur = None

        # Normalize payload keys
        foja = payload.get('folio') or payload.get('foja')
        numero = payload.get('numero_acta') or payload.get('numero')
        ministro = payload.get('ministro')
        padrino = payload.get('padrino')
        nombre_esposo = payload.get('nombre_esposo') or payload.get('esposo') or payload.get('spouse_name')
        nombre_esposa = payload.get('nombre_esposa') or payload.get('esposa') or payload.get('spouse_name_2')
        reg_civil = payload.get('reg_civil')
        fecha_mat = payload.get('fecha_matrimonio') or payload.get('fecha_sacramento')
        lugar_mat = payload.get('lugar_matrimonio') or payload.get('lugar')

        # helper to upsert into a details table
        def _upsert_detail(table, cols_map):
            # cols_map: dict of column_name -> value
            if not any(v is not None for v in cols_map.values()):
                return
            exists = db.execute(text(f"SELECT 1 FROM {table} WHERE sacramento_id = :id LIMIT 1"), {"id": id}).fetchone()
            if exists:
                sets = []
                params_local = {"id": id}
                for col, val in cols_map.items():
                    if val is not None:
                        sets.append(f"{col} = :{col}")
                        params_local[col] = val
                if sets:
                    sql_up = text(f"UPDATE {table} SET {', '.join(sets)} WHERE sacramento_id = :id")
                    db.execute(sql_up, params_local)
                    db.commit()
            else:
                # Provide defaults for NOT NULL required columns in detalle tables
                params_local = {"sacramento_id": id}
                # Defaults per table
                if table == 'detalles_bautizo':
                    defaults = {
                        'padrino': '', 'ministro': '', 'foja': '', 'numero': '', 'fecha_bautizo': payload.get('fecha_sacramento') or datetime.now().date()
                    }
                elif table == 'detalles_confirmacion':
                    defaults = {
                        'padrino': '', 'ministro': '', 'foja': '', 'numero': '', 'fecha_confirmacion': payload.get('fecha_sacramento') or datetime.now().date()
                    }
                elif table == 'detalles_matrimonio':
                    defaults = {
                        'nombre_esposo': '', 'nombre_esposa': '', 'apellido_peterno_esposo': '', 'apellido_materno_esposo': '',
                        'apellido_peterno_esposa': '', 'apellido_materno_esposa': '', 'nombre_padre_esposo': '', 'nombre_madre_esposo': '',
                        'nombre_padre_esposa': '', 'nombre_madre_esposa': '', 'padrino': '', 'ministro': '', 'foja': '', 'numero': '',
                        'reg_civil': '', 'fecha_matrimonio': payload.get('fecha_sacramento') or datetime.now().date(), 'lugar_matrimonio': ''
                    }
                else:
                    defaults = {}
                # Merge provided cols_map over defaults
                merged = {**defaults, **{k: v for k, v in cols_map.items() if v is not None}}
                cols = ['sacramento_id']
                vals = [':sacramento_id']
                for col, val in merged.items():
                    cols.append(col)
                    vals.append(f":{col}")
                    params_local[col] = val
                sql_ins = text(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(vals)})")
                db.execute(sql_ins, params_local)
                db.commit()

        # Choose which detail table to update/insert
        try:
            # Bautizo
            if tipo_id_cur == 1 or (isinstance(tipo_nombre_cur, str) and 'bautizo' in tipo_nombre_cur):
                _upsert_detail('detalles_bautizo', {
                    'padrino': padrino,
                    'ministro': ministro,
                    'foja': foja,
                    'numero': numero,
                    'fecha_bautizo': payload.get('fecha_sacramento')
                })
            # Confirmacion
            elif tipo_id_cur == 2 or (isinstance(tipo_nombre_cur, str) and 'confirm' in tipo_nombre_cur):
                _upsert_detail('detalles_confirmacion', {
                    'padrino': padrino,
                    'ministro': ministro,
                    'foja': foja,
                    'numero': numero,
                    'fecha_confirmacion': payload.get('fecha_sacramento')
                })
            # Matrimonio
            elif tipo_id_cur == 3 or (isinstance(tipo_nombre_cur, str) and 'matrim' in tipo_nombre_cur):
                _upsert_detail('detalles_matrimonio', {
                    'nombre_esposo': nombre_esposo,
                    'nombre_esposa': nombre_esposa,
                    'padrino': padrino,
                    'ministro': ministro,
                    'foja': foja,
                    'numero': numero,
                    'reg_civil': reg_civil,
                    'fecha_matrimonio': fecha_mat,
                    'lugar_matrimonio': lugar_mat
                })
            else:
                # for other sacramentos, attempt to write to detalles_bautizo if fields match (safe fallback)
                _upsert_detail('detalles_bautizo', {
                    'padrino': padrino,
                    'ministro': ministro,
                    'foja': foja,
                    'numero': numero,
                    'fecha_bautizo': payload.get('fecha_sacramento')
                })
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    return get_sacramento(id, db)


@router.delete("/{id}")
def delete_sacramento(id: int, db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM sacramentos WHERE id_sacramento = :id"), {"id": id})
    db.commit()
    return {"message": "Sacramento eliminado"}
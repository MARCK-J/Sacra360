from typing import Any, Dict, Optional
import json, urllib.request, urllib.parse

from app.utils.pb_client import get_pb
from app.utils.config import get_settings
from app.entities.resultado import Resultado
from app.dto.resultado_dto import ResultadoCreateDTO, ResultadoUpdateDTO
from app.services._common import export_record, first_non_null

try:
    from pocketbase.client import ClientResponseError
except Exception:
    from pocketbase.utils import ClientResponseError

COL = "resultado_test"  # usa el nombre EXACTO en PB

# ---------- helpers ----------
def _record_to_dict(rec: Any) -> Dict[str, Any]:
    d_user = export_record(rec) or {}
    sys = {}
    for k in ("id", "created", "updated", "collectionId", "collectionName"):
        v = getattr(rec, k, None)
        if v is not None:
            sys[k] = v
    for k in ("id", "created", "updated"):
        if k not in sys and k in d_user and d_user[k] is not None:
            sys[k] = d_user[k]
    return {**d_user, **sys}

def _to_int(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    if isinstance(v, int):
        return v
    try:
        return int(str(v).strip())
    except Exception:
        return None

def _serialize_for_pb(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializa datos para PocketBase, convirtiendo objetos date/datetime a strings
    y mapeando nombres de campos del DTO a nombres de PocketBase
    """
    from datetime import date, datetime
    
    serialized = {}
    
    # Mapeo de campos del DTO a nombres en PocketBase
    field_mapping = {
        'id_test': 'test',        # id_test -> test
        'id_paciente': 'paciente' # id_paciente -> paciente
    }
    
    for key, value in data.items():
        # Mapear nombre del campo si es necesario
        pb_field_name = field_mapping.get(key, key)
        
        if isinstance(value, datetime):
            # Convertir datetime a string ISO
            serialized[pb_field_name] = value.isoformat()
        elif isinstance(value, date):
            # Convertir date a string en formato YYYY-MM-DD
            serialized[pb_field_name] = value.strftime('%Y-%m-%d')
        else:
            serialized[pb_field_name] = value
    
    return serialized

def _to_resultado_from_dict(d: Dict[str, Any]) -> Resultado:
    return Resultado(
        id                = first_non_null(d, "id", "ID", default=""),
        fecha_realizacion = first_non_null(d, "fecha_realizacion", "fechaRealizacion"),
        puntuacion_total  = _to_int(first_non_null(d, "puntuacion_total", "puntuacionTotal")),
        interpretacion    = first_non_null(d, "interpretacion"),
        comentario        = first_non_null(d, "comentario", "comentarios"),
        # Mapeo inverso: PocketBase usa 'test' y 'paciente', pero nuestro entity espera 'id_test' e 'id_paciente'
        id_test           = first_non_null(d, "test", "id_test", "idTest"),
        id_paciente       = first_non_null(d, "paciente", "id_paciente", "idPaciente"),
        active            = bool(first_non_null(d, "active", "isActive", "enabled", default=True)),
        created           = first_non_null(d, "created", "createdAt"),
        updated           = first_non_null(d, "updated", "updatedAt"),
    )

def _to_resultado(rec: Any) -> Resultado:
    return _to_resultado_from_dict(_record_to_dict(rec))

def _http_get_json(url: str, headers: Dict[str, str] | None = None, timeout: int = 8) -> Dict[str, Any]:
    req = urllib.request.Request(url, method="GET", headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        txt = resp.read().decode("utf-8") or "{}"
        return json.loads(txt)

def _auth_header() -> Dict[str, str]:
    st = get_settings()
    if st.PB_ADMIN_TOKEN:
        return {"Authorization": f"Bearer {st.PB_ADMIN_TOKEN}"}
    return {}

# ---------- service ----------
class ResultadoService:
    @staticmethod
    def create(dto: ResultadoCreateDTO) -> None:
        data = dto.model_dump(exclude_none=True)
        # Serializar fechas y mapear campos para PocketBase
        data = _serialize_for_pb(data)
        try:
            get_pb().collection(COL).create(data)
        except ClientResponseError as e:
            raise e

    @staticmethod
    def get(id: str) -> Resultado:
        try:
            rec = get_pb().collection(COL).get_one(id)
            r = _to_resultado(rec)
            if not r.id or r.id == "":
                raise RuntimeError("SDK get_one returned empty/invalid record; using HTTP fallback")
            return r
        except Exception:
            base = get_settings().pb_base()
            url = f"{base}/api/collections/{COL}/records/{id}"
            data = _http_get_json(url, headers=_auth_header())
            return _to_resultado_from_dict(data)

    @staticmethod
    def list(page: int = 1, per_page: int = 20, filtro: str | None = None, solo_activos: bool = True):
        params: Dict[str, Any] = {}
        if filtro and solo_activos:
            params["filter"] = f"({filtro}) && active = true"
        elif filtro:
            params["filter"] = f"({filtro})"
        elif solo_activos:
            params["filter"] = "active = true"

        try:
            res = get_pb().collection(COL).get_list(page, per_page, params)
            items = getattr(res, "items", []) or []
            mapped = [_record_to_dict(i) for i in items]
            if not mapped or all((not x) or (x.get("id") is None) for x in mapped):
                raise RuntimeError("SDK returned empty/invalid records; using HTTP fallback")
            return {
                "page": getattr(res, "page", page),
                "per_page": getattr(res, "per_page", getattr(res, "perPage", per_page)),
                "total_items": getattr(res, "total_items", getattr(res, "totalItems", None)),
                "items": [_to_resultado_from_dict(x).__dict__ for x in mapped],
            }
        except Exception:
            base = get_settings().pb_base()
            q = {"page": str(page), "perPage": str(per_page)}
            if "filter" in params and params["filter"]:
                q["filter"] = params["filter"]
            url = f"{base}/api/collections/{COL}/records?{urllib.parse.urlencode(q)}"
            data = _http_get_json(url, headers=_auth_header())
            items = data.get("items", [])
            return {
                "page": data.get("page", page),
                "per_page": data.get("perPage", per_page),
                "total_items": data.get("totalItems"),
                "items": [_to_resultado_from_dict(it).__dict__ for it in items],
            }

    @staticmethod
    def update(id: str, dto: ResultadoUpdateDTO) -> Resultado:
        data = dto.model_dump(exclude_none=True)
        # Serializar fechas y mapear campos para PocketBase
        data = _serialize_for_pb(data)
        try:
            rec = get_pb().collection(COL).update(id, data)
            r = _to_resultado(rec)
            if not r.id:
                raise RuntimeError("SDK update returned empty/invalid record; using HTTP fallback")
            return r
        except Exception:
            base = get_settings().pb_base()
            url = f"{base}/api/collections/{COL}/records/{id}"
            data_http = _http_get_json(url, headers=_auth_header())
            return _to_resultado_from_dict(data_http)

    @staticmethod
    def soft_delete(id: str) -> None:
        get_pb().collection(COL).update(id, {"active": False})

import time
import requests

AUTH_URL = "http://localhost:8001/api/v1/auth/login"
LIBROS_URL = "http://localhost:8002/api/v1/libros/"
EMAIL = "admin@sacra360.com"
PASSWORD = "admin123"

login_payload = {"email": EMAIL, "password": PASSWORD}
login_resp = requests.post(AUTH_URL, json=login_payload, timeout=30)
login_status = login_resp.status_code

if login_resp.ok:
    login_json = login_resp.json()
    token = login_json.get("access_token") or login_json.get("token")
else:
    token = None

create_status = None
libro_id = None
get_status = None
libro_json = None

if token:
    ts = int(time.time())
    create_payload = {
        "nombre": f"Libro temporal {ts}",
        "fecha_inicio": "2026-04-21",
        "fecha_fin": "2030-12-31",
        "observaciones": "Creado por script temporal; pendiente de eliminacion por el usuario."
    }
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = requests.post(LIBROS_URL, json=create_payload, headers=headers, timeout=30)
    create_status = create_resp.status_code

    if create_resp.ok:
        create_json = create_resp.json()
        libro_id = create_json.get("id_libro") or create_json.get("id")

        if libro_id is not None:
            get_resp = requests.get(f"{LIBROS_URL}{libro_id}", headers=headers, timeout=30)
            get_status = get_resp.status_code
            if get_resp.ok:
                libro_json = get_resp.json()
            else:
                libro_json = {"error": get_resp.text}
        else:
            libro_json = {"error": "No se pudo extraer id del libro creado", "create_response": create_json}
    else:
        libro_json = {"error": create_resp.text}

print(f"login_status={login_status}")
print(f"create_status={create_status}")
print(f"libro_id={libro_id}")
print(f"get_status={get_status}")
print("libro_json=")
print(libro_json)

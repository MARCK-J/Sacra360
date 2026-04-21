import requests

AUTH_URL = "http://localhost:8001/api/v1/auth/login"
LIBRO_URL = "http://localhost:8002/api/v1/libros/11"
EMAIL = "admin@sacra360.com"
PASSWORD = "admin123"

login_status = None
delete_status = None
delete_body = None
get_after_delete_status = None
get_after_delete_body = None

try:
    login_resp = requests.post(AUTH_URL, json={"email": EMAIL, "password": PASSWORD}, timeout=30)
    login_status = login_resp.status_code
    token = None
    if login_resp.ok:
        data = login_resp.json()
        token = data.get("access_token") or data.get("token")

    if token:
        headers = {"Authorization": f"Bearer {token}"}

        del_resp = requests.delete(LIBRO_URL, headers=headers, timeout=30)
        delete_status = del_resp.status_code
        try:
            delete_body = del_resp.json()
        except Exception:
            delete_body = del_resp.text

        get_resp = requests.get(LIBRO_URL, headers=headers, timeout=30)
        get_after_delete_status = get_resp.status_code
        try:
            get_after_delete_body = get_resp.json()
        except Exception:
            get_after_delete_body = get_resp.text
    else:
        delete_body = "No token obtenido en login"
        get_after_delete_body = "No token obtenido en login"

except Exception as e:
    delete_body = f"Error de ejecución: {e}"
    get_after_delete_body = f"Error de ejecución: {e}"

print(f"login_status={login_status}")
print(f"delete_status={delete_status}")
print(f"delete_body={delete_body}")
print(f"get_after_delete_status={get_after_delete_status}")
print(f"get_after_delete_body={get_after_delete_body}")

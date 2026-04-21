import requests
import time

BASE_URL = "http://localhost:8000"

def run_tests():
    print("🚀 Iniciando prueba de humo contra Supabase usando microservicios locales...\n")
    
    # 1. Autenticación para obtener el Token (usando el usuario admin por defecto)
    print("Autenticando usuario (POST /api/v1/auth/login)...")
    try:
        login_response = requests.post("http://localhost:8001/api/v1/auth/login", json={
            "email": "admin@sacra360.com",
            "password": "admin123"
        })
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login Exitoso. Token obtenido.")
        else:
            print(f"❌ Fallo el login (HTTP {login_response.status_code}). Verifica si inyectaste los scripts SQL en Supabase.")
            print(f"Detalle: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Error al conectar con el Gateway local: {e}")
        return

    # 2. Crear un libro nuevo en Sacramentos (CRUD)
    libro_payload = {
        "nombre": "Libro de Bautismos Automatizado - Demo",
        "fecha_inicio": "2026-04-20",
        "fecha_fin": "2030-12-31",
        "observaciones": "Libro creado para corroborar conexión a Supabase AWS/Cloud"
    }
    
    print("\nCreando un Libro (POST /api/v1/libros)...")
    create_response = requests.post("http://localhost:8002/api/v1/libros/", json=libro_payload, headers=headers)
    if create_response.status_code in [200, 201]:
        libro = create_response.json()
        libro_id = libro.get("id_libro")
        print(f"✅ Libro Creado Exitosamente en la Nube con ID: {libro_id}")
    else:
        print(f"❌ Fallo al crear libro: {create_response.text}")
        return

    # Esperar un segundo
    time.sleep(1)

    # 3. Obtener el libro recién creado
    print(f"\nObteniendo el libro ID {libro_id} de Supabase (GET /api/v1/libros/{libro_id})...")
    get_response = requests.get(f"http://localhost:8002/api/v1/libros/{libro_id}", headers=headers)
    if get_response.status_code == 200:
        print(f"✅ Libro obtenido. Confirmación desde la Base de Datos: {get_response.json().get('nombre')}")
    else:
        print(f"❌ Fallo al obtener: {get_response.text}")
        return

    # 4. Modificar el libro
    update_payload = {
        "observaciones": "Libro actualizado durante test de Supabase Cloud!"
    }
    print(f"\nActualizando el libro ID {libro_id} (PUT /api/v1/libros/{libro_id})...")
    update_response = requests.put(f"http://localhost:8002/api/v1/libros/{libro_id}", json=update_payload, headers=headers)
    if update_response.status_code == 200:
        print("✅ Libro Actualizado Exitosamente")
    else:
        print(f"❌ Fallo al actualizar: {update_response.text}")
        return

    # 5. Obtener nuevamente el libro actualizado
    print(f"\nObteniendo nuevamente el libro ID {libro_id} después del update...")
    get_after_update_response = requests.get(f"http://localhost:8002/api/v1/libros/{libro_id}", headers=headers)
    if get_after_update_response.status_code == 200:
        observaciones = get_after_update_response.json().get("observaciones")
        print(f"✅ Libro actualizado confirmado. Observaciones: {observaciones}")
    else:
        print(f"❌ Fallo al obtener después del update: {get_after_update_response.text}")
        return

    # 6. Eliminar el libro
    print(f"\nEliminando el libro ID {libro_id} (DELETE /api/v1/libros/{libro_id})...")
    delete_response = requests.delete(f"http://localhost:8002/api/v1/libros/{libro_id}", headers=headers)
    if delete_response.status_code in [200, 204]:
        print("✅ Libro Eliminado Exitosamente de la base de datos.")
    else:
        print(f"❌ Fallo al eliminar: {delete_response.text}")

    print("\n🎉 PRUEBA CLOUD FINALIZADA CON ÉXITO. Tu infraestructura está 100% lista para presentarse con Ngrok.")

if __name__ == "__main__":
    run_tests()
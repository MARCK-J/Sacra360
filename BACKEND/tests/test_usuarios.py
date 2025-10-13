#!/usr/bin/env python3
"""
Tests para los endpoints de Usuarios
Módulo: /api/v1/usuarios/
"""

import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import APITestClient, print_test_header, print_response_info, validate_schema_fields


def test_auth_endpoints():
    """Test de endpoints de autenticación"""
    print_test_header("Tests de Autenticación - Usuarios")
    
    client = APITestClient()
    
    # Test 1: Login exitoso
    print("\n1️⃣ Test: Login con credenciales correctas")
    login_success = client.login()
    if login_success:
        print("✅ Login exitoso - Token obtenido")
    else:
        print("❌ Login falló")
        return
    
    # Test 2: Obtener información del usuario autenticado
    print("\n2️⃣ Test: Obtener información del usuario actual (/me)")
    response = client.get("/usuarios/me")
    print_response_info(response, "Obtener información del usuario actual")
    
    if response.status_code == 200:
        required_fields = ['id_usuario', 'nombre', 'email', 'rol', 'activo']
        validate_schema_fields(response.json(), required_fields, "Info usuario actual")
    
    # Test 3: Login con credenciales incorrectas
    print("\n3️⃣ Test: Login con credenciales incorrectas")
    client_bad = APITestClient()
    login_data = {
        "email": "wrong@email.com",
        "password": "wrongpassword"
    }
    
    response = client_bad.session.post(
        f"{client_bad.base_url}/usuarios/login",
        json=login_data
    )
    print_response_info(response, "Login con credenciales incorrectas")
    
    if response.status_code == 401:
        print("✅ Correctamente rechazado - Status 401")
    else:
        print("❌ Debería haber sido rechazado con 401")


def test_user_management():
    """Test de gestión de usuarios"""
    print_test_header("Tests de Gestión de Usuarios")
    
    client = APITestClient()
    
    # Login como admin
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Obtener lista de usuarios
    print("\n1️⃣ Test: Obtener lista de usuarios")
    response = client.get("/usuarios/")
    print_response_info(response, "Obtener lista de usuarios")
    
    if response.status_code == 200:
        users = response.json()
        if isinstance(users, list) and len(users) > 0:
            print(f"✅ Se obtuvieron {len(users)} usuarios")
            required_fields = ['id_usuario', 'nombre', 'email', 'rol']
            validate_schema_fields(users[0], required_fields, "Estructura de usuario")
        else:
            print("⚠️  Lista de usuarios vacía")
    
    # Test 2: Registro de nuevo usuario
    print("\n2️⃣ Test: Registrar nuevo usuario")
    new_user_data = {
        "nombre": "Usuario",
        "apellido_paterno": "De Prueba",
        "apellido_materno": "Test",
        "email": "test@sacra360.com",
        "fecha_nacimiento": "1990-01-01",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "activo": True,
        "id_rol": 4  # Rol consultor
    }
    
    response = client.post("/usuarios/register", new_user_data)
    print_response_info(response, "Registrar nuevo usuario")
    
    if response.status_code in [200, 201]:
        created_user = response.json()
        user_id = created_user.get('id_usuario')
        print(f"✅ Usuario creado con ID: {user_id}")
        
        # Test 3: Obtener usuario por ID
        print("\n3️⃣ Test: Obtener usuario por ID")
        response = client.get(f"/usuarios/{user_id}")
        print_response_info(response, f"Obtener usuario ID {user_id}")
        
        if response.status_code == 200:
            required_fields = ['id_usuario', 'nombre', 'email', 'rol', 'activo']
            validate_schema_fields(response.json(), required_fields, "Usuario por ID")
        
        # Test 4: Actualizar usuario
        print("\n4️⃣ Test: Actualizar usuario")
        update_data = {
            "nombre": "Usuario Actualizado",
            "apellido_paterno": "Apellido Nuevo"
        }
        
        response = client.put(f"/usuarios/{user_id}", update_data)
        print_response_info(response, f"Actualizar usuario ID {user_id}")
        
        # Test 5: Cambiar estado del usuario
        print("\n5️⃣ Test: Cambiar estado del usuario")
        response = client.post(f"/usuarios/{user_id}/toggle-status")
        print_response_info(response, f"Cambiar estado usuario ID {user_id}")


def test_user_search_and_pagination():
    """Test de búsqueda y paginación de usuarios"""
    print_test_header("Tests de Búsqueda y Paginación - Usuarios")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Búsqueda por nombre
    print("\n1️⃣ Test: Búsqueda de usuarios por nombre")
    response = client.get("/usuarios/", params={"search": "admin"})
    print_response_info(response, "Búsqueda por 'admin'")
    
    # Test 2: Filtro por estado activo
    print("\n2️⃣ Test: Filtro por usuarios activos")
    response = client.get("/usuarios/", params={"activo": True})
    print_response_info(response, "Filtro usuarios activos")
    
    # Test 3: Filtro por rol
    print("\n3️⃣ Test: Filtro por rol de administrador")
    response = client.get("/usuarios/", params={"id_rol": 1})
    print_response_info(response, "Filtro rol administrador")
    
    # Test 4: Paginación
    print("\n4️⃣ Test: Paginación")
    response = client.get("/usuarios/", params={"page": 1, "limit": 2})
    print_response_info(response, "Paginación - Página 1, Límite 2")


def test_setup_admin():
    """Test del endpoint especial setup-admin"""
    print_test_header("Test Setup Admin")
    
    client = APITestClient()
    
    # Test: Intentar crear admin cuando ya existe uno
    print("\n1️⃣ Test: Intentar setup-admin cuando ya existe")
    admin_data = {
        "nombre": "Segundo",
        "apellido_paterno": "Admin",
        "email": "admin2@sacra360.com",
        "fecha_nacimiento": "1980-01-01",
        "password": "Admin456!",
        "confirm_password": "Admin456!",
        "activo": True,
        "id_rol": 1
    }
    
    response = client.post("/usuarios/setup-admin", admin_data)
    print_response_info(response, "Setup segundo admin")
    
    if response.status_code == 400:
        print("✅ Correctamente rechazado - Ya existe un admin")
    else:
        print("⚠️  Respuesta inesperada para setup-admin")


def run_all_user_tests():
    """Ejecutar todos los tests de usuarios"""
    print("🚀 Iniciando Tests Completos de Usuarios")
    print("=" * 80)
    
    test_auth_endpoints()
    test_user_management()
    test_user_search_and_pagination()
    test_setup_admin()
    
    print("\n" + "=" * 80)
    print("🏁 Tests de Usuarios Completados")


if __name__ == "__main__":
    run_all_user_tests()
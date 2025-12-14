"""
Script de prueba exhaustiva para AuthProfiles Service
Prueba todos los endpoints: Auth, CRUD Usuarios, Auditoría y Reportes
"""

import requests
import json
from datetime import datetime
from typing import Optional

# Configuración
BASE_URL = "http://localhost:8001/api/v1"
ADMIN_EMAIL = "admin@sacra360.com"
ADMIN_PASSWORD = "Diego0102:;"

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.total = 0
    
    def add_pass(self, test_name: str):
        self.passed.append(test_name)
        self.total += 1
        print(f"   {Colors.GREEN}✅ PASS{Colors.RESET}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed.append((test_name, error))
        self.total += 1
        print(f"   {Colors.RED}❌ FAIL: {error}{Colors.RESET}")
    
    def print_summary(self):
        print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 RESUMEN DE PRUEBAS{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"\n{Colors.GREEN}✅ Pasadas: {len(self.passed)}/{self.total}{Colors.RESET}")
        print(f"{Colors.RED}❌ Fallidas: {len(self.failed)}/{self.total}{Colors.RESET}")
        
        if self.failed:
            print(f"\n{Colors.RED}Tests fallidos:{Colors.RESET}")
            for test, error in self.failed:
                print(f"  • {test}: {error}")
        
        success_rate = (len(self.passed) / self.total * 100) if self.total > 0 else 0
        print(f"\n{Colors.BOLD}Tasa de éxito: {success_rate:.1f}%{Colors.RESET}\n")

# Variables globales
token = None
test_user_id = None
results = TestResults()

def print_header(title: str):
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_test(test_number: int, description: str):
    print(f"{Colors.YELLOW}🧪 Test {test_number}: {description}{Colors.RESET}")

def print_detail(detail: str):
    print(f"   {Colors.GRAY}{detail}{Colors.RESET}")

# ==================== TESTS DE AUTENTICACIÓN ====================

def test_login():
    """Test 1: Login y obtención de token"""
    global token
    print_test(1, "POST /auth/login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "contrasenia": ADMIN_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print_detail(f"Token obtenido: {token[:50]}...")
            print_detail(f"Usuario: {data['user_info']['nombre']} {data['user_info']['apellido_paterno']}")
            print_detail(f"Rol: {data['user_info']['nombre_rol']}")
            print_detail(f"Permisos: {', '.join(data['permissions'])}")
            results.add_pass("Login")
            return True
        else:
            results.add_fail("Login", f"Status {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("Login", str(e))
        return False

def test_get_me():
    """Test 2: Obtener información del usuario actual"""
    print_test(2, "GET /auth/me")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Usuario: {data['nombre']} {data['apellido_paterno']} {data.get('apellido_materno', '')}")
            print_detail(f"Email: {data['email']}")
            print_detail(f"Rol: {data['nombre_rol']} (ID: {data['rol_id']})")
            print_detail(f"Activo: {data['activo']}")
            results.add_pass("GET /me")
        else:
            results.add_fail("GET /me", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /me", str(e))

def test_get_roles():
    """Test 3: Obtener roles disponibles"""
    print_test(3, "GET /auth/roles")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/roles",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Roles encontrados: {len(data['roles'])}")
            for rol in data['roles']:
                print_detail(f"  [{rol['id_rol']}] {rol['nombre_rol']}: {rol.get('descripcion', 'N/A')}")
            results.add_pass("GET /auth/roles")
        else:
            results.add_fail("GET /auth/roles", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /auth/roles", str(e))

# ==================== TESTS DE CRUD USUARIOS ====================

def test_list_usuarios():
    """Test 4: Listar todos los usuarios"""
    print_test(4, "GET /usuarios")
    
    try:
        response = requests.get(
            f"{BASE_URL}/usuarios",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Total usuarios: {len(data)}")
            activos = sum(1 for u in data if u['activo'])
            print_detail(f"Activos: {activos} | Inactivos: {len(data) - activos}")
            results.add_pass("GET /usuarios")
        else:
            results.add_fail("GET /usuarios", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /usuarios", str(e))

def test_list_usuarios_filtered():
    """Test 5: Listar usuarios con filtros"""
    print_test(5, "GET /usuarios?activo=true&limit=5")
    
    try:
        response = requests.get(
            f"{BASE_URL}/usuarios?activo=true&limit=5",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Usuarios activos (límite 5): {len(data)}")
            results.add_pass("GET /usuarios (filtros)")
        else:
            results.add_fail("GET /usuarios (filtros)", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /usuarios (filtros)", str(e))

def test_get_usuario_by_id():
    """Test 6: Obtener usuario por ID"""
    print_test(6, "GET /usuarios/{id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/usuarios/5",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Usuario ID 5: {data['nombre']} {data['apellido_paterno']}")
            print_detail(f"Email: {data['email']} | Rol: {data['nombre_rol']}")
            results.add_pass("GET /usuarios/{id}")
        else:
            results.add_fail("GET /usuarios/{id}", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /usuarios/{id}", str(e))

def test_list_roles():
    """Test 7: Listar roles del sistema"""
    print_test(7, "GET /usuarios/roles/listar")
    
    try:
        response = requests.get(
            f"{BASE_URL}/usuarios/roles/listar",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Total roles: {len(data)}")
            for rol in data:
                print_detail(f"  [{rol['id_rol']}] {rol['nombre']}: {rol.get('descripcion', 'N/A')}")
            results.add_pass("GET /usuarios/roles/listar")
        else:
            results.add_fail("GET /usuarios/roles/listar", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /usuarios/roles/listar", str(e))

def test_create_usuario():
    """Test 8: Crear nuevo usuario"""
    global test_user_id
    print_test(8, "POST /usuarios (crear)")
    
    try:
        timestamp = datetime.now().strftime("%H%M%S")
        new_user = {
            "nombre": "Test",
            "apellido_paterno": "Usuario",
            "apellido_materno": "Prueba",
            "email": f"test.usuario.{timestamp}@sacra360.com",
            "contrasenia": "TestPass123!",
            "rol_id": 3,
            "activo": True
        }
        
        response = requests.post(
            f"{BASE_URL}/usuarios",
            json=new_user,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            test_user_id = data['id_usuario']
            print_detail(f"Usuario creado con ID: {test_user_id}")
            print_detail(f"Datos: {data['nombre']} {data['apellido_paterno']} - {data['email']}")
            print_detail(f"Rol: {data['nombre_rol']}")
            results.add_pass("POST /usuarios")
        else:
            error_msg = response.json().get('detail', f'Status {response.status_code}')
            results.add_fail("POST /usuarios", error_msg)
    except Exception as e:
        results.add_fail("POST /usuarios", str(e))

def test_update_usuario():
    """Test 9: Actualizar usuario"""
    print_test(9, "PUT /usuarios/{id} (actualizar)")
    
    if not test_user_id:
        print_detail("Saltado - usuario de prueba no creado")
        return
    
    try:
        update_data = {
            "nombre": "Test Actualizado",
            "apellido_materno": "Modificado"
        }
        
        response = requests.put(
            f"{BASE_URL}/usuarios/{test_user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Usuario actualizado: {data['nombre']} {data['apellido_paterno']}")
            results.add_pass("PUT /usuarios/{id}")
        else:
            results.add_fail("PUT /usuarios/{id}", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("PUT /usuarios/{id}", str(e))

def test_change_password():
    """Test 10: Cambiar contraseña"""
    print_test(10, "PATCH /usuarios/{id}/password")
    
    if not test_user_id:
        print_detail("Saltado - usuario de prueba no creado")
        return
    
    try:
        password_data = {
            "contrasenia": "NewPassword456!"
        }
        
        response = requests.patch(
            f"{BASE_URL}/usuarios/{test_user_id}/password",
            json=password_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Mensaje: {data.get('message', 'Contraseña actualizada')}")
            results.add_pass("PATCH /usuarios/{id}/password")
        else:
            results.add_fail("PATCH /usuarios/{id}/password", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("PATCH /usuarios/{id}/password", str(e))

def test_delete_usuario():
    """Test 11: Desactivar usuario"""
    print_test(11, "DELETE /usuarios/{id} (desactivar)")
    
    if not test_user_id:
        print_detail("Saltado - usuario de prueba no creado")
        return
    
    try:
        response = requests.delete(
            f"{BASE_URL}/usuarios/{test_user_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Mensaje: {data.get('message', 'Usuario desactivado')}")
            results.add_pass("DELETE /usuarios/{id}")
        else:
            results.add_fail("DELETE /usuarios/{id}", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("DELETE /usuarios/{id}", str(e))

def test_activate_usuario():
    """Test 12: Reactivar usuario"""
    print_test(12, "PATCH /usuarios/{id}/activar")
    
    if not test_user_id:
        print_detail("Saltado - usuario de prueba no creado")
        return
    
    try:
        response = requests.patch(
            f"{BASE_URL}/usuarios/{test_user_id}/activar",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Mensaje: {data.get('message', 'Usuario reactivado')}")
            results.add_pass("PATCH /usuarios/{id}/activar")
        else:
            results.add_fail("PATCH /usuarios/{id}/activar", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("PATCH /usuarios/{id}/activar", str(e))

# ==================== TESTS DE AUDITORÍA ====================

def test_get_auditoria():
    """Test 13: Obtener registros de auditoría"""
    print_test(13, "GET /auditoria")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auditoria",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Registros de auditoría encontrados: {len(data)}")
            if data:
                print_detail(f"Último registro: {data[0].get('accion', 'N/A')} - {data[0].get('fecha', 'N/A')}")
            results.add_pass("GET /auditoria")
        else:
            results.add_fail("GET /auditoria", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /auditoria", str(e))

def test_get_auditoria_filtered():
    """Test 14: Obtener auditoría filtrada"""
    print_test(14, "GET /auditoria?limit=10")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auditoria?limit=10",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_detail(f"Registros (límite 10): {len(data)}")
            results.add_pass("GET /auditoria (filtros)")
        else:
            results.add_fail("GET /auditoria (filtros)", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /auditoria (filtros)", str(e))

# ==================== TESTS DE REPORTES ====================

def test_get_reportes():
    """Test 15: Obtener reportes disponibles"""
    print_test(15, "GET /reportes")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reportes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_detail(f"Reportes disponibles: {len(data)}")
            else:
                print_detail(f"Respuesta: {json.dumps(data, indent=2)}")
            results.add_pass("GET /reportes")
        else:
            results.add_fail("GET /reportes", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("GET /reportes", str(e))

# ==================== MAIN ====================

def main():
    print_header("🔐 TEST EXHAUSTIVO - AuthProfiles Service")
    print(f"{Colors.WHITE}Base URL: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.WHITE}Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    # Tests de Autenticación
    print_header("🔑 TESTS DE AUTENTICACIÓN")
    if not test_login():
        print(f"\n{Colors.RED}❌ Login falló. No se pueden ejecutar más tests.{Colors.RESET}\n")
        return
    
    test_get_me()
    test_get_roles()
    
    # Tests de CRUD Usuarios
    print_header("👥 TESTS DE CRUD USUARIOS")
    test_list_usuarios()
    test_list_usuarios_filtered()
    test_get_usuario_by_id()
    test_list_roles()
    test_create_usuario()
    test_update_usuario()
    test_change_password()
    test_delete_usuario()
    test_activate_usuario()
    
    # Tests de Auditoría
    print_header("📋 TESTS DE AUDITORÍA")
    test_get_auditoria()
    test_get_auditoria_filtered()
    
    # Tests de Reportes
    print_header("📊 TESTS DE REPORTES")
    test_get_reportes()
    
    # Resumen final
    results.print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Tests interrumpidos por el usuario{Colors.RESET}\n")
    except Exception as e:
        print(f"\n\n{Colors.RED}❌ Error fatal: {e}{Colors.RESET}\n")

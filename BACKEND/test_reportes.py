"""
Script de prueba para endpoints de Reportes
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"
ADMIN_EMAIL = "admin@sacra360.com"
ADMIN_PASSWORD = "Diego0102:;"

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Login
print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
print(f"{Colors.BOLD}🔐 Autenticando...{Colors.RESET}")
print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

response = requests.post(f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL, "contrasenia": ADMIN_PASSWORD})
if response.status_code != 200:
    print(f"{Colors.RED}❌ Error en login{Colors.RESET}")
    exit(1)

token = response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}
print(f"{Colors.GREEN}✅ Login exitoso{Colors.RESET}\n")

print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
print(f"{Colors.BOLD}📊 TESTS DE REPORTES{Colors.RESET}")
print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

passed = 0
failed = 0

# Test 1: Reporte de usuarios
print(f"{Colors.YELLOW}🧪 Test 1: GET /reportes/usuarios{Colors.RESET}")
try:
    response = requests.get(f"{BASE_URL}/reportes/usuarios", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   {Colors.GREEN}✅ Total usuarios: {data['total_usuarios']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Activos: {data['usuarios_activos']} ({data['porcentaje_activos']}%){Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Inactivos: {data['usuarios_inactivos']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Distribución por roles: {len(data['usuarios_por_rol'])} roles{Colors.RESET}")
        for rol in data['usuarios_por_rol']:
            print(f"      • {rol['rol']}: {rol['cantidad']} ({rol['porcentaje']}%)")
        passed += 1
    else:
        print(f"   {Colors.RED}❌ Status {response.status_code}: {response.text}{Colors.RESET}")
        failed += 1
except Exception as e:
    print(f"   {Colors.RED}❌ Error: {e}{Colors.RESET}")
    failed += 1

# Test 2: Reporte de accesos
print(f"\n{Colors.YELLOW}🧪 Test 2: GET /reportes/accesos{Colors.RESET}")
try:
    response = requests.get(f"{BASE_URL}/reportes/accesos", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   {Colors.GREEN}✅ Total accesos: {data['total_accesos']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Logins exitosos: {data['logins_exitosos']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Logins fallidos: {data['logins_fallidos']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Tasa de éxito: {data['tasa_exito']:.2f}%{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Días con registros: {len(data['accesos_por_dia'])}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Usuarios más activos: {len(data['usuarios_mas_activos'])}{Colors.RESET}")
        passed += 1
    else:
        print(f"   {Colors.RED}❌ Status {response.status_code}: {response.text}{Colors.RESET}")
        failed += 1
except Exception as e:
    print(f"   {Colors.RED}❌ Error: {e}{Colors.RESET}")
    failed += 1

# Test 3: Estadísticas generales
print(f"\n{Colors.YELLOW}🧪 Test 3: GET /reportes/estadisticas{Colors.RESET}")
try:
    response = requests.get(f"{BASE_URL}/reportes/estadisticas", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   {Colors.GREEN}✅ Total usuarios: {data['total_usuarios']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Total accesos: {data['total_accesos']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Total acciones: {data['total_acciones']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Promedio accesos/día: {data['promedio_accesos_por_dia']:.2f}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Promedio accesos/usuario: {data['promedio_accesos_por_usuario']:.2f}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Eventos de auditoría: {data['total_eventos_auditoria']}{Colors.RESET}")
        passed += 1
    else:
        print(f"   {Colors.RED}❌ Status {response.status_code}: {response.text}{Colors.RESET}")
        failed += 1
except Exception as e:
    print(f"   {Colors.RED}❌ Error: {e}{Colors.RESET}")
    failed += 1

# Test 4: Reporte de actividad de usuario específico
print(f"\n{Colors.YELLOW}🧪 Test 4: GET /reportes/actividad/5{Colors.RESET}")
try:
    response = requests.get(f"{BASE_URL}/reportes/actividad/5", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   {Colors.GREEN}✅ Usuario: {data['nombre_completo']} ({data['email']}){Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Rol: {data['rol']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Total acciones: {data['total_acciones']}{Colors.RESET}")
        if data['ultimo_acceso']:
            print(f"   {Colors.GREEN}✅ Último acceso: {data['ultimo_acceso']}{Colors.RESET}")
        print(f"   {Colors.GREEN}✅ Acciones por módulo: {len(data['acciones_por_modulo'])}{Colors.RESET}")
        passed += 1
    else:
        print(f"   {Colors.RED}❌ Status {response.status_code}: {response.text}{Colors.RESET}")
        failed += 1
except Exception as e:
    print(f"   {Colors.RED}❌ Error: {e}{Colors.RESET}")
    failed += 1

# Resumen
total = passed + failed
print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
print(f"{Colors.BOLD}📊 RESUMEN DE PRUEBAS DE REPORTES{Colors.RESET}")
print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")
print(f"{Colors.GREEN}✅ Pasadas: {passed}/{total}{Colors.RESET}")
print(f"{Colors.RED}❌ Fallidas: {failed}/{total}{Colors.RESET}")
success_rate = (passed / total * 100) if total > 0 else 0
print(f"\n{Colors.BOLD}Tasa de éxito: {success_rate:.1f}%{Colors.RESET}\n")

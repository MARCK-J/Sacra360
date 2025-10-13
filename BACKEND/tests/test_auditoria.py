#!/usr/bin/env python3
"""
Tests para los endpoints de Auditoría
Módulo: /api/v1/auditoria/
"""

import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import APITestClient, print_test_header, print_response_info, validate_schema_fields


def test_auditoria_logs():
    """Test de logs de auditoría"""
    print_test_header("Tests de Logs de Auditoría")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Obtener logs de auditoría
    print("\n1️⃣ Test: Obtener logs de auditoría")
    response = client.get("/auditoria/logs")
    print_response_info(response, "Obtener logs de auditoría")
    
    if response.status_code == 200:
        logs = response.json()
        if isinstance(logs, list):
            print(f"✅ Se obtuvieron {len(logs)} logs de auditoría")
            
            # Verificar estructura si hay logs
            if logs and len(logs) > 0:
                required_fields = ['id_auditoria', 'tabla_afectada', 'operacion', 'fecha_operacion', 'id_usuario']
                validate_schema_fields(logs[0], required_fields, "Estructura log auditoría")
        else:
            print("⚠️  Respuesta no es una lista")


def test_auditoria_by_table():
    """Test de auditoría por tabla"""
    print_test_header("Tests Auditoría por Tabla")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test logs de diferentes tablas
    tablas = ["usuarios", "personas", "sacramentos", "documentos"]
    
    for i, tabla in enumerate(tablas, 1):
        print(f"\n{i}️⃣ Test: Logs de auditoría tabla '{tabla}'")
        response = client.get(f"/auditoria/logs/{tabla}")
        print_response_info(response, f"Logs tabla {tabla}")
        
        if response.status_code == 200:
            logs = response.json()
            if isinstance(logs, list):
                print(f"✅ Se encontraron {len(logs)} logs para tabla {tabla}")


def test_auditoria_by_user():
    """Test de auditoría por usuario"""
    print_test_header("Tests Auditoría por Usuario")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Logs del usuario actual
    print("\n1️⃣ Test: Logs del usuario actual")
    response = client.get("/auditoria/usuario/1")  # Asumiendo admin tiene ID 1
    print_response_info(response, "Logs del usuario ID 1")
    
    if response.status_code == 200:
        logs = response.json()
        if isinstance(logs, list):
            print(f"✅ Se encontraron {len(logs)} logs para el usuario")
            
            # Verificar que todos los logs pertenecen al usuario
            if logs:
                user_ids = set(log.get('id_usuario') for log in logs)
                if len(user_ids) == 1 and 1 in user_ids:
                    print("✅ Todos los logs pertenecen al usuario correcto")
                else:
                    print("⚠️  Logs de múltiples usuarios o usuario incorrecto")


def test_auditoria_by_operation():
    """Test de auditoría por tipo de operación"""
    print_test_header("Tests Auditoría por Operación")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test logs de diferentes operaciones
    operaciones = ["INSERT", "UPDATE", "DELETE"]
    
    for i, operacion in enumerate(operaciones, 1):
        print(f"\n{i}️⃣ Test: Logs de operación '{operacion}'")
        response = client.get("/auditoria/logs", params={"operacion": operacion})
        print_response_info(response, f"Logs operación {operacion}")
        
        if response.status_code == 200:
            logs = response.json()
            if isinstance(logs, list):
                print(f"✅ Se encontraron {len(logs)} logs de operación {operacion}")
                
                # Verificar que todos los logs son de la operación correcta
                if logs:
                    operaciones_encontradas = set(log.get('operacion') for log in logs)
                    if len(operaciones_encontradas) == 1 and operacion in operaciones_encontradas:
                        print(f"✅ Todos los logs son de operación {operacion}")
                    else:
                        print(f"⚠️  Logs de múltiples operaciones encontrados")


def test_auditoria_date_range():
    """Test de auditoría por rango de fechas"""
    print_test_header("Tests Auditoría por Rango de Fechas")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Logs del último mes
    print("\n1️⃣ Test: Logs del último mes")
    response = client.get("/auditoria/logs", params={
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-01-31"
    })
    print_response_info(response, "Logs enero 2024")
    
    # Test 2: Logs del año actual
    print("\n2️⃣ Test: Logs del año 2024")
    response = client.get("/auditoria/logs", params={
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-12-31"
    })
    print_response_info(response, "Logs año 2024")
    
    # Test 3: Logs de un día específico
    print("\n3️⃣ Test: Logs de un día específico")
    response = client.get("/auditoria/logs", params={
        "fecha_inicio": "2024-01-15",
        "fecha_fin": "2024-01-15"
    })
    print_response_info(response, "Logs del 15 enero 2024")


def test_auditoria_search():
    """Test de búsqueda en auditoría"""
    print_test_header("Tests de Búsqueda en Auditoría")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Búsqueda por descripción
    print("\n1️⃣ Test: Búsqueda por descripción")
    response = client.get("/auditoria/logs", params={"search": "usuario"})
    print_response_info(response, "Búsqueda por 'usuario'")
    
    # Test 2: Búsqueda combinada
    print("\n2️⃣ Test: Búsqueda combinada")
    response = client.get("/auditoria/logs", params={
        "tabla_afectada": "usuarios",
        "operacion": "INSERT",
        "search": "admin"
    })
    print_response_info(response, "Búsqueda combinada")


def test_auditoria_pagination():
    """Test de paginación en auditoría"""
    print_test_header("Tests de Paginación - Auditoría")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Primera página
    print("\n1️⃣ Test: Primera página de logs")
    response = client.get("/auditoria/logs", params={"page": 1, "limit": 5})
    print_response_info(response, "Página 1, límite 5")
    
    if response.status_code == 200:
        logs = response.json()
        if isinstance(logs, list):
            print(f"✅ Se obtuvieron {len(logs)} logs (máximo 5)")
            if len(logs) <= 5:
                print("✅ Paginación funcionando correctamente")
    
    # Test 2: Segunda página
    print("\n2️⃣ Test: Segunda página de logs")
    response = client.get("/auditoria/logs", params={"page": 2, "limit": 5})
    print_response_info(response, "Página 2, límite 5")
    
    # Test 3: Página con límite alto
    print("\n3️⃣ Test: Página con límite alto")
    response = client.get("/auditoria/logs", params={"page": 1, "limit": 50})
    print_response_info(response, "Página 1, límite 50")


def test_auditoria_statistics():
    """Test de estadísticas de auditoría"""
    print_test_header("Tests de Estadísticas de Auditoría")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Estadísticas generales
    print("\n1️⃣ Test: Estadísticas generales de auditoría")
    response = client.get("/auditoria/estadisticas")
    print_response_info(response, "Estadísticas generales")
    
    if response.status_code == 200:
        stats = response.json()
        if isinstance(stats, dict):
            expected_fields = ['total_logs', 'operaciones_por_tipo', 'tablas_mas_activas']
            validate_schema_fields(stats, expected_fields, "Estadísticas auditoría")
    
    # Test 2: Estadísticas por tabla
    print("\n2️⃣ Test: Estadísticas por tabla")
    response = client.get("/auditoria/estadisticas/tabla/usuarios")
    print_response_info(response, "Estadísticas tabla usuarios")
    
    # Test 3: Estadísticas por usuario
    print("\n3️⃣ Test: Estadísticas por usuario")
    response = client.get("/auditoria/estadisticas/usuario/1")
    print_response_info(response, "Estadísticas usuario ID 1")


def test_auditoria_permissions():
    """Test de permisos en auditoría"""
    print_test_header("Tests de Permisos - Auditoría")
    
    # Test con usuario admin
    client_admin = APITestClient()
    
    if client_admin.login():
        print("\n1️⃣ Test: Admin accede a logs de auditoría")
        response = client_admin.get("/auditoria/logs")
        print_response_info(response, "Admin - Acceso a logs")
        
        if response.status_code == 200:
            print("✅ Admin tiene acceso completo a auditoría")
        else:
            print("❌ Admin no puede acceder a auditoría")
    
    # Nota: En un entorno real, aquí probaríamos con diferentes roles
    # para verificar que solo los usuarios autorizados pueden acceder


def run_all_auditoria_tests():
    """Ejecutar todos los tests de auditoría"""
    print("🚀 Iniciando Tests Completos de Auditoría")
    print("=" * 80)
    
    test_auditoria_logs()
    test_auditoria_by_table()
    test_auditoria_by_user()
    test_auditoria_by_operation()
    test_auditoria_date_range()
    test_auditoria_search()
    test_auditoria_pagination()
    test_auditoria_statistics()
    test_auditoria_permissions()
    
    print("\n" + "=" * 80)
    print("🏁 Tests de Auditoría Completados")


if __name__ == "__main__":
    run_all_auditoria_tests()
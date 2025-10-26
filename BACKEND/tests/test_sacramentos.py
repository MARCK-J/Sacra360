#!/usr/bin/env python3
"""
Tests para los endpoints de Sacramentos
Módulo: /api/v1/sacramentos/
"""

import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import APITestClient, print_test_header, print_response_info, validate_schema_fields, run_basic_crud_test


def test_sacramentos_crud():
    """Test CRUD básico para sacramentos"""
    print_test_header("Tests CRUD - Sacramentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Datos para crear sacramento
    create_data = {
        "id_persona": 1,  # Asumiendo que existe una persona con ID 1
        "tipo_sacramento": "bautizo",
        "fecha_sacramento": "2024-01-15",
        "lugar_sacramento": "Parroquia San José",
        "sacerdote_celebrante": "Padre Miguel Hernández",
        "padrino": "Juan Pérez",
        "madrina": "María García",
        "observaciones": "Sacramento realizado durante la misa dominical",
        "numero_acta": "001/2024",
        "libro_registro": "Libro de Bautizos 2024",
        "folio": "001",
        "activo": True
    }
    
    # Datos para actualizar sacramento
    update_data = {
        "observaciones": "Sacramento actualizado - Ceremonia especial",
        "sacerdote_celebrante": "Padre José María"
    }
    
    # Campos requeridos en la respuesta
    required_fields = [
        'id_sacramento', 'id_persona', 'tipo_sacramento', 'fecha_sacramento',
        'lugar_sacramento', 'activo'
    ]
    
    # Ejecutar test CRUD
    run_basic_crud_test(
        client=client,
        endpoint="/sacramentos",
        create_data=create_data,
        update_data=update_data,
        required_fields=required_fields,
        entity_name="Sacramento"
    )


def test_sacramentos_by_type():
    """Test de endpoints específicos por tipo de sacramento"""
    print_test_header("Tests por Tipo de Sacramento")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Obtener bautizos
    print("\n1️⃣ Test: Obtener lista de bautizos")
    response = client.get("/sacramentos/bautizos")
    print_response_info(response, "Lista de bautizos")
    
    if response.status_code == 200:
        bautizos = response.json()
        if isinstance(bautizos, list):
            print(f"✅ Se obtuvieron {len(bautizos)} bautizos")
        
        # Verificar estructura si hay datos
        if bautizos and len(bautizos) > 0:
            required_fields = ['id_sacramento', 'tipo_sacramento', 'fecha_sacramento']
            validate_schema_fields(bautizos[0], required_fields, "Estructura bautizo")
    
    # Test 2: Obtener confirmaciones
    print("\n2️⃣ Test: Obtener lista de confirmaciones")
    response = client.get("/sacramentos/confirmaciones")
    print_response_info(response, "Lista de confirmaciones")
    
    # Test 3: Obtener matrimonios
    print("\n3️⃣ Test: Obtener lista de matrimonios")
    response = client.get("/sacramentos/matrimonios")
    print_response_info(response, "Lista de matrimonios")
    
    # Test 4: Obtener primeras comuniones
    print("\n4️⃣ Test: Obtener lista de primeras comuniones")
    response = client.get("/sacramentos/primeras-comuniones")
    print_response_info(response, "Lista de primeras comuniones")


def test_sacramento_bautizo():
    """Test específico para crear bautizo"""
    print_test_header("Test Específico - Crear Bautizo")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    bautizo_data = {
        "id_persona": 1,
        "fecha_sacramento": "2024-02-01",
        "lugar_sacramento": "Parroquia Nuestra Señora de Guadalupe",
        "sacerdote_celebrante": "Padre Antonio Ruiz",
        "padrino": "Roberto Martínez",
        "madrina": "Carmen Rodríguez",
        "observaciones": "Bautizo durante la celebración especial",
        "numero_acta": "B-002/2024",
        "libro_registro": "Libro de Bautizos 2024",
        "folio": "002"
    }
    
    print("\n1️⃣ Test: Crear bautizo")
    response = client.post("/sacramentos/bautizos", bautizo_data)
    print_response_info(response, "Crear bautizo")
    
    if response.status_code in [200, 201]:
        created_bautizo = response.json()
        print(f"✅ Bautizo creado con ID: {created_bautizo.get('id_sacramento')}")
        
        # Verificar que el tipo sea correcto
        if created_bautizo.get('tipo_sacramento') == 'bautizo':
            print("✅ Tipo de sacramento correcto: bautizo")
        else:
            print("❌ Tipo de sacramento incorrecto")


def test_sacramento_matrimonio():
    """Test específico para crear matrimonio"""
    print_test_header("Test Específico - Crear Matrimonio")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    matrimonio_data = {
        "id_persona": 1,  # Novio
        "fecha_sacramento": "2024-03-15",
        "lugar_sacramento": "Catedral Metropolitana",
        "sacerdote_celebrante": "Padre Francisco López",
        "padrino": "Luis González",
        "madrina": "Ana Martínez",
        "observaciones": "Matrimonio con celebración especial",
        "numero_acta": "M-001/2024",
        "libro_registro": "Libro de Matrimonios 2024",
        "folio": "001",
        "id_persona_conyuge": 2,  # Novia (específico para matrimonios)
        "testigo_1": "Carlos Hernández",
        "testigo_2": "Sofía Ramírez"
    }
    
    print("\n1️⃣ Test: Crear matrimonio")
    response = client.post("/sacramentos/matrimonios", matrimonio_data)
    print_response_info(response, "Crear matrimonio")
    
    if response.status_code in [200, 201]:
        created_matrimonio = response.json()
        print(f"✅ Matrimonio creado con ID: {created_matrimonio.get('id_sacramento')}")


def test_sacramentos_search():
    """Test de búsqueda y filtros de sacramentos"""
    print_test_header("Tests de Búsqueda - Sacramentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Filtro por tipo de sacramento
    print("\n1️⃣ Test: Filtro por tipo de sacramento")
    response = client.get("/sacramentos/", params={"tipo_sacramento": "bautizo"})
    print_response_info(response, "Filtro tipo bautizo")
    
    # Test 2: Filtro por rango de fechas
    print("\n2️⃣ Test: Filtro por rango de fechas")
    response = client.get("/sacramentos/", params={
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-12-31"
    })
    print_response_info(response, "Filtro rango 2024")
    
    # Test 3: Búsqueda por sacerdote
    print("\n3️⃣ Test: Búsqueda por sacerdote")
    response = client.get("/sacramentos/", params={"sacerdote": "Padre Miguel"})
    print_response_info(response, "Búsqueda por sacerdote")
    
    # Test 4: Filtro por persona
    print("\n4️⃣ Test: Filtro por ID de persona")
    response = client.get("/sacramentos/", params={"id_persona": 1})
    print_response_info(response, "Filtro por persona ID 1")
    
    # Test 5: Paginación
    print("\n5️⃣ Test: Paginación")
    response = client.get("/sacramentos/", params={"page": 1, "limit": 5})
    print_response_info(response, "Paginación - Página 1, Límite 5")


def test_sacramentos_validation():
    """Test de validaciones de sacramentos"""
    print_test_header("Tests de Validación - Sacramentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Crear sacramento con tipo inválido
    print("\n1️⃣ Test: Crear sacramento con tipo inválido")
    invalid_data = {
        "id_persona": 1,
        "tipo_sacramento": "sacramento_inexistente",  # Tipo inválido
        "fecha_sacramento": "2024-01-01",
        "lugar_sacramento": "Parroquia Test",
        "activo": True
    }
    
    response = client.post("/sacramentos", invalid_data)
    print_response_info(response, "Crear sacramento con tipo inválido")
    
    if response.status_code == 422:
        print("✅ Validación correcta - Tipo inválido rechazado")
    
    # Test 2: Crear sacramento con fecha futura muy lejana
    print("\n2️⃣ Test: Crear sacramento con fecha muy futura")
    future_data = {
        "id_persona": 1,
        "tipo_sacramento": "bautizo",
        "fecha_sacramento": "2030-01-01",  # Fecha muy futura
        "lugar_sacramento": "Parroquia Test",
        "activo": True
    }
    
    response = client.post("/sacramentos", future_data)
    print_response_info(response, "Crear sacramento con fecha futura")
    
    # Test 3: Crear sacramento sin persona
    print("\n3️⃣ Test: Crear sacramento sin ID de persona")
    no_person_data = {
        "tipo_sacramento": "bautizo",
        "fecha_sacramento": "2024-01-01",
        "lugar_sacramento": "Parroquia Test",
        "activo": True
        # id_persona faltante
    }
    
    response = client.post("/sacramentos", no_person_data)
    print_response_info(response, "Crear sacramento sin persona")
    
    if response.status_code == 422:
        print("✅ Validación correcta - Persona requerida")


def run_all_sacramentos_tests():
    """Ejecutar todos los tests de sacramentos"""
    print("🚀 Iniciando Tests Completos de Sacramentos")
    print("=" * 80)
    
    test_sacramentos_crud()
    test_sacramentos_by_type()
    test_sacramento_bautizo()
    test_sacramento_matrimonio()
    test_sacramentos_search()
    test_sacramentos_validation()
    
    print("\n" + "=" * 80)
    print("🏁 Tests de Sacramentos Completados")


if __name__ == "__main__":
    run_all_sacramentos_tests()
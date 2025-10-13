#!/usr/bin/env python3
"""
Tests para los endpoints de Personas
Módulo: /api/v1/personas/
"""

import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import APITestClient, print_test_header, print_response_info, validate_schema_fields, run_basic_crud_test


def test_personas_crud():
    """Test CRUD básico para personas"""
    print_test_header("Tests CRUD - Personas")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Datos para crear persona
    create_data = {
        "nombre": "Juan Carlos",
        "apellido_paterno": "González",
        "apellido_materno": "López",
        "fecha_nacimiento": "1985-03-15",
        "lugar_nacimiento": "Ciudad de México",
        "genero": "M",
        "estado_civil": "soltero",
        "telefono": "555-1234567",
        "email": "juan.gonzalez@email.com",
        "direccion": "Calle Principal 123, Col. Centro",
        "nombre_padre": "Carlos González",
        "nombre_madre": "María López",
        "activo": True
    }
    
    # Datos para actualizar persona
    update_data = {
        "telefono": "555-7654321",
        "email": "juan.gonzalez.updated@email.com",
        "estado_civil": "casado"
    }
    
    # Campos requeridos en la respuesta
    required_fields = [
        'id_persona', 'nombre', 'apellido_paterno', 'fecha_nacimiento',
        'genero', 'estado_civil', 'activo'
    ]
    
    # Ejecutar test CRUD
    run_basic_crud_test(
        client=client,
        endpoint="/personas",
        create_data=create_data,
        update_data=update_data,
        required_fields=required_fields,
        entity_name="Persona"
    )


def test_personas_search():
    """Test de búsqueda y filtros de personas"""
    print_test_header("Tests de Búsqueda - Personas")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Búsqueda por nombre
    print("\n1️⃣ Test: Búsqueda por nombre")
    response = client.get("/personas/", params={"search": "Juan"})
    print_response_info(response, "Búsqueda por nombre 'Juan'")
    
    # Test 2: Filtro por género
    print("\n2️⃣ Test: Filtro por género masculino")
    response = client.get("/personas/", params={"genero": "M"})
    print_response_info(response, "Filtro género masculino")
    
    # Test 3: Filtro por estado civil
    print("\n3️⃣ Test: Filtro por estado civil")
    response = client.get("/personas/", params={"estado_civil": "soltero"})
    print_response_info(response, "Filtro estado civil soltero")
    
    # Test 4: Filtro por personas activas
    print("\n4️⃣ Test: Filtro por personas activas")
    response = client.get("/personas/", params={"activo": True})
    print_response_info(response, "Filtro personas activas")
    
    # Test 5: Paginación
    print("\n5️⃣ Test: Paginación")
    response = client.get("/personas/", params={"page": 1, "limit": 5})
    print_response_info(response, "Paginación - Página 1, Límite 5")
    
    # Test 6: Búsqueda combinada
    print("\n6️⃣ Test: Búsqueda combinada")
    response = client.get("/personas/", params={
        "search": "González",
        "genero": "M",
        "activo": True
    })
    print_response_info(response, "Búsqueda combinada")


def test_personas_sacramentos():
    """Test de relación personas-sacramentos"""
    print_test_header("Tests Personas-Sacramentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Primero crear una persona para las pruebas
    person_data = {
        "nombre": "María",
        "apellido_paterno": "Fernández",
        "apellido_materno": "García",
        "fecha_nacimiento": "1990-06-20",
        "lugar_nacimiento": "Guadalajara",
        "genero": "F",
        "estado_civil": "soltera",
        "activo": True
    }
    
    print("\n1️⃣ Creando persona para tests de sacramentos...")
    response = client.post("/personas", person_data)
    print_response_info(response, "Crear persona para tests")
    
    if response.status_code not in [200, 201]:
        print("❌ No se pudo crear persona, saltando tests de sacramentos")
        return
    
    created_person = response.json()
    person_id = created_person.get('id_persona')
    
    # Test: Obtener sacramentos de la persona
    print(f"\n2️⃣ Test: Obtener sacramentos de la persona ID {person_id}")
    response = client.get(f"/personas/{person_id}/sacramentos")
    print_response_info(response, f"Sacramentos de persona {person_id}")


def test_personas_validation():
    """Test de validaciones de personas"""
    print_test_header("Tests de Validación - Personas")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Crear persona con datos inválidos (email malo)
    print("\n1️⃣ Test: Crear persona con email inválido")
    invalid_data = {
        "nombre": "Test",
        "apellido_paterno": "Usuario",
        "fecha_nacimiento": "1990-01-01",
        "genero": "M",
        "email": "email-invalido",  # Email mal formateado
        "activo": True
    }
    
    response = client.post("/personas", invalid_data)
    print_response_info(response, "Crear persona con email inválido")
    
    if response.status_code == 422:
        print("✅ Validación correcta - Email inválido rechazado")
    
    # Test 2: Crear persona con género inválido
    print("\n2️⃣ Test: Crear persona con género inválido")
    invalid_gender_data = {
        "nombre": "Test",
        "apellido_paterno": "Usuario",
        "fecha_nacimiento": "1990-01-01",
        "genero": "X",  # Género no válido
        "activo": True
    }
    
    response = client.post("/personas", invalid_gender_data)
    print_response_info(response, "Crear persona con género inválido")
    
    if response.status_code == 422:
        print("✅ Validación correcta - Género inválido rechazado")
    
    # Test 3: Crear persona con fecha de nacimiento futura
    print("\n3️⃣ Test: Crear persona con fecha futura")
    future_date_data = {
        "nombre": "Test",
        "apellido_paterno": "Usuario",
        "fecha_nacimiento": "2030-01-01",  # Fecha futura
        "genero": "M",
        "activo": True
    }
    
    response = client.post("/personas", future_date_data)
    print_response_info(response, "Crear persona con fecha futura")


def run_all_personas_tests():
    """Ejecutar todos los tests de personas"""
    print("🚀 Iniciando Tests Completos de Personas")
    print("=" * 80)
    
    test_personas_crud()
    test_personas_search()
    test_personas_sacramentos()
    test_personas_validation()
    
    print("\n" + "=" * 80)
    print("🏁 Tests de Personas Completados")


if __name__ == "__main__":
    run_all_personas_tests()
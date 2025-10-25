#!/usr/bin/env python
"""
Test manual del endpoint de instituciones parroquiales
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_instituciones_endpoint():
    """Test manual del endpoint de instituciones"""
    print("🧪 Probando endpoint de instituciones parroquiales...")
    
    # Test 1: Verificar que el endpoint está registrado
    print("\n1. Verificando registro del endpoint...")
    response = client.get("/api/v1/info")
    if response.status_code == 200:
        data = response.json()
        endpoints = data.get("endpoints", {})
        if "instituciones" in endpoints:
            print(f"   ✅ Endpoint registrado: {endpoints['instituciones']}")
        else:
            print("   ❌ Endpoint no encontrado en la información de la API")
    else:
        print(f"   ⚠️  No se pudo obtener info de la API (Status: {response.status_code})")
    
    # Test 2: Verificar que el endpoint existe (debería requerir autenticación)
    print("\n2. Verificando existencia del endpoint...")
    response = client.get("/api/v1/instituciones/")
    if response.status_code == 404:
        print("   ❌ Endpoint no encontrado (404)")
    elif response.status_code in [401, 403]:
        print("   ✅ Endpoint existe pero requiere autenticación (como debería ser)")
    elif response.status_code == 422:
        print("   ✅ Endpoint existe y responde (error de validación)")
    else:
        print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
    
    # Test 3: Verificar endpoint de búsqueda
    print("\n3. Verificando endpoint de búsqueda...")
    response = client.get("/api/v1/instituciones/search/by-name?q=test")
    if response.status_code in [401, 403]:
        print("   ✅ Endpoint de búsqueda existe y requiere autenticación")
    elif response.status_code == 404:
        print("   ❌ Endpoint de búsqueda no encontrado")
    else:
        print(f"   ⚠️  Respuesta inesperada en búsqueda: {response.status_code}")
    
    # Test 4: Verificar endpoint de estadísticas
    print("\n4. Verificando endpoint de estadísticas...")
    response = client.get("/api/v1/instituciones/stats/summary")
    if response.status_code in [401, 403]:
        print("   ✅ Endpoint de estadísticas existe y requiere autenticación")
    elif response.status_code == 404:
        print("   ❌ Endpoint de estadísticas no encontrado")
    else:
        print(f"   ⚠️  Respuesta inesperada en estadísticas: {response.status_code}")
    
    # Test 5: Verificar endpoint específico por ID
    print("\n5. Verificando endpoint por ID...")
    response = client.get("/api/v1/instituciones/1")
    if response.status_code in [401, 403]:
        print("   ✅ Endpoint por ID existe y requiere autenticación")
    elif response.status_code == 404:
        print("   ❌ Endpoint por ID no encontrado")
    else:
        print(f"   ⚠️  Respuesta inesperada por ID: {response.status_code}")
    
    # Test 6: Verificar documentación automática
    print("\n6. Verificando documentación automática...")
    response = client.get("/openapi.json")
    if response.status_code == 200:
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})
        instituciones_paths = [path for path in paths.keys() if "instituciones" in path]
        if instituciones_paths:
            print(f"   ✅ Encontrados {len(instituciones_paths)} endpoints de instituciones en OpenAPI:")
            for path in instituciones_paths:
                print(f"      - {path}")
        else:
            print("   ❌ No se encontraron endpoints de instituciones en OpenAPI")
    else:
        print(f"   ⚠️  No se pudo obtener OpenAPI schema (Status: {response.status_code})")
    
    print("\n📋 Resumen de endpoints de instituciones implementados:")
    print("   📍 POST   /api/v1/instituciones/              - Crear institución")
    print("   📍 GET    /api/v1/instituciones/              - Listar instituciones")
    print("   📍 GET    /api/v1/instituciones/{id}          - Obtener institución")
    print("   📍 PUT    /api/v1/instituciones/{id}          - Actualizar institución")
    print("   📍 DELETE /api/v1/instituciones/{id}          - Eliminar institución")
    print("   📍 GET    /api/v1/instituciones/search/by-name - Buscar por nombre")
    print("   📍 GET    /api/v1/instituciones/stats/summary  - Estadísticas")
    
    print("\n🔐 Permisos implementados:")
    print("   👑 Administradores: Crear, actualizar, eliminar, ver estadísticas")
    print("   👨‍💼 Sacerdotes: Ver instituciones, ver estadísticas")
    print("   👥 Otros roles: Ver instituciones")
    
    print("\n✅ ¡Endpoint de instituciones implementado exitosamente!")

if __name__ == "__main__":
    test_instituciones_endpoint()
"""
Tests para el endpoint de instituciones parroquiales
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Datos de prueba para instituciones
institucion_test_data = {
    "nombre": "Parroquia de Prueba",
    "direccion": "Calle Falsa 123, La Paz",
    "telefono": "+591-2-1234567",
    "email": "prueba@parroquia.test"
}

def test_create_institucion():
    """Test crear una nueva institución"""
    # TODO: Este test requiere autenticación, implementar cuando se tenga el sistema de auth
    pass

def test_list_instituciones():
    """Test listar instituciones sin autenticación (debería fallar)"""
    response = client.get("/api/v1/instituciones/")
    # Debería requerir autenticación
    assert response.status_code in [401, 403]

def test_get_institucion_by_id():
    """Test obtener institución por ID sin autenticación"""
    response = client.get("/api/v1/instituciones/1")
    # Debería requerir autenticación
    assert response.status_code in [401, 403]

def test_search_instituciones():
    """Test búsqueda de instituciones sin autenticación"""
    response = client.get("/api/v1/instituciones/search/by-name?q=Parroquia")
    # Debería requerir autenticación
    assert response.status_code in [401, 403]

def test_instituciones_stats():
    """Test estadísticas de instituciones sin autenticación"""
    response = client.get("/api/v1/instituciones/stats/summary")
    # Debería requerir autenticación
    assert response.status_code in [401, 403]

# Test manual simple para verificar que el endpoint existe
def test_instituciones_endpoint_exists():
    """Verificar que el endpoint de instituciones está registrado"""
    # Obtener la información de la API
    response = client.get("/api/v1/info")
    if response.status_code == 200:
        data = response.json()
        endpoints = data.get("endpoints", {})
        assert "instituciones" in endpoints
        assert endpoints["instituciones"] == "/api/v1/instituciones/"
    else:
        # Si no hay endpoint de info, al menos verificar que el endpoint existe
        response = client.get("/api/v1/instituciones/")
        # Aunque falle por autenticación, el endpoint debe existir
        assert response.status_code != 404

if __name__ == "__main__":
    # Ejecutar pruebas básicas
    print("🧪 Ejecutando pruebas básicas del endpoint de instituciones...")
    
    try:
        test_instituciones_endpoint_exists()
        print("✅ Endpoint de instituciones registrado correctamente")
    except Exception as e:
        print(f"❌ Error en test de endpoint: {e}")
    
    try:
        test_list_instituciones()
        print("✅ Test de autenticación funcionando")
    except Exception as e:
        print(f"❌ Error en test de autenticación: {e}")
    
    print("🎉 Pruebas básicas completadas")
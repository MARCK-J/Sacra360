"""
Script de prueba para verificar el funcionamiento del OCR Service
"""

import requests
import json

# Configuración del servicio
BASE_URL = "http://localhost:8003"
API_URL = f"{BASE_URL}/api/v1"

def test_health_check():
    """Test del health check"""
    print("1. Testing health check...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_service_status():
    """Test del status del servicio"""
    print("\n2. Testing service status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Service status OK")
            data = response.json()
            print(f"Service: {data.get('service')}")
            print(f"Version: {data.get('version')}")
            print(f"Port: {data.get('port')}")
        else:
            print(f"❌ Service status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Service status error: {e}")

def test_ocr_endpoint():
    """Test del endpoint de OCR (sin imagen real)"""
    print("\n3. Testing OCR endpoint structure...")
    try:
        response = requests.get(f"{API_URL}/ocr/test")
        if response.status_code == 200:
            print("✅ OCR endpoint test OK")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ OCR endpoint test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OCR endpoint error: {e}")

def test_api_docs():
    """Test de documentación de API"""
    print("\n4. Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API docs available")
            print(f"Docs URL: {BASE_URL}/docs")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 TESTING OCR SERVICE - SACRA360")
    print("=" * 50)
    
    test_health_check()
    test_service_status()
    test_ocr_endpoint()
    test_api_docs()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas!")
    print(f"💡 Para realizar pruebas completas, visita: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
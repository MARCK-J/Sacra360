"""
Script de cliente para probar el endpoint de HTR
"""

import requests
import sys
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8004"
TEST_IMAGE = "test_image.jpg"  # Reemplazar con una imagen de prueba real

def test_health():
    """Test del health check"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_status():
    """Test del status endpoint"""
    print("\n🔍 Testing status endpoint...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_process_htr(image_path: str, documento_id: int = 1):
    """Test del endpoint de procesamiento HTR"""
    print(f"\n🔍 Testing HTR processing with image: {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Imagen {image_path} no encontrada")
        return False
    
    with open(image_path, 'rb') as img_file:
        files = {'file': img_file}
        data = {
            'documento_id': documento_id,
            'tipo_sacramento': 'bautizo'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/htr/procesar",
            files=files,
            data=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

def main():
    """Función principal"""
    print("=" * 60)
    print("HTR Service - Test Client")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("❌ Health check failed!")
        return
    
    # Test status
    if not test_status():
        print("❌ Status check failed!")
        return
    
    # Test HTR processing si hay imagen disponible
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_process_htr(image_path)
    else:
        print("\n⚠️  Para probar el procesamiento HTR, pasa la ruta de una imagen:")
        print(f"   python test_endpoint_client.py <ruta_imagen>")
    
    print("\n✅ Tests completados!")

if __name__ == "__main__":
    main()

"""
Script de prueba simplificado para OCR Service
Hace una prueba directa sin depender de imports complejos
"""

import requests
import json
import os

def test_ocr_simple():
    """Prueba simple del OCR service"""
    
    print("🧪 PRUEBA SIMPLE DEL OCR SERVICE")
    print("=" * 50)
    
    # Configuración
    url = "http://localhost:8003/api/v1/ocr/procesar"
    image_path = "test_registro_confirmacion.jpg"
    
    # Verificar que existe la imagen
    if not os.path.exists(image_path):
        print("❌ No se encuentra la imagen de prueba")
        print("💡 Ejecuta: python crear_imagen_test.py")
        return
    
    print(f"📷 Usando imagen: {image_path}")
    
    try:
        # Preparar datos
        with open(image_path, 'rb') as f:
            files = {
                'archivo': ('test.jpg', f, 'image/jpeg')
            }
            data = {
                'libros_id': 1,
                'tipo_sacramento': 2,
                'guardar_en_bd': False  # False para no depender de BD
            }
            
            print("🚀 Enviando imagen al OCR...")
            response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            resultado = response.json()
            print("✅ ÉXITO!")
            print(f"📊 Tuplas encontradas: {resultado.get('total_tuplas', 0)}")
            print(f"📊 Calidad general: {resultado.get('calidad_general', 0):.2f}")
            
            # Mostrar algunas tuplas
            tuplas = resultado.get('tuplas', [])
            if tuplas:
                print("\n📋 PRIMERAS TUPLAS EXTRAÍDAS:")
                for i, tupla in enumerate(tuplas[:2], 1):
                    confirmando = tupla.get('confirmando', {}).get('valor_extraido', 'N/A')
                    fecha_nac = tupla.get('fecha_nacimiento', {}).get('valor_extraido', 'N/A') 
                    print(f"   {i}. {confirmando} - Nac: {fecha_nac}")
            
            # Guardar resultado
            with open("resultado_simple.json", 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print("\n💾 Resultado guardado en: resultado_simple.json")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Detalle: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servicio OCR")
        print("💡 Asegúrate de que esté ejecutándose en http://localhost:8003")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health():
    """Probar health check"""
    try:
        response = requests.get("http://localhost:8003/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except:
        print("❌ Servicio no disponible")
        return False

if __name__ == "__main__":
    print("🔍 VERIFICANDO SERVICIO OCR...")
    
    if test_health():
        test_ocr_simple()
    else:
        print("\n💡 Para iniciar el servicio:")
        print("   cd OCR-service")
        print("   python -m uvicorn app.main:app --host localhost --port 8003")
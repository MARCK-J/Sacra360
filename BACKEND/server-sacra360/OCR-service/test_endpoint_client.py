"""
Script para probar el endpoint OCR con Tabla1.pdf
"""

import requests
import json
import time

# Configuración
url = "http://localhost:8003/api/v1/ocr/procesar"
file_path = r"d:\MARCK-J\TRABAJOS\GITHUB\Sacra360\BACKEND\Images\Tabla1.pdf"

print("=" * 70)
print("🧪 TEST ENDPOINT OCR V2 - Tabla1.pdf")
print("=" * 70)
print(f"📍 URL: {url}")
print(f"📄 Archivo: {file_path}")
print()

# Abrir archivo
with open(file_path, 'rb') as f:
    files = {'file': ('Tabla1.pdf', f, 'application/pdf')}
    
    print("📤 Enviando archivo...")
    inicio = time.time()
    
    try:
        response = requests.post(url, files=files, timeout=600)  # 10 min timeout
        
        tiempo = time.time() - inicio
        print(f"⏱️  Tiempo: {tiempo:.2f} segundos")
        print()
        
        print(f"📊 Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            resultado = response.json()
            print("✅ RESPUESTA EXITOSA")
            print("=" * 70)
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            print("=" * 70)
            
            # Verificar resultado
            if 'documento_id' in resultado:
                print()
                print(f"📝 Documento ID: {resultado['documento_id']}")
                print(f"📊 Total tuplas: {resultado['total_tuplas']}")
                print(f"☁️  Archivo URL: {resultado.get('archivo_url', 'N/A')}")
        else:
            print("❌ ERROR EN RESPUESTA")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - El procesamiento tardó más de 10 minutos")
    except Exception as e:
        print(f"❌ ERROR: {e}")

print()
print("=" * 70)
input("Presiona Enter para salir...")

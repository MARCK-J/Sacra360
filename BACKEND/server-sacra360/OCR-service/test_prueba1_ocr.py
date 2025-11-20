#!/usr/bin/env python3
"""
Script para probar el microservicio OCR con la imagen Prueba1.png
Muestra el resultado JSON tal como lo hace el algoritmo en OCR.py
"""

import requests
import json
import sys
from pathlib import Path

def test_ocr_with_prueba1():
    """
    Prueba el microservicio OCR con la imagen Prueba1.png
    """
    
    # Configuración del servicio
    base_url = "http://localhost:8003"
    image_path = Path("Prueba1.png")
    
    if not image_path.exists():
        print(f"❌ Error: No se encontró la imagen {image_path}")
        return False
    
    print("🔄 Iniciando prueba del OCR con Prueba1.png...")
    print(f"📁 Archivo: {image_path.absolute()}")
    print(f"🌐 Servicio: {base_url}")
    print("=" * 60)
    
    try:
        # Verificar que el servicio esté disponible
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"❌ Error: Servicio no disponible (status: {response.status_code})")
            return False
        
        print("✅ Servicio OCR disponible")
        print(f"ℹ️  Info del servicio: {response.json()}")
        print("-" * 60)
        
        # Preparar el archivo para upload
        with open(image_path, 'rb') as f:
            files = {
                'archivo': (image_path.name, f, 'image/png')
            }
            
            data = {
                'libros_id': 1,
                'tipo_sacramento': 2,
                'extract_fields': True
            }
            
            print("🔄 Enviando imagen para procesamiento OCR...")
            
            # Enviar solicitud de OCR
            response = requests.post(
                f"{base_url}/api/v1/ocr/procesar",
                files=files,
                data=data,
                timeout=300  # 5 minutos de timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ Procesamiento OCR completado exitosamente!")
                print("=" * 60)
                print("📊 RESULTADO JSON (igual que OCR.py):")
                print("=" * 60)
                
                # Mostrar el JSON formateado y bonito
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                print("=" * 60)
                print("📈 RESUMEN DEL PROCESAMIENTO:")
                print("=" * 60)
                
                # Extraer información clave del resultado
                if 'documento_digitalizado' in result:
                    doc = result['documento_digitalizado']
                    print(f"📄 ID Documento: {doc.get('id_documento', 'N/A')}")
                    print(f"📚 Libros ID: {doc.get('libros_id', 'N/A')}")
                    print(f"⛪ Tipo Sacramento: {doc.get('tipo_sacramento', 'N/A')}")
                    print(f"🤖 Modelo: {doc.get('modelo_fuente', 'N/A')}")
                    print(f"📊 Confianza General: {doc.get('confianza', 'N/A')}")
                
                if 'campos_extraidos' in result:
                    campos = result['campos_extraidos']
                    print(f"🔍 Campos Extraídos: {len(campos)} campos")
                    
                    for i, campo in enumerate(campos, 1):
                        print(f"   {i}. {campo.get('campo', 'N/A')}: {campo.get('valor_extraido', 'N/A')} (confianza: {campo.get('confianza', 'N/A')})")
                
                if 'ocr_texto' in result.get('documento_digitalizado', {}):
                    try:
                        ocr_data = json.loads(result['documento_digitalizado']['ocr_texto'])
                        if 'tuplas' in ocr_data:
                            print(f"📝 Tuplas Procesadas: {len(ocr_data['tuplas'])} registros")
                    except:
                        pass
                
                print("\n🎉 ¡Prueba completada exitosamente!")
                return True
                
            else:
                print(f"❌ Error en el procesamiento OCR:")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("⏰ Error: Timeout en el procesamiento (más de 5 minutos)")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Error: No se puede conectar al servicio OCR")
        print("   Asegúrate de que Docker esté ejecutando los contenedores")
        return False
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_ocr_with_prueba1()
    sys.exit(0 if success else 1)
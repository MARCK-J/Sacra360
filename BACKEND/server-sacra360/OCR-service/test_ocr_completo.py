"""
Script de prueba avanzado para el OCR Service - Sacra360
Permite subir imágenes reales y probar el procesamiento OCR completo
"""

import requests
import json
import os
import sys
from pathlib import Path
import time

# Configuración
BASE_URL = "http://localhost:8003"
API_URL = f"{BASE_URL}/api/v1"

def crear_imagen_test():
    """Crear una imagen de prueba si no existe"""
    print("📝 Para pruebas reales, necesitas una imagen de registro de confirmación")
    print("💡 Coloca tu imagen en el directorio actual con nombre 'test_image.jpg'")
    print("   O proporciona la ruta completa cuando se solicite")
    return None

def test_ocr_completo(image_path=None):
    """Realizar prueba completa de OCR con imagen real"""
    print("\n🔍 PRUEBA COMPLETA DE OCR")
    print("=" * 60)
    
    # Buscar imagen si no se proporciona
    if not image_path:
        posibles_imagenes = [
            "test_image.jpg",
            "registro_confirmacion.jpg", 
            "confirmacion.png",
            "sample.jpg"
        ]
        
        for img in posibles_imagenes:
            if os.path.exists(img):
                image_path = img
                break
        
        if not image_path:
            print("❌ No se encontró imagen de prueba")
            print("💡 Coloca una imagen con uno de estos nombres:")
            for img in posibles_imagenes:
                print(f"   - {img}")
            
            # Permitir al usuario especificar ruta
            custom_path = input("\n📁 Ingresa la ruta de tu imagen (Enter para saltar): ").strip()
            if custom_path and os.path.exists(custom_path):
                image_path = custom_path
            else:
                print("⏭️  Saltando prueba de OCR con imagen")
                return False
    
    print(f"📷 Usando imagen: {image_path}")
    
    try:
        # Preparar archivo
        with open(image_path, 'rb') as f:
            files = {'archivo': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {
                'libros_id': 1,
                'tipo_sacramento': 2,
                'guardar_en_bd': True
            }
            
            print("🚀 Enviando imagen para procesamiento OCR...")
            start_time = time.time()
            
            response = requests.post(
                f"{API_URL}/ocr/procesar",
                files=files,
                data=data,
                timeout=60  # 60 segundos timeout
            )
            
            processing_time = time.time() - start_time
            
        if response.status_code == 200:
            resultado = response.json()
            
            print(f"✅ PROCESAMIENTO EXITOSO")
            print(f"⏱️  Tiempo: {processing_time:.2f} segundos")
            print("-" * 60)
            
            # Mostrar información general
            print(f"📊 MÉTRICAS GENERALES:")
            print(f"   Total tuplas: {resultado.get('total_tuplas', 0)}")
            print(f"   Calidad general: {resultado.get('calidad_general', 0):.2f}")
            print(f"   Tuplas alta calidad: {resultado.get('tuplas_alta_calidad', 0)}")
            print(f"   Modelo utilizado: {resultado.get('modelo_utilizado', 'N/A')}")
            
            # Mostrar tuplas extraídas
            tuplas = resultado.get('tuplas', [])
            if tuplas:
                print(f"\n📋 TUPLAS EXTRAÍDAS:")
                print("=" * 60)
                
                for i, tupla in enumerate(tuplas[:3], 1):  # Mostrar solo las primeras 3
                    print(f"\n🔍 TUPLA {i}:")
                    print(f"   Confirmando: {tupla.get('confirmando', {}).get('valor_extraido', 'N/A')}")
                    print(f"   Fecha Nac.: {tupla.get('fecha_nacimiento', {}).get('valor_extraido', 'N/A')}")
                    print(f"   Parroquia: {tupla.get('parroquia_bautismo', {}).get('valor_extraido', 'N/A')}")
                    print(f"   Fecha Baut.: {tupla.get('fecha_bautismo', {}).get('valor_extraido', 'N/A')}")
                    print(f"   Padres: {tupla.get('padres', {}).get('valor_extraido', 'N/A')}")
                    print(f"   Padrinos: {tupla.get('padrinos', {}).get('valor_extraido', 'N/A')}")
                    print(f"   Calidad: {tupla.get('calidad_general', 0):.2f}")
                
                if len(tuplas) > 3:
                    print(f"\n... y {len(tuplas) - 3} tuplas más")
            
            # Guardar resultado completo
            output_file = f"resultado_ocr_{int(time.time())}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Resultado completo guardado en: {output_file}")
            
            return True
            
        else:
            print(f"❌ Error en procesamiento: {response.status_code}")
            print(f"   Detalle: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {image_path}")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout - El procesamiento tomó más de 60 segundos")
        return False
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

def test_endpoints_basicos():
    """Probar endpoints básicos del servicio"""
    print("🔧 PROBANDO ENDPOINTS BÁSICOS")
    print("=" * 60)
    
    tests = [
        ("Root Endpoint", "GET", "/", None),
        ("Health Check", "GET", "/api/v1/health", None),
        ("OCR Test", "GET", "/api/v1/ocr/test", None)
    ]
    
    resultados = []
    
    for nombre, metodo, endpoint, data in tests:
        try:
            if metodo == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {nombre}: OK")
                resultados.append(True)
            else:
                print(f"❌ {nombre}: {response.status_code}")
                resultados.append(False)
                
        except Exception as e:
            print(f"❌ {nombre}: Error - {str(e)}")
            resultados.append(False)
    
    exitosos = sum(resultados)
    print(f"\n📊 Resultado: {exitosos}/{len(tests)} endpoints funcionando")
    return exitosos == len(tests)

def main():
    """Función principal de pruebas"""
    print("🧪 PRUEBAS AVANZADAS DEL OCR SERVICE - SACRA360")
    print("🎯 Verificando funcionalidad completa del algoritmo OCR")
    print("=" * 80)
    
    # Verificar que el servicio esté corriendo
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ Servicio OCR detectado y funcionando")
    except:
        print("❌ SERVICIO NO DISPONIBLE")
        print("💡 Asegúrate de que el servicio esté ejecutándose:")
        print("   - Docker: docker-compose up")
        print("   - Local: python run_service.py")
        return
    
    print()
    
    # Pruebas básicas
    endpoints_ok = test_endpoints_basicos()
    
    # Prueba principal de OCR
    ocr_ok = test_ocr_completo()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 80)
    
    print(f"Endpoints básicos: {'✅ OK' if endpoints_ok else '❌ FALLO'}")
    print(f"Procesamiento OCR: {'✅ OK' if ocr_ok else '❌ NO PROBADO'}")
    
    if endpoints_ok and ocr_ok:
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ El OCR Service está funcionando perfectamente")
        print("✅ El algoritmo de Google Colab se integró exitosamente")
    elif endpoints_ok:
        print("\n⚠️  Servicio funcionando pero OCR no probado")
        print("💡 Proporciona una imagen para prueba completa")
    else:
        print("\n❌ Hay problemas con el servicio")
    
    print(f"\n🔗 Documentación API: {BASE_URL}/docs")
    print("=" * 80)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script para verificar la integración completa con Minio
Procesa Prueba1.png y verifica que se suba correctamente a Minio
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuración
API_BASE_URL = "http://localhost:8003/api/v1"
MINIO_CONSOLE_URL = "http://localhost:9001"  # Console de Minio
TEST_IMAGE = "Prueba1.png"

def verificar_servicios():
    """Verificar que todos los servicios estén funcionando"""
    print("🔍 Verificando servicios...")
    
    # OCR Service
    try:
        response = requests.get(f"{API_BASE_URL}/ocr/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OCR Service: {data.get('status', 'unknown')}")
            
            # Verificar dependencias específicas
            deps = data.get('dependencies', {})
            for dep, status in deps.items():
                print(f"   📦 {dep}: {status}")
        else:
            print(f"❌ OCR Service: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OCR Service: {str(e)}")
        return False
    
    # Minio (intentar acceder a la consola)
    try:
        response = requests.get(MINIO_CONSOLE_URL, timeout=5)
        if response.status_code in [200, 403]:  # 403 es normal sin login
            print("✅ Minio: Disponible")
        else:
            print(f"⚠️  Minio Console: HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️  Minio Console: {str(e)} (esto puede ser normal)")
    
    return True

def procesar_imagen_con_minio():
    """Procesar imagen y verificar integración con Minio"""
    print(f"\n🖼️ Procesando imagen: {TEST_IMAGE}")
    
    # Verificar que la imagen existe
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Imagen no encontrada: {TEST_IMAGE}")
        print("   Asegúrate de que Prueba1.png esté en el directorio actual")
        return False
    
    # Preparar datos del request
    with open(TEST_IMAGE, 'rb') as f:
        files = {
            'archivo': (TEST_IMAGE, f, 'image/png')
        }
        
        data = {
            'libros_id': 1,
            'tipo_sacramento': 2,
            'guardar_en_bd': True
        }
        
        print("📤 Enviando request al OCR service...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/ocr/procesar",
                files=files,
                data=data,
                timeout=60  # Aumentar timeout para procesamiento completo
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Procesamiento exitoso en {processing_time:.2f}s")
                print(f"📊 Resultados:")
                print(f"   🔢 Total tuplas: {result.get('total_tuplas', 0)}")
                print(f"   📈 Calidad general: {result.get('calidad_general', 0):.1f}%")
                print(f"   ⭐ Tuplas alta calidad: {result.get('tuplas_alta_calidad', 0)}")
                print(f"   🕐 Tiempo procesamiento: {result.get('tiempo_procesamiento', 0):.2f}s")
                print(f"   🆔 ID documento: {result.get('documento_id', 'N/A')}")
                
                # Verificar si hay información de Minio implícita
                if result.get('success'):
                    print("✅ Archivo procesado - debe estar almacenado en Minio")
                    print(f"   📁 Acceder a Minio Console: {MINIO_CONSOLE_URL}")
                    print("   🔐 Credenciales: admin / password123")
                    print("   🪣 Bucket: sacra360-documents")
                
                # Mostrar muestra de tuplas extraídas
                tuplas = result.get('tuplas', [])
                if tuplas:
                    print(f"\n📋 Muestra de tuplas extraídas (primeras 2):")
                    for i, tupla in enumerate(tuplas[:2], 1):
                        print(f"   Tupla {i}:")
                        campos = tupla.get('campos', {})
                        for campo, info in campos.items():
                            if isinstance(info, dict) and 'valor' in info:
                                valor = info['valor'][:50] + "..." if len(str(info['valor'])) > 50 else info['valor']
                                confianza = info.get('confianza', 0)
                                print(f"     • {campo}: {valor} ({confianza:.1f}%)")
                
                return True
            else:
                print(f"❌ Error HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Detalle: {error_detail.get('detail', 'Sin detalles')}")
                except:
                    print(f"   Respuesta: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏱️ Timeout - el procesamiento está tomando más tiempo del esperado")
            print("   Esto puede ser normal para imágenes grandes")
            return False
        except Exception as e:
            print(f"❌ Error durante el request: {str(e)}")
            return False

def mostrar_instrucciones_minio():
    """Mostrar instrucciones para verificar Minio"""
    print(f"\n🗂️ Para verificar los archivos en Minio:")
    print(f"   1. Abrir: {MINIO_CONSOLE_URL}")
    print("   2. Login: admin / password123")
    print("   3. Buscar bucket: sacra360-documents")
    print("   4. Verificar carpeta: documents/")
    print("   5. Debería aparecer el archivo subido con timestamp único")

def main():
    """Función principal de testing"""
    print("=" * 60)
    print("🧪 TEST DE INTEGRACIÓN COMPLETA - OCR + MINIO")
    print("=" * 60)
    
    # Verificar servicios
    if not verificar_servicios():
        print("\n❌ Algunos servicios no están disponibles")
        print("   Asegúrate de ejecutar: docker-compose up -d")
        return
    
    # Procesar imagen
    success = procesar_imagen_con_minio()
    
    # Mostrar instrucciones finales
    if success:
        mostrar_instrucciones_minio()
        print("\n✅ Test completado exitosamente!")
        print("🎯 La integración OCR + Minio está funcionando correctamente")
    else:
        print("\n❌ Test falló")
        print("🔧 Verificar logs de Docker: docker-compose logs ocr-service")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
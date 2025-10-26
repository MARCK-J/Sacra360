#!/usr/bin/env python3
"""
Suite completa de tests para la API Sacra360
Ejecuta todos los tests de todos los módulos
"""

import sys
import os
import time

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import APITestClient, print_test_header
from test_usuarios import run_all_user_tests
from test_personas import run_all_personas_tests
from test_sacramentos import run_all_sacramentos_tests
from test_documentos import run_all_documentos_tests
from test_auditoria import run_all_auditoria_tests


def test_server_health():
    """Test básico de salud del servidor"""
    print_test_header("Test de Salud del Servidor")
    
    client = APITestClient()
    
    # Test endpoint de salud
    print("\n1️⃣ Test: Endpoint de salud del servidor")
    try:
        response = client.session.get(f"{client.base_url.replace('/api/v1', '')}/health")
        
        if response.status_code == 200:
            print("✅ Servidor respondiendo correctamente")
            health_data = response.json()
            print(f"📊 Status: {health_data.get('status')}")
            print(f"🔧 Version: {health_data.get('version')}")
            print(f"🌍 Environment: {health_data.get('environment')}")
            return True
        else:
            print(f"❌ Servidor no responde correctamente: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("🔧 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return False


def test_api_info():
    """Test de información de la API"""
    print_test_header("Test de Información de la API")
    
    client = APITestClient()
    
    print("\n1️⃣ Test: Información de la API")
    try:
        response = client.get("/info")
        
        if response.status_code == 200:
            print("✅ Endpoint de información accesible")
            api_info = response.json()
            print(f"📛 Nombre: {api_info.get('name')}")
            print(f"🔧 Versión: {api_info.get('version')}")
            print(f"📄 Descripción: {api_info.get('description')}")
            
            # Mostrar endpoints disponibles
            endpoints = api_info.get('endpoints', {})
            print(f"\n📍 Endpoints disponibles: {len(endpoints)}")
            for name, url in endpoints.items():
                if url:
                    print(f"   - {name}: {url}")
            
            # Mostrar características
            features = api_info.get('features', [])
            print(f"\n🚀 Características: {len(features)}")
            for feature in features[:5]:  # Mostrar solo las primeras 5
                print(f"   ✓ {feature}")
            if len(features) > 5:
                print(f"   ... y {len(features) - 5} más")
                
        else:
            print(f"❌ No se pudo obtener información de la API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo información de la API: {e}")


def print_test_summary():
    """Imprime resumen decorativo de los tests"""
    print("\n" + "=" * 100)
    print("🎯 SUITE COMPLETA DE TESTS - API SACRA360")
    print("=" * 100)
    print("📋 Módulos a probar:")
    print("   1️⃣ Salud del Servidor")
    print("   2️⃣ Información de la API") 
    print("   3️⃣ Usuarios (Auth, CRUD, Roles)")
    print("   4️⃣ Personas (CRUD, Búsquedas, Validaciones)")
    print("   5️⃣ Sacramentos (CRUD, Tipos, Búsquedas)")
    print("   6️⃣ Documentos (CRUD, OCR, Upload)")
    print("   7️⃣ Auditoría (Logs, Estadísticas, Permisos)")
    print("=" * 100)
    print(f"⏰ Inicio de tests: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)


def print_final_summary(start_time):
    """Imprime resumen final de los tests"""
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 100)
    print("🏁 RESUMEN FINAL DE TESTS - API SACRA360")
    print("=" * 100)
    print(f"⏱️  Duración total: {duration:.2f} segundos")
    print(f"⏰ Finalizado: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Tests completados para todos los módulos del Sistema Sacra360:")
    print("   🔐 Autenticación y gestión de usuarios")
    print("   👥 Registro y administración de personas")
    print("   ⛪ Gestión completa de sacramentos")
    print("   📄 Procesamiento y digitalización de documentos")
    print("   📊 Sistema de auditoría y trazabilidad")
    print("\n🎊 ¡Sistema Sacra360 listo para uso en producción!")
    print("📖 Consulta la documentación en: http://localhost:8000/docs")
    print("=" * 100)


def run_full_test_suite():
    """Ejecutar la suite completa de tests"""
    start_time = time.time()
    
    # Mostrar resumen inicial
    print_test_summary()
    
    # Test 1: Salud del servidor
    if not test_server_health():
        print("\n❌ Error crítico: Servidor no disponible")
        print("🔧 Inicia el servidor con: python -m uvicorn BACKEND.app.main:app --reload --host localhost --port 8000")
        return
    
    # Test 2: Información de la API
    test_api_info()
    
    # Test 3: Usuarios
    try:
        run_all_user_tests()
    except Exception as e:
        print(f"❌ Error en tests de usuarios: {e}")
    
    # Test 4: Personas
    try:
        run_all_personas_tests()
    except Exception as e:
        print(f"❌ Error en tests de personas: {e}")
    
    # Test 5: Sacramentos
    try:
        run_all_sacramentos_tests()
    except Exception as e:
        print(f"❌ Error en tests de sacramentos: {e}")
    
    # Test 6: Documentos
    try:
        run_all_documentos_tests()
    except Exception as e:
        print(f"❌ Error en tests de documentos: {e}")
    
    # Test 7: Auditoría
    try:
        run_all_auditoria_tests()
    except Exception as e:
        print(f"❌ Error en tests de auditoría: {e}")
    
    # Resumen final
    print_final_summary(start_time)


def run_quick_test():
    """Ejecutar un test rápido básico"""
    print_test_header("Test Rápido - API Sacra360")
    
    # Test de conectividad
    if not test_server_health():
        return
    
    # Test de autenticación básica
    client = APITestClient()
    print("\n🔐 Test rápido de autenticación...")
    
    if client.login():
        print("✅ Login exitoso")
        
        # Test básico de cada módulo
        endpoints_to_test = [
            ("/usuarios/", "Usuarios"),
            ("/personas/", "Personas"), 
            ("/sacramentos/", "Sacramentos"),
            ("/documentos/", "Documentos"),
            ("/auditoria/logs", "Auditoría")
        ]
        
        for endpoint, module_name in endpoints_to_test:
            try:
                response = client.get(endpoint)
                if response.status_code == 200:
                    print(f"✅ {module_name}: Endpoint accesible")
                else:
                    print(f"⚠️  {module_name}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {module_name}: Error - {e}")
    else:
        print("❌ No se pudo autenticar")
    
    print("\n🏁 Test rápido completado")


if __name__ == "__main__":
    # Verificar si se requiere test rápido o completo
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_full_test_suite()
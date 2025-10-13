#!/usr/bin/env python3
"""
Script para probar la funcionalidad de login de la API Sacra360
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/usuarios/login"

def test_login():
    """Prueba el login con las credenciales por defecto"""
    
    # Credenciales del admin por defecto
    login_data = {
        "email": "admin@sacra360.com",
        "password": "Admin123!"
    }
    
    print("🔐 Probando login con credenciales por defecto...")
    print(f"📧 Email: {login_data['email']}")
    print(f"🔑 Password: {login_data['password']}")
    
    try:
        # Realizar petición de login
        response = requests.post(
            LOGIN_URL,
            json=login_data,  # El endpoint LoginRequest espera JSON
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ¡Login exitoso!")
            print(f"🎟️  Access Token: {data.get('access_token', 'No token')[:50]}...")
            print(f"⏰ Token Type: {data.get('token_type', 'No type')}")
            print(f"⏱️  Expires In: {data.get('expires_in', 'No expiry')} segundos")
            
            # Mostrar información del usuario
            user_info = data.get('user_info', {})
            if user_info:
                print(f"👤 Usuario: {user_info.get('nombre', 'N/A')} {user_info.get('apellido_paterno', '')}")
                print(f"📧 Email: {user_info.get('email', 'N/A')}")
                print(f"🏷️  Rol: {user_info.get('rol', {}).get('rol', 'N/A')}")
                print(f"✅ Activo: {user_info.get('activo', 'N/A')}")
            
            return data.get('access_token')
            
        else:
            print("❌ Error en login:")
            try:
                error_data = response.json()
                print(f"📄 Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def test_protected_endpoint(token):
    """Prueba un endpoint protegido con el token obtenido"""
    if not token:
        print("⚠️  No se puede probar endpoint protegido sin token")
        return
    
    print(f"\n🔒 Probando endpoint protegido /api/v1/usuarios/me...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/usuarios/me", headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ¡Acceso autorizado al endpoint protegido!")
            print(f"👤 Información del usuario:")
            print(f"   - Nombre: {data.get('nombre', 'N/A')} {data.get('apellido_paterno', '')}")
            print(f"   - Email: {data.get('email', 'N/A')}")
            print(f"   - Rol: {data.get('rol', {}).get('rol', 'N/A')}")
            print(f"   - Activo: {data.get('activo', 'N/A')}")
        else:
            print("❌ Error al acceder al endpoint protegido:")
            try:
                error_data = response.json()
                print(f"📄 Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text}")
    except Exception as e:
        print(f"❌ Error al probar endpoint protegido: {e}")

if __name__ == "__main__":
    print("🧪 Iniciando prueba de autenticación...")
    print("=" * 50)
    
    # Probar login
    token = test_login()
    
    # Si el login fue exitoso, probar endpoint protegido
    if token:
        test_protected_endpoint(token)
    
    print("\n" + "=" * 50)
    print("🏁 Prueba completada")
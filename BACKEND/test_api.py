"""
Script de ejemplo para probar la API de Sacra360
"""

import requests
import json
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class APIClient:
    """Cliente para interactuar con la API de Sacra360"""
    
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def set_token(self, token: str):
        """Establece el token de autenticación"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra un nuevo usuario"""
        response = requests.post(
            f"{self.base_url}/users/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Inicia sesión y obtiene un token"""
        response = requests.post(
            f"{self.base_url}/users/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        result = self._handle_response(response)
        
        if "access_token" in result:
            self.set_token(result["access_token"])
        
        return result
    
    def get_current_user(self) -> Dict[str, Any]:
        """Obtiene información del usuario actual"""
        response = requests.get(
            f"{self.base_url}/users/me",
            headers=self.headers
        )
        return self._handle_response(response)
    
    def get_users(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Obtiene lista de usuarios"""
        response = requests.get(
            f"{self.base_url}/users/",
            params={"page": page, "limit": limit},
            headers=self.headers
        )
        return self._handle_response(response)
    
    def create_resource(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo recurso"""
        response = requests.post(
            f"{self.base_url}/resources/",
            json=resource_data,
            headers=self.headers
        )
        return self._handle_response(response)
    
    def get_resources(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Obtiene lista de recursos"""
        response = requests.get(
            f"{self.base_url}/resources/",
            params={"page": page, "limit": limit},
            headers=self.headers
        )
        return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Maneja la respuesta de la API"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"error": "Invalid JSON response"}
        
        if response.status_code >= 400:
            print(f"❌ Error {response.status_code}: {data}")
            return {"error": True, "status_code": response.status_code, "data": data}
        
        return data


def test_api():
    """Función principal para probar la API"""
    print("🚀 Probando la API de Sacra360...\n")
    
    client = APIClient()
    
    # 1. Verificar que la API esté funcionando
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API está funcionando")
            print(f"   {response.json()}\n")
        else:
            print("❌ API no está disponible")
            return
    except Exception as e:
        print(f"❌ No se puede conectar a la API: {e}")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return
    
    # 2. Registrar un usuario de prueba
    print("📝 Registrando usuario de prueba...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "full_name": "Usuario de Prueba"
    }
    
    register_result = client.register_user(user_data)
    if "error" in register_result:
        print("   ⚠️  El usuario probablemente ya existe, continuando...")
    else:
        print("   ✅ Usuario registrado exitosamente")
        print(f"   ID: {register_result.get('id')}, Username: {register_result.get('username')}\n")
    
    # 3. Iniciar sesión
    print("🔐 Iniciando sesión...")
    login_result = client.login("testuser", "TestPassword123!")
    if "error" in login_result:
        print("   ❌ Error al iniciar sesión")
        return
    
    print("   ✅ Sesión iniciada exitosamente")
    print(f"   Token obtenido (primeros 20 chars): {login_result.get('access_token', '')[:20]}...\n")
    
    # 4. Obtener información del usuario actual
    print("👤 Obteniendo información del usuario actual...")
    user_info = client.get_current_user()
    if "error" not in user_info:
        print("   ✅ Información obtenida:")
        print(f"   - ID: {user_info.get('id')}")
        print(f"   - Username: {user_info.get('username')}")
        print(f"   - Email: {user_info.get('email')}")
        print(f"   - Rol: {user_info.get('role')}\n")
    
    # 5. Crear un recurso de prueba
    print("📦 Creando recurso de prueba...")
    resource_data = {
        "name": "Recurso de Prueba",
        "description": "Este es un recurso creado para probar la API",
        "status": "active"
    }
    
    resource_result = client.create_resource(resource_data)
    if "error" not in resource_result:
        print("   ✅ Recurso creado exitosamente")
        print(f"   ID: {resource_result.get('id')}, Nombre: {resource_result.get('name')}\n")
    
    # 6. Obtener lista de recursos
    print("📋 Obteniendo lista de recursos...")
    resources_list = client.get_resources()
    if "error" not in resources_list:
        print(f"   ✅ Se encontraron {len(resources_list)} recursos:")
        for resource in resources_list:
            print(f"   - ID: {resource.get('id')}, Nombre: {resource.get('name')}")
    
    print("\n🎉 ¡Todas las pruebas completadas!")
    print("\n📚 Puedes ver la documentación interactiva en:")
    print(f"   - Swagger UI: {BASE_URL}/docs")
    print(f"   - ReDoc: {BASE_URL}/redoc")


if __name__ == "__main__":
    test_api()
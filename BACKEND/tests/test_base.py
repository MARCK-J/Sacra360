"""
Configuración base para tests de la API Sacra360
"""

import requests
import json
from typing import Optional, Dict, Any

class TestConfig:
    """Configuración base para todos los tests"""
    BASE_URL = "http://localhost:8000"
    API_VERSION = "/api/v1"
    
    # Credenciales de prueba
    ADMIN_EMAIL = "admin@sacra360.com"
    ADMIN_PASSWORD = "Admin123!"
    
    # Headers comunes
    JSON_HEADERS = {"Content-Type": "application/json"}
    

class APITestClient:
    """Cliente base para realizar tests de API"""
    
    def __init__(self):
        self.base_url = TestConfig.BASE_URL + TestConfig.API_VERSION
        self.token = None
        self.session = requests.Session()
    
    def login(self, email: str = TestConfig.ADMIN_EMAIL, password: str = TestConfig.ADMIN_PASSWORD) -> bool:
        """
        Realiza login y guarda el token para requests autenticados
        """
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/usuarios/login",
                json=login_data,
                headers=TestConfig.JSON_HEADERS
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                # Agregar token a headers de la sesión
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                return True
            else:
                print(f"❌ Error en login: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión en login: {e}")
            return False
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Realizar GET request"""
        return self.session.get(f"{self.base_url}{endpoint}", params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Realizar POST request"""
        return self.session.post(f"{self.base_url}{endpoint}", json=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Realizar PUT request"""
        return self.session.put(f"{self.base_url}{endpoint}", json=data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Realizar DELETE request"""
        return self.session.delete(f"{self.base_url}{endpoint}")


def print_test_header(test_name: str):
    """Imprime header decorativo para tests"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")


def print_response_info(response: requests.Response, test_description: str):
    """Imprime información detallada de la respuesta"""
    print(f"\n📋 {test_description}")
    print(f"📊 Status Code: {response.status_code}")
    print(f"⏱️  Response Time: {response.elapsed.total_seconds():.3f}s")
    
    if response.status_code == 200:
        print("✅ SUCCESS")
    elif response.status_code == 201:
        print("✅ CREATED")
    elif response.status_code in [400, 401, 403, 404, 422]:
        print("⚠️  CLIENT ERROR")
    elif response.status_code >= 500:
        print("❌ SERVER ERROR")
    
    try:
        if response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print(f"📄 Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"📄 Response Text: {response.text}")


def validate_schema_fields(data: Dict, required_fields: list, test_name: str) -> bool:
    """Valida que la respuesta contenga los campos requeridos"""
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        print(f"❌ {test_name} - Campos faltantes: {missing_fields}")
        return False
    else:
        print(f"✅ {test_name} - Todos los campos requeridos presentes")
        return True


def run_basic_crud_test(client: APITestClient, endpoint: str, create_data: Dict, 
                       update_data: Dict, required_fields: list, entity_name: str):
    """
    Ejecuta un test CRUD básico para cualquier entidad
    """
    print_test_header(f"Test CRUD Básico - {entity_name}")
    
    # 1. CREATE
    print(f"\n1️⃣ Creando {entity_name}...")
    response = client.post(endpoint, create_data)
    print_response_info(response, f"Crear {entity_name}")
    
    if response.status_code in [200, 201]:
        created_data = response.json()
        entity_id = created_data.get('id') or created_data.get('id_' + entity_name.lower())
        validate_schema_fields(created_data, required_fields, f"Crear {entity_name}")
    else:
        print(f"❌ No se pudo crear {entity_name}, saltando tests restantes")
        return
    
    # 2. READ (Get by ID)
    print(f"\n2️⃣ Obteniendo {entity_name} por ID...")
    response = client.get(f"{endpoint}/{entity_id}")
    print_response_info(response, f"Obtener {entity_name} por ID")
    
    if response.status_code == 200:
        validate_schema_fields(response.json(), required_fields, f"Obtener {entity_name}")
    
    # 3. READ (Get All)
    print(f"\n3️⃣ Obteniendo lista de {entity_name}s...")
    response = client.get(endpoint)
    print_response_info(response, f"Obtener lista de {entity_name}s")
    
    # 4. UPDATE
    print(f"\n4️⃣ Actualizando {entity_name}...")
    response = client.put(f"{endpoint}/{entity_id}", update_data)
    print_response_info(response, f"Actualizar {entity_name}")
    
    # 5. DELETE (si aplica)
    print(f"\n5️⃣ Eliminando {entity_name}...")
    response = client.delete(f"{endpoint}/{entity_id}")
    print_response_info(response, f"Eliminar {entity_name}")
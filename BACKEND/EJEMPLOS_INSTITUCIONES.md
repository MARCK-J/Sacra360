# Ejemplos de Uso - Endpoint Instituciones Parroquiales

## Configuración Inicial

```bash
# URL base de la API
export API_BASE="http://localhost:8000"

# Token de autenticación (obtener mediante login)
export TOKEN="tu_jwt_token_aqui"
```

## 1. Crear una Nueva Institución

```bash
curl -X POST "${API_BASE}/api/v1/instituciones/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "nombre": "Parroquia Nuestra Señora de La Paz",
    "direccion": "Calle Comercio 1234, La Paz, Bolivia",
    "telefono": "+591-2-2345678",
    "email": "contacto@parroquialapaz.bo"
  }'
```

**Respuesta esperada:**
```json
{
  "id_institucion": 3,
  "nombre": "Parroquia Nuestra Señora de La Paz",
  "direccion": "Calle Comercio 1234, La Paz, Bolivia",
  "telefono": "+591-2-2345678",
  "email": "contacto@parroquialapaz.bo"
}
```

## 2. Listar Todas las Instituciones

```bash
curl -X GET "${API_BASE}/api/v1/instituciones/" \
  -H "Authorization: Bearer ${TOKEN}"
```

## 3. Listar con Filtros y Paginación

```bash
# Filtrar por nombre y paginar
curl -X GET "${API_BASE}/api/v1/instituciones/?nombre=San&skip=0&limit=5" \
  -H "Authorization: Bearer ${TOKEN}"
```

## 4. Obtener una Institución Específica

```bash
curl -X GET "${API_BASE}/api/v1/instituciones/1" \
  -H "Authorization: Bearer ${TOKEN}"
```

## 5. Buscar Instituciones por Nombre

```bash
# Búsqueda para autocompletado
curl -X GET "${API_BASE}/api/v1/instituciones/search/by-name?q=Parroquia" \
  -H "Authorization: Bearer ${TOKEN}"
```

## 6. Actualizar una Institución

```bash
curl -X PUT "${API_BASE}/api/v1/instituciones/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "telefono": "+591-2-9999999",
    "email": "nuevo@email.bo"
  }'
```

## 7. Obtener Estadísticas

```bash
curl -X GET "${API_BASE}/api/v1/instituciones/stats/summary" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Respuesta esperada:**
```json
{
  "total_instituciones": 3,
  "con_telefono": 3,
  "con_email": 3,
  "porcentaje_contacto_completo": 100.0
}
```

## 8. Eliminar una Institución

```bash
curl -X DELETE "${API_BASE}/api/v1/instituciones/3" \
  -H "Authorization: Bearer ${TOKEN}"
```

## Ejemplos con Python - requests

```python
import requests

API_BASE = "http://localhost:8000"
TOKEN = "tu_jwt_token_aqui"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Crear institución
def crear_institucion():
    data = {
        "nombre": "Parroquia Santa María",
        "direccion": "Av. Bolivar 567, El Alto",
        "telefono": "+591-2-2876543",
        "email": "info@santamaria.bo"
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/instituciones/",
        json=data,
        headers=headers
    )
    
    if response.status_code == 201:
        print("✅ Institución creada:")
        print(response.json())
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

# Listar instituciones
def listar_instituciones():
    response = requests.get(
        f"{API_BASE}/api/v1/instituciones/",
        headers=headers
    )
    
    if response.status_code == 200:
        instituciones = response.json()
        print(f"📋 Encontradas {len(instituciones)} instituciones:")
        for inst in instituciones:
            print(f"  - {inst['nombre']} (ID: {inst['id_institucion']})")
    else:
        print(f"❌ Error: {response.status_code}")

# Buscar institución
def buscar_institucion(termino):
    response = requests.get(
        f"{API_BASE}/api/v1/instituciones/search/by-name",
        params={"q": termino},
        headers=headers
    )
    
    if response.status_code == 200:
        resultados = response.json()
        print(f"🔍 Resultados para '{termino}':")
        for inst in resultados:
            print(f"  - {inst['nombre']}")
    else:
        print(f"❌ Error: {response.status_code}")

# Obtener estadísticas
def obtener_estadisticas():
    response = requests.get(
        f"{API_BASE}/api/v1/instituciones/stats/summary",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print("📊 Estadísticas de Instituciones:")
        print(f"  Total: {stats['total_instituciones']}")
        print(f"  Con teléfono: {stats['con_telefono']}")
        print(f"  Con email: {stats['con_email']}")
        print(f"  Contacto completo: {stats['porcentaje_contacto_completo']}%")
    else:
        print(f"❌ Error: {response.status_code}")

# Ejecutar ejemplos
if __name__ == "__main__":
    crear_institucion()
    listar_instituciones()
    buscar_institucion("San")
    obtener_estadisticas()
```

## Integración con Frontend (JavaScript)

```javascript
class InstitucionesAPI {
    constructor(baseURL, token) {
        this.baseURL = baseURL;
        this.token = token;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    async crearInstitucion(data) {
        const response = await fetch(`${this.baseURL}/api/v1/instituciones/`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${await response.text()}`);
        }
        
        return await response.json();
    }

    async listarInstituciones(filtros = {}) {
        const params = new URLSearchParams(filtros);
        const response = await fetch(`${this.baseURL}/api/v1/instituciones/?${params}`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${await response.text()}`);
        }
        
        return await response.json();
    }

    async buscarPorNombre(termino) {
        const response = await fetch(
            `${this.baseURL}/api/v1/instituciones/search/by-name?q=${encodeURIComponent(termino)}`,
            { headers: this.headers }
        );
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${await response.text()}`);
        }
        
        return await response.json();
    }

    async obtenerEstadisticas() {
        const response = await fetch(`${this.baseURL}/api/v1/instituciones/stats/summary`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${await response.text()}`);
        }
        
        return await response.json();
    }
}

// Uso del cliente
const instituciones = new InstitucionesAPI('http://localhost:8000', 'tu_token');

// Crear institución
instituciones.crearInstitucion({
    nombre: "Capilla San Pedro",
    direccion: "Zona Norte, El Alto",
    telefono: "+591-2-2567890"
}).then(result => {
    console.log('Institución creada:', result);
}).catch(error => {
    console.error('Error:', error);
});

// Autocompletado en tiempo real
async function autocompletarInstituciones(input) {
    if (input.length >= 2) {
        try {
            const resultados = await instituciones.buscarPorNombre(input);
            return resultados.map(inst => ({
                value: inst.id_institucion,
                label: inst.nombre
            }));
        } catch (error) {
            console.error('Error en autocompletado:', error);
            return [];
        }
    }
    return [];
}
```

## Casos de Uso Comunes

### 1. Autocompletado en Formularios de Sacramentos
```python
def get_instituciones_for_select():
    """Obtener lista para dropdown/select en formularios"""
    response = requests.get(f"{API_BASE}/api/v1/instituciones/", headers=headers)
    if response.status_code == 200:
        instituciones = response.json()
        return [
            {"value": inst["id_institucion"], "label": inst["nombre"]}
            for inst in instituciones
        ]
    return []
```

### 2. Validación de Institución Existente
```python
def validar_institucion_existe(institucion_id):
    """Verificar si una institución existe antes de crear un sacramento"""
    response = requests.get(
        f"{API_BASE}/api/v1/instituciones/{institucion_id}",
        headers=headers
    )
    return response.status_code == 200
```

### 3. Búsqueda Avanzada para Reportes
```python
def buscar_instituciones_por_zona(zona):
    """Buscar instituciones en una zona específica"""
    response = requests.get(
        f"{API_BASE}/api/v1/instituciones/",
        params={"nombre": zona},
        headers=headers
    )
    if response.status_code == 200:
        return [
            inst for inst in response.json()
            if zona.lower() in inst.get("direccion", "").lower()
        ]
    return []
```

## Manejo de Errores Comunes

```python
def manejar_errores_instituciones(response):
    """Función para manejar errores comunes de la API"""
    if response.status_code == 401:
        print("❌ Error: Token de autenticación inválido o expirado")
    elif response.status_code == 403:
        print("❌ Error: Sin permisos suficientes para esta operación")
    elif response.status_code == 404:
        print("❌ Error: Institución no encontrada")
    elif response.status_code == 400:
        error_data = response.json()
        print(f"❌ Error de validación: {error_data.get('detail', 'Datos inválidos')}")
    elif response.status_code == 422:
        errors = response.json().get('detail', [])
        print("❌ Errores de validación:")
        for error in errors:
            field = error.get('loc', [''])[1] if len(error.get('loc', [])) > 1 else 'campo'
            message = error.get('msg', 'error desconocido')
            print(f"  - {field}: {message}")
    else:
        print(f"❌ Error inesperado: {response.status_code}")
        print(response.text)
```
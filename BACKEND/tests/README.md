# Tests para API Sacra360

Esta carpeta contiene una suite completa de tests para todos los endpoints de la API Sacra360.

## 📁 Estructura de Tests

```
tests/
├── test_base.py           # Configuración base y utilidades comunes
├── test_usuarios.py       # Tests para módulo de usuarios
├── test_personas.py       # Tests para módulo de personas  
├── test_sacramentos.py    # Tests para módulo de sacramentos
├── test_documentos.py     # Tests para módulo de documentos
├── test_auditoria.py      # Tests para módulo de auditoría
├── run_all_tests.py       # Suite completa de tests
└── README.md             # Este archivo
```

## 🚀 Cómo ejecutar los tests

### Prerequisitos

1. **Servidor corriendo**: Asegúrate de que el servidor esté ejecutándose
   ```bash
   python -m uvicorn BACKEND.app.main:app --reload --host localhost --port 8000
   ```

2. **Dependencias**: Los tests requieren la librería `requests`
   ```bash
   pip install requests
   ```

### Ejecutar tests individuales

```bash
# Tests de usuarios (autenticación, CRUD, roles)
python BACKEND/tests/test_usuarios.py

# Tests de personas (registro, búsquedas, validaciones)  
python BACKEND/tests/test_personas.py

# Tests de sacramentos (CRUD, tipos específicos)
python BACKEND/tests/test_sacramentos.py

# Tests de documentos (upload, OCR, gestión)
python BACKEND/tests/test_documentos.py

# Tests de auditoría (logs, estadísticas)
python BACKEND/tests/test_auditoria.py
```

### Ejecutar suite completa

```bash
# Suite completa (todos los módulos)
python BACKEND/tests/run_all_tests.py

# Test rápido (verificación básica)
python BACKEND/tests/run_all_tests.py --quick
```

## 📋 Tipos de Tests Incluidos

### 🔐 Tests de Usuarios (`test_usuarios.py`)
- ✅ Autenticación (login/logout)
- ✅ Registro de nuevos usuarios
- ✅ Gestión de permisos por roles
- ✅ CRUD completo de usuarios
- ✅ Búsquedas y filtros
- ✅ Paginación
- ✅ Validaciones de datos

### 👥 Tests de Personas (`test_personas.py`)
- ✅ CRUD completo de personas
- ✅ Búsquedas por nombre, género, estado civil
- ✅ Filtros y paginación
- ✅ Relación con sacramentos
- ✅ Validaciones de datos (emails, fechas, géneros)

### ⛪ Tests de Sacramentos (`test_sacramentos.py`)
- ✅ CRUD de sacramentos generales
- ✅ Endpoints específicos por tipo:
  - Bautizos
  - Confirmaciones  
  - Matrimonios
  - Primeras Comuniones
- ✅ Búsquedas por fecha, sacerdote, persona
- ✅ Validaciones específicas por sacramento

### 📄 Tests de Documentos (`test_documentos.py`)
- ✅ CRUD de documentos
- ✅ Simulación de upload de archivos
- ✅ Procesamiento OCR
- ✅ Filtros por tipo de documento
- ✅ Documentos por persona
- ✅ Búsquedas y validaciones

### 📊 Tests de Auditoría (`test_auditoria.py`)
- ✅ Logs de auditoría
- ✅ Filtros por tabla, usuario, operación
- ✅ Búsquedas por rango de fechas
- ✅ Estadísticas del sistema
- ✅ Permisos de acceso

## 🔧 Configuración

Los tests utilizan la configuración definida en `test_base.py`:

```python
class TestConfig:
    BASE_URL = "http://localhost:8000"
    API_VERSION = "/api/v1"
    ADMIN_EMAIL = "admin@sacra360.com"
    ADMIN_PASSWORD = "Admin123!"
```

## 📊 Salida de Tests

Los tests proporcionan información detallada:

```
🧪 Tests de Autenticación - Usuarios
==================================================
1️⃣ Test: Login con credenciales correctas
✅ Login exitoso - Token obtenido

📋 Obtener información del usuario actual (/me)
📊 Status Code: 200
⏱️ Response Time: 0.245s
✅ SUCCESS
✅ Info usuario actual - Todos los campos requeridos presentes
```

## 🎯 Características de los Tests

### ✅ **Tests Comprehensivos**
- Cubren todos los endpoints de la API
- Incluyen casos de éxito y error
- Validan esquemas de respuesta
- Verifican códigos de estado HTTP

### 🔐 **Autenticación Automática**
- Login automático con credenciales admin
- Manejo de tokens JWT
- Tests de permisos por roles

### 📊 **Validación de Datos**
- Verificación de campos requeridos
- Validación de tipos de datos
- Tests de casos edge
- Manejo de errores

### 🚀 **Fácil Ejecución**
- Scripts independientes por módulo
- Suite completa unificada
- Modo rápido para verificaciones
- Salida clara y detallada

## 🛠️ Personalización

Para personalizar los tests:

1. **Modificar configuración** en `test_base.py`
2. **Agregar nuevos tests** siguiendo el patrón existente
3. **Customizar datos de prueba** en cada archivo de test
4. **Ajustar validaciones** según necesidades específicas

## 📈 Métricas de Cobertura

Los tests cubren:
- ✅ **27 endpoints** principales
- ✅ **5 módulos** completos
- ✅ **CRUD completo** para todas las entidades
- ✅ **Autenticación y autorización**
- ✅ **Validaciones de datos**
- ✅ **Manejo de errores**
- ✅ **Búsquedas y filtros**
- ✅ **Paginación**

## 🎊 ¡Listo para Producción!

Esta suite de tests garantiza que el Sistema Sacra360 esté completamente funcional y listo para su uso en un entorno parroquial real.
# 🧪 **Documents Service - Testing HTTP**

Esta carpeta contiene archivos `.http` para probar todos los endpoints del microservicio **Documents-service**.

## 📁 **Archivos de Testing**

### 1. **`personas.http`** - Testing completo de Personas API
- **32 requests** que cubren todos los endpoints de personas
- Incluye casos exitosos, validaciones y errores
- Prueba todos los filtros, paginación y búsquedas

### 2. **`libros.http`** - Testing completo de Libros API  
- **36 requests** que cubren todos los endpoints de libros
- Incluye casos exitosos, validaciones y errores
- Prueba todos los filtros, paginación y búsquedas

### 3. **`documents-service-complete-test.http`** - Flujo completo
- **36 requests** de testing integral
- Flujo completo desde creación hasta eliminación
- Ideal para testing rápido de funcionalidad completa

### 4. **`http-client.env.json`** - Configuración de entornos
- Variables para desarrollo y producción
- IDs y datos de ejemplo configurables

## 🚀 **Cómo usar los archivos HTTP**

### **Prerequisitos:**
1. **VS Code** con extensión **REST Client** instalada
2. **Docker** con el microservicio Documents-service ejecutándose
3. **PostgreSQL** conectado y funcionando

### **Pasos para testing:**

#### 1. **Levantar el microservicio:**
```powershell
cd d:\MARCK-J\TRABAJOS\GITHUB\Sacra360\BACKEND
docker-compose up -d postgres redis
docker-compose up --build documents-service
```

#### 2. **Verificar que esté funcionando:**
- Abrir: http://localhost:8002/health
- Debe responder: `{"status": "healthy", "service": "documents-service", ...}`

#### 3. **Testing con VS Code:**
- Abrir cualquier archivo `.http` en VS Code
- Hacer clic en **"Send Request"** sobre cada endpoint
- Ver las respuestas en el panel derecho

## 🎯 **Endpoints disponibles**

### **📋 Personas API (`/api/v1/personas/`)**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/personas/` | Crear persona |
| GET | `/personas/{id}` | Obtener por ID |
| GET | `/personas/` | Listar con filtros |
| PUT | `/personas/{id}` | Actualizar |
| DELETE | `/personas/{id}` | Soft delete |
| GET | `/personas/count/total` | Contar registros |
| GET | `/personas/search/by-name` | Buscar por nombre |
| GET | `/personas/filter/estado-civil/{estado}` | Filtrar por estado civil |

### **📚 Libros API (`/api/v1/libros/`)**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/libros/` | Crear libro |
| GET | `/libros/{id}` | Obtener por ID |
| GET | `/libros/` | Listar con filtros |
| PUT | `/libros/{id}` | Actualizar |
| DELETE | `/libros/{id}` | Soft delete |
| GET | `/libros/count/total` | Contar registros |
| GET | `/libros/search/by-name` | Buscar por nombre |
| GET | `/libros/filter/date-range` | Filtrar por fechas |

## ✅ **Testing Casos Cubiertos**

### **✅ Casos Exitosos:**
- Creación de registros válidos
- Consulta por ID existente
- Listado con paginación
- Filtros múltiples
- Actualización parcial y completa
- Búsquedas por nombre
- Contadores de registros

### **❌ Casos de Error:**
- Validaciones Pydantic (regex, fechas, longitud)
- IDs inexistentes
- Campos requeridos faltantes
- Formatos de fecha incorrectos
- Rangos de fechas inválidos
- Caracteres especiales en nombres

### **🗑️ Soft Delete:**
- Desactivación de registros
- Verificación de registros inactivos
- Listado incluyendo inactivos

## 🔧 **Personalización**

### **Cambiar URLs:**
Editar `http-client.env.json`:
```json
{
  "development": {
    "baseUrl": "http://localhost:8002"
  }
}
```

### **Variables en requests:**
Usar en archivos `.http`:
```http
@baseUrl = http://localhost:8002/api/v1
GET {{baseUrl}}/personas/1
```

## 📊 **Ejemplo de Flujo de Testing Completo**

1. **Health Check** → ✅ Servicio funcionando
2. **Crear Personas** → ✅ Validaciones OK
3. **Crear Libros** → ✅ Validaciones OK  
4. **Listar datos** → ✅ Paginación OK
5. **Filtros** → ✅ Búsquedas OK
6. **Actualizaciones** → ✅ Updates OK
7. **Soft Delete** → ✅ Eliminación OK
8. **Casos de error** → ✅ Validaciones OK

## 📝 **Notas importantes**

- **Puerto:** El servicio corre en puerto `8002`
- **Base de datos:** Requiere PostgreSQL funcionando
- **Validaciones:** Todos los campos tienen validaciones Pydantic estrictas
- **IDs:** Se autogeneran como enteros secuenciales
- **Fechas:** Formato requerido: `YYYY-MM-DD`
- **Soft Delete:** Los registros se marcan como `active=false`

## 🐛 **Solución de problemas**

### **Error de conexión:**
```
Connection refused
```
→ Verificar que Docker esté ejecutando el servicio

### **Error 503 Service Unhealthy:**
```
Service unhealthy
```
→ Verificar conexión a PostgreSQL

### **Error 422 Validation Error:**
```
Unprocessable Entity
```
→ Revisar formato de datos en el request

¡Happy Testing! 🎉
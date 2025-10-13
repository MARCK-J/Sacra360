# Sistema Sacra360 - API de Gestión Sacramental

## 🏛️ Descripción del Sistema

Sacra360 es un sistema integral para la gestión de sacramentos y documentos parroquiales que incluye:

- **Gestión de Usuarios** con roles específicos para parroquias
- **Administración de Personas** y sus datos personales
- **Gestión Completa de Sacramentos** (bautizo, confirmación, matrimonio)
- **Digitalización y Procesamiento OCR** de documentos
- **Sistema de Auditoría** y trazabilidad completa
- **API RESTful** con documentación automática

## 🚀 Características Principales

### 1. Sistema de Usuarios con Roles Parroquiales
- **Admin**: Acceso completo al sistema
- **Sacerdote**: Gestión de sacramentos y consultas
- **Secretario**: Carga de documentos y procesamiento
- **Consultor**: Solo lectura de información

### 2. Gestión de Personas
- Registro completo de personas con datos genealógicos
- Búsquedas avanzadas por nombres, apellidos y fechas
- Validación de duplicados
- Historial completo de sacramentos por persona

### 3. Sacramentos Especializados
- **Bautizos**: Con datos de padrinos y detalles específicos
- **Confirmaciones**: Con información de padrinos
- **Matrimonios**: Con datos de cónyuges y testigos
- Búsquedas específicas por tipo de sacramento

### 4. Digitalización y OCR
- Carga de documentos (PDF, JPG, PNG, TIFF)
- Procesamiento automático con OCR
- Sistema de correcciones para mejorar precisión
- Trazabilidad completa del proceso

### 5. Auditoría Completa
- Registro de todas las acciones del sistema
- Seguimiento por usuario, tabla y registro específico
- Estadísticas de uso y actividad
- Historial completo de cambios

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno para Python
- **Pydantic v2**: Validación de datos con type hints
- **JWT**: Autenticación basada en tokens
- **PostgreSQL**: Base de datos principal (esquema incluido)
- **Python 3.11**: Lenguaje de programación
- **Uvicorn**: Servidor ASGI de alto rendimiento

## 📁 Estructura del Proyecto

```
BACKEND/
├── app/
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── core/
│   │   ├── config.py          # Configuración del sistema
│   │   └── security.py        # Seguridad y JWT
│   ├── schemas/
│   │   └── sacra360_schemas.py # Modelos Pydantic para Sacra360
│   └── api/
│       ├── usuarios.py        # 👥 Gestión de usuarios
│       ├── personas.py        # 👤 Administración de personas
│       ├── sacramentos.py     # ⛪ Gestión de sacramentos
│       ├── documentos.py      # 📄 Documentos y OCR
│       └── auditoria.py       # 📊 Sistema de auditoría
├── .env                       # Variables de entorno
└── requirements.txt           # Dependencias Python
```

## 🔗 Endpoints Principales

### 👥 Usuarios (`/api/v1/usuarios`)
- `POST /register` - Registro de nuevos usuarios
- `POST /login` - Autenticación y obtención de token
- `GET /me` - Información del usuario actual
- `GET /` - Lista de usuarios (admin/sacerdote)
- `PUT /{user_id}` - Actualización de usuarios
- `DELETE /{user_id}` - Eliminación de usuarios (admin)

### 👤 Personas (`/api/v1/personas`)
- `POST /` - Registro de nuevas personas
- `GET /` - Lista paginada de personas
- `POST /buscar` - Búsqueda avanzada de personas
- `GET /{persona_id}` - Obtener persona por ID
- `PUT /{persona_id}` - Actualizar información de persona
- `DELETE /{persona_id}` - Eliminar persona (admin)
- `GET /{persona_id}/sacramentos` - Sacramentos de una persona

### ⛪ Sacramentos (`/api/v1/sacramentos`)
- `POST /` - Registro de nuevos sacramentos
- `GET /` - Lista paginada de sacramentos
- `GET /bautizos/buscar` - Búsqueda específica de bautizos
- `GET /confirmaciones/buscar` - Búsqueda específica de confirmaciones
- `GET /matrimonios/buscar` - Búsqueda específica de matrimonios
- `GET /{sacramento_id}` - Obtener sacramento por ID
- `PUT /{sacramento_id}` - Actualizar sacramento
- `DELETE /{sacramento_id}` - Eliminar sacramento (admin)
- `GET /persona/{persona_id}` - Sacramentos por persona

### 📄 Documentos (`/api/v1/documentos`)
- `POST /upload` - Carga de documentos digitalizados
- `GET /` - Lista de documentos con filtros
- `GET /{documento_id}` - Obtener documento por ID
- `POST /{documento_id}/procesar-ocr` - Procesar OCR
- `GET /{documento_id}/ocr` - Obtener resultado OCR
- `POST /{documento_id}/ocr/corregir` - Crear corrección OCR
- `GET /{documento_id}/ocr/correcciones` - Lista de correcciones
- `PUT /{documento_id}` - Actualizar documento
- `DELETE /{documento_id}` - Eliminar documento (admin)

### 📊 Auditoría (`/api/v1/auditoria`)
- `GET /` - Logs de auditoría con filtros
- `GET /usuario/{usuario_id}` - Logs por usuario
- `GET /tabla/{tabla}` - Logs por tabla
- `GET /registro/{tabla}/{registro_id}` - Historial de registro
- `GET /estadisticas` - Estadísticas de auditoría

## 🔐 Sistema de Autenticación

### Roles y Permisos

| Rol | Usuarios | Personas | Sacramentos | Documentos | Auditoría |
|-----|----------|----------|-------------|------------|-----------|
| **Admin** | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Full |
| **Sacerdote** | ✅ Read | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Read |
| **Secretario** | ❌ | ✅ CRU | ✅ CRU | ✅ CRUD | ❌ |
| **Consultor** | ❌ | ✅ Read | ✅ Read | ✅ Read | ❌ |

### Autenticación JWT
```python
# Headers requeridos para endpoints protegidos
{
    "Authorization": "Bearer <your_jwt_token>"
}
```

## 📊 Base de Datos PostgreSQL

El sistema está diseñado para trabajar con el siguiente esquema de PostgreSQL:

### Tablas Principales
- `usuarios` - Usuarios del sistema con roles
- `personas` - Registro de personas
- `sacramentos` - Sacramentos administrados
- `documentos_digitalizados` - Documentos cargados
- `ocr_resultados` - Resultados del procesamiento OCR
- `ocr_correcciones` - Correcciones realizadas al OCR
- `auditoria` - Logs de auditoría del sistema

## 🚀 Instalación y Configuración

### 1. Requisitos Previos
```bash
Python 3.11+
PostgreSQL 12+
```

### 2. Instalación de Dependencias
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración del Archivo `.env`
```env
# Configuración de la aplicación
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/sacra360_db

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### 4. Ejecutar el Servidor
```bash
# Desde el directorio raíz del proyecto
python -m uvicorn BACKEND.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Acceder a la Documentación
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Info**: http://localhost:8000/api/v1/info

## 📖 Uso del Sistema

### 1. Registro de Usuario
```bash
curl -X POST "http://localhost:8000/api/v1/usuarios/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sacra360.com",
    "password": "password123",
    "nombre_completo": "Administrador",
    "rol": "admin"
  }'
```

### 2. Inicio de Sesión
```bash
curl -X POST "http://localhost:8000/api/v1/usuarios/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@sacra360.com&password=password123"
```

### 3. Registro de Persona
```bash
curl -X POST "http://localhost:8000/api/v1/personas/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Juan Carlos",
    "apellido_paterno": "Pérez",
    "apellido_materno": "González",
    "fecha_nacimiento": "1990-05-15"
  }'
```

### 4. Registro de Sacramento
```bash
curl -X POST "http://localhost:8000/api/v1/sacramentos/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id_persona": 1,
    "tipo_sacramento": "bautizo",
    "fecha_sacramento": "2023-06-10",
    "parroquia": "San José",
    "celebrante": "Padre Miguel",
    "detalles_bautizo": {
      "nombre_padrino": "Carlos Pérez",
      "nombre_madrina": "María González"
    }
  }'
```

## 🔧 Características Técnicas

### Validaciones Implementadas
- **Email único** para usuarios
- **Validación de contraseñas** seguras
- **Prevención de duplicados** en personas
- **Validación de roles** específicos
- **Verificación de permisos** por endpoint
- **Validación de tipos de archivo** para documentos
- **Límites de tamaño** para cargas

### Manejo de Errores
- **Respuestas consistentes** con códigos HTTP apropiados
- **Mensajes descriptivos** en español
- **Logging detallado** de errores y requests
- **Manejo de excepciones** personalizado

### Características de Rendimiento
- **Paginación automática** en listados
- **Filtros optimizados** para búsquedas
- **Caching de configuración** con `@lru_cache`
- **Validación asíncrona** con FastAPI
- **Middleware de logging** con métricas de tiempo

## 📈 Monitoreo y Logs

### Logs del Sistema
- **Requests entrantes** con método y URL
- **Tiempo de procesamiento** por request
- **Errores detallados** con stack traces
- **Startup y shutdown** del servidor

### Auditoría Completa
- **Todas las acciones** registradas automáticamente
- **Usuario, tabla y registro** afectado
- **Valores anteriores y nuevos** en actualizaciones
- **IP address y user agent** del cliente
- **Estadísticas de uso** por periodo

## 🎯 Próximas Funcionalidades

- [ ] Conexión real a PostgreSQL con SQLAlchemy
- [ ] Implementación real de OCR con Tesseract
- [ ] Sistema de notificaciones
- [ ] Reportes en PDF
- [ ] Dashboard con métricas
- [ ] Backup automático de documentos
- [ ] API para integración con otros sistemas parroquiales

## 🤝 Contribución

Este sistema ha sido desarrollado específicamente para la gestión de sacramentos parroquiales, adaptándose al esquema de base de datos PostgreSQL proporcionado y siguiendo las mejores prácticas de desarrollo con FastAPI y Pydantic v2.

## 📞 Soporte

Para soporte técnico o consultas sobre la implementación, contactar al equipo de desarrollo.

---

*Sacra360 - Sistema de Gestión Sacramental v1.0.0*
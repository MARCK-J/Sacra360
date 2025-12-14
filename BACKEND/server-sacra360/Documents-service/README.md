# Documents Service - Sacra360

Microservicio para gestión de documentos sacramentales convertido de PocketBase a PostgreSQL.

## Características Implementadas

### ✅ Arquitectura PostgreSQL
- **Modelos SQLAlchemy**: Definición completa de tablas `personas` y `libros`
- **Migraciones**: Configuración para Alembic (opcional)
- **Conexión**: Pool de conexiones con configuración optimizada
- **Sesiones**: Manejo automático de sesiones con dependency injection

### ✅ Validaciones Pydantic Mejoradas
- **Personas**: Validación de nombres (solo letras), fechas (no futuras), estados civiles
- **Libros**: Validación de nombres, rangos de fechas coherentes, límites de caracteres
- **Sanitización**: Limpieza automática de espacios y capitalización
- **Errores**: Mensajes de error descriptivos y específicos

### ✅ Endpoints CRUD Completos
- **Personas**: 8 endpoints con filtros por nombre, estado civil, fechas
- **Libros**: 8 endpoints con filtros por nombre y rangos de fechas
- **Búsquedas**: Endpoints específicos para búsquedas complejas
- **Paginación**: Skip/limit en lugar de page/per_page
- **Contadores**: Endpoints para obtener totales de registros

### ✅ Servicios con SQLAlchemy
- **CRUD Completo**: Create, Read, Update, Delete (soft delete)
- **Filtros Avanzados**: Búsquedas con múltiples criterios
- **Manejo de Errores**: HTTPException con códigos apropiados
- **Transacciones**: Rollback automático en caso de error

## Estructura de Archivos

```
Documents-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app con routers incluidos
│   ├── config.py                  # Configuración con pydantic-settings
│   ├── database.py                # SQLAlchemy setup y dependency
│   ├── controllers/
│   │   ├── persona_controller.py  # 8 endpoints para personas
│   │   └── libro_controller.py    # 8 endpoints para libros
│   ├── dto/
│   │   ├── persona_dto.py         # DTOs con validaciones Pydantic
│   │   └── libro_dto.py           # DTOs con validaciones avanzadas
│   ├── entities/
│   │   ├── persona.py             # Entidad con from_orm()
│   │   └── libro.py               # Entidad con from_orm()
│   ├── models/
│   │   └── __init__.py            # Modelos SQLAlchemy
│   └── services/
│       ├── persona_service.py     # Servicio con SQLAlchemy
│       └── libro_service.py       # Servicio con SQLAlchemy
├── requirements.txt               # Dependencias PostgreSQL
├── .env.example                   # Variables de entorno
└── README.md                      # Este archivo
```

## Instalación y Configuración

### 1. Instalar Dependencias

```bash
cd Documents-service
pip install -r requirements.txt
```

### 2. Configurar Base de Datos

Crear base de datos PostgreSQL:
```sql
CREATE DATABASE sacra360_documents;
CREATE USER sacra_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE sacra360_documents TO sacra_user;
```

### 3. Variables de Entorno

Copiar y configurar:
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
```env
DATABASE_URL=postgresql://sacra_user:secure_password@localhost:5432/sacra360_documents
```

### 4. Crear Tablas

Las tablas se crean automáticamente al iniciar la aplicación:
```python
# En main.py
Base.metadata.create_all(bind=engine)
```

### 5. Ejecutar Servicio

```bash
cd Documents-service
uvicorn app.main:app --reload --port 8002
```

### 6. Documentación API

Acceder a:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Endpoints Disponibles

### Personas (`/api/personas/`)
1. `POST /` - Crear persona
2. `GET /{persona_id}` - Obtener por ID
3. `GET /` - Listar con filtros
4. `GET /count/total` - Contar registros
5. `PUT /{persona_id}` - Actualizar
6. `DELETE /{persona_id}` - Desactivar (soft delete)
7. `GET /search/by-name` - Buscar por nombre
8. `GET /filter/estado-civil/{estado_civil}` - Filtrar por estado civil

### Libros (`/api/libros/`)
1. `POST /` - Crear libro
2. `GET /{libro_id}` - Obtener por ID
3. `GET /` - Listar con filtros
4. `GET /count/total` - Contar registros
5. `PUT /{libro_id}` - Actualizar
6. `DELETE /{libro_id}` - Desactivar (soft delete)
7. `GET /search/by-name` - Buscar por nombre
8. `GET /filter/date-range` - Filtrar por rango de fechas

## Validaciones Implementadas

### Personas
- **Nombres/Apellidos**: Solo letras, espacios, acentos y guiones
- **Fecha Nacimiento**: No puede ser futura
- **Estado Civil**: Lista cerrada de valores válidos
- **Lugar Nacimiento**: Opcional, máximo 200 caracteres
- **Ocupación**: Opcional, máximo 150 caracteres

### Libros
- **Nombre**: Obligatorio, máximo 200 caracteres, no solo espacios
- **Fecha Inicio**: Obligatoria, debe ser anterior a fecha_fin
- **Fecha Fin**: Obligatoria, debe ser posterior a fecha_inicio
- **Observaciones**: Opcional, máximo 500 caracteres

## Dependencias Principales

```txt
fastapi==0.110.0              # Framework web
sqlalchemy==2.0.25           # ORM
psycopg2-binary==2.9.9       # Driver PostgreSQL
pydantic==2.5.3              # Validaciones
uvicorn[standard]==0.28.0    # Servidor ASGI
```

## Características PostgreSQL

### Modelos de Base de Datos
```sql
-- Tabla personas
CREATE TABLE personas (
    id_persona SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    lugar_nacimiento VARCHAR(200),
    estado_civil VARCHAR(50) NOT NULL,
    ocupacion VARCHAR(150),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla libros
CREATE TABLE libros (
    id_libro SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    observaciones TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices Recomendados
```sql
-- Personas
CREATE INDEX idx_personas_nombres ON personas(nombres);
CREATE INDEX idx_personas_apellidos ON personas(apellidos);
CREATE INDEX idx_personas_estado_civil ON personas(estado_civil);
CREATE INDEX idx_personas_active ON personas(active);

-- Libros  
CREATE INDEX idx_libros_nombre ON libros(nombre);
CREATE INDEX idx_libros_fechas ON libros(fecha_inicio, fecha_fin);
CREATE INDEX idx_libros_active ON libros(active);
```

## Notas Técnicas

### Migraciones Futuras
Para usar Alembic (opcional):
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Soft Delete
Todos los endpoints de eliminación usan soft delete (marcar `active=False`) en lugar de eliminación física.

### Manejo de Errores
- **404**: Registro no encontrado
- **400**: Error de validación o base de datos
- **422**: Error de validación Pydantic

### Paginación
Se usa `skip` y `limit` en lugar de `page` y `per_page` para mayor eficiencia con PostgreSQL.

## Migración desde PocketBase

### Cambios Realizados
1. ✅ **IDs**: String → Integer (PostgreSQL SERIAL)
2. ✅ **Fechas**: String → date (validación nativa)
3. ✅ **Servicios**: PocketBase client → SQLAlchemy Session
4. ✅ **Filtros**: PocketBase syntax → SQLAlchemy filters
5. ✅ **Errores**: ClientResponseError → HTTPException
6. ✅ **Paginación**: page/per_page → skip/limit
7. ✅ **Validaciones**: Básicas → Avanzadas con Pydantic

### Equivalencias de Endpoints
| PocketBase | PostgreSQL |
|------------|------------|
| `POST ""` | `POST /` |
| `GET "/{id}"` | `GET /{id}` |
| `GET ""` | `GET /` |
| `PATCH "/{id}"` | `PUT /{id}` |
| `DELETE "/{id}"` | `DELETE /{id}` |

¡El microservicio está listo para usar con PostgreSQL! 🚀
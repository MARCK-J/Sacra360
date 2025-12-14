INTRODUCCIÓN

Esta sección está dirigida al equipo de desarrollo o personal técnico encargado de la instalación, configuración y mantenimiento del sistema Sacra360. Aquí se describen las tecnologías empleadas, la arquitectura del proyecto, pasos de instalación y despliegue, además de herramientas para pruebas, monitoreo y generación de documentación técnica.

Dentro de esta guía se describen las tecnologías empleadas en el desarrollo del sistema, incluyendo lenguajes de programación como Python para el backend y JavaScript para el frontend, frameworks como FastAPI para APIs RESTful y React con Vite para la interfaz de usuario, motores de bases de datos como PostgreSQL para persistencia relacional y Redis para caché de alto rendimiento, sistemas de almacenamiento de objetos como MinIO compatible con S3, y herramientas de documentación como Swagger/OpenAPI para la descripción y prueba interactiva de endpoints. También se detalla la arquitectura de microservicios implementada, la estructura modular de cada servicio (routers, middlewares, entities, DTOs), las convenciones de código utilizadas siguiendo estándares PEP 8 para Python y ESLint para JavaScript, así como los patrones de diseño aplicados (RBAC para control de acceso, JWT stateless para autenticación, Repository pattern para acceso a datos) para mantener la calidad, escalabilidad y coherencia del software.

Se incluyen instrucciones claras para la instalación del entorno de desarrollo, tanto local con Docker Compose como en producción con Kubernetes, configuración de variables de entorno críticas para seguridad (JWT_SECRET_KEY, credenciales de base de datos), gestión de dependencias con pip para Python y npm para Node.js, inicialización de la base de datos mediante scripts SQL automatizados, y ejecución del sistema completo con múltiples servicios containerizados comunicándose en una red privada Docker.

Finalmente, se explican los procedimientos de despliegue del sistema en distintos entornos (desarrollo local, staging, producción), incluyendo la containerización con Docker, orquestación con Kubernetes para alta disponibilidad, automatización de CI/CD con GitHub Actions, estrategias de escalado horizontal mediante HorizontalPodAutoscaler, gestión de secretos con Kubernetes Secrets, y configuración de ingress controllers con nginx para exposición HTTPS con certificados SSL de Let's Encrypt. Se abordan también las herramientas de prueba implementadas, tanto para pruebas unitarias con pytest, pruebas de integración con bases de datos de prueba, como para pruebas end-to-end automatizadas, con ejemplos de comandos de ejecución y análisis de cobertura. Además, se proporciona una sección dedicada a la generación de reportes técnicos como logs centralizados, métricas de rendimiento en Prometheus + Grafana, tracking de errores en Sentry, documentación automática de APIs con Swagger UI, y auditoría de seguridad con herramientas como Trivy para escaneo de vulnerabilidades en imágenes Docker, todo orientado a mantener la trazabilidad, estabilidad, seguridad y calidad del sistema a lo largo del tiempo.

El presente documento se enfoca específicamente en el Módulo de Gestión de Usuarios (AuthProfiles Service), que constituye el núcleo de seguridad del sistema Sacra360. Este módulo implementa toda la funcionalidad de autenticación, autorización mediante control de acceso basado en roles (RBAC), auditoría exhaustiva de acciones de usuarios y reportes analíticos, sirviendo como capa de seguridad transversal para el resto de componentes del sistema y garantizando que cada operación crítica esté protegida, trazada y auditada de forma automática.


ARQUITECTURA DEL MÓDULO DE GESTIÓN DE USUARIOS (AUTHPROFILES SERVICE)

El módulo AuthProfiles constituye el núcleo de seguridad del sistema Sacra360, encargado de la autenticación, autorización, auditoría y generación de reportes analíticos. Implementa un patrón de microservicio independiente que se comunica mediante API REST protegida con tokens JWT.


Resumen de Arquitectura

Patrón: Microservicio de seguridad centralizado con autenticación stateless JWT.
Comunicación: HTTP REST con tokens JWT en headers (Authorization: Bearer).
Almacenamiento: PostgreSQL para datos relacionales (usuarios, roles, auditoría) y Redis para caché de reportes.
Seguridad: Bcrypt para hashing de contraseñas, rate limiting (100 req/min), security headers (CSP, HSTS).


Componentes Principales

Frontend (React + Vite)
Interfaz de usuario desarrollada con React 19 y Tailwind CSS, incluye las siguientes pantallas:

- Login.jsx: Formulario de autenticación con validación de credenciales.
- Dashboard.jsx: Panel principal con estadísticas del sistema en tiempo real.
- Usuarios.jsx: CRUD completo de usuarios con tabla paginada, filtros y asignación de roles.
- Auditoria.jsx: Visualización de logs con filtros avanzados (usuario, acción, fechas).
- Reportes.jsx: Reportes analíticos con gráficos y filtros de periodo.
- Perfil.jsx: Gestión de perfil personal y cambio de contraseña.

Context Global: AuthContext.jsx provee el estado de autenticación y permisos a toda la aplicación.


Backend (FastAPI + Python)
Microservicio corriendo en puerto 8004, desarrollado con FastAPI utilizando programación asíncrona.

Stack Tecnológico:
- Python 3.11+
- FastAPI (framework web async)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 15 (base de datos)
- Redis 7 (caché)
- python-jose (JWT)
- passlib + bcrypt (hashing)

Estructura del Proyecto:
```
AuthProfiles-service/
├── app/
│   ├── main.py                      # Aplicación FastAPI
│   ├── database.py                  # Configuración BD
│   ├── dto/auth_dto.py             # Modelos Pydantic
│   ├── entities/user_entity.py     # Modelos SQLAlchemy
│   ├── middleware/
│   │   ├── permissions.py          # Sistema RBAC
│   │   └── security.py             # Rate limiting
│   ├── routers/
│   │   ├── auth_router_adapted.py  # Autenticación (6 endpoints)
│   │   ├── usuarios_router.py      # Gestión usuarios (8 endpoints)
│   │   ├── auditoria_router.py     # Auditoría (6 endpoints)
│   │   └── reportes_router.py      # Reportes (10 endpoints)
│   └── utils/auth_utils.py         # JWT, bcrypt, validaciones
```


Middlewares de Seguridad

1. Security Headers Middleware: Agrega headers HTTP de seguridad (X-Frame-Options, Content-Security-Policy, HSTS).
2. Rate Limiting: Limita a 100 requests por minuto por IP.
3. RBAC Permission Guard: Valida permisos basados en roles con 144 combinaciones (4 roles × 9 módulos × 4 acciones CRUD).


Modelo de Datos

El módulo utiliza tres tablas principales en PostgreSQL:

Tabla Roles:
```sql
CREATE TABLE Roles (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);
```
Roles predefinidos: Administrador, Digitalizador, Validador, Consultor.

Tabla usuarios:
```sql
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    rol_id INTEGER REFERENCES Roles(id_rol),
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasenia TEXT NOT NULL,  -- Hash bcrypt
    fecha_creacion DATE DEFAULT CURRENT_DATE,
    activo BOOLEAN DEFAULT true
);
```

Tabla Auditoria:
```sql
CREATE TABLE Auditoria (
    id_auditoria SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id_usuario),
    accion TEXT NOT NULL,
    registro_afectado TEXT NOT NULL,
    Id_registro INTEGER NOT NULL,
    fecha TIMESTAMP DEFAULT NOW()
);
```

Acciones registradas: LOGIN, LOGOUT, CREAR_USUARIO, ACTUALIZAR_USUARIO, ELIMINAR_USUARIO, ACTIVAR_USUARIO, CAMBIAR_CONTRASENA, ACCESO_DENEGADO, EXPORTAR_REPORTE.


Flujo de Autenticación JWT

1. Usuario ingresa credenciales en el frontend.
2. Frontend envía POST /api/v1/auth/login con email y contraseña.
3. Backend valida credenciales contra BD usando bcrypt.
4. Si es válido, genera token JWT (HS256, expiración 30 minutos).
5. Backend registra LOGIN en tabla Auditoria.
6. Frontend recibe token y lo almacena en localStorage.
7. Todas las peticiones subsecuentes incluyen header: Authorization: Bearer {token}.


Sistema RBAC (Control de Acceso)

Cada request a endpoints protegidos ejecuta:
1. Extraer token del header Authorization.
2. Verificar firma JWT y decodificar payload.
3. Obtener rol_id del usuario desde la BD.
4. Validar si el rol tiene permiso para el módulo y acción solicitada.
5. Si tiene permiso, ejecutar endpoint; sino, retornar 403 Forbidden.

Matriz de Permisos:
- Administrador: Acceso total (CRUD en todos los módulos).
- Digitalizador: Acceso a digitalización, lectura de usuarios/reportes.
- Validador: Acceso a revisión OCR, lectura de registros.
- Consultor: Solo lectura en módulos públicos.


Endpoints API Principales

Autenticación (6 endpoints):
- POST /api/v1/auth/login - Autenticación con email/password
- POST /api/v1/auth/register - Registro de nuevos usuarios
- GET /api/v1/auth/me - Información del usuario actual
- POST /api/v1/auth/change-password - Cambio de contraseña
- POST /api/v1/auth/logout - Cierre de sesión
- GET /api/v1/auth/roles - Lista de roles disponibles

Gestión de Usuarios (8 endpoints):
- GET /api/v1/usuarios - Lista todos los usuarios con paginación
- GET /api/v1/usuarios/{usuario_id} - Obtener un usuario específico
- POST /api/v1/usuarios - Crear nuevo usuario
- PUT /api/v1/usuarios/{usuario_id} - Actualizar datos de usuario
- PATCH /api/v1/usuarios/{usuario_id}/password - Cambiar contraseña de usuario
- DELETE /api/v1/usuarios/{usuario_id} - Desactivar usuario (soft delete)
- PATCH /api/v1/usuarios/{usuario_id}/activar - Reactivar usuario desactivado
- GET /api/v1/usuarios/roles/listar - Listar todos los roles

Auditoría (4 endpoints):
- GET /api/v1/auditoria - Lista logs con filtros y paginación
- GET /api/v1/auditoria/{log_id} - Obtener un log específico
- GET /api/v1/auditoria/usuario/{usuario_id} - Logs de un usuario específico
- GET /api/v1/auditoria/stats/resumen - Estadísticas de auditoría

Reportes (5 endpoints):
- GET /api/v1/reportes/usuarios - Resumen de usuarios del sistema
- GET /api/v1/reportes/accesos - Resumen de accesos y actividad
- GET /api/v1/reportes/actividad/{usuario_id} - Actividad de usuario específico
- GET /api/v1/reportes/estadisticas - Estadísticas generales del sistema
- GET /api/v1/reportes/permisos/{usuario_id} - Permisos de usuario específico


Optimización con Caché Redis

Para evitar consultas SQL pesadas en reportes, se implementa caché con Redis:
- Key pattern: cache:reportes:{tipo}:{periodo}
- TTL: 300 segundos (5 minutos)
- Beneficio: Reduce tiempo de respuesta de ~500ms a ~10ms en requests repetidas.


INSTALACIÓN Y DESPLIEGUE

Requisitos del Sistema

Hardware recomendado:
- CPU: 4+ cores
- RAM: 8 GB mínimo
- Almacenamiento: 20 GB

Software requerido:
- Python 3.8+ (desarrollo local)
- Node.js 18+ (desarrollo frontend)
- PostgreSQL 15
- Docker 20.10+ y Docker Compose 2.0+ (despliegue con contenedores)


Instalación Local del Backend (AuthProfiles)

1. Navegar al directorio del servicio:
```bash
cd BACKEND/server-sacra360/AuthProfiles-service
```

2. Crear y activar entorno virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r ../../requirements.txt
```

4. Configurar variables de entorno (.env):
```bash
# Base de datos PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=lolsito101
POSTGRES_DB=sacra360

# JWT y Seguridad
SECRET_KEY=tu-clave-secreta-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8004

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

5. Inicializar base de datos (desde directorio BACKEND):
```bash
cd ../..
psql -U postgres -d sacra360 -f sql/Database.sql
psql -U postgres -d sacra360 -f sql/Create_Users_All_Roles.sql
```

6. Ejecutar el servicio:
```bash
cd server-sacra360/AuthProfiles-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```

7. Acceder a la API:
- Swagger UI: http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc


Instalación del Frontend

1. Navegar a carpeta frontend:
```bash
cd frontend
```

2. Instalar dependencias:
```bash
npm install
```

3. Configurar variables de entorno (.env):
```bash
VITE_AUTH_API_URL=http://localhost:8004
VITE_API_URL=http://localhost:8004
```

4. Ejecutar en modo desarrollo:
```bash
npm run dev
```
Acceder a: http://localhost:5173

5. Build para producción:
```bash
npm run build
# Los archivos estáticos se generan en carpeta dist/
```


Despliegue con Docker Compose

1. Navegar al directorio BACKEND:
```bash
cd BACKEND
```

2. Iniciar servicios base:
```bash
docker-compose up -d postgres redis minio
```

3. Inicializar base de datos:
```bash
docker exec -i postgres psql -U postgres sacra360 < sql/Database.sql
docker exec -i postgres psql -U postgres sacra360 < sql/Create_Users_All_Roles.sql
```

4. Iniciar servicio AuthProfiles:
```bash
docker-compose up -d auth-service
```

5. Verificar servicios:
```bash
docker ps
# Verificar: postgres, redis, minio, sacra360_auth_service
```

6. Ver logs:
```bash
docker logs -f sacra360_auth_service
```

Nota: El docker-compose.yml tiene configurado el puerto 8001:8001, pero el código usa puerto 8004. Verificar main.py antes de ejecutar.


PRUEBAS Y CALIDAD

Pruebas Unitarias

Ejecutar tests con pytest:
```bash
cd BACKEND
pytest tests/ -v --cov=app --cov-report=html
```

Cobertura de código:
- Objetivo: >80%
- Reporte HTML generado en htmlcov/index.html


Pruebas de Integración

Pruebas con base de datos de test:
```bash
pytest tests/test_usuarios.py -v
pytest tests/test_auditoria.py -v
pytest tests/test_reportes.py -v
```


Herramientas de Monitoreo

Logs: Logs centralizados con configuración de logging en Python.
Métricas: Prometheus + Grafana para monitoreo de rendimiento.
Errores: Sentry para tracking de excepciones en producción.
Documentación: Swagger UI automático en /docs.
Seguridad: Trivy para escaneo de vulnerabilidades en imágenes Docker.


CONFIGURACIÓN DE SEGURIDAD

Variables de Entorno del Servicio AuthProfiles

```bash
# Base de datos PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/sacra360
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password_seguro_minimo_16_caracteres
POSTGRES_DB=sacra360

# JWT y Seguridad
SECRET_KEY=clave_secreta_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8004

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Logs
LOG_LEVEL=INFO
```

Variables de Entorno del Frontend

```bash
VITE_AUTH_API_URL=http://localhost:8004
VITE_API_URL=http://localhost:8004
```


Recomendaciones de Seguridad

1. Nunca commitear archivos .env al repositorio (ya está en .gitignore).
2. Cambiar SECRET_KEY por una clave fuerte en producción (mínimo 32 caracteres).
3. Usar contraseñas seguras para PostgreSQL (mínimo 16 caracteres).
4. Rotar SECRET_KEY cada 90 días.
5. Habilitar HTTPS en producción con certificados SSL válidos.
6. Configurar backup automático de PostgreSQL.
7. El sistema ya implementa rate limiting (100 req/min) y security headers.
8. Auditar logs de auditoría regularmente.
9. Mantener dependencias actualizadas: pip install --upgrade -r requirements.txt


RESOLUCIÓN DE PROBLEMAS COMUNES

Problema 1: Error 401 Unauthorized
Causa: Token JWT expirado o inválido.
Solución: Hacer logout y login nuevamente para obtener nuevo token.

Problema 2: Error 403 Forbidden
Causa: Usuario no tiene permisos para la acción solicitada.
Solución: Verificar rol del usuario y matriz de permisos RBAC.

Problema 3: Base de datos no conecta
Causa: PostgreSQL no está corriendo o credenciales incorrectas.
Solución: Verificar docker ps y variables de entorno en .env.

Problema 4: Reportes lentos
Causa: Caché Redis no configurado o expirado.
Solución: Verificar conexión a Redis, aumentar TTL si necesario.

Problema 5: Frontend no se conecta al backend
Causa: Variable VITE_AUTH_API_URL incorrecta.
Solución: Verificar archivo .env en carpeta frontend.


CONCLUSIÓN

El módulo AuthProfiles Service constituye la base de seguridad del sistema Sacra360, implementando autenticación robusta con JWT, control de acceso granular mediante RBAC, auditoría completa de acciones y reportes analíticos optimizados. La arquitectura de microservicio permite escalabilidad horizontal, mientras que el uso de Docker y Kubernetes facilita el despliegue en múltiples entornos. La documentación técnica completa, pruebas automatizadas y herramientas de monitoreo garantizan la mantenibilidad y calidad del sistema a largo plazo.

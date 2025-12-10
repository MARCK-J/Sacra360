# 🏗️ Arquitectura del Sistema Sacra360

## 📑 Índice
1. [Visión General](#visión-general)
2. [Arquitectura de Microservicios](#arquitectura-de-microservicios)
3. [Arquitectura en Capas](#arquitectura-en-capas)
4. [Componentes Principales](#componentes-principales)
5. [Patrones de Diseño](#patrones-de-diseño)
6. [Flujo de Datos](#flujo-de-datos)
7. [Seguridad](#seguridad)
8. [Escalabilidad](#escalabilidad)

---

## 🎯 Visión General

Sacra360 es un sistema de gestión de archivos sacramentales basado en una **arquitectura de microservicios** con las siguientes características:

### Características Arquitectónicas

| Característica | Implementación |
|----------------|----------------|
| **Patrón Arquitectónico** | Microservicios + Event-Driven |
| **Frontend** | SPA (Single Page Application) |
| **Backend** | RESTful API con FastAPI |
| **Base de Datos** | PostgreSQL (Relacional) |
| **Cache** | Redis (In-memory) |
| **Storage** | MinIO (S3-compatible) |
| **Orquestación** | Docker Compose |
| **Autenticación** | JWT (HS256) |
| **Autorización** | RBAC (Role-Based Access Control) |

---

## 🔧 Arquitectura de Microservicios

### Diagrama General
Ver: `esquema-arquitectura.puml`

### Microservicios Implementados

#### 1. **AuthProfiles Service** (:8004)
**Responsabilidad:** Autenticación, autorización y gestión de usuarios

**Características:**
- ✅ Autenticación JWT (HS256, 30 min expiration)
- ✅ RBAC con 144 permisos (4 roles × 9 módulos × 4 acciones)
- ✅ CRUD completo de usuarios
- ✅ Sistema de auditoría (logs de acciones)
- ✅ Generación de reportes y estadísticas
- ✅ Rate limiting (100 req/min por IP)
- ✅ Security headers (CSP, HSTS, X-Frame-Options, etc.)

**Tecnologías:**
- FastAPI 0.115
- SQLAlchemy 2.0
- python-jose (JWT)
- passlib + bcrypt (hashing)
- PostgreSQL

**Endpoints:** 20 (Auth: 6, Usuarios: 8, Auditoría: 4, Reportes: 5)

---

#### 2. **Documents Service** (:8002)
**Responsabilidad:** Gestión de sacramentos, personas y libros

**Características:**
- ✅ CRUD de sacramentos (bautismo, confirmación, matrimonio)
- ✅ CRUD de personas (feligreses)
- ✅ Búsquedas avanzadas (por nombre, fecha, sacramento)
- ✅ Gestión de libros sacramentales
- ✅ Validación de datos
- ✅ Vinculación documento-sacramento

**Tecnologías:**
- FastAPI
- SQLAlchemy
- PostgreSQL

---

#### 3. **OCR Service** (:8003)
**Responsabilidad:** Extracción de texto de documentos digitalizados

**Características:**
- ✅ Procesamiento con Tesseract 5.x
- ✅ Preprocesamiento de imágenes (binarización, deskew, denoise)
- ✅ Extracción de campos estructurados
- ✅ Cálculo de confianza (0.0 - 1.0)
- ✅ Idioma: Español
- ✅ Soporte manuscritos antiguos

**Tecnologías:**
- FastAPI
- Tesseract OCR
- OpenCV (preprocesamiento)
- PIL/Pillow

**Workflow:**
1. Recibir documento digitalizado
2. Preprocesar imagen
3. Ejecutar Tesseract
4. Extraer campos (nombre, fecha, padrino, etc.)
5. Calcular confianza
6. Guardar resultados en BD
7. Enviar a revisión si confianza < 70%

---

#### 4. **HTR Service** (:8004)
**Responsabilidad:** Reconocimiento de escritura manual (Handwritten Text Recognition)

**Características:**
- ✅ Modelo TensorFlow/PyTorch custom
- ✅ Especializado en manuscritos del siglo XIX-XX
- ✅ Segmentación de líneas de texto
- ✅ Reconocimiento carácter por carácter
- ✅ Post-procesamiento con diccionario histórico

**Tecnologías:**
- FastAPI
- TensorFlow 2.x
- NumPy, OpenCV

---

#### 5. **AI Processing Service** (:8005)
**Responsabilidad:** Mejora de datos con IA

**Características:**
- ✅ Integración con OpenAI GPT
- ✅ Procesamiento de lenguaje natural (NLP)
- ✅ Reconocimiento de entidades (NER)
- ✅ Corrección y normalización de nombres
- ✅ Extracción de relaciones familiares

**Tecnologías:**
- FastAPI
- OpenAI API
- spaCy (NLP)

---

#### 6. **File Storage Service** (:8007)
**Responsabilidad:** Almacenamiento y gestión de archivos

**Características:**
- ✅ Upload de documentos (JPG, PNG, PDF)
- ✅ Integración con MinIO (S3-compatible)
- ✅ Validación de formato y tamaño (max 10MB)
- ✅ Generación de URLs firmadas
- ✅ Gestión de buckets

**Tecnologías:**
- FastAPI
- MinIO Python SDK
- PIL/Pillow (validación)

**Storage:**
- Bucket: `sacra360`
- Estructura: `/documentos/{año}/{mes}/{uuid}.{ext}`

---

#### 7. **Reports Service** (:8006)
**Responsabilidad:** Generación de reportes y exportación

**Características:**
- ✅ Generación de PDFs
- ✅ Exportación a Excel
- ✅ Gráficos y visualizaciones
- ✅ Agregaciones SQL optimizadas

**Tecnologías:**
- FastAPI
- ReportLab (PDF)
- openpyxl (Excel)
- Matplotlib/Plotly (gráficos)

---

## 🏛️ Arquitectura en Capas

Ver: `arquitectura-capas.puml`

### Capa 1: Presentación (Frontend)
**Tecnologías:** React 19.1, Vite 7.1, React Router 7.9, Tailwind CSS 3.4

**Componentes:**
- Pages (Dashboard, Usuarios, Digitalizacion, etc.)
- Components (Layout, PrivateRoute, PermissionGuard)
- Context (AuthContext para estado global)
- Config (permissions.js con matriz RBAC)

**Responsabilidades:**
- Interfaz de usuario
- Validación de formularios
- Gestión de estado local
- Enrutamiento SPA
- Verificación de permisos local

---

### Capa 2: API Gateway
**Puerto:** 8000

**Responsabilidades:**
- Punto de entrada único
- Enrutamiento a microservicios
- Autenticación centralizada
- Rate limiting global
- Load balancing
- CORS handling

**Tecnologías:** FastAPI / Express.js

---

### Capa 3: Lógica de Negocio (Microservicios)
**Puertos:** 8001-8007

**Responsabilidades:**
- Procesamiento de negocio
- Validaciones complejas
- Orquestación de operaciones
- Transformación de datos
- Aplicación de reglas de negocio

---

### Capa 4: Acceso a Datos
**Componentes:**
- SQLAlchemy ORM (PostgreSQL)
- Redis Client (Cache)
- MinIO SDK (Storage)
- Connection Pooling

**Responsabilidades:**
- Abstracción de base de datos
- Manejo de transacciones
- Pool de conexiones
- Query optimization

---

### Capa 5: Persistencia
**Bases de Datos:**
- PostgreSQL 15 (:5432) - Datos relacionales
- Redis 7 (:6379) - Cache y sesiones
- MinIO (:9000) - Object storage

---

### Capa 6: Infraestructura
**Componentes:**
- Docker Engine
- Docker Compose
- Docker Network (sacra360_network)
- Docker Volumes (persistencia)

---

## 🧩 Componentes Principales

Ver: `diagrama-componentes.puml`

### Frontend Components

#### Core
```
App.jsx
├── Router (React Router)
├── AuthContext (Estado global)
└── Layout (Navegación y sidebar)
```

#### Pages
- `Dashboard.jsx` - Resumen del sistema
- `Usuarios.jsx` - Gestión de usuarios (CRUD)
- `Digitalizacion.jsx` - Upload de documentos
- `RevisionOCR.jsx` - Validación y corrección
- `Registros.jsx` - CRUD sacramentos
- `Personas.jsx` - CRUD personas
- `Auditoria.jsx` - Logs del sistema
- `Reportes.jsx` - Analytics y estadísticas
- `Perfil.jsx` - Información y cambio de contraseña

#### Security Components
- `PrivateRoute.jsx` - Protección de rutas
- `PermissionGuard.jsx` - Validación de permisos RBAC

---

### Backend Components (AuthProfiles)

#### Routers (Endpoints)
```python
auth_router_adapted.py          # 6 endpoints
├── POST /login                 # Autenticación
├── POST /register              # Registro
├── GET /me                     # Perfil actual
├── POST /change-password       # Cambiar contraseña
├── POST /logout                # Cerrar sesión
└── GET /roles                  # Listar roles

usuarios_router.py              # 8 endpoints
├── GET /usuarios               # Listar (paginado)
├── POST /usuarios              # Crear
├── GET /usuarios/{id}          # Obtener por ID
├── PUT /usuarios/{id}          # Actualizar
├── DELETE /usuarios/{id}       # Desactivar
├── PATCH /usuarios/{id}/activar    # Reactivar
├── PATCH /usuarios/{id}/password   # Cambiar contraseña
└── GET /usuarios/roles/listar      # Roles disponibles

auditoria_router.py             # 4 endpoints
├── GET /auditoria              # Listar logs
├── GET /auditoria/{id}         # Log por ID
├── GET /auditoria/usuario/{id} # Logs de usuario
└── GET /auditoria/stats/resumen    # Estadísticas

reportes_router.py              # 5 endpoints
├── GET /reportes/usuarios      # Reporte usuarios
├── GET /reportes/accesos       # Reporte accesos
├── GET /reportes/actividad/{id}    # Actividad usuario
├── GET /reportes/estadisticas      # Stats generales
└── GET /reportes/permisos/{id}     # Permisos usuario
```

#### Middleware
```python
RateLimitMiddleware
├── max_requests: 100
├── window_seconds: 60
└── storage: memory (dict)

SecurityHeadersMiddleware
├── X-Frame-Options: DENY
├── X-Content-Type-Options: nosniff
├── X-XSS-Protection: 1; mode=block
├── Strict-Transport-Security
├── Content-Security-Policy
└── Referrer-Policy

permissions.py (RBAC)
├── PERMISSIONS_MATRIX (144 permisos)
├── has_permission(rol, modulo, accion)
└── require_permission decorator
```

#### Utils
```python
auth_utils.py
├── get_password_hash(password)      # bcrypt hash
├── verify_password(plain, hashed)    # bcrypt verify
├── create_access_token(data)         # JWT creation
├── decode_token(token)               # JWT decode
└── get_current_user(token)           # Dependency injection
```

#### Entities (SQLAlchemy Models)
```python
usuario.py
├── Usuario (id, email, contrasenia, rol_id, activo)
├── Rol (id, nombre, descripcion)
└── Auditoria (id, usuario_id, accion, fecha)
```

---

## 🎨 Patrones de Diseño

### 1. **Microservices Pattern**
Cada servicio es independiente, desplegable y escalable por separado.

### 2. **API Gateway Pattern**
Punto de entrada único que enruta a los microservicios correspondientes.

### 3. **Repository Pattern**
Abstracción de acceso a datos a través de SQLAlchemy ORM.

### 4. **Dependency Injection**
FastAPI usa DI para inyectar dependencias (DB sessions, current user, etc.).

```python
@router.get("/usuarios")
async def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    ...
```

### 5. **Middleware Pattern**
Interceptores que procesan requests/responses (auth, rate limit, logging).

### 6. **DTO Pattern (Data Transfer Objects)**
Pydantic models para validar entrada/salida de APIs.

```python
class LoginRequest(BaseModel):
    email: str
    password: str

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    rol: str
```

### 7. **Decorator Pattern**
Decoradores para validación de permisos.

```python
@require_permission("usuarios", "create")
async def crear_usuario(...):
    ...
```

### 8. **Strategy Pattern**
Diferentes estrategias de procesamiento (OCR, HTR, AI).

### 9. **Observer Pattern**
Sistema de auditoría que registra todas las acciones.

### 10. **Factory Pattern**
Creación de tokens JWT, hash de contraseñas.

---

## 🔄 Flujo de Datos

### Flujo de Autenticación
```
Usuario → Frontend → API Gateway → AuthProfiles
                                    ↓
                                PostgreSQL (validar)
                                    ↓
                                JWT Token ← AuthProfiles
                                    ↓
Frontend (localStorage) ← API Gateway
```

### Flujo de Digitalización
```
Usuario → Upload → Files Service → MinIO
                        ↓
                   PostgreSQL (metadata)
                        ↓
                   OCR Service → Tesseract
                        ↓
                   PostgreSQL (ocr_resultado)
                        ↓
                   Frontend (mostrar campos)
                        ↓
                   Usuario revisa/corrige
                        ↓
                   Documents Service (crear sacramento)
```

### Flujo de Reportes
```
Usuario → Frontend → AuthProfiles Service
                          ↓
                     Redis (cache check)
                          ↓
                     PostgreSQL (queries)
                          ↓
                     Redis (guardar cache 5min)
                          ↓
                     Frontend (renderizar gráficos)
```

---

## 🔒 Seguridad

### Autenticación
- **JWT HS256** con secret key de 32+ caracteres
- **Expiración:** 30 minutos
- **Refresh:** Re-login necesario
- **Storage:** localStorage (frontend)

### Autorización (RBAC)
- **144 permisos** configurados
- **4 roles:** Administrador, Digitalizador, Revisor, Consultor
- **9 módulos** protegidos
- **4 acciones:** create, read, update, delete

### Hashing de Contraseñas
- **Algoritmo:** bcrypt
- **Rounds:** 12 (2^12 = 4096 iterations)
- **Salt:** Automático por bcrypt

### Rate Limiting
- **Límite:** 100 requests / minuto por IP
- **Storage:** In-memory dict (producción: Redis)
- **Headers:** X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

### Security Headers
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### CORS
- **Orígenes permitidos:** http://localhost:5173, http://localhost:3000
- **Credenciales:** Habilitadas
- **Métodos:** Todos
- **Headers:** Todos

---

## 📈 Escalabilidad

### Horizontal Scaling
- Cada microservicio puede escalarse independientemente
- Load balancer distribuye tráfico
- Stateless services (JWT en cliente)

### Vertical Scaling
- Aumentar recursos de containers Docker
- Pool de conexiones PostgreSQL configurable (5-20)

### Caching Strategy
- **Redis** para cache de reportes (TTL: 5 minutos)
- **Redis** para sesiones activas
- **CDN** para assets estáticos (futuro)

### Database Optimization
- **Índices** en columnas frecuentes (email, fecha, usuario_id)
- **Paginación** en listados (skip/limit)
- **Queries optimizadas** con agregaciones SQL
- **Connection pooling** (SQLAlchemy)

### Future Improvements
- **Kubernetes** para orquestación avanzada
- **Message Queue** (RabbitMQ/Kafka) para procesamiento asíncrono
- **CDN** para distribuir assets
- **Read replicas** de PostgreSQL
- **Elasticsearch** para búsquedas full-text
- **Prometheus + Grafana** para monitoreo

---

## 📊 Métricas del Sistema

| Métrica | Valor |
|---------|-------|
| **Microservicios** | 7 |
| **Endpoints totales** | ~50+ |
| **Tablas BD** | 14 |
| **Índices BD** | ~25 |
| **Permisos RBAC** | 144 |
| **Security Headers** | 7 |
| **Containers Docker** | 10 |
| **Puerto frontend** | 5173 |
| **Puertos backend** | 8000-8007 |

---

## 🔗 Documentos Relacionados

- `esquema-arquitectura.puml` - Diagrama de microservicios
- `arquitectura-capas.puml` - Diagrama de capas
- `diagrama-componentes.puml` - Componentes detallados
- `../diagramas/01-proceso-autenticacion.puml` - Flujo de autenticación
- `base-datos-fisica.md` - Estructura de base de datos

---

**Última actualización:** 9 de diciembre de 2025  
**Versión:** 1.0.0  
**Autor:** Equipo Sacra360

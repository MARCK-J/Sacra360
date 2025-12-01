# AuthProfiles Service - Sistema Sacra360

Microservicio de autenticación y gestión de perfiles de usuario para el Sistema de Gestión de Archivos Sacramentales.

## 📋 Descripción

El servicio AuthProfiles es el núcleo de seguridad del sistema Sacra360. Gestiona la autenticación de usuarios, control de acceso basado en roles (RBAC), auditoría de accesos y administración de perfiles de usuario.

**Puerto:** `8004`

## 🏗️ Arquitectura

```
AuthProfiles-service/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Aplicación FastAPI principal
│   ├── database.py                  # Configuración SQLAlchemy + PostgreSQL
│   ├── dto/
│   │   └── auth_dto.py             # Modelos Pydantic (Request/Response)
│   ├── entities/
│   │   └── user_entity.py          # Modelos SQLAlchemy (Usuario, Rol, Auditoria)
│   ├── routers/
│   │   ├── auth_router_adapted.py  # Endpoints de autenticación
│   │   ├── usuarios_router.py      # CRUD de usuarios
│   │   └── auditoria_router.py     # Logs de auditoría
│   └── utils/
│       └── auth_utils.py           # Funciones JWT, hashing, validaciones
├── update_passwords.py              # Script para migrar contraseñas a bcrypt
├── .env                            # Variables de entorno
└── README.md
```

## 🔑 Características Principales

### 1. **Autenticación JWT**
- Login con email y contraseña
- Tokens JWT con expiración de 30 minutos
- Algoritmo: HS256
- Hashing de contraseñas: bcrypt

### 2. **Sistema de Roles (RBAC)**
Roles disponibles:
- **Administrador** (id: 1): Acceso total al sistema
- **Digitalizador** (id: 2): Digitalización de documentos
- **Revisor** (id: 3): Revisión OCR y validación
- **Consultor** (id: 4): Solo lectura

### 3. **Gestión de Usuarios**
- CRUD completo de usuarios
- Activación/desactivación de cuentas
- Cambio de contraseña
- Asignación de roles
- Búsqueda y filtrado avanzado

### 4. **Auditoría de Accesos**
- Registro automático de login/logout
- Log de acciones por módulo
- Tracking de intentos fallidos
- Registro de IP de origen
- Timestamps con zona horaria

## 🗄️ Modelos de Datos

### Usuario (usuarios)
```python
id_usuario: int (PK)
nombre: str(100)
apellido_paterno: str(100)
apellido_materno: str(100)
email: str(255) UNIQUE
contrasenia_hash: str(255)
rol_id: int (FK -> roles)
activo: bool
fecha_creacion: datetime
ultima_sesion: datetime
```

### Rol (roles)
```python
id_rol: int (PK)
nombre: str(50) UNIQUE
descripcion: text
activo: bool
```

### Auditoría (auditoria_accesos)
```python
id_auditoria: int (PK)
usuario_id: int (FK -> usuarios)
accion: str(100)
modulo: str(100)
detalle: text
fecha_hora: datetime
ip_origen: str(50)
exitoso: bool
```

## 🚀 Endpoints Principales

### Autenticación
```
POST   /api/v1/auth/login              # Login de usuario
POST   /api/v1/auth/register           # Registro de nuevo usuario
POST   /api/v1/auth/logout             # Logout (registra en auditoría)
POST   /api/v1/auth/change-password    # Cambiar contraseña
GET    /api/v1/auth/me                 # Obtener usuario actual
```

### Usuarios
```
GET    /api/v1/usuarios                # Listar usuarios (paginado)
POST   /api/v1/usuarios                # Crear usuario (Admin)
GET    /api/v1/usuarios/{id}           # Obtener usuario por ID
PUT    /api/v1/usuarios/{id}           # Actualizar usuario (Admin)
DELETE /api/v1/usuarios/{id}           # Eliminar usuario (Admin)
PATCH  /api/v1/usuarios/{id}/toggle    # Activar/desactivar usuario
GET    /api/v1/usuarios/roles/listar   # Listar roles disponibles
```

### Auditoría
```
GET    /api/v1/auditoria               # Listar logs (filtros avanzados)
GET    /api/v1/auditoria/stats         # Estadísticas de accesos
GET    /api/v1/auditoria/acciones      # Tipos de acciones registradas
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# Base de datos PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=lolsito101
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sacra360

# JWT
SECRET_KEY=tu_clave_secreta_super_segura_de_al_menos_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Base de Datos
El servicio se conecta a PostgreSQL con las siguientes configuraciones:
- **Pool size:** 5 conexiones
- **Max overflow:** 10 conexiones adicionales
- **Pool pre-ping:** Habilitado (verifica conexiones antes de usar)

## 📦 Instalación y Ejecución

### 1. Instalar dependencias
```bash
cd BACKEND/server-sacra360/AuthProfiles-service
pip install -r requirements.txt
```

Dependencias principales:
- fastapi
- uvicorn[standard]
- sqlalchemy
- psycopg2-binary
- python-jose[cryptography]
- passlib[bcrypt]
- python-multipart
- pydantic

### 2. Configurar base de datos
```bash
# Asegurarse de que PostgreSQL está corriendo
# Crear la base de datos si no existe
createdb sacra360

# Ejecutar script de creación de tablas (si es necesario)
psql -U postgres -d sacra360 -f ../../sql/Database.sql
```

### 3. Migrar contraseñas a bcrypt (si vienes de otra versión)
```bash
python update_passwords.py
```

### 4. Ejecutar el servicio
```bash
uvicorn app.main:app --reload --port 8004 --host 0.0.0.0
```

El servicio estará disponible en:
- **API:** http://localhost:8004
- **Swagger Docs:** http://localhost:8004/docs
- **ReDoc:** http://localhost:8004/redoc

## 🔐 Seguridad

### Autenticación
1. El usuario envía credenciales (email + password)
2. Se verifica el hash bcrypt de la contraseña
3. Se genera un JWT con información del usuario y rol
4. El token expira en 30 minutos
5. Todos los endpoints protegidos requieren el token en el header:
   ```
   Authorization: Bearer <token>
   ```

### Protección de Endpoints
- Los endpoints de usuarios requieren rol de **Administrador**
- Los endpoints de auditoría son accesibles para usuarios autenticados
- El middleware `get_current_user` valida el token en cada request

### Registro de Auditoría
Todas las acciones críticas se registran automáticamente:
- Login exitoso
- Login fallido
- Logout
- Creación de usuarios
- Modificación de usuarios
- Eliminación de usuarios
- Cambios de contraseña

## 🧪 Usuarios de Prueba

Los usuarios por defecto se crean con el script `sql/Create_Users_All_Roles.sql`:

| Email | Contraseña | Rol | Descripción |
|-------|-----------|-----|-------------|
| admin@sacra360.com | Admin123! | Administrador | Acceso total |
| digitalizador@sacra360.com | Digit123! | Digitalizador | Digitalización |
| revisor@sacra360.com | Reviso123! | Revisor | Revisión OCR |
| consultor@sacra360.com | Consul123! | Consultor | Solo lectura |

## 📊 Monitoreo y Logs

### Health Check
```bash
curl http://localhost:8004/health
```

### Logs del Servicio
El servicio utiliza `logging` de Python. Los logs incluyen:
- Inicio/detención del servicio
- Errores de autenticación
- Errores de base de datos
- Acciones de usuarios

## 🔄 Integración con Frontend

El frontend React se conecta al servicio usando:
```javascript
// frontend/.env
VITE_AUTH_API_URL=http://localhost:8004

// Ejemplo de login
const response = await axios.post(
  `${import.meta.env.VITE_AUTH_API_URL}/api/v1/auth/login`,
  { email, password }
)

// Token se almacena en localStorage
localStorage.setItem('token', response.data.access_token)
```

## 🛠️ Desarrollo

### Estructura de DTOs (Pydantic)
Todos los request/response usan modelos Pydantic para validación automática:
- `LoginRequest`, `LoginResponse`
- `RegisterRequest`, `RegisterResponse`
- `UsuarioResponse`
- `ChangePasswordRequest`
- `AuditoriaResponse`

### Utilidades (auth_utils.py)
```python
verify_password(plain, hashed)      # Verificar contraseña bcrypt
get_password_hash(password)         # Hashear contraseña
create_access_token(data, expires)  # Crear JWT
get_current_user()                  # Dependency para FastAPI
```

### Testing
```bash
# Ejecutar todos los tests
pytest tests/

# Test específico de autenticación
pytest tests/test_auth.py -v
```

## 📝 Notas Importantes

1. **Seguridad del SECRET_KEY**: Cambiar el SECRET_KEY en producción por uno generado criptográficamente
   ```python
   import secrets
   secrets.token_urlsafe(32)
   ```

2. **CORS**: Actualmente configurado para `localhost:5173` (Vite) y `localhost:3000`. Ajustar en producción.

3. **Expiración de Tokens**: Los tokens expiran en 30 minutos. El frontend debe manejar la renovación o re-login.

4. **Migraciones**: Si cambias los modelos de SQLAlchemy, considera usar Alembic para migraciones de BD.

5. **Contraseñas**: Todas las contraseñas se almacenan hasheadas con bcrypt (12 rounds).

## 🐛 Troubleshooting

### Error: "Could not connect to database"
- Verificar que PostgreSQL está corriendo: `sudo systemctl status postgresql`
- Verificar credenciales en `.env`
- Verificar que la BD `sacra360` existe

### Error: "Invalid credentials"
- Verificar que el usuario existe en la BD
- Ejecutar `update_passwords.py` si las contraseñas no están en bcrypt
- Verificar que el usuario está activo (`activo=true`)

### Error: "Token has expired"
- El token JWT expiró (30 min). Hacer login nuevamente.

### Error: "CORS policy"
- Agregar el origen del frontend en `app.main:CORSMiddleware`

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/)
- [Python-JOSE JWT](https://python-jose.readthedocs.io/)
- [Passlib Bcrypt](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)

## 👥 Equipo de Desarrollo

Proyecto Sacra360 - Sistema de Gestión de Archivos Sacramentales

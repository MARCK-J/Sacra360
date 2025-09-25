# Sacra360 API Backend

API RESTful desarrollada con FastAPI y Pydantic para el sistema Sacra360.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs
- **Pydantic**: Validación robusta de datos de entrada y salida
- **JWT Authentication**: Autenticación segura con tokens
- **Documentación automática**: Swagger UI y ReDoc
- **Validaciones avanzadas**: Esquemas de datos con validaciones personalizadas
- **Manejo de errores**: Respuestas de error consistentes y informativas
- **CORS configurado**: Soporte para aplicaciones frontend
- **Logging**: Sistema de logs para monitoreo
- **Paginación**: Endpoints con soporte de paginación
- **Filtros de búsqueda**: Capacidades de búsqueda y filtrado

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

1. **Clona el repositorio y navega al directorio backend:**
   ```bash
   cd BACKEND
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   - Copia el archivo `.env` y ajusta los valores según tu entorno
   - Cambia el `SECRET_KEY` por uno seguro en producción

## 🚦 Uso

### Iniciar el servidor de desarrollo:

```bash
# Desde el directorio BACKEND
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Acceder a la documentación:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Información de la API**: http://localhost:8000/api/v1/info

## 📚 Estructura del Proyecto

```
BACKEND/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── api/                 # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── users.py         # Endpoints de usuarios
│   │   └── resources.py     # Endpoints de recursos
│   ├── core/                # Configuración central
│   │   ├── __init__.py
│   │   ├── config.py        # Configuraciones de la app
│   │   └── security.py      # Manejo de seguridad y JWT
│   ├── schemas/             # Esquemas Pydantic
│   │   └── __init__.py      # Modelos de validación
│   ├── models/              # Modelos de base de datos (futuro)
│   └── services/            # Lógica de negocio (futuro)
├── requirements.txt         # Dependencias de Python
├── .env                     # Variables de entorno
├── .gitignore              # Archivos ignorados por Git
└── README.md               # Este archivo
```

## 🔗 Endpoints Principales

### Autenticación
- `POST /api/v1/users/register` - Registrar nuevo usuario
- `POST /api/v1/users/login` - Iniciar sesión
- `GET /api/v1/users/me` - Información del usuario actual

### Usuarios
- `GET /api/v1/users/` - Listar usuarios (admin)
- `GET /api/v1/users/{user_id}` - Obtener usuario por ID
- `PUT /api/v1/users/{user_id}` - Actualizar usuario
- `DELETE /api/v1/users/{user_id}` - Eliminar usuario (admin)

### Recursos
- `POST /api/v1/resources/` - Crear recurso
- `GET /api/v1/resources/` - Listar recursos
- `GET /api/v1/resources/{resource_id}` - Obtener recurso por ID
- `PUT /api/v1/resources/{resource_id}` - Actualizar recurso
- `DELETE /api/v1/resources/{resource_id}` - Eliminar recurso

### Sistema
- `GET /health` - Health check
- `GET /` - Información básica de la API
- `GET /api/v1/info` - Información detallada de la API

## 🔐 Autenticación

La API utiliza JWT (JSON Web Tokens) para autenticación:

1. **Registro**: Crea una cuenta con `POST /api/v1/users/register`
2. **Login**: Obtén un token con `POST /api/v1/users/login`
3. **Uso**: Incluye el token en el header: `Authorization: Bearer <token>`

### Ejemplo de uso:

```python
import requests

# Registrar usuario
response = requests.post("http://localhost:8000/api/v1/users/register", json={
    "email": "user@example.com",
    "username": "testuser",
    "password": "Password123!",
    "confirm_password": "Password123!",
    "full_name": "Test User"
})

# Login
response = requests.post("http://localhost:8000/api/v1/users/login", json={
    "username": "testuser",
    "password": "Password123!"
})

token = response.json()["access_token"]

# Usar el token para requests autenticados
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
```

## 📝 Validaciones con Pydantic

El proyecto utiliza Pydantic para validaciones robustas:

### Validaciones de Usuario:
- **Email**: Formato válido de email
- **Username**: 3-50 caracteres, solo alfanuméricos y guiones bajos
- **Password**: Mínimo 8 caracteres, debe incluir mayúscula, minúscula y número
- **Roles**: Enum con valores predefinidos (admin, user, moderator)

### Validaciones de Recursos:
- **Name**: 1-200 caracteres, requerido
- **Description**: Máximo 1000 caracteres, opcional
- **Status**: Enum con valores predefinidos (active, inactive, pending)

### Ejemplos de Respuestas de Error:

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "La contraseña debe tener al menos una mayúscula",
      "type": "value_error"
    }
  ]
}
```

## 🧪 Testing

Para ejecutar tests (próximamente):

```bash
pytest
```

## 🔧 Configuración

### Variables de Entorno (.env):

```env
# Configuración de la aplicación
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Base de datos
DATABASE_URL=sqlite:///./sacra360.db

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## 📈 Próximas Mejoras

- [ ] Integración con base de datos (SQLAlchemy)
- [ ] Tests automatizados
- [ ] Migraciones de base de datos (Alembic)
- [ ] Rate limiting
- [ ] Caching con Redis
- [ ] Logging avanzado
- [ ] Métricas y monitoreo
- [ ] Docker support
- [ ] CI/CD pipeline

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Equipo

- **Desarrollo**: Sacra360 Team
- **Versión**: 1.0.0
- **Estado**: En desarrollo activo

---

### 💡 Notas para el Desarrollo

Este código base te proporciona:

1. **Estructura sólida**: Organización clara y escalable
2. **Validaciones robustas**: Pydantic para entrada y salida de datos
3. **Seguridad**: JWT, validación de contraseñas, manejo de permisos
4. **Documentación**: Swagger UI automático
5. **Manejo de errores**: Respuestas consistentes y informativas
6. **Logging**: Sistema de logs para debugging y monitoreo
7. **CORS**: Configurado para desarrollo frontend
8. **Paginación**: Soporte para listas grandes de datos

**Para personalizar según tu dominio:**

1. Modifica los schemas en `app/schemas/__init__.py`
2. Ajusta los endpoints en `app/api/`
3. Actualiza las validaciones según tus reglas de negocio
4. Configura la base de datos real cuando esté lista
5. Añade nuevos endpoints siguiendo el patrón establecido
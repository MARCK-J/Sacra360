# Endpoint de Instituciones Parroquiales - Sacra360

## Descripción
El endpoint de instituciones parroquiales permite gestionar las diferentes iglesias, parroquias y centros religiosos que forman parte del sistema Sacra360.

## Ubicación del archivo
`app/api/instituciones.py`

## Endpoints implementados

### 1. Crear Institución
- **Método**: `POST`
- **URL**: `/api/v1/instituciones/`
- **Permisos**: Solo administradores
- **Descripción**: Registra una nueva institución parroquial

#### Cuerpo de la petición:
```json
{
  "nombre": "Parroquia San José",
  "direccion": "Av. Principal 123, La Paz",
  "telefono": "+591-2-2234567",
  "email": "info@parroquiasanjose.bo"
}
```

#### Respuesta exitosa (201):
```json
{
  "id_institucion": 1,
  "nombre": "Parroquia San José",
  "direccion": "Av. Principal 123, La Paz",
  "telefono": "+591-2-2234567",
  "email": "info@parroquiasanjose.bo"
}
```

### 2. Listar Instituciones
- **Método**: `GET`
- **URL**: `/api/v1/instituciones/`
- **Permisos**: Todos los usuarios autenticados
- **Parámetros de consulta**:
  - `skip`: Número de registros a omitir (default: 0)
  - `limit`: Número máximo de registros (default: 10, max: 100)
  - `nombre`: Filtrar por nombre de institución

#### Ejemplo de petición:
```
GET /api/v1/instituciones/?skip=0&limit=10&nombre=San
```

#### Respuesta exitosa (200):
```json
[
  {
    "id_institucion": 1,
    "nombre": "Parroquia San José",
    "direccion": "Av. Principal 123, La Paz",
    "telefono": "+591-2-2234567",
    "email": "info@parroquiasanjose.bo"
  }
]
```

### 3. Obtener Institución por ID
- **Método**: `GET`
- **URL**: `/api/v1/instituciones/{institucion_id}`
- **Permisos**: Todos los usuarios autenticados

#### Respuesta exitosa (200):
```json
{
  "id_institucion": 1,
  "nombre": "Parroquia San José",
  "direccion": "Av. Principal 123, La Paz",
  "telefono": "+591-2-2234567",
  "email": "info@parroquiasanjose.bo"
}
```

### 4. Actualizar Institución
- **Método**: `PUT`
- **URL**: `/api/v1/instituciones/{institucion_id}`
- **Permisos**: Solo administradores

#### Cuerpo de la petición (campos opcionales):
```json
{
  "nombre": "Nuevo nombre",
  "direccion": "Nueva dirección",
  "telefono": "+591-2-9999999",
  "email": "nuevo@email.bo"
}
```

### 5. Eliminar Institución
- **Método**: `DELETE`
- **URL**: `/api/v1/instituciones/{institucion_id}`
- **Permisos**: Solo administradores

#### Respuesta exitosa (200):
```json
{
  "message": "Institución con ID 1 eliminada exitosamente"
}
```

### 6. Buscar Instituciones por Nombre
- **Método**: `GET`
- **URL**: `/api/v1/instituciones/search/by-name`
- **Permisos**: Todos los usuarios autenticados
- **Parámetros**: `q` (término de búsqueda, mínimo 2 caracteres)

#### Ejemplo:
```
GET /api/v1/instituciones/search/by-name?q=San
```

### 7. Estadísticas de Instituciones
- **Método**: `GET`
- **URL**: `/api/v1/instituciones/stats/summary`
- **Permisos**: Administradores y sacerdotes

#### Respuesta exitosa (200):
```json
{
  "total_instituciones": 2,
  "con_telefono": 2,
  "con_email": 2,
  "porcentaje_contacto_completo": 100.0
}
```

## Permisos por Rol

### 👑 Administrador
- ✅ Crear instituciones
- ✅ Listar instituciones
- ✅ Ver institución específica
- ✅ Actualizar instituciones
- ✅ Eliminar instituciones
- ✅ Buscar instituciones
- ✅ Ver estadísticas

### 👨‍💼 Sacerdote
- ❌ Crear instituciones
- ✅ Listar instituciones
- ✅ Ver institución específica
- ❌ Actualizar instituciones
- ❌ Eliminar instituciones
- ✅ Buscar instituciones
- ✅ Ver estadísticas

### 👥 Secretario/Consultor
- ❌ Crear instituciones
- ✅ Listar instituciones
- ✅ Ver institución específica
- ❌ Actualizar instituciones
- ❌ Eliminar instituciones
- ✅ Buscar instituciones
- ❌ Ver estadísticas

## Validaciones Implementadas

### Campos requeridos
- `nombre`: 3-100 caracteres, único en el sistema

### Campos opcionales
- `direccion`: máximo 150 caracteres
- `telefono`: solo números, espacios, guiones y +
- `email`: formato de email válido, máximo 100 caracteres

### Validaciones de negocio
- No puede haber dos instituciones con el mismo nombre
- El teléfono debe tener formato válido
- Al eliminar una institución, se debe verificar que no tenga sacramentos asociados (TODO)

## Datos de Ejemplo Incluidos

El sistema incluye dos instituciones de ejemplo:

1. **Parroquia San José**
   - Dirección: Av. Principal 123, La Paz
   - Teléfono: +591-2-2234567
   - Email: info@parroquiasanjose.bo

2. **Catedral Metropolitana**
   - Dirección: Plaza Murillo S/N, La Paz
   - Teléfono: +591-2-2280123
   - Email: catedral@iglesia.bo

## Integración con el Sistema

### Relacionado con Sacramentos
Las instituciones están diseñadas para ser referenciadas en los registros de sacramentos como el lugar donde se realizó la ceremonia.

### Base de Datos
Actualmente usa almacenamiento en memoria (`fake_instituciones_db`). Para producción, debe integrarse con la base de datos real usando SQLAlchemy.

### Autenticación
Utiliza el sistema de autenticación existente (`get_current_user`) para validar permisos.

## Códigos de Respuesta HTTP

- **200**: Operación exitosa
- **201**: Institución creada exitosamente
- **400**: Error de validación o institución duplicada
- **401**: No autenticado
- **403**: Sin permisos suficientes
- **404**: Institución no encontrada
- **422**: Error de validación de datos

## Próximos Pasos

1. **Integración con Base de Datos**: Reemplazar almacenamiento en memoria por SQLAlchemy
2. **Relaciones**: Conectar con sacramentos y otros módulos
3. **Geolocalización**: Agregar coordenadas GPS para funcionalidades GIS
4. **Imágenes**: Permitir subir fotos de las instituciones
5. **Horarios**: Agregar horarios de misas y actividades
6. **Capacidad**: Agregar información sobre capacidad y servicios disponibles

## Pruebas

### Archivo de pruebas
- `tests/test_instituciones.py`: Pruebas unitarias
- `test_instituciones_manual.py`: Pruebas manuales de verificación

### Ejecutar pruebas
```bash
# Pruebas manuales básicas
python test_instituciones_manual.py

# Pruebas con pytest (cuando esté configurado)
pytest tests/test_instituciones.py -v
```
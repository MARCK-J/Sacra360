# Validación de Duplicados - Sacra360

## 📋 Resumen

Se implementó un sistema completo de validación de duplicados para **Personas** y **Documentos** en los módulos CRUD y de digitalización, con validación tanto en **Backend** como en **Frontend**.

---

## 🗄️ Backend

### 1. Base de Datos - Constraints UNIQUE

**Archivo:** `BACKEND/sql/Migration_Add_Unique_Constraints.sql`

Se agregaron constraints únicos para prevenir duplicados a nivel de base de datos:

#### Tabla `personas`
```sql
ALTER TABLE personas 
ADD CONSTRAINT personas_datos_basicos_unique 
UNIQUE (nombres, apellido_paterno, apellido_materno, fecha_nacimiento);
```
Una persona es única por: nombres + apellidos + fecha de nacimiento

#### Tabla `sacramentos`
```sql
ALTER TABLE sacramentos 
ADD CONSTRAINT sacramentos_unico_por_registro 
UNIQUE (persona_id, tipo_id, fecha_sacramento, libro_id);
```
Evita registrar el mismo sacramento dos veces

> **Nota:** Los documentos digitalizados y resultados OCR NO tienen restricciones de duplicados, ya que pueden necesitar reprocesarse o subirse múltiples veces durante el flujo de trabajo.

---

### 2. Servicios Backend

#### PersonaService - `persona_service.py`

**Método nuevo:** `check_duplicate()`
```python
def check_duplicate(
    db: Session,
    nombres: str,
    apellido_paterno: str,
    apellido_materno: str,
    fecha_nacimiento: date,
    exclude_id: Optional[int] = None
) -> Optional[Persona]:
```

**Modificaciones:**
- `create()`: Valida duplicados antes de crear
- `update()`: Valida duplicados antes de actualizar
- Manejo de `IntegrityError` para constraints de BD

**Respuesta en caso de duplicado (HTTP 409):**
```json
{
  "message": "Ya existe una persona con los mismos datos",
  "persona_existente": {
    "id": 123,
    "nombres": "Juan",
    "apellido_paterno": "Pérez",
    "apellido_materno": "García",
    "fecha_nacimiento": "1990-05-15"
  }
}
```

---

### 3. Endpoints API

#### Personas - `/api/v1/personas/check-duplicate`

**Método:** `POST`

**Query Params:**
- `nombres` (required)
- `apellido_paterno` (required)
- `apellido_materno` (required)
- `fecha_nacimiento` (required, formato: YYYY-MM-DD)
- `exclude_id` (optional, para updates)

**Respuesta exitosa:**
```json
{
  "exists": true,
  "persona": {
    "id_persona": 123,
    "nombres": "Juan",
    "apellido_paterno": "Pérez",
    "apellido_materno": "García",
    "fecha_nacimiento": "1990-05-15",
    ...
  }
}
```

**Respuesta sin duplicado:**
```json
{
  "exists": false,
  "persona": null
}
```

---

## 🖥️ Frontend

### 1. Formulario de Personas - `Personas.jsx`

**Características implementadas:**

✅ **Validación en tiempo real con debounce (800ms)**
- Se verifica automáticamente mientras el usuario escribe
- Solo valida cuando se tienen todos los campos críticos

✅ **Indicador visual de validación**
```jsx
{isCheckingDuplicate && (
  <div className="bg-blue-50 border-l-4 border-blue-400">
    Verificando duplicados...
  </div>
)}
```

✅ **Alerta de duplicado encontrado**
```jsx
{duplicateAlert && (
  <div className="bg-yellow-50 border-l-4 border-yellow-400">
    Posible Duplicado Encontrado
    ...
  </div>
)}
```

✅ **Confirmación antes de guardar**
- Si hay duplicado, solicita confirmación al usuario
- Puede proceder o cancelar el registro

**Flujo de validación:**
1. Usuario completa campos → Debounce 800ms
2. Llamada a `/check-duplicate`
3. Si existe: Muestra alerta amarilla con datos del duplicado
4. Al enviar: Pide confirmación si hay duplicado
5. Backend valida nuevamente al crear

---

### 2. Formulario de Digitalización - `Digitalizacion.jsx`

> **Nota:** La digitalización NO valida duplicados de archivos, permitiendo reprocesar documentos si es necesario.

**Características implementadas:**

✅ **Validación de tipo y tamaño de archivo**
```javascript
const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
const maxSize = 50 * 1024 * 1024 // 50MB
```

✅ **Manejo de errores del servidor**
```javascript
if (!response.ok) {
  newUploadedFiles.push({
    fileName: file.name,
    status: 'error',
    error: `Error ${response.status}`
  })
}
```

---

## 🔒 Seguridad y Validación

### Niveles de Validación

1. **Frontend (UX):** Validación inmediata para mejor experiencia
2. **Backend (API):** Validación antes de INSERT/UPDATE
3. **Base de Datos (Constraints):** Última capa de seguridad

### Casos de Borde Cubiertos

✅ Bypass de validación frontend (constraints de BD lo previenen)
✅ Peticiones concurrentes (constraint UNIQUE es atómico)
✅ Updates sin modificar campos críticos (exclude_id en validación)
✅ Documentos pueden reprocesarse (sin restricción de duplicados)

---

## 📝 Aplicar Migration

Para aplicar los constraints a la base de datos:

```bash
# Conectar a PostgreSQL
psql -U postgres -d sacra360_db

# Ejecutar migration
\i BACKEND/sql/Migration_Add_Unique_Constraints.sql
```

O usando Docker:
```bash
docker exec -i <postgres_container> psql -U postgres -d sacra360_db < BACKEND/sql/Migration_Add_Unique_Constraints.sql
```

---

## 🧪 Pruebas

### Probar validación de personas

1. **Frontend:**
   - Ir a `/personas`
   - Completar formulario con datos existentes
   - Observar alerta de duplicado en tiempo real

2. **Backend directo:**
```bash
curl -X POST "http://localhost:8002/api/v1/personas/check-duplicate?nombres=Juan&apellido_paterno=Perez&apellido_materno=Garcia&fecha_nacimiento=1990-05-15"
```

3. **Intentar crear duplicado:**
```bash
curl -X POST "http://localhost:8002/api/v1/personas/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Juan",
    "apellido_paterno": "Perez",
    "apellido_materno": "Garcia",
    "fecha_nacimiento": "1990-05-15",
    "lugar_nacimiento": "Lima",
    "nombre_padre": "Pedro",
    "nombre_madre": "Maria"
  }'
```

Debería retornar `409 Conflict`

---

## 🔄 Próximas Mejoras

- [ ] Agregar fuzzy matching para nombres similares (Juan/Joan, García/Garcia)
- [ ] Implementar merge de registros duplicados de personas
- [ ] Dashboard de duplicados detectados y resueltos
- [ ] Logs de auditoría para intentos de duplicados en sacramentos
- [ ] Sistema de versionado para documentos reprocesados

---

## 📚 Referencias

- **Migration SQL:** `BACKEND/sql/Migration_Add_Unique_Constraints.sql`
- **PersonaService:** `BACKEND/server-sacra360/Documents-service/app/services/persona_service.py`
- **PersonaController:** `BACKEND/server-sacra360/Documents-service/app/controllers/persona_controller.py`
- **Frontend Personas:** `FRONTEND/src/pages/Personas.jsx`
- **Frontend Digitalización:** `FRONTEND/src/pages/Digitalizacion.jsx`

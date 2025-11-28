# Sistema de Registro de Sacramentos - Lógica Correcta

## 📌 Concepto Fundamental

El sistema es para registrar **SACRAMENTOS** (no solo personas). Una persona puede tener múltiples sacramentos a lo largo de su vida.

## ✅ Lógica Correcta

### Personas
- **Una persona física = Una fila en tabla `personas`**
- Juanito Pérez → 1 registro en tabla personas
- Puede tener múltiples sacramentos asociados (bautizo, confirmación, matrimonio)
- **NO hay validación de duplicados en personas** (pueden existir múltiples personas con mismo nombre)

### Sacramentos  
- **Una persona NO puede tener el mismo sacramento dos veces**
- Constraint: `UNIQUE (persona_id, tipo_id, fecha_sacramento, libro_id)`
- Ejemplos válidos:
  - Juanito Pérez → 1 bautizo + 1 confirmación + 1 matrimonio ✅
- Ejemplos inválidos:
  - Juanito Pérez → 2 bautizos ❌
  - Juanito Pérez → 2 confirmaciones en mismo libro ❌

## 🔄 Flujo de Registro (Usuario)

### Pantalla: **Registros.jsx** (Principal)

1. **Selección de Contexto** (ComboBoxes):
   ```
   [Tipo de Sacramento ▼] → Bautizo / Confirmación / Matrimonio
   [Libro              ▼] → Bautizos 2024 / Confirmaciones 2024 / etc.
   [Parroquia          ▼] → San Juan / Catedral Metropolitana / etc.
   ```

2. **Formulario de Datos** (según tipo de sacramento):
   
   **Para Bautizo/Confirmación:**
   - Nombres de la persona
   - Apellido paterno
   - Apellido materno
   - Fecha de nacimiento
   - Lugar de nacimiento
   - Nombre del padre
   - Nombre de la madre
   - Fecha del sacramento
   - Padrino
   - Ministro
   - Foja y número

   **Para Matrimonio:**
   - Datos del esposo (nombres, apellidos, padres)
   - Datos de la esposa (nombres, apellidos, padres)
   - Fecha del matrimonio
   - Lugar
   - Padrino, ministro
   - Registro civil

3. **Validación al Guardar**:
   - ✅ Buscar si persona ya existe (por nombres + apellidos + fecha nacimiento)
   - ✅ Si existe, reutilizar `persona_id`
   - ✅ Si no existe, crear nueva persona
   - ✅ Validar que esa persona NO tenga ese sacramento ya registrado
   - ❌ Si ya tiene ese sacramento → mostrar alerta y NO permitir guardar
   - ✅ Si no tiene ese sacramento → guardar en tabla `sacramentos`

## 🗄️ Base de Datos

### Tablas Principales

```sql
personas (
  id_persona,
  nombres,
  apellido_paterno,
  apellido_materno,
  fecha_nacimiento,
  lugar_nacimiento,
  nombre_padre,
  nombre_madre
)
-- Sin constraint UNIQUE (permitir búsqueda pero no forzar unicidad)

sacramentos (
  id_sacramento,
  persona_id,         -- FK a personas
  tipo_id,            -- FK a tipos_sacramentos (1=Bautizo, 2=Confirmación, 3=Matrimonio)
  usuario_id,         -- Quién registró
  institucion_id,     -- En qué parroquia
  libro_id,           -- En qué libro
  fecha_sacramento,   -- Cuándo se hizo el sacramento
  fecha_registro
)
-- CON constraint UNIQUE (persona_id, tipo_id, fecha_sacramento, libro_id)
```

## 🔧 Backend - Endpoints Necesarios

### Personas
- `GET /api/v1/personas` - Listar todas
- `GET /api/v1/personas/search?nombres=Juan&apellido_paterno=Perez&fecha_nacimiento=1990-05-15` - Buscar persona existente
- `POST /api/v1/personas` - Crear nueva persona
- `GET /api/v1/personas/{id}` - Ver detalles + historial de sacramentos

### Sacramentos
- `GET /api/v1/tipos-sacramentos` - Listar tipos (Bautizo, Confirmación, Matrimonio)
- `GET /api/v1/instituciones` - Listar parroquias
- `GET /api/v1/libros` - Listar libros
- `GET /api/v1/sacramentos/check-duplicate?persona_id=1&tipo_id=1&libro_id=5` - Validar duplicado
- `POST /api/v1/sacramentos` - Registrar nuevo sacramento (con validación de duplicados)
- `GET /api/v1/sacramentos?persona_id=1` - Historial de sacramentos de una persona

### Detalles por Tipo
- `POST /api/v1/detalles-bautizo` - Guardar detalles específicos de bautizo
- `POST /api/v1/detalles-confirmacion` - Guardar detalles de confirmación
- `POST /api/v1/detalles-matrimonio` - Guardar detalles de matrimonio

## 💻 Frontend - Módulos

### 1. **Registros.jsx** (Pantalla Principal)
- **Propósito**: Registrar nuevos sacramentos
- **Flujo**: Sacramento → Libro → Parroquia → Datos persona(s) → Guardar
- **Validación**: Evitar sacramento duplicado

### 2. **Personas.jsx** (Gestión)
- **Propósito**: Buscar y ver personas registradas
- **Funciones**: 
  - Búsqueda de personas
  - Ver historial de sacramentos de una persona
  - Editar datos de persona
- **NO se usa para**: Registrar sacramentos (eso va en Registros.jsx)

### 3. **Digitalizacion.jsx** (OCR)
- **Propósito**: Subir fotos de libros antiguos
- **Funciones**:
  - Upload de imágenes
  - Procesar con OCR
  - Validar resultados
- **Flujo posterior**: Los datos validados del OCR se convierten en registros de sacramentos

## 📊 Ejemplo Completo

### Caso: Registro de Juanito Pérez

**Paso 1 - Bautizo (1995)**:
```
Registros.jsx:
  Sacramento: Bautizo
  Libro: Bautizos 1995
  Parroquia: San Juan
  
  Datos:
    Nombres: Juanito
    Apellido Paterno: Pérez
    Apellido Materno: García
    Fecha Nacimiento: 1995-03-15
    ...
  
Backend:
  1. Buscar persona (Juanito Pérez García, 1995-03-15) → No existe
  2. Crear en tabla personas → id_persona = 1
  3. Validar duplicado sacramento (persona_id=1, tipo=Bautizo) → No existe
  4. Crear en tabla sacramentos (persona_id=1, tipo_id=1, ...)
  5. Crear en tabla detalles_bautizo (sacramento_id=X, padrino, ministro, ...)
```

**Paso 2 - Confirmación (2007)**:
```
Registros.jsx:
  Sacramento: Confirmación
  Libro: Confirmaciones 2007
  Parroquia: Catedral
  
  Datos:
    Nombres: Juanito
    Apellido Paterno: Pérez
    Apellido Materno: García
    Fecha Nacimiento: 1995-03-15
    ...

Backend:
  1. Buscar persona (Juanito Pérez García, 1995-03-15) → ¡Existe! id_persona = 1
  2. Reutilizar persona existente
  3. Validar duplicado sacramento (persona_id=1, tipo=Confirmación) → No existe
  4. Crear en tabla sacramentos (persona_id=1, tipo_id=2, ...)
  5. Crear en tabla detalles_confirmacion (sacramento_id=Y, ...)
```

**Paso 3 - Intento de 2do Bautizo (ERROR)**:
```
Registros.jsx:
  Sacramento: Bautizo
  Libro: Bautizos 2024
  ...
  
Backend:
  1. Buscar persona → Existe (id=1)
  2. Validar duplicado sacramento (persona_id=1, tipo=Bautizo) → ¡YA EXISTE!
  3. Retornar ERROR 409: "Esta persona ya tiene un bautizo registrado"
  
Frontend:
  Mostrar alerta: ⚠️ Juanito Pérez García ya tiene un bautizo registrado
                   Fecha: 1995-05-20
                   Libro: Bautizos 1995
```

## ❌ Lo que NO debe hacerse

1. ❌ Impedir crear personas con mismo nombre → Pueden existir 2 Juan Pérez diferentes
2. ❌ Validar duplicados en módulo Personas.jsx → La validación va en Sacramentos
3. ❌ Permitir registrar 2 bautizos para la misma persona
4. ❌ Confundir Digitalizacion.jsx (OCR) con Registros.jsx (registro manual)

## ✅ Resumen

| Concepto | Puede Duplicarse | Validación |
|----------|------------------|------------|
| Personas | ✅ Sí (mismo nombre, diferente persona física) | Búsqueda por similitud, no forzar unicidad |
| Sacramentos | ❌ No (misma persona + mismo tipo) | Constraint UNIQUE en BD + validación API |


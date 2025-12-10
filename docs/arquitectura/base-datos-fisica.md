# 📊 Diagrama de Base de Datos Física - Sacra360

## 🗄️ Descripción General

Base de datos relacional PostgreSQL 15 que almacena toda la información del sistema Sacra360: usuarios, sacramentos, documentos digitalizados y resultados de OCR/HTR.

**Archivo:** `07-base-datos-fisica.puml`

---

## 📋 Estructura de Tablas

### 🔐 Módulo de Autenticación y Seguridad

#### 1. **Roles**
```sql
CREATE TABLE Roles (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);
```

**Registros:**
- 1: Administrador (acceso total)
- 2: Digitalizador (subir y procesar documentos)
- 3: Revisor (validar OCR y corregir)
- 4: Consultor (solo lectura)

---

#### 2. **usuarios**
```sql
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    rol_id INTEGER NOT NULL REFERENCES Roles(id_rol),
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    contrasenia TEXT NOT NULL,  -- Hashed con bcrypt (12 rounds)
    fecha_creacion DATE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT true
);

-- Índices
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_rol_id ON usuarios(rol_id);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
```

**Campos importantes:**
- `email`: Único, usado para login
- `contrasenia`: Hash bcrypt, nunca en texto plano
- `activo`: Soft delete (false = desactivado)

---

#### 3. **Auditoria**
```sql
CREATE TABLE Auditoria (
    id_auditoria SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    accion TEXT NOT NULL,
    registro_afectado TEXT NOT NULL,
    Id_registro INTEGER NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_auditoria_usuario_id ON Auditoria(usuario_id);
CREATE INDEX idx_auditoria_fecha ON Auditoria(fecha);
CREATE INDEX idx_auditoria_accion ON Auditoria(accion);
```

**Acciones registradas:**
- `LOGIN` / `LOGOUT` / `LOGIN_FAILED`
- `CREAR_USUARIO` / `ACTUALIZAR_USUARIO` / `ELIMINAR_USUARIO` / `ACTIVAR_USUARIO`
- `CAMBIAR_CONTRASENA`
- `CREAR_SACRAMENTO` / `ACTUALIZAR_SACRAMENTO`
- `VALIDAR_OCR` / `CORREGIR_OCR`

---

### 👥 Módulo de Personas y Sacramentos

#### 4. **personas**
```sql
CREATE TABLE personas (
    id_persona SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    lugar_nacimiento VARCHAR(100) NOT NULL,
    nombre_padre VARCHAR(100) NOT NULL,
    nombre_madre VARCHAR(100) NOT NULL
);

-- Índices
CREATE INDEX idx_personas_nombres_apellidos ON personas(nombres, apellido_paterno, apellido_materno);
CREATE INDEX idx_personas_fecha_nacimiento ON personas(fecha_nacimiento);
```

---

#### 5. **tipos_sacramentos**
```sql
CREATE TABLE tipos_sacramentos (
    id_tipo SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);
```

**Tipos disponibles:**
1. Bautismo
2. Confirmación
3. Matrimonio
4. Primera Comunión
5. Unción de Enfermos

---

#### 6. **InstitucionesParroquias**
```sql
CREATE TABLE InstitucionesParroquias (
    id_institucion SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(150),
    telefono VARCHAR(15),
    email VARCHAR(100)
);
```

---

#### 7. **libros**
```sql
CREATE TABLE libros (
    id_libro SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    observaciones TEXT
);

-- Índices
CREATE INDEX idx_libros_fecha_inicio ON libros(fecha_inicio);
CREATE INDEX idx_libros_fecha_fin ON libros(fecha_fin);
```

**Ejemplos:**
- "Libro de Bautismos 1950-1960"
- "Libro de Matrimonios Parroquia San José 1980-1990"

---

#### 8. **sacramentos**
```sql
CREATE TABLE sacramentos (
    id_sacramento SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL REFERENCES personas(id_persona),
    tipo_id INTEGER NOT NULL REFERENCES tipos_sacramentos(id_tipo),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    institucion_id INTEGER NOT NULL REFERENCES InstitucionesParroquias(id_institucion),
    libro_id INTEGER NOT NULL REFERENCES libros(id_libro),
    fecha_sacramento DATE NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_sacramentos_persona_id ON sacramentos(persona_id);
CREATE INDEX idx_sacramentos_tipo_id ON sacramentos(tipo_id);
CREATE INDEX idx_sacramentos_fecha_sacramento ON sacramentos(fecha_sacramento);
CREATE INDEX idx_sacramentos_libro_id ON sacramentos(libro_id);
```

---

### 📜 Módulo de Detalles de Sacramentos

#### 9. **detalles_bautizo**
```sql
CREATE TABLE detalles_bautizo (
    id_bautizo SERIAL PRIMARY KEY,
    sacramento_id INTEGER NOT NULL REFERENCES sacramentos(id_sacramento),
    padrino VARCHAR(100) NOT NULL,
    ministro VARCHAR(100) NOT NULL,
    foja VARCHAR(10) NOT NULL,
    numero VARCHAR(10) NOT NULL,
    fecha_bautizo DATE NOT NULL
);
```

---

#### 10. **detalles_confirmacion**
```sql
CREATE TABLE detalles_confirmacion (
    id_confirmacion SERIAL PRIMARY KEY,
    sacramento_id INTEGER NOT NULL REFERENCES sacramentos(id_sacramento),
    padrino VARCHAR(100) NOT NULL,
    ministro VARCHAR(100) NOT NULL,
    foja VARCHAR(10) NOT NULL,
    numero VARCHAR(10) NOT NULL,
    fecha_confirmacion DATE NOT NULL
);
```

---

#### 11. **detalles_matrimonio**
```sql
CREATE TABLE detalles_matrimonio (
    id_matrimonio SERIAL PRIMARY KEY,
    sacramento_id INTEGER NOT NULL REFERENCES sacramentos(id_sacramento),
    nombre_esposo VARCHAR(100) NOT NULL,
    nombre_esposa VARCHAR(100) NOT NULL,
    apellido_peterno_esposo VARCHAR(50) NOT NULL,
    apellido_materno_esposo VARCHAR(50) NOT NULL,
    apellido_peterno_esposa VARCHAR(50) NOT NULL,
    apellido_materno_esposa VARCHAR(50) NOT NULL,
    nombre_padre_esposo VARCHAR(100) NOT NULL,
    nombre_madre_esposo VARCHAR(100) NOT NULL,
    nombre_padre_esposa VARCHAR(100) NOT NULL,
    nombre_madre_esposa VARCHAR(100) NOT NULL,
    padrino VARCHAR(100) NOT NULL,
    ministro VARCHAR(100) NOT NULL,
    foja VARCHAR(10) NOT NULL,
    numero VARCHAR(10) NOT NULL,
    reg_civil VARCHAR(100) NOT NULL,
    fecha_matrimonio DATE NOT NULL,
    lugar_matrimonio VARCHAR(100) NOT NULL
);
```

---

### 📄 Módulo de Digitalización y OCR

#### 12. **documento_digitalizado**
```sql
CREATE TABLE documento_digitalizado (
    id_documento SERIAL PRIMARY KEY,
    libros_id INTEGER NOT NULL REFERENCES libros(id_libro),
    tipo_sacramento INTEGER REFERENCES tipos_sacramentos(id_tipo),
    imagen_url TEXT NOT NULL,  -- URL en MinIO
    ocr_texto TEXT NOT NULL,
    modelo_fuente VARCHAR(100) NOT NULL,  -- 'Tesseract', 'HTR', etc.
    confianza DECIMAL(4,3) NOT NULL,  -- 0.000 a 1.000
    fecha_procesamiento TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_documentos_libros_id ON documento_digitalizado(libros_id);
CREATE INDEX idx_documentos_fecha ON documento_digitalizado(fecha_procesamiento);
CREATE INDEX idx_documentos_confianza ON documento_digitalizado(confianza);
```

**Formatos soportados:** JPG, PNG, PDF  
**Storage:** MinIO (S3-compatible)

---

#### 13. **ocr_resultado**
```sql
CREATE TABLE ocr_resultado (
    id_ocr SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documento_digitalizado(id_documento),
    campo VARCHAR(50) NOT NULL,  -- 'nombre', 'fecha', 'padrino', etc.
    valor_extraido TEXT NOT NULL,
    confianza DECIMAL(4,3) NOT NULL,
    fuente_modelo VARCHAR(100) NOT NULL,
    validado BOOLEAN NOT NULL DEFAULT false
);

-- Índices
CREATE INDEX idx_ocr_documento_id ON ocr_resultado(documento_id);
CREATE INDEX idx_ocr_validado ON ocr_resultado(validado);
CREATE INDEX idx_ocr_confianza ON ocr_resultado(confianza);
```

**Campos extraídos comunes:**
- `nombre_completo`
- `fecha_sacramento`
- `lugar`
- `padrino` / `padrinos`
- `ministro`
- `foja`
- `numero`

---

#### 14. **correccion_documento**
```sql
CREATE TABLE correccion_documento (
    id_correccion SERIAL PRIMARY KEY,
    ocr_resultado_id INTEGER NOT NULL REFERENCES ocr_resultado(id_ocr),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    valor_original TEXT NOT NULL,
    valor_corregido TEXT NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_correcciones_ocr_id ON correccion_documento(ocr_resultado_id);
CREATE INDEX idx_correcciones_usuario_id ON correccion_documento(usuario_id);
CREATE INDEX idx_correcciones_fecha ON correccion_documento(fecha);
```

**Propósito:** Trazabilidad completa de correcciones manuales realizadas por revisores.

---

## 🔗 Relaciones Principales

### Relaciones de Autenticación
```
Roles (1) ──── (N) usuarios
usuarios (1) ──── (N) Auditoria
```

### Relaciones de Sacramentos
```
personas (1) ──── (N) sacramentos
tipos_sacramentos (1) ──── (N) sacramentos
usuarios (1) ──── (N) sacramentos (registra)
InstitucionesParroquias (1) ──── (N) sacramentos
libros (1) ──── (N) sacramentos

sacramentos (1) ──── (1) detalles_bautizo
sacramentos (1) ──── (1) detalles_confirmacion
sacramentos (1) ──── (1) detalles_matrimonio
```

### Relaciones de Digitalización
```
libros (1) ──── (N) documento_digitalizado
documento_digitalizado (1) ──── (N) ocr_resultado
ocr_resultado (1) ──── (N) correccion_documento
usuarios (1) ──── (N) correccion_documento (realiza)
```

---

## 📊 Estadísticas de la Base de Datos

| Métrica | Valor |
|---------|-------|
| **Total de Tablas** | 14 |
| **Tablas de Sistema** | 3 (Roles, usuarios, Auditoria) |
| **Tablas de Negocio** | 8 (personas, sacramentos, etc.) |
| **Tablas de Digitalización** | 3 (documentos, OCR, correcciones) |
| **Total de Índices** | ~25 |
| **Foreign Keys** | 18 |
| **Campos con UNIQUE** | 1 (usuarios.email) |

---

## 🔍 Consultas SQL Útiles

### Usuarios activos por rol
```sql
SELECT r.nombre as rol, COUNT(*) as total
FROM usuarios u
JOIN Roles r ON u.rol_id = r.id_rol
WHERE u.activo = true
GROUP BY r.nombre;
```

### Sacramentos por tipo (últimos 30 días)
```sql
SELECT ts.nombre, COUNT(*) as cantidad
FROM sacramentos s
JOIN tipos_sacramentos ts ON s.tipo_id = ts.id_tipo
WHERE s.fecha_registro >= NOW() - INTERVAL '30 days'
GROUP BY ts.nombre
ORDER BY cantidad DESC;
```

### Documentos pendientes de validación
```sql
SELECT d.id_documento, d.imagen_url, d.confianza
FROM documento_digitalizado d
LEFT JOIN ocr_resultado o ON d.id_documento = o.documento_id
WHERE o.validado = false OR d.confianza < 0.7
ORDER BY d.fecha_procesamiento DESC;
```

### Actividad de usuarios (últimos 7 días)
```sql
SELECT u.nombre, u.apellido_paterno, COUNT(*) as acciones
FROM Auditoria a
JOIN usuarios u ON a.usuario_id = u.id_usuario
WHERE a.fecha >= NOW() - INTERVAL '7 days'
GROUP BY u.id_usuario, u.nombre, u.apellido_paterno
ORDER BY acciones DESC
LIMIT 10;
```

---

## 🛠️ Mantenimiento

### Backup
```bash
# Backup completo
pg_dump -U postgres -d sacra360 -F c -f sacra360_backup_$(date +%Y%m%d).dump

# Backup solo esquema
pg_dump -U postgres -d sacra360 --schema-only -f sacra360_schema.sql
```

### Restore
```bash
pg_restore -U postgres -d sacra360 -F c sacra360_backup_20251209.dump
```

### Vacuum y Analyze (mantenimiento)
```sql
VACUUM ANALYZE usuarios;
VACUUM ANALYZE sacramentos;
VACUUM ANALYZE Auditoria;
```

---

## 📈 Escalabilidad

### Particionamiento (futuro)
La tabla `Auditoria` puede particionarse por fecha para mejorar el rendimiento:

```sql
CREATE TABLE Auditoria_2025 PARTITION OF Auditoria
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Índices adicionales según uso
```sql
-- Si hay muchas búsquedas por nombre completo
CREATE INDEX idx_personas_fulltext ON personas 
USING gin(to_tsvector('spanish', nombres || ' ' || apellido_paterno || ' ' || apellido_materno));

-- Índice compuesto para sacramentos
CREATE INDEX idx_sacramentos_persona_tipo ON sacramentos(persona_id, tipo_id);
```

---

## 🔐 Seguridad

### Políticas de acceso
- ✅ Contraseñas siempre hasheadas (bcrypt, 12 rounds)
- ✅ Email único para evitar duplicados
- ✅ Soft delete (activo=false) para trazabilidad
- ✅ Auditoría de todas las acciones críticas
- ✅ Foreign keys para integridad referencial
- ✅ NOT NULL en campos esenciales

### Usuarios de base de datos
```sql
-- Usuario de aplicación (permisos limitados)
CREATE USER sacra360_app WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO sacra360_app;

-- Usuario de solo lectura (reportes)
CREATE USER sacra360_readonly WITH PASSWORD 'readonly_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sacra360_readonly;
```

---

## 📝 Notas de Implementación

1. **Encoding:** UTF-8 para soportar caracteres especiales en nombres y apellidos
2. **Timezone:** UTC para timestamps, conversión a local en frontend
3. **Pool de conexiones:** Mínimo 5, máximo 20 conexiones
4. **Backup automático:** Diario a las 2:00 AM
5. **Retención de auditoría:** 2 años, luego archivo

---

**Última actualización:** 9 de diciembre de 2025  
**Versión del esquema:** 1.0.0  
**PostgreSQL:** 15.x

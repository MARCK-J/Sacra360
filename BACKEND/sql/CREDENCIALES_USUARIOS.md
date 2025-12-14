# 🔐 CREDENCIALES DE USUARIOS - SISTEMA SACRA360

## ⚠️ IMPORTANTE - SEGURIDAD
Este archivo contiene información sensible. NO compartir públicamente ni subir a repositorios públicos.

---

## 👥 USUARIOS DISPONIBLES

### 🔴 ADMINISTRADORES (Acceso Completo)

#### Usuario 1: Carlos Moron
- **Email:** `admin@sacra360.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Administrador
- **Permisos:** CRUD en todos los módulos

#### Usuario 2: Diego Moron
- **Email:** `diego.moron@ucb.edu.bo`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Administrador
- **Permisos:** CRUD en todos los módulos

#### Usuario 3: Pepe Moron
- **Email:** `diego.moras@gmail.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Administrador
- **Permisos:** CRUD en todos los módulos

#### Usuario 4: María González
- **Email:** `superadmin@sacra360.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Administrador
- **Permisos:** CRUD en todos los módulos

---

### 🟡 DIGITALIZADORES (Carga y Edición de Documentos)

#### Usuario 5: Ana Rodríguez
- **Email:** `revisor@sacra360.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Digitalizador
- **Permisos:** CRU en digitalización, R en otros módulos

#### Usuario 6: Ramon Gómez
- **Email:** `intento@sacra.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Digitalizador
- **Permisos:** CRU en digitalización, R en otros módulos

#### Usuario 7: Orlando Rivera
- **Email:** `consultor1@sacra360.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Digitalizador
- **Permisos:** CRU en digitalización, R en otros módulos

---

### 🟢 VALIDADORES (Revisión OCR)

#### Usuario 8: Pepe Pérez
- **Email:** `digitalizador@sacra360.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Validador
- **Permisos:** CRUD en OCR/validación, CRU en registros

---

### 🔵 USUARIOS (Solo Lectura)

#### Usuario 9: Sofía Gómez
- **Email:** `consultor@sacra360.com`
- **Contraseña:** `[CONTRASEÑA ORIGINAL - Contactar administrador]`
- **Rol:** Usuario
- **Permisos:** Solo lectura en todos los módulos

#### Usuario 10: Carlos Rodríguez ❌ INACTIVO
- **Email:** `admin4@sacra360.com`
- **Estado:** DESACTIVADO
- **Nota:** Este usuario no puede iniciar sesión

---

## 🔧 CÓMO USAR ESTAS CREDENCIALES

### Para Desarrolladores:
1. Ejecutar primero `Database.sql` para crear las tablas
2. Ejecutar `Insert_Usuarios_Roles_Completo.sql` para insertar usuarios
3. Las contraseñas ya están hasheadas, se insertan directamente
4. **NO necesitas saber las contraseñas originales para la migración**

### Para Testing:
Si necesitas las contraseñas en texto plano para probar:
1. Contactar al administrador del proyecto (Diego)
2. Alternativamente, crear nuevos usuarios de prueba:

```sql
-- Crear usuario de prueba con contraseña conocida
-- Primero hashear la contraseña en Python:
-- from passlib.hash import bcrypt
-- print(bcrypt.hash("MiContraseña123!"))

INSERT INTO usuarios (nombre, apellido_paterno, email, contrasenia, rol_id, activo, fecha_creacion)
VALUES ('Test', 'Usuario', 'test@sacra360.com', 
        '$2b$12$TU_HASH_AQUI', 
        1, true, CURRENT_DATE);
```

---

## 🔐 RESETEAR CONTRASEÑAS

### Opción 1: Script Python (Recomendado)
```python
from passlib.hash import bcrypt
import psycopg2

# Conectar a la base de datos
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="sacra360",
    user="postgres",
    password="lolsito101"
)

# Nueva contraseña
nueva_password = "NuevaContraseña123!"
hash_password = bcrypt.hash(nueva_password)

# Actualizar usuario
cursor = conn.cursor()
cursor.execute(
    "UPDATE usuarios SET contrasenia = %s WHERE email = %s",
    (hash_password, "admin@sacra360.com")
)
conn.commit()
print("Contraseña actualizada exitosamente")
```

### Opción 2: Desde Docker
```bash
# Ejecutar script Python dentro del contenedor
docker exec -it sacra360_auth_service python
>>> from passlib.hash import bcrypt
>>> bcrypt.hash("TuNuevaContraseña")
'$2b$12$...'  # Copiar este hash

# Actualizar en la base de datos
docker exec sacra360-postgres psql -U postgres -d sacra360 -c \
  "UPDATE usuarios SET contrasenia = '$2b$12$...' WHERE email = 'admin@sacra360.com';"
```

---

## 📊 RESUMEN DE USUARIOS

| Rol | Cantidad | Activos | Inactivos |
|-----|----------|---------|-----------|
| Administrador | 4 | 4 | 0 |
| Digitalizador | 3 | 3 | 0 |
| Validador | 1 | 1 | 0 |
| Usuario | 2 | 1 | 1 |
| **TOTAL** | **10** | **9** | **1** |

---

## 🚀 INICIO RÁPIDO

### Para tu primer login:
1. Usar cualquier email de administrador (recomendado: `admin@sacra360.com`)
2. Solicitar contraseña al administrador
3. Endpoint: `POST http://localhost:8001/api/v1/auth/login`
4. Body:
```json
{
  "email": "admin@sacra360.com",
  "contrasenia": "TU_CONTRASEÑA_AQUI"
}
```

### Respuesta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id_usuario": 5,
    "email": "admin@sacra360.com",
    "nombre": "Carlos",
    "rol_id": 1,
    "rol_nombre": "Administrador"
  }
}
```

---

## 📝 NOTAS PARA EL EQUIPO

1. **Seguridad:** Las contraseñas están hasheadas con bcrypt (12 rounds)
2. **Migración:** El script SQL incluye los hashes, no necesitan las contraseñas originales
3. **Testing:** Si necesitan crear usuarios de prueba, pueden generar nuevos hashes
4. **Producción:** Cambiar TODAS las contraseñas antes de ir a producción
5. **Backup:** Guardar este archivo en un lugar seguro (no en git público)

---

## 🔒 POLÍTICA DE CONTRASEÑAS

Para nuevos usuarios o reseteos, las contraseñas deben cumplir:
- Mínimo 8 caracteres
- Al menos 1 mayúscula
- Al menos 1 minúscula
- Al menos 1 número
- Al menos 1 carácter especial
- No usar contraseñas comunes

---

**Última actualización:** Diciembre 2025
**Responsable:** Equipo Sacra360
**Contacto:** diego.moron@ucb.edu.bo

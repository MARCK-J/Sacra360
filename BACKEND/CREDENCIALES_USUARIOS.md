# 🔐 CREDENCIALES DE USUARIOS - SISTEMA SACRA360

## Usuarios Creados por Rol

### 👤 1. ADMINISTRADOR
- **Email:** `admin@sacra360.com`
- **Contraseña:** `Admin123!`
- **Rol:** Administrador (id_rol: 1)
- **Nombre:** Carlos Mendoza López
- **Permisos:** Control total del sistema
- **ID Usuario:** 5

---

### 👤 2. REVISOR
- **Email:** `revisor@sacra360.com`
- **Contraseña:** `Revisor123!`
- **Rol:** Revisor (id_rol: 2)
- **Nombre:** Ana Rodríguez Martínez
- **Permisos:** Revisar y validar registros OCR
- **ID Usuario:** 7

---

### 👤 3. DIGITALIZADOR
- **Email:** `digitalizador@sacra360.com`
- **Contraseña:** `Digita123!`
- **Rol:** Digitalizador (id_rol: 3)
- **Nombre:** Juan Pérez García
- **Permisos:** Digitalizar y subir documentos
- **ID Usuario:** 6

---

### 👤 4. CONSULTOR
- **Email:** `consultor@sacra360.com`
- **Contraseña:** `Consul123!`
- **Rol:** Consultor (id_rol: 4)
- **Nombre:** Sofía Gómez Torres
- **Permisos:** Solo lectura/consulta
- **ID Usuario:** 8

---

## 🔗 Endpoint de Login

```bash
POST http://localhost:8004/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@sacra360.com",
  "contrasenia": "Admin123!"
}
```

## 🧪 Ejemplo de Prueba con PowerShell

```powershell
# Login como Administrador
$body = @{
    email = 'admin@sacra360.com'
    contrasenia = 'Admin123!'
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri 'http://localhost:8004/api/v1/auth/login' `
    -Method POST `
    -Body $body `
    -ContentType 'application/json'

$response.Content | ConvertFrom-Json
```

## 🧪 Ejemplo de Prueba con cURL

```bash
# Login como Revisor
curl -X POST "http://localhost:8004/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "revisor@sacra360.com",
    "contrasenia": "Revisor123!"
  }'
```

## ⚠️ IMPORTANTE - SEGURIDAD

1. **Cambiar contraseñas en producción:** Estas son contraseñas de desarrollo/prueba
2. **Política de contraseñas:** Las contraseñas cumplen con:
   - Mínimo 8 caracteres
   - Al menos una mayúscula
   - Al menos una minúscula
   - Al menos un número
   - Al menos un carácter especial
3. **No compartir credenciales** en repositorios públicos
4. **Rotar contraseñas** periódicamente en producción

## 📋 Matriz de Permisos por Rol

| Módulo | Administrador | Revisor | Digitalizador | Consultor |
|--------|--------------|---------|---------------|-----------|
| Digitalización | ✅ CRUD | ✅ R/U | ✅ C/R/U | ❌ Solo R |
| Revisión OCR | ✅ CRUD | ✅ CRUD | ✅ R | ❌ Solo R |
| Registros | ✅ CRUD | ✅ R/U | ✅ R | ❌ Solo R |
| Personas | ✅ CRUD | ✅ R/U | ❌ Solo R | ❌ Solo R |
| Libros | ✅ CRUD | ✅ R/U | ✅ R | ❌ Solo R |
| Usuarios | ✅ CRUD | ❌ | ❌ | ❌ |
| Auditoría | ✅ R | ❌ | ❌ | ❌ |
| Reportes | ✅ R | ✅ R | ❌ | ❌ |

**Leyenda:**
- C = Create (Crear)
- R = Read (Leer)
- U = Update (Actualizar)
- D = Delete (Eliminar)

## 🗄️ Información de Base de Datos

**Tabla:** `usuarios`
**Relación:** `usuarios.rol_id` → `roles.id_rol`

### Roles disponibles:
1. Administrador - Control total
2. Revisor - Validación y revisión
3. Digitalizador - Carga de documentos
4. Consultor - Solo lectura

---

**Fecha de creación:** 28 de Noviembre de 2025  
**Sistema:** Sacra360 - Gestión de Archivos Sacramentales  
**Versión:** 1.0.0

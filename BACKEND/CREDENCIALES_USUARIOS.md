# ­ƒöÉ CREDENCIALES DE USUARIOS - SISTEMA SACRA360

## Usuarios Creados por Rol

### ­ƒæñ 1. ADMINISTRADOR
- **Email:** `admin@sacra360.com`
- **Contrase├▒a:** `Admin123!`
- **Rol:** Administrador (id_rol: 1)
- **Nombre:** Carlos Mendoza L├│pez
- **Permisos:** Control total del sistema
- **ID Usuario:** 5

---
### 🔑 1.1. ADMINISTRADOR NUEVO (USAR ESTE)
- **Email:** `superadmin@sacra360.com`
- **Contraseña:** `Admin2024!`
- **Rol:** Administrador (id_rol: 1)
- **Nombre:** María González López
- **Permisos:** Control total del sistema
- **ID Usuario:** (se asignará automáticamente)
- **NOTA:** ⚠️ Usa este usuario si no recuerdas las otras contraseñas

---
### ­ƒæñ 2. REVISOR
- **Email:** `revisor@sacra360.com`
- **Contrase├▒a:** `Revisor123!`
- **Rol:** Revisor (id_rol: 2)
- **Nombre:** Ana Rodr├¡guez Mart├¡nez
- **Permisos:** Revisar y validar registros OCR
- **ID Usuario:** 7

---

### ­ƒæñ 3. DIGITALIZADOR
- **Email:** `digitalizador@sacra360.com`
- **Contrase├▒a:** `Digita123!`
- **Rol:** Digitalizador (id_rol: 3)
- **Nombre:** Juan P├®rez Garc├¡a
- **Permisos:** Digitalizar y subir documentos
- **ID Usuario:** 6

---

### ­ƒæñ 4. CONSULTOR
- **Email:** `consultor@sacra360.com`
- **Contrase├▒a:** `Consul123!`
- **Rol:** Consultor (id_rol: 4)
- **Nombre:** Sof├¡a G├│mez Torres
- **Permisos:** Solo lectura/consulta
- **ID Usuario:** 8

---

## ­ƒöù Endpoint de Login

```bash
POST http://localhost:8004/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@sacra360.com",
  "contrasenia": "Admin123!"
}
```

## ­ƒº¬ Ejemplo de Prueba con PowerShell

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

## ­ƒº¬ Ejemplo de Prueba con cURL

```bash
# Login como Revisor
curl -X POST "http://localhost:8004/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "revisor@sacra360.com",
    "contrasenia": "Revisor123!"
  }'
```

## ÔÜá´©Å IMPORTANTE - SEGURIDAD

1. **Cambiar contrase├▒as en producci├│n:** Estas son contrase├▒as de desarrollo/prueba
2. **Pol├¡tica de contrase├▒as:** Las contrase├▒as cumplen con:
   - M├¡nimo 8 caracteres
   - Al menos una may├║scula
   - Al menos una min├║scula
   - Al menos un n├║mero
   - Al menos un car├ícter especial
3. **No compartir credenciales** en repositorios p├║blicos
4. **Rotar contrase├▒as** peri├│dicamente en producci├│n

## ­ƒôï Matriz de Permisos por Rol

| M├│dulo | Administrador | Revisor | Digitalizador | Consultor |
|--------|--------------|---------|---------------|-----------|
| Digitalizaci├│n | Ô£à CRUD | Ô£à R/U | Ô£à C/R/U | ÔØî Solo R |
| Revisi├│n OCR | Ô£à CRUD | Ô£à CRUD | Ô£à R | ÔØî Solo R |
| Registros | Ô£à CRUD | Ô£à R/U | Ô£à R | ÔØî Solo R |
| Personas | Ô£à CRUD | Ô£à R/U | ÔØî Solo R | ÔØî Solo R |
| Libros | Ô£à CRUD | Ô£à R/U | Ô£à R | ÔØî Solo R |
| Usuarios | Ô£à CRUD | ÔØî | ÔØî | ÔØî |
| Auditor├¡a | Ô£à R | ÔØî | ÔØî | ÔØî |
| Reportes | Ô£à R | Ô£à R | ÔØî | ÔØî |

**Leyenda:**
- C = Create (Crear)
- R = Read (Leer)
- U = Update (Actualizar)
- D = Delete (Eliminar)

## ­ƒùä´©Å Informaci├│n de Base de Datos

**Tabla:** `usuarios`
**Relaci├│n:** `usuarios.rol_id` ÔåÆ `roles.id_rol`

### Roles disponibles:
1. Administrador - Control total
2. Revisor - Validaci├│n y revisi├│n
3. Digitalizador - Carga de documentos
4. Consultor - Solo lectura

---

**Fecha de creaci├│n:** 28 de Noviembre de 2025  
**Sistema:** Sacra360 - Gesti├│n de Archivos Sacramentales  
**Versi├│n:** 1.0.0
# ­ƒöÉ Sistema de Permisos RBAC - Sacra360

## Ô£à Implementaci├│n Completada

Se ha implementado un sistema completo de **Role-Based Access Control (RBAC)** en el frontend que controla el acceso a m├│dulos y funcionalidades seg├║n el rol del usuario.

## ­ƒôü Archivos Creados

### 1. **Config** - Sistema de permisos
- `src/config/permissions.js` - Definici├│n de permisos CRUD por m├│dulo y rol

### 2. **Context** - Gesti├│n de autenticaci├│n
- `src/context/AuthContext.jsx` - Contexto global de autenticaci├│n

### 3. **Components** - Protecci├│n de rutas y contenido
- `src/components/PrivateRoute.jsx` - Componente para rutas privadas
- `src/components/PermissionGuard.jsx` - Componente para proteger contenido espec├¡fico

### 4. **Hooks** - Utilidades de permisos
- `src/hooks/usePermissions.js` - Hook personalizado para verificar permisos

## ­ƒÄ» Matriz de Permisos Implementada

| M├│dulo | Administrador | Digitalizador | Validador | Usuario |
|--------|--------------|---------------|-----------|---------|
| **Digitalizaci├│n** | Ô£à CRUD | Ô£à CRU | Ô£à RU | Ô£à R |
| **Revisi├│n OCR** | Ô£à CRUD | Ô£à R | Ô£à CRUD | Ô£à R |
| **Registros** | Ô£à CRUD | Ô£à R | Ô£à RU | Ô£à R |
| **Personas** | Ô£à CRUD | Ô£à R | Ô£à RU | Ô£à R |
| **Libros** | Ô£à CRUD | Ô£à R | Ô£à R | Ô£à R |
| **Certificados** | Ô£à CRUD | Ô£à R | Ô£à CR | Ô£à R |
| **Usuarios** | Ô£à CRUD | ÔØî | ÔØî | ÔØî |
| **Auditor├¡a** | Ô£à R | ÔØî | ÔØî | ÔØî |
| **Reportes** | Ô£à R | ÔØî | Ô£à R | ÔØî |

**Leyenda:**
- C = Create (Crear)
- R = Read (Leer/Ver)
- U = Update (Actualizar/Editar)
- D = Delete (Eliminar)

## ­ƒÜÇ C├│mo Usar el Sistema

### 1. **Proteger Rutas Completas**

Ya implementado en `App.jsx`:

```jsx
import PrivateRoute from './components/PrivateRoute'

<Route path="/usuarios" element={
  <PrivateRoute>
    <Usuarios />
  </PrivateRoute>
} />
```

### 2. **Usar el Hook de Permisos**

En cualquier componente:

```jsx
import { usePermissions } from '../hooks/usePermissions'

function MiComponente() {
  const { canCreate, canUpdate, canDelete, isAdmin } = usePermissions()

  return (
    <div>
      {/* Mostrar bot├│n solo si puede crear */}
      {canCreate('digitalizacion') && (
        <button>Crear Documento</button>
      )}

      {/* Mostrar bot├│n solo si puede editar */}
      {canUpdate('personas') && (
        <button>Editar Persona</button>
      )}

      {/* Mostrar secci├│n solo para admins */}
      {isAdmin() && (
        <div>Panel de Administraci├│n</div>
      )}
    </div>
  )
}
```

### 3. **Proteger Contenido Espec├¡fico con PermissionGuard**

```jsx
import PermissionGuard from '../components/PermissionGuard'

<PermissionGuard module="usuarios" action="create">
  <button>Crear Usuario</button>
</PermissionGuard>

<PermissionGuard module="registros" action="delete"
  fallback={<p>No tienes permisos para eliminar</p>}>
  <button>Eliminar Registro</button>
</PermissionGuard>
```

### 4. **Verificaci├│n Directa de Permisos**

```jsx
import { hasPermission } from '../config/permissions'
import { useAuth } from '../context/AuthContext'

const { getUserRole } = useAuth()
const userRole = getUserRole()

if (hasPermission(userRole, 'usuarios', 'delete')) {
  // El usuario puede eliminar usuarios
}
```

## ­ƒôØ Ejemplos de Uso por M├│dulo

### Digitalizaci├│n
```jsx
import { usePermissions } from '../hooks/usePermissions'

export default function Digitalizacion() {
  const { canCreate, canUpdate, canDelete } = usePermissions()

  return (
    <Layout title="Digitalizaci├│n">
      {canCreate('digitalizacion') && (
        <button onClick={handleUpload}>
          Subir Documento
        </button>
      )}

      {canUpdate('digitalizacion') && (
        <button onClick={handleEdit}>
          Editar
        </button>
      )}

      {canDelete('digitalizacion') && (
        <button onClick={handleDelete}>
          Eliminar
        </button>
      )}
    </Layout>
  )
}
```

### Usuarios
```jsx
import { usePermissions } from '../hooks/usePermissions'
import { Navigate } from 'react-router-dom'

export default function Usuarios() {
  const { canAccess } = usePermissions()

  // Redirigir si no tiene acceso al m├│dulo
  if (!canAccess('usuarios')) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <Layout title="Usuarios">
      {/* Contenido del m├│dulo */}
    </Layout>
  )
}
```

## ­ƒöä Flujo de Autenticaci├│n

1. **Login** ÔåÆ Usuario ingresa credenciales
2. **Validaci├│n** ÔåÆ Backend verifica y retorna token + datos de usuario
3. **Almacenamiento** ÔåÆ Token y usuario se guardan en localStorage y contexto
4. **Navegaci├│n** ÔåÆ Sistema filtra rutas y opciones seg├║n rol
5. **Permisos** ÔåÆ Cada acci├│n verifica permisos antes de ejecutar

## ­ƒÄ¿ Interfaz Adaptativa

### Navegaci├│n Lateral
- **Se ocultan autom├íticamente** los m├│dulos a los que el usuario no tiene acceso
- El men├║ muestra solo las opciones permitidas seg├║n el rol

### Botones de Acci├│n
- **Crear**: Visible solo si `canCreate(module)` es true
- **Editar**: Visible solo si `canUpdate(module)` es true
- **Eliminar**: Visible solo si `canDelete(module)` es true

### Informaci├│n del Usuario
- **Avatar** con inicial del nombre
- **Nombre completo** del usuario logueado
- **Rol** del usuario (Administrador, Digitalizador, etc.)
- **Bot├│n de cierre de sesi├│n**

## ­ƒöÆ Niveles de Acceso por Rol

### ­ƒææ Administrador
- **Acceso total** a todos los m├│dulos
- **CRUD completo** en todas las funcionalidades
- **├Ünico rol** con acceso a Usuarios y Auditor├¡a
- **Gesti├│n de roles y permisos**

### ­ƒôä Digitalizador
- **Enfocado en digitalizaci├│n** de documentos
- **Puede subir, ver y editar** documentos
- **No puede eliminar** documentos
- **Acceso de solo lectura** a otros m├│dulos

### ­ƒöì Validador (Revisor)
- **Enfocado en validaci├│n OCR**
- **CRUD completo** en revisi├│n OCR
- **Puede editar** registros y personas validadas
- **Acceso a reportes**

### ­ƒæü´©Å Usuario (Consultor)
- **Solo lectura** en todos los m├│dulos
- **No puede modificar** ning├║n dato
- **Puede consultar** informaci├│n
- **Ideal para consultas externas**

## ÔÜÖ´©Å Configuraci├│n Personalizada

Para modificar permisos, edita `src/config/permissions.js`:

```javascript
export const PERMISSIONS = {
  miModulo: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: true, read: true, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: true, update: true, delete: false },
    [ROLES.USUARIO]: { create: false, read: true, update: false, delete: false }
  }
}
```

## ­ƒº¬ Pruebas

### Login con Diferentes Roles:

1. **Administrador:**
   - Email: `admin@sacra360.com`
   - Password: `Admin123!`
   - Ver├ís TODOS los m├│dulos en el men├║

2. **Digitalizador:**
   - Email: `digitalizador@sacra360.com`
   - Password: `Digita123!`
   - Ver├ís m├│dulos de digitalizaci├│n, registros, personas, libros

3. **Revisor:**
   - Email: `revisor@sacra360.com`
   - Password: `Revisor123!`
   - Ver├ís m├│dulos de OCR, registros, personas, reportes

4. **Consultor:**
   - Email: `consultor@sacra360.com`
   - Password: `Consul123!`
   - Ver├ís todos los m├│dulos pero SIN botones de acci├│n

## ­ƒôè Estado Actual

Ô£à **Completado:**
- Sistema de permisos RBAC
- Contexto de autenticaci├│n
- Protecci├│n de rutas
- Filtrado de navegaci├│n
- Hook de permisos
- Componentes de protecci├│n

­ƒöä **Siguiente paso:**
- Aplicar `PermissionGuard` en cada m├│dulo
- Ocultar/mostrar botones seg├║n permisos
- Implementar validaci├│n en cada acci├│n

## ­ƒÄ» Pr├│ximos Pasos Recomendados

1. **Actualizar cada p├ígina** para usar `usePermissions`
2. **Envolver botones de acci├│n** con `PermissionGuard`
3. **Validar acciones** en el backend tambi├®n
4. **Agregar mensajes de error** cuando no hay permisos
5. **Logging de acciones** seg├║n permisos

---

**Sistema implementado por:** GitHub Copilot  
**Fecha:** 28 de Noviembre de 2025  
**Versi├│n:** 1.0.0
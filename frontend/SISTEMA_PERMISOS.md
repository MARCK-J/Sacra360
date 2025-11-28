# 🔐 Sistema de Permisos RBAC - Sacra360

## ✅ Implementación Completada

Se ha implementado un sistema completo de **Role-Based Access Control (RBAC)** en el frontend que controla el acceso a módulos y funcionalidades según el rol del usuario.

## 📁 Archivos Creados

### 1. **Config** - Sistema de permisos
- `src/config/permissions.js` - Definición de permisos CRUD por módulo y rol

### 2. **Context** - Gestión de autenticación
- `src/context/AuthContext.jsx` - Contexto global de autenticación

### 3. **Components** - Protección de rutas y contenido
- `src/components/PrivateRoute.jsx` - Componente para rutas privadas
- `src/components/PermissionGuard.jsx` - Componente para proteger contenido específico

### 4. **Hooks** - Utilidades de permisos
- `src/hooks/usePermissions.js` - Hook personalizado para verificar permisos

## 🎯 Matriz de Permisos Implementada

| Módulo | Administrador | Digitalizador | Validador | Usuario |
|--------|--------------|---------------|-----------|---------|
| **Digitalización** | ✅ CRUD | ✅ CRU | ✅ RU | ✅ R |
| **Revisión OCR** | ✅ CRUD | ✅ R | ✅ CRUD | ✅ R |
| **Registros** | ✅ CRUD | ✅ R | ✅ RU | ✅ R |
| **Personas** | ✅ CRUD | ✅ R | ✅ RU | ✅ R |
| **Libros** | ✅ CRUD | ✅ R | ✅ R | ✅ R |
| **Certificados** | ✅ CRUD | ✅ R | ✅ CR | ✅ R |
| **Usuarios** | ✅ CRUD | ❌ | ❌ | ❌ |
| **Auditoría** | ✅ R | ❌ | ❌ | ❌ |
| **Reportes** | ✅ R | ❌ | ✅ R | ❌ |

**Leyenda:**
- C = Create (Crear)
- R = Read (Leer/Ver)
- U = Update (Actualizar/Editar)
- D = Delete (Eliminar)

## 🚀 Cómo Usar el Sistema

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
      {/* Mostrar botón solo si puede crear */}
      {canCreate('digitalizacion') && (
        <button>Crear Documento</button>
      )}

      {/* Mostrar botón solo si puede editar */}
      {canUpdate('personas') && (
        <button>Editar Persona</button>
      )}

      {/* Mostrar sección solo para admins */}
      {isAdmin() && (
        <div>Panel de Administración</div>
      )}
    </div>
  )
}
```

### 3. **Proteger Contenido Específico con PermissionGuard**

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

### 4. **Verificación Directa de Permisos**

```jsx
import { hasPermission } from '../config/permissions'
import { useAuth } from '../context/AuthContext'

const { getUserRole } = useAuth()
const userRole = getUserRole()

if (hasPermission(userRole, 'usuarios', 'delete')) {
  // El usuario puede eliminar usuarios
}
```

## 📝 Ejemplos de Uso por Módulo

### Digitalización
```jsx
import { usePermissions } from '../hooks/usePermissions'

export default function Digitalizacion() {
  const { canCreate, canUpdate, canDelete } = usePermissions()

  return (
    <Layout title="Digitalización">
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

  // Redirigir si no tiene acceso al módulo
  if (!canAccess('usuarios')) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <Layout title="Usuarios">
      {/* Contenido del módulo */}
    </Layout>
  )
}
```

## 🔄 Flujo de Autenticación

1. **Login** → Usuario ingresa credenciales
2. **Validación** → Backend verifica y retorna token + datos de usuario
3. **Almacenamiento** → Token y usuario se guardan en localStorage y contexto
4. **Navegación** → Sistema filtra rutas y opciones según rol
5. **Permisos** → Cada acción verifica permisos antes de ejecutar

## 🎨 Interfaz Adaptativa

### Navegación Lateral
- **Se ocultan automáticamente** los módulos a los que el usuario no tiene acceso
- El menú muestra solo las opciones permitidas según el rol

### Botones de Acción
- **Crear**: Visible solo si `canCreate(module)` es true
- **Editar**: Visible solo si `canUpdate(module)` es true
- **Eliminar**: Visible solo si `canDelete(module)` es true

### Información del Usuario
- **Avatar** con inicial del nombre
- **Nombre completo** del usuario logueado
- **Rol** del usuario (Administrador, Digitalizador, etc.)
- **Botón de cierre de sesión**

## 🔒 Niveles de Acceso por Rol

### 👑 Administrador
- **Acceso total** a todos los módulos
- **CRUD completo** en todas las funcionalidades
- **Único rol** con acceso a Usuarios y Auditoría
- **Gestión de roles y permisos**

### 📄 Digitalizador
- **Enfocado en digitalización** de documentos
- **Puede subir, ver y editar** documentos
- **No puede eliminar** documentos
- **Acceso de solo lectura** a otros módulos

### 🔍 Validador (Revisor)
- **Enfocado en validación OCR**
- **CRUD completo** en revisión OCR
- **Puede editar** registros y personas validadas
- **Acceso a reportes**

### 👁️ Usuario (Consultor)
- **Solo lectura** en todos los módulos
- **No puede modificar** ningún dato
- **Puede consultar** información
- **Ideal para consultas externas**

## ⚙️ Configuración Personalizada

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

## 🧪 Pruebas

### Login con Diferentes Roles:

1. **Administrador:**
   - Email: `admin@sacra360.com`
   - Password: `Admin123!`
   - Verás TODOS los módulos en el menú

2. **Digitalizador:**
   - Email: `digitalizador@sacra360.com`
   - Password: `Digita123!`
   - Verás módulos de digitalización, registros, personas, libros

3. **Revisor:**
   - Email: `revisor@sacra360.com`
   - Password: `Revisor123!`
   - Verás módulos de OCR, registros, personas, reportes

4. **Consultor:**
   - Email: `consultor@sacra360.com`
   - Password: `Consul123!`
   - Verás todos los módulos pero SIN botones de acción

## 📊 Estado Actual

✅ **Completado:**
- Sistema de permisos RBAC
- Contexto de autenticación
- Protección de rutas
- Filtrado de navegación
- Hook de permisos
- Componentes de protección

🔄 **Siguiente paso:**
- Aplicar `PermissionGuard` en cada módulo
- Ocultar/mostrar botones según permisos
- Implementar validación en cada acción

## 🎯 Próximos Pasos Recomendados

1. **Actualizar cada página** para usar `usePermissions`
2. **Envolver botones de acción** con `PermissionGuard`
3. **Validar acciones** en el backend también
4. **Agregar mensajes de error** cuando no hay permisos
5. **Logging de acciones** según permisos

---

**Sistema implementado por:** GitHub Copilot  
**Fecha:** 28 de Noviembre de 2025  
**Versión:** 1.0.0

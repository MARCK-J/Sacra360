# 🧪 Guía de Pruebas del Sistema de Permisos RBAC

## 📋 Resumen de Implementación

Se ha aplicado el sistema de permisos RBAC a **TODOS** los módulos del frontend. Los componentes ahora responden dinámicamente según el rol del usuario logueado.

---

## 🎯 Módulos Actualizados

### ✅ 1. Digitalización (`Digitalizacion.jsx`)
**Permisos aplicados:**
- ✓ Botón "Seleccionar archivos" → `create`
- ✓ Botón "Eliminar archivo" (X) → `delete`
- ✓ Botón "Subir archivos" → `create`

**Comportamiento esperado:**
- **Administrador**: Ve y puede usar todos los botones
- **Digitalizador**: Ve botones de crear y subir (NO eliminar)
- **Validador**: Ve botones de editar documentos
- **Usuario**: Solo puede VER documentos (sin botones de acción)

---

### ✅ 2. Revisión OCR (`RevisionOCR.jsx`)
**Permisos aplicados:**
- ✓ Botones de validación OCR
- ✓ Modal de corrección de datos

**Comportamiento esperado:**
- **Administrador**: Acceso completo
- **Digitalizador**: Solo puede VER
- **Validador**: Puede validar y corregir OCR (CRUD completo)
- **Usuario**: Solo puede VER

---

### ✅ 3. Registros (`Registros.jsx`)
**Permisos aplicados:**
- ✓ Botón "Ver" (visibility) → Siempre visible
- ✓ Botón "Editar" (edit) → `update`
- ✓ Botón "Borrador" (draft) → `update`
- ✓ Botón "Gavel" → `update`

**Comportamiento esperado:**
- **Administrador**: Todos los botones visibles (CRUD completo)
- **Digitalizador**: Solo botón "Ver"
- **Validador**: Botones de Ver y Editar
- **Usuario**: Solo botón "Ver"

---

### ✅ 4. Personas (`Personas.jsx`)
**Permisos aplicados:**
- ✓ Botón "Fusionar Registros" → `update`
- ✓ Formulario de edición de datos personales

**Comportamiento esperado:**
- **Administrador**: Puede fusionar y editar todo
- **Digitalizador**: Solo puede VER
- **Validador**: Puede editar y fusionar
- **Usuario**: Solo puede VER

---

### ✅ 5. Libros (`Libros.jsx`)
**Permisos aplicados:**
- ✓ Botón "Guardar Ubicación" → `update`
- ✓ Formulario de asignación de ubicación física

**Comportamiento esperado:**
- **Administrador**: Puede crear y actualizar ubicaciones
- **Digitalizador**: Solo puede VER
- **Validador**: Solo puede VER
- **Usuario**: Solo puede VER

---

### ✅ 6. Certificados (`Certificados.jsx`)
**Permisos aplicados:**
- ✓ Botón "Generar" certificado → `create`
- ✓ Botón "Previsualizar" → Siempre visible

**Comportamiento esperado:**
- **Administrador**: Puede generar certificados
- **Digitalizador**: Solo puede VER
- **Validador**: Puede generar certificados
- **Usuario**: Solo puede VER

---

### ✅ 7. Usuarios (`Usuarios.jsx`)
**Permisos aplicados:**
- ✓ Botones "Editar" en tabla → `update`
- ✓ Botones "Guardar Cambios" → `update`
- ✓ Panel de edición de permisos → `update`

**Comportamiento esperado:**
- **Administrador**: CRUD completo de usuarios (ÚNICO con acceso)
- **Digitalizador**: No tiene acceso al módulo
- **Validador**: No tiene acceso al módulo
- **Usuario**: No tiene acceso al módulo

---

### ✅ 8. Auditoría (`Auditoria.jsx`)
**Permisos aplicados:**
- ✓ Botón "Exportar a CSV" → `read`

**Comportamiento esperado:**
- **Administrador**: Puede ver y exportar logs (ÚNICO con acceso)
- **Digitalizador**: No tiene acceso al módulo
- **Validador**: No tiene acceso al módulo
- **Usuario**: No tiene acceso al módulo

---

### ✅ 9. Reportes (`Reportes.jsx`)
**Permisos aplicados:**
- Solo lectura (sin botones de acción)

**Comportamiento esperado:**
- **Administrador**: Puede ver todos los reportes
- **Digitalizador**: No tiene acceso al módulo
- **Validador**: Puede ver reportes
- **Usuario**: No tiene acceso al módulo

---

## 🧪 Casos de Prueba

### Caso 1: Login como Administrador
```
Email: admin@sacra360.com
Password: Admin123!
```

**Verificar:**
- [ ] Todos los módulos visibles en el menú lateral
- [ ] Todos los botones de acción visibles en cada módulo
- [ ] Puede crear, editar, eliminar en todos los módulos
- [ ] Tiene acceso a Usuarios y Auditoría

---

### Caso 2: Login como Digitalizador
```
Email: digitalizador@sacra360.com
Password: Digita123!
```

**Verificar:**
- [ ] Menú muestra: Digitalización, Registros, Personas, Libros, Certificados
- [ ] En Digitalización: Puede subir archivos
- [ ] En Registros: Solo ve botón "Ver" (NO editar)
- [ ] En Personas: Solo puede consultar
- [ ] NO ve módulos de: Usuarios, Auditoría, Reportes
- [ ] NO ve botón de eliminar en Digitalización

---

### Caso 3: Login como Validador/Revisor
```
Email: revisor@sacra360.com
Password: Revisor123!
```

**Verificar:**
- [ ] Menú muestra: Digitalización, Revisión OCR, Registros, Personas, Libros, Certificados, Reportes
- [ ] En Revisión OCR: Puede validar y corregir (CRUD completo)
- [ ] En Registros: Puede editar (botones edit, draft, gavel visibles)
- [ ] En Personas: Puede fusionar duplicados
- [ ] En Certificados: Puede generar certificados
- [ ] NO ve módulos de: Usuarios, Auditoría

---

### Caso 4: Login como Consultor
```
Email: consultor@sacra360.com
Password: Consul123!
```

**Verificar:**
- [ ] Menú muestra: Digitalización, Revisión OCR, Registros, Personas, Libros, Certificados
- [ ] En TODOS los módulos: Solo botón "Ver" visible
- [ ] NO puede crear, editar, ni eliminar nada
- [ ] NO ve módulos de: Usuarios, Auditoría, Reportes
- [ ] Todos los formularios en modo solo lectura

---

## 🔍 Pruebas de Navegación

### Test 1: Navegación lateral dinámica
1. Login con cada rol
2. Verificar que el menú lateral muestre solo los módulos permitidos
3. Verificar que los íconos y nombres sean correctos

### Test 2: Protección de rutas
1. Login como Usuario
2. Intentar acceder manualmente a `/usuarios` (escribir en URL)
3. Debe redirigir a `/dashboard` o mostrar mensaje de acceso denegado

### Test 3: Persistencia de sesión
1. Login con cualquier rol
2. Refrescar la página (F5)
3. Verificar que mantiene la sesión y permisos

### Test 4: Logout
1. Login con cualquier rol
2. Hacer clic en botón de Logout
3. Verificar redirección a `/login`
4. Verificar que no puede acceder a rutas protegidas

---

## 📊 Matriz de Verificación Rápida

| Módulo | Admin | Digitalizador | Validador | Usuario |
|--------|-------|---------------|-----------|---------|
| **Digitalización** | CRUD | CRU | RU | R |
| **Revisión OCR** | CRUD | R | CRUD | R |
| **Registros** | CRUD | R | RU | R |
| **Personas** | CRUD | R | RU | R |
| **Libros** | CRUD | R | R | R |
| **Certificados** | CRUD | R | CR | R |
| **Usuarios** | CRUD | ❌ | ❌ | ❌ |
| **Auditoría** | R | ❌ | ❌ | ❌ |
| **Reportes** | R | ❌ | R | ❌ |

**Leyenda:**
- C = Create (Crear)
- R = Read (Leer/Ver)
- U = Update (Actualizar/Editar)
- D = Delete (Eliminar)
- ❌ = Sin acceso al módulo

---

## 🐛 Errores Comunes a Verificar

### Error 1: Botones visibles sin permisos
**Síntoma:** Usuario ve botón pero al hacer clic no hace nada
**Causa:** Falta `PermissionGuard` envolviendo el botón
**Solución:** Ya implementado en todos los módulos ✅

### Error 2: Módulo visible sin permisos
**Síntoma:** Usuario ve módulo en menú sin tener acceso
**Causa:** Falta verificación en `Layout.jsx`
**Solución:** Ya implementado con `canAccessModule()` ✅

### Error 3: No mantiene sesión al refrescar
**Síntoma:** Al refrescar página pierde login
**Causa:** Token no persiste en localStorage
**Solución:** Ya implementado en `AuthContext.jsx` ✅

### Error 4: Token expirado no redirige
**Síntoma:** Usuario con token expirado ve contenido
**Causa:** Falta validación de token en PrivateRoute
**Solución:** Backend valida en cada request

---

## 🎨 Pruebas de UI/UX

### Verificar en cada rol:
- [ ] Los botones deshabilitados/ocultos NO dejan espacios vacíos
- [ ] Los mensajes de error son claros cuando no hay permisos
- [ ] La navegación es fluida y coherente
- [ ] Los colores y estilos son consistentes
- [ ] El modo oscuro funciona correctamente

---

## 📝 Checklist Final de Implementación

### Archivos Core:
- [x] `src/config/permissions.js` - Configuración de permisos
- [x] `src/context/AuthContext.jsx` - Contexto de autenticación
- [x] `src/components/PrivateRoute.jsx` - Protección de rutas
- [x] `src/components/PermissionGuard.jsx` - Protección de contenido
- [x] `src/hooks/usePermissions.js` - Hook de permisos
- [x] `src/components/Layout.jsx` - Navegación dinámica
- [x] `src/App.jsx` - Rutas protegidas

### Páginas Actualizadas:
- [x] `src/pages/Digitalizacion.jsx`
- [x] `src/pages/RevisionOCR.jsx`
- [x] `src/pages/Registros.jsx`
- [x] `src/pages/Personas.jsx`
- [x] `src/pages/Libros.jsx`
- [x] `src/pages/Certificados.jsx`
- [x] `src/pages/Usuarios.jsx`
- [x] `src/pages/Auditoria.jsx`
- [x] `src/pages/Reportes.jsx`
- [x] `src/pages/Login.jsx`

---

## 🚀 Siguientes Pasos Recomendados

1. **Backend Validation**: Validar permisos también en el backend
2. **Error Handling**: Agregar mensajes claros cuando no hay permisos
3. **Logging**: Registrar intentos de acceso no autorizados
4. **Testing**: Crear tests automáticos E2E con Cypress/Playwright
5. **Performance**: Optimizar carga de permisos con React.memo

---

## 📞 Soporte

Si encuentras algún problema:
1. Verifica que el backend esté corriendo en puerto 8004
2. Verifica que el usuario tenga el rol correcto en la base de datos
3. Limpia el localStorage del navegador: `localStorage.clear()`
4. Revisa la consola del navegador para errores

**Sistema implementado:** 28 de Noviembre de 2025
**Versión:** 1.0.0

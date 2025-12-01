# ­ƒº¬ Gu├¡a de Pruebas del Sistema de Permisos RBAC

## ­ƒôï Resumen de Implementaci├│n

Se ha aplicado el sistema de permisos RBAC a **TODOS** los m├│dulos del frontend. Los componentes ahora responden din├ímicamente seg├║n el rol del usuario logueado.

---

## ­ƒÄ» M├│dulos Actualizados

### Ô£à 1. Digitalizaci├│n (`Digitalizacion.jsx`)
**Permisos aplicados:**
- Ô£ô Bot├│n "Seleccionar archivos" ÔåÆ `create`
- Ô£ô Bot├│n "Eliminar archivo" (X) ÔåÆ `delete`
- Ô£ô Bot├│n "Subir archivos" ÔåÆ `create`

**Comportamiento esperado:**
- **Administrador**: Ve y puede usar todos los botones
- **Digitalizador**: Ve botones de crear y subir (NO eliminar)
- **Validador**: Ve botones de editar documentos
- **Usuario**: Solo puede VER documentos (sin botones de acci├│n)

---

### Ô£à 2. Revisi├│n OCR (`RevisionOCR.jsx`)
**Permisos aplicados:**
- Ô£ô Botones de validaci├│n OCR
- Ô£ô Modal de correcci├│n de datos

**Comportamiento esperado:**
- **Administrador**: Acceso completo
- **Digitalizador**: Solo puede VER
- **Validador**: Puede validar y corregir OCR (CRUD completo)
- **Usuario**: Solo puede VER

---

### Ô£à 3. Registros (`Registros.jsx`)
**Permisos aplicados:**
- Ô£ô Bot├│n "Ver" (visibility) ÔåÆ Siempre visible
- Ô£ô Bot├│n "Editar" (edit) ÔåÆ `update`
- Ô£ô Bot├│n "Borrador" (draft) ÔåÆ `update`
- Ô£ô Bot├│n "Gavel" ÔåÆ `update`

**Comportamiento esperado:**
- **Administrador**: Todos los botones visibles (CRUD completo)
- **Digitalizador**: Solo bot├│n "Ver"
- **Validador**: Botones de Ver y Editar
- **Usuario**: Solo bot├│n "Ver"

---

### Ô£à 4. Personas (`Personas.jsx`)
**Permisos aplicados:**
- Ô£ô Bot├│n "Fusionar Registros" ÔåÆ `update`
- Ô£ô Formulario de edici├│n de datos personales

**Comportamiento esperado:**
- **Administrador**: Puede fusionar y editar todo
- **Digitalizador**: Solo puede VER
- **Validador**: Puede editar y fusionar
- **Usuario**: Solo puede VER

---

### Ô£à 5. Libros (`Libros.jsx`)
**Permisos aplicados:**
- Ô£ô Bot├│n "Guardar Ubicaci├│n" ÔåÆ `update`
- Ô£ô Formulario de asignaci├│n de ubicaci├│n f├¡sica

**Comportamiento esperado:**
- **Administrador**: Puede crear y actualizar ubicaciones
- **Digitalizador**: Solo puede VER
- **Validador**: Solo puede VER
- **Usuario**: Solo puede VER

---

### Ô£à 6. Certificados (`Certificados.jsx`)
**Permisos aplicados:**
- Ô£ô Bot├│n "Generar" certificado ÔåÆ `create`
- Ô£ô Bot├│n "Previsualizar" ÔåÆ Siempre visible

**Comportamiento esperado:**
- **Administrador**: Puede generar certificados
- **Digitalizador**: Solo puede VER
- **Validador**: Puede generar certificados
- **Usuario**: Solo puede VER

---

### Ô£à 7. Usuarios (`Usuarios.jsx`)
**Permisos aplicados:**
- Ô£ô Botones "Editar" en tabla ÔåÆ `update`
- Ô£ô Botones "Guardar Cambios" ÔåÆ `update`
- Ô£ô Panel de edici├│n de permisos ÔåÆ `update`

**Comportamiento esperado:**
- **Administrador**: CRUD completo de usuarios (├ÜNICO con acceso)
- **Digitalizador**: No tiene acceso al m├│dulo
- **Validador**: No tiene acceso al m├│dulo
- **Usuario**: No tiene acceso al m├│dulo

---

### Ô£à 8. Auditor├¡a (`Auditoria.jsx`)
**Permisos aplicados:**
- Ô£ô Bot├│n "Exportar a CSV" ÔåÆ `read`

**Comportamiento esperado:**
- **Administrador**: Puede ver y exportar logs (├ÜNICO con acceso)
- **Digitalizador**: No tiene acceso al m├│dulo
- **Validador**: No tiene acceso al m├│dulo
- **Usuario**: No tiene acceso al m├│dulo

---

### Ô£à 9. Reportes (`Reportes.jsx`)
**Permisos aplicados:**
- Solo lectura (sin botones de acci├│n)

**Comportamiento esperado:**
- **Administrador**: Puede ver todos los reportes
- **Digitalizador**: No tiene acceso al m├│dulo
- **Validador**: Puede ver reportes
- **Usuario**: No tiene acceso al m├│dulo

---

## ­ƒº¬ Casos de Prueba

### Caso 1: Login como Administrador
```
Email: admin@sacra360.com
Password: Admin123!
```

**Verificar:**
- [ ] Todos los m├│dulos visibles en el men├║ lateral
- [ ] Todos los botones de acci├│n visibles en cada m├│dulo
- [ ] Puede crear, editar, eliminar en todos los m├│dulos
- [ ] Tiene acceso a Usuarios y Auditor├¡a

---

### Caso 2: Login como Digitalizador
```
Email: digitalizador@sacra360.com
Password: Digita123!
```

**Verificar:**
- [ ] Men├║ muestra: Digitalizaci├│n, Registros, Personas, Libros, Certificados
- [ ] En Digitalizaci├│n: Puede subir archivos
- [ ] En Registros: Solo ve bot├│n "Ver" (NO editar)
- [ ] En Personas: Solo puede consultar
- [ ] NO ve m├│dulos de: Usuarios, Auditor├¡a, Reportes
- [ ] NO ve bot├│n de eliminar en Digitalizaci├│n

---

### Caso 3: Login como Validador/Revisor
```
Email: revisor@sacra360.com
Password: Revisor123!
```

**Verificar:**
- [ ] Men├║ muestra: Digitalizaci├│n, Revisi├│n OCR, Registros, Personas, Libros, Certificados, Reportes
- [ ] En Revisi├│n OCR: Puede validar y corregir (CRUD completo)
- [ ] En Registros: Puede editar (botones edit, draft, gavel visibles)
- [ ] En Personas: Puede fusionar duplicados
- [ ] En Certificados: Puede generar certificados
- [ ] NO ve m├│dulos de: Usuarios, Auditor├¡a

---

### Caso 4: Login como Consultor
```
Email: consultor@sacra360.com
Password: Consul123!
```

**Verificar:**
- [ ] Men├║ muestra: Digitalizaci├│n, Revisi├│n OCR, Registros, Personas, Libros, Certificados
- [ ] En TODOS los m├│dulos: Solo bot├│n "Ver" visible
- [ ] NO puede crear, editar, ni eliminar nada
- [ ] NO ve m├│dulos de: Usuarios, Auditor├¡a, Reportes
- [ ] Todos los formularios en modo solo lectura

---

## ­ƒöì Pruebas de Navegaci├│n

### Test 1: Navegaci├│n lateral din├ímica
1. Login con cada rol
2. Verificar que el men├║ lateral muestre solo los m├│dulos permitidos
3. Verificar que los ├¡conos y nombres sean correctos

### Test 2: Protecci├│n de rutas
1. Login como Usuario
2. Intentar acceder manualmente a `/usuarios` (escribir en URL)
3. Debe redirigir a `/dashboard` o mostrar mensaje de acceso denegado

### Test 3: Persistencia de sesi├│n
1. Login con cualquier rol
2. Refrescar la p├ígina (F5)
3. Verificar que mantiene la sesi├│n y permisos

### Test 4: Logout
1. Login con cualquier rol
2. Hacer clic en bot├│n de Logout
3. Verificar redirecci├│n a `/login`
4. Verificar que no puede acceder a rutas protegidas

---

## ­ƒôè Matriz de Verificaci├│n R├ípida

| M├│dulo | Admin | Digitalizador | Validador | Usuario |
|--------|-------|---------------|-----------|---------|
| **Digitalizaci├│n** | CRUD | CRU | RU | R |
| **Revisi├│n OCR** | CRUD | R | CRUD | R |
| **Registros** | CRUD | R | RU | R |
| **Personas** | CRUD | R | RU | R |
| **Libros** | CRUD | R | R | R |
| **Certificados** | CRUD | R | CR | R |
| **Usuarios** | CRUD | ÔØî | ÔØî | ÔØî |
| **Auditor├¡a** | R | ÔØî | ÔØî | ÔØî |
| **Reportes** | R | ÔØî | R | ÔØî |

**Leyenda:**
- C = Create (Crear)
- R = Read (Leer/Ver)
- U = Update (Actualizar/Editar)
- D = Delete (Eliminar)
- ÔØî = Sin acceso al m├│dulo

---

## ­ƒÉø Errores Comunes a Verificar

### Error 1: Botones visibles sin permisos
**S├¡ntoma:** Usuario ve bot├│n pero al hacer clic no hace nada
**Causa:** Falta `PermissionGuard` envolviendo el bot├│n
**Soluci├│n:** Ya implementado en todos los m├│dulos Ô£à

### Error 2: M├│dulo visible sin permisos
**S├¡ntoma:** Usuario ve m├│dulo en men├║ sin tener acceso
**Causa:** Falta verificaci├│n en `Layout.jsx`
**Soluci├│n:** Ya implementado con `canAccessModule()` Ô£à

### Error 3: No mantiene sesi├│n al refrescar
**S├¡ntoma:** Al refrescar p├ígina pierde login
**Causa:** Token no persiste en localStorage
**Soluci├│n:** Ya implementado en `AuthContext.jsx` Ô£à

### Error 4: Token expirado no redirige
**S├¡ntoma:** Usuario con token expirado ve contenido
**Causa:** Falta validaci├│n de token en PrivateRoute
**Soluci├│n:** Backend valida en cada request

---

## ­ƒÄ¿ Pruebas de UI/UX

### Verificar en cada rol:
- [ ] Los botones deshabilitados/ocultos NO dejan espacios vac├¡os
- [ ] Los mensajes de error son claros cuando no hay permisos
- [ ] La navegaci├│n es fluida y coherente
- [ ] Los colores y estilos son consistentes
- [ ] El modo oscuro funciona correctamente

---

## ­ƒôØ Checklist Final de Implementaci├│n

### Archivos Core:
- [x] `src/config/permissions.js` - Configuraci├│n de permisos
- [x] `src/context/AuthContext.jsx` - Contexto de autenticaci├│n
- [x] `src/components/PrivateRoute.jsx` - Protecci├│n de rutas
- [x] `src/components/PermissionGuard.jsx` - Protecci├│n de contenido
- [x] `src/hooks/usePermissions.js` - Hook de permisos
- [x] `src/components/Layout.jsx` - Navegaci├│n din├ímica
- [x] `src/App.jsx` - Rutas protegidas

### P├íginas Actualizadas:
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

## ­ƒÜÇ Siguientes Pasos Recomendados

1. **Backend Validation**: Validar permisos tambi├®n en el backend
2. **Error Handling**: Agregar mensajes claros cuando no hay permisos
3. **Logging**: Registrar intentos de acceso no autorizados
4. **Testing**: Crear tests autom├íticos E2E con Cypress/Playwright
5. **Performance**: Optimizar carga de permisos con React.memo

---

## ­ƒô× Soporte

Si encuentras alg├║n problema:
1. Verifica que el backend est├® corriendo en puerto 8004
2. Verifica que el usuario tenga el rol correcto en la base de datos
3. Limpia el localStorage del navegador: `localStorage.clear()`
4. Revisa la consola del navegador para errores

**Sistema implementado:** 28 de Noviembre de 2025
**Versi├│n:** 1.0.0
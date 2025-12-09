# Implementación de Context para Polling OCR

## 🎯 Problema Resuelto

**Bug crítico**: El modal de progreso OCR creaba cientos de solicitudes simultáneas al endpoint `/api/v1/ocr/progreso/{id}`, causando:
- Sobrecarga del servidor
- Problemas de rendimiento
- Re-renders en cascada

**Causa raíz**: El componente `OcrProgressModal` se remontaba constantemente debido a re-renders del padre, y cada vez que se montaba creaba un nuevo `setInterval` sin limpiar el anterior correctamente.

## ✅ Solución Implementada

Arquitectura con **React Context** que centraliza el polling en un nivel superior al árbol de componentes:

### 1. Context Provider (`OcrProgressContext.jsx`)

```jsx
// Estado global para todos los documentos en procesamiento
const [documentosEnProceso, setDocumentosEnProceso] = useState({})

// Métodos expuestos
- iniciarSeguimiento(documentoId)    // Agregar documento a tracking
- detenerSeguimiento(documentoId)    // Remover documento de tracking

// Polling centralizado
- UN SOLO setInterval para TODOS los documentos
- Se inicia automáticamente cuando hay documentos activos
- Se detiene automáticamente cuando no hay documentos
- Usa Promise.all() para consultas paralelas
- Intervalo de 3 segundos (era 2s antes)
```

**Características clave**:
- ✅ Un único `setInterval` global
- ✅ Refs (`intervalRef`, `isPollingRef`) previenen duplicación
- ✅ Auto-limpieza cuando `documentosEnProceso` está vacío
- ✅ Manejo de múltiples documentos en paralelo
- ✅ Detección automática de completado/error

### 2. Integración en App.jsx

```jsx
import { OcrProgressProvider } from './context/OcrProgressContext'

<OcrProgressProvider>
  <Routes>
    {/* todas las rutas */}
  </Routes>
</OcrProgressProvider>
```

### 3. OcrProgressModal Refactorizado

**ANTES** (❌ Problema):
```jsx
const [progreso, setProgreso] = useState({...})

useEffect(() => {
  // Cada vez que el componente se monta, crea un nuevo interval
  const intervalId = setInterval(consultarProgreso, 2000)
  return () => clearInterval(intervalId) // Cleanup fallaba por re-renders
}, [documentoId])
```

**DESPUÉS** (✅ Solución):
```jsx
const { documentosEnProceso } = useOcrProgress()

// Solo lee del Context, NO hace polling
const progreso = documentosEnProceso[documentoId] || { estado: 'iniciando', progreso: 0, ... }

useEffect(() => {
  // Solo monitorea cambios para notificar completado/error
  if (progreso.estado === 'completado') onComplete(documentoId)
  if (progreso.estado === 'error') onError(progreso.mensaje)
}, [progreso.estado, documentoId, onComplete, onError, progreso.mensaje])
```

### 4. Digitalizacion.jsx Actualizado

**ANTES**:
```jsx
if (result.documento_id) {
  // Modal deshabilitado por bug de polling
  // setProcessingDocId(result.documento_id)
  // setShowProgressModal(true)
}
```

**DESPUÉS**:
```jsx
import { useOcrProgress } from '../context/OcrProgressContext'

const { iniciarSeguimiento } = useOcrProgress()

if (result.documento_id) {
  console.log('🔍 Iniciando seguimiento OCR para documento:', result.documento_id)
  
  // Registrar documento en Context global
  iniciarSeguimiento(result.documento_id)
  
  // Mostrar modal (ahora seguro)
  setProcessingDocId(result.documento_id)
  setShowProgressModal(true)
}

// Modal re-habilitado
{showProgressModal && processingDocId && (
  <OcrProgressModal
    documentoId={processingDocId}
    onComplete={handleOcrComplete}
    onError={handleOcrError}
  />
)}
```

## 📊 Flujo de Datos

```
1. Usuario sube PDF
   ↓
2. Digitalizacion.jsx recibe documento_id
   ↓
3. iniciarSeguimiento(documento_id) → Context agrega documento al estado
   ↓
4. Context detecta documentosEnProceso no está vacío
   ↓
5. Context inicia UN SOLO setInterval(3s)
   ↓
6. Cada 3s: Promise.all([fetch progreso para cada doc])
   ↓
7. Context actualiza documentosEnProceso con nuevos datos
   ↓
8. OcrProgressModal lee documentosEnProceso[id] → re-render automático
   ↓
9. Cuando progreso.estado === 'completado':
   - Context lo detecta y puede detenerSeguimiento automáticamente
   - Modal detecta y llama onComplete()
   ↓
10. Si documentosEnProceso queda vacío:
    - Context limpia el interval
    - Polling se detiene
```

## 🔍 Ventajas de esta Arquitectura

1. **Un solo punto de polling**: Toda la lógica de consulta está en un lugar
2. **Resistente a re-renders**: El Context vive arriba en el árbol, no se afecta por cambios de UI
3. **Escalable**: Puede manejar múltiples documentos en paralelo con un solo interval
4. **Automático**: Se inicia y detiene según necesidad, sin intervención manual
5. **Eficiente**: Promise.all() hace todas las consultas en paralelo
6. **Limpio**: Componentes son "tontos" - solo leen estado, no manejan lógica de polling

## 🧪 Cómo Probar

1. **Hard refresh del frontend**: `Ctrl + Shift + R`
2. Ir a `/digitalizacion`
3. Subir un PDF con sacramento y libro seleccionados
4. **Verificar en Console**:
   ```
   🔍 Iniciando seguimiento OCR para documento: 123
   🔄 Iniciando polling global para 1 documento(s)
   📊 Progreso actualizado: {...}
   ```
5. **Verificar en Network Tab**:
   - Debe haber UNA solicitud cada 3 segundos
   - NO deben aparecer cientos de solicitudes simultáneas
6. Modal debe mostrar progreso: 5% → 15% → 25% → ... → 100%
7. Al llegar a 100%, modal se cierra y redirige a `/revision-ocr`

## 📁 Archivos Modificados

- ✅ `FRONTEND/src/context/OcrProgressContext.jsx` (NUEVO - 145 líneas)
- ✅ `FRONTEND/src/App.jsx` (wrapper con Provider)
- ✅ `FRONTEND/src/components/OcrProgressModal.jsx` (refactorizado - removido polling local)
- ✅ `FRONTEND/src/pages/Digitalizacion.jsx` (integrado Context, modal re-habilitado)

## 🐛 Debugging

Si el polling no funciona:

1. **Check React DevTools**:
   - Ver si `OcrProgressContext` existe en árbol de componentes
   - Inspeccionar `documentosEnProceso` - debe tener el documento agregado

2. **Check Console**:
   - Buscar: "Iniciando polling global"
   - Si no aparece, el useEffect del Context no se disparó

3. **Check Network Tab**:
   - Filtrar por `/progreso/`
   - Debe haber solicitudes cada 3 segundos
   - Si hay cientos simultáneas, el Context no se integró correctamente

4. **Verificar imports**:
   ```jsx
   // OcrProgressModal.jsx
   import { useOcrProgress } from '../context/OcrProgressContext'
   
   // Digitalizacion.jsx
   import { useOcrProgress } from '../context/OcrProgressContext'
   
   // App.jsx
   import { OcrProgressProvider } from './context/OcrProgressContext'
   ```

## 🚀 Mejoras Futuras (Opcional)

1. **WebSockets**: Reemplazar polling HTTP con WebSocket para actualizaciones push
2. **Persistencia**: Guardar `documentosEnProceso` en localStorage para sobrevivir refreshes
3. **Notificaciones**: Toast notifications cuando un documento en background completa
4. **Lista global**: Panel que muestre todos los documentos procesándose actualmente
5. **Reintentos**: Auto-retry si una consulta falla temporalmente

## 📝 Notas Técnicas

- **Intervalo**: 3 segundos (cambio de 2s para reducir carga)
- **Timeout**: Context no tiene timeout, confía en que el backend marcará estado 'error'
- **Cleanup**: useEffect tiene return que limpia el interval al desmontar
- **Refs**: `intervalRef` y `isPollingRef` previenen race conditions
- **Promise.all**: Espera todas las consultas antes de actualizar estado (evita renders parciales)

---

**Fecha**: Diciembre 2024  
**Problema**: Infinite polling loop en progress modal  
**Solución**: React Context con polling centralizado  
**Estado**: ✅ Implementado y listo para pruebas

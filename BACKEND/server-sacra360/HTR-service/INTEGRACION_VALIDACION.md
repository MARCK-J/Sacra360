# Integración HTR con Flujo de Validación

## 📋 Resumen

El servicio HTR ahora está completamente integrado con el mismo flujo de validación que OCR-Service, permitiendo que los resultados de documentos manuscritos se validen a través del mismo modal de revisión en el frontend.

## 🔄 Flujo Completo

### 1. **Upload de Documento**
```bash
POST http://localhost:8002/api/v1/digitalizacion/upload
Content-Type: multipart/form-data

archivo: Tabla2.pdf
libro_id: 1
tipo_sacramento: 1
modelo_procesamiento: htr  # ← Diferenciador clave
procesar_automaticamente: true
```

### 2. **Procesamiento HTR**
- Documents-service detecta `modelo_procesamiento='htr'`
- Envía al HTR-service en `http://htr-service:8004`
- HTR procesa con 4 engines:
  - BolivianContext (150+ nombres)
  - GridDetector (10 columnas fijas)
  - ManuscriptOCR (EasyOCR + CLAHE)
  - HybridHTRProcessor (alternancia inteligente)

### 3. **Almacenamiento**
```sql
-- documento_digitalizado
modelo_procesamiento = 'htr'
modelo_fuente = 'HTR_Sacra360'
estado_procesamiento = 'ocr_completado'

-- ocr_resultado (10 filas)
fuente_modelo = 'HTR_Sacra360'
datos_ocr = JSONB con {col_1, col_2, ..., col_10}

-- validacion_tuplas (10 registros)
estado = 'pendiente'
```

### 4. **Frontend - Revisión OCR/HTR**

**Ruta:** `http://localhost:5173/revision-ocr`

**Características:**
- ✅ Badge diferenciado: `📝 OCR` vs `✍️ HTR`
- ✅ Misma tabla lista ambos tipos de documentos
- ✅ Columna "Modelo" muestra origen del procesamiento
- ✅ Mismo modal de validación para ambos

### 5. **Endpoints Actualizados**

#### GET /api/v1/digitalizacion/documentos-pendientes
```json
[
  {
    "id": 6,
    "nombre_archivo": "Tabla2.pdf",
    "modelo_procesamiento": "htr",      // ← Nuevo
    "modelo_fuente": "HTR_Sacra360",    // ← Nuevo
    "fuente_modelo": "HTR_Sacra360",    // ← Nuevo
    "total_tuplas": 10,
    "tuplas_pendientes": 10,
    "tuplas_validadas": 0,
    "progreso": 0
  }
]
```

#### GET /api/v1/validacion/tuplas-pendientes/{documento_id}
```json
[
  {
    "documento_id": 6,
    "tupla_numero": 1,
    "id_ocr": 313,
    "fuente_modelo": "HTR_Sacra360",    // ← Nuevo
    "campos_ocr": [
      {
        "id_ocr": 313,
        "campo": "col_1",                 // ← Generado desde JSONB
        "valor_extraido": "CHEPANA NINA JUAN MAIKOL",
        "confianza": 0.85,
        "validado": false
      },
      // ... col_2 a col_10
    ],
    "estado_validacion": "pendiente",
    "total_tuplas_documento": 10
  }
]
```

#### POST /api/v1/validacion/validar-tupla
```json
{
  "documento_id": 6,
  "tupla_numero": 1,
  "usuario_validador_id": 4,
  "accion": "aprobar",        // 'aprobar', 'corregir', 'rechazar'
  "correcciones": [           // ← Actualiza datos_ocr JSONB
    {
      "campo": "col_1",
      "valor_original": "CHEPANA NINA JUAN MAIKOL",
      "valor_corregido": "CHIPANA NINA JUAN MAYKOL",
      "comentario": "Corrección ortográfica"
    }
  ],
  "observaciones": "Tupla validada OK"
}
```

**Respuesta:**
```json
{
  "documento_id": 6,
  "tupla_actual": 1,
  "tupla_validada": true,
  "siguiente_tupla": 2,
  "tuplas_pendientes": 9,
  "tuplas_validadas": 1,
  "total_tuplas": 10,
  "completado": false,
  "mensaje": "Tupla validada exitosamente. Siguiente: 2"
}
```

## 🗄️ Cambios en Base de Datos

### Tabla: documento_digitalizado
```sql
-- Ya existente (sin cambios)
modelo_procesamiento VARCHAR(20) DEFAULT 'ocr'  -- 'ocr' | 'htr'
modelo_fuente VARCHAR(100)                      -- 'EasyOCR V2' | 'HTR_Sacra360'
```

### Tabla: ocr_resultado
```sql
-- Ya existente (sin cambios)
datos_ocr JSONB NOT NULL               -- {"col_1": "...", "col_2": "...", ...}
fuente_modelo VARCHAR(100) NOT NULL    -- 'OCR_V2_EasyOCR' | 'HTR_Sacra360'
```

### Tabla: validacion_tuplas
```sql
-- Ya existente (sin cambios)
-- Se usa para AMBOS modelos (OCR y HTR)
```

## 🎨 Cambios en Frontend

### RevisionOCR.jsx
```jsx
// Badge diferenciado por modelo
<span className={`px-2 py-1 rounded-full text-xs font-semibold ${
  doc.modelo_procesamiento === 'htr' 
    ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300' 
    : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
}`}>
  {doc.modelo_procesamiento === 'htr' ? '✍️ HTR' : '📝 OCR'}
</span>
```

### ValidacionOCRModal.jsx
- ✅ Sin cambios necesarios
- ✅ Trabaja con `campos_ocr` sin importar el origen
- ✅ Correcciones actualizan datos_ocr JSONB automáticamente

## 🧪 Testing

### 1. Verificar documento HTR en lista
```bash
curl http://localhost:8002/api/v1/digitalizacion/documentos-pendientes
```

Buscar: `"modelo_procesamiento": "htr"`

### 2. Verificar tuplas HTR
```bash
curl http://localhost:8002/api/v1/validacion/tuplas-pendientes/6
```

Debe retornar 10 tuplas con `fuente_modelo: "HTR_Sacra360"`

### 3. Validar desde frontend
1. Abrir `http://localhost:5173/revision-ocr`
2. Ver documento ID=6 con badge "✍️ HTR"
3. Click en "Validar"
4. Modal muestra 10 tuplas con col_1 a col_10
5. Validar tupla
6. Verificar siguiente tupla automáticamente

## 📊 Diferencias OCR vs HTR

| Característica | OCR (EasyOCR V2) | HTR (HTR_Sacra360) |
|---------------|------------------|-------------------|
| **Tipo de texto** | Impreso | Manuscrito |
| **Modelo** | EasyOCR Reader | 4 engines personalizados |
| **Formato datos** | JSONB datos_ocr | JSONB datos_ocr (mismo) |
| **Columnas** | Variable | 10 fijas (col_1 a col_10) |
| **Validación** | Modal único | Modal único (mismo) |
| **Badge** | 📝 OCR (azul) | ✍️ HTR (púrpura) |
| **Endpoints** | Compartidos | Compartidos |

## ✅ Checklist de Integración

- [x] HTR-service procesa documentos manuscritos
- [x] Resultados guardados en ocr_resultado con fuente_modelo='HTR_Sacra360'
- [x] Endpoint documentos-pendientes incluye documentos HTR
- [x] Endpoint tuplas-pendientes convierte datos_ocr a campos_ocr
- [x] Endpoint validar-tupla actualiza datos_ocr JSONB con correcciones
- [x] Frontend muestra badge diferenciado para HTR
- [x] Modal de validación funciona con datos HTR
- [x] Registros en validacion_tuplas creados automáticamente
- [x] Flujo completo probado con documento Tabla2.pdf (id=6)

## 🚀 Próximos Pasos Sugeridos

1. **Automatizar creación de validacion_tuplas**
   - HTR-service podría crear registros al finalizar procesamiento
   
2. **Metricas comparativas**
   - Dashboard que compare accuracy OCR vs HTR
   
3. **Configuración dinámica**
   - Permitir cambiar modelo de procesamiento desde frontend
   - Endpoint PUT /modelo/{documento_id} ya existe

4. **Training feedback loop**
   - Usar correcciones para mejorar modelo HTR

## 📝 Notas Importantes

- **Shared Tables:** OCR y HTR comparten `ocr_resultado` y `validacion_tuplas`
- **Diferenciación:** Se logra mediante `fuente_modelo` y `modelo_procesamiento`
- **Compatibilidad:** Endpoints diseñados para trabajar con ambos modelos sin modificaciones en frontend
- **Escalabilidad:** Agregar nuevos modelos (e.g., GPT-4 Vision) solo requiere nuevo fuente_modelo

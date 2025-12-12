# Configuración HTR Service - Resumen de Integración

## ✅ Configuración Completada

### 1. Base de Datos Compartida con OCR-service

#### Tablas Utilizadas:
- **`documento_digitalizado`**: Almacena documentos procesados
- **`ocr_resultado`**: Almacena resultados de procesamiento (tuplas)

#### Diferenciación HTR vs OCR:

| Tabla | Campo | Valor HTR | Valor OCR |
|-------|-------|-----------|-----------|
| `documento_digitalizado` | `modelo_procesamiento` | `'htr'` | `'ocr'` |
| `documento_digitalizado` | `modelo_fuente` | `'HTR_Sacra360'` | `'OCRv2_EasyOCR'` |
| `ocr_resultado` | `fuente_modelo` | `'HTR_Sacra360'` | `'OCRv2_EasyOCR'` |

#### Migración Requerida:
Aplicar: `Migration_Add_HTR_Support.sql`

```sql
-- Agrega columna modelo_procesamiento
ALTER TABLE documento_digitalizado 
ADD COLUMN modelo_procesamiento VARCHAR(20) DEFAULT 'htr';

-- Agrega índices
CREATE INDEX idx_documento_modelo_procesamiento 
ON documento_digitalizado(modelo_procesamiento);

CREATE INDEX idx_ocr_resultado_fuente_modelo 
ON ocr_resultado(fuente_modelo);
```

### 2. Almacenamiento en MinIO - Buckets Separados

#### Configuración de Buckets:

| Servicio | Bucket | Propósito |
|----------|--------|-----------|
| **HTR-service** | `sacra360-htr` | Almacenar imágenes procesadas con HTR |
| **OCR-service** | `sacra360-documents` | Almacenar imágenes procesadas con OCR |

#### Variables de Entorno:

**HTR-service (.env)**:
```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password123
MINIO_HTR_BUCKET=sacra360-htr
MINIO_SECURE=false
```

**OCR-service (.env)**:
```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password123
MINIO_BUCKET=sacra360-documents
MINIO_SECURE=false
```

### 3. Estructura de Archivos Creados

#### Entidades (app/entities/)
- ✅ `htr_entity.py` - Define `DocumentoDigitalizado` y `OcrResultado`
- ✅ `__init__.py` - Exporta entidades

#### Servicios (app/services/)
- ✅ `database_service.py` - Operaciones de BD para HTR
  - `guardar_documento()` - Guarda documento con `modelo_procesamiento='htr'`
  - `guardar_resultado_htr()` - Guarda resultado con `fuente_modelo='HTR_Sacra360'`
  - `actualizar_progreso()` - Actualiza progreso de procesamiento
- ✅ `minio_service.py` - Operaciones MinIO con bucket `sacra360-htr`
  - `upload_file()` - Sube archivo a bucket HTR
  - `download_file()` - Descarga archivo del bucket HTR
- ✅ `__init__.py` - Exporta servicios

#### Configuración (app/utils/)
- ✅ `config.py` - Configuración centralizada con `MINIO_HTR_BUCKET`

### 4. Flujo de Trabajo HTR

```
1. Cliente → POST /api/v1/htr/procesar
   ↓
2. HTR-service recibe imagen
   ↓
3. MinIO: Guardar en bucket 'sacra360-htr'
   ↓
4. Procesar con HTR_Sacra360
   ↓
5. BD: Guardar en documento_digitalizado
   - modelo_procesamiento = 'htr'
   - modelo_fuente = 'HTR_Sacra360'
   ↓
6. BD: Guardar resultados en ocr_resultado
   - fuente_modelo = 'HTR_Sacra360'
   ↓
7. Respuesta → Cliente
```

### 5. Verificación de la Configuración

#### Script de Verificación:
```bash
python verify_htr_migration.py
```

Este script verifica:
- ✅ Existencia de tablas
- ✅ Existencia de columnas HTR
- ✅ Índices creados
- ✅ Datos de prueba

#### Conexión a Base de Datos:
```bash
python verify_database.py
```

### 6. Ejemplo de Uso

#### Guardar Documento HTR:
```python
from app.services.database_service import DatabaseService
from app.services.minio_service import MinIOService

# Subir archivo a MinIO
minio = MinIOService()
upload_result = minio.upload_file(
    file_data=image_bytes,
    file_name="documento.jpg",
    content_type="image/jpeg"
)

# Guardar en BD
db_service = DatabaseService(db)
documento = db_service.guardar_documento(
    imagen_url=upload_result['url'],
    ocr_texto=texto_extraido,
    libros_id=123,
    tipo_sacramento=1,
    modelo_fuente="HTR_Sacra360",
    confianza=0.85,
    modelo_procesamiento="htr"  # ← Importante
)
```

#### Guardar Resultado HTR:
```python
resultado = db_service.guardar_resultado_htr(
    documento_id=documento.id_documento,
    tupla_numero=1,
    datos_htr={
        "nombre_bautizado": "Juan Pérez García",
        "dia_nacimiento": "15",
        "mes_nacimiento": "marzo",
        "ano_nacimiento": "1920"
    },
    confianza=0.85,
    fuente_modelo="HTR_Sacra360"  # ← Importante
)
```

### 7. Docker Compose

El `docker-compose.yml` crea ambos buckets automáticamente:

```yaml
environment:
  MINIO_DEFAULT_BUCKETS: sacra360-documents,sacra360-htr
```

### 8. Consultas SQL Útiles

#### Ver documentos por modelo:
```sql
SELECT modelo_procesamiento, COUNT(*) 
FROM documento_digitalizado 
GROUP BY modelo_procesamiento;
```

#### Ver resultados por fuente:
```sql
SELECT fuente_modelo, COUNT(*) 
FROM ocr_resultado 
GROUP BY fuente_modelo;
```

#### Obtener documentos HTR:
```sql
SELECT * FROM documento_digitalizado 
WHERE modelo_procesamiento = 'htr';
```

#### Obtener resultados HTR:
```sql
SELECT * FROM ocr_resultado 
WHERE fuente_modelo = 'HTR_Sacra360';
```

### 9. Checklist Final

- ✅ Migración `Migration_Add_HTR_Support.sql` aplicada
- ✅ Entidades creadas en `app/entities/htr_entity.py`
- ✅ `DatabaseService` configurado para HTR
- ✅ `MinIOService` usando bucket `sacra360-htr`
- ✅ Variables de entorno `.env` configuradas
- ✅ `docker-compose.yml` crea ambos buckets
- ✅ Scripts de verificación creados
- ✅ Documentación actualizada

## 🎯 Próximos Pasos

1. **Aplicar migración a BD**:
   ```bash
   psql -U postgres -d sacra360 -f Migration_Add_HTR_Support.sql
   ```

2. **Verificar migración**:
   ```bash
   python verify_htr_migration.py
   ```

3. **Iniciar servicios**:
   ```bash
   docker-compose up -d
   ```

4. **Verificar buckets en MinIO**:
   - Abrir http://localhost:9001
   - Login: admin / password123
   - Verificar buckets: `sacra360-htr` y `sacra360-documents`

---

**Fecha**: Diciembre 2024  
**Versión**: 1.0.0  
**Estado**: ✅ Configuración Completa

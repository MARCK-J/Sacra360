# Guía de Integración: HTR-service

## 📋 Resumen

El HTR-service está **100% integrado** con el sistema Sacra360:

- ✅ **Mismo almacenamiento DB**: Usa las tablas `documento_digitalizado` y `ocr_resultado`
- ✅ **Diferenciación**: Campo `modelo_procesamiento = 'htr'` (vs `'ocr'`)
- ✅ **Bucket MinIO separado**: `sacra360-htr` (vs `sacra360-documents` para OCR)
- ✅ **Misma conexión**: Documents-Service llama a HTR-service igual que a OCR-service
- ✅ **Modelo integrado**: HTR_Sacra360_Colab_Final.ipynb funciona idéntico en el servicio

## 🔄 Flujo de Integración

```
Usuario (Frontend)
    ↓
Documents-Service (8002)
    ↓ (valida modelo_procesamiento)
    ├─→ si modelo = 'ocr'  → POST http://ocr-service:8003/api/v1/ocr/procesar-desde-bd/{id}
    └─→ si modelo = 'htr'  → POST http://htr-service:8004/api/v1/htr/procesar-desde-bd/{id}
    ↓
HTR-Service (8004)
    ↓
1. Lee documento_digitalizado WHERE id_documento = {id}
2. Descarga PDF desde MinIO (bucket: sacra360-htr)
3. Procesa con HTR_Sacra360 (4 motores):
   - BolivianContext: Corrector
   - GridDetector: Detecta 10 columnas
   - ManuscriptOCR: EasyOCR + CLAHE
   - HybridHTRProcessor: Alternancia inteligente
4. Guarda resultados en ocr_resultado
   - documento_id: {id}
   - fuente_modelo: 'HTR_Sacra360'
   - datos_ocr: JSON con col_1 a col_10
5. Actualiza documento_digitalizado
   - estado_procesamiento = 'ocr_completado'
   - modelo_procesamiento = 'htr'
   - modelo_fuente = 'HTR_Sacra360'
```

## 🗄️ Esquema de Base de Datos

### Tabla: `documento_digitalizado`

```sql
CREATE TABLE documento_digitalizado (
    id_documento SERIAL PRIMARY KEY,
    nombre_archivo VARCHAR(255),
    imagen_url TEXT,
    estado_procesamiento VARCHAR(50),
    modelo_procesamiento VARCHAR(20),  -- 'htr' o 'ocr' ✅
    modelo_fuente VARCHAR(100),        -- 'HTR_Sacra360' o 'EasyOCR V2'
    progreso_ocr INTEGER,
    mensaje_progreso TEXT,
    -- ... otros campos
);
```

### Tabla: `ocr_resultado`

```sql
CREATE TABLE ocr_resultado (
    id_resultado SERIAL PRIMARY KEY,
    documento_id INTEGER REFERENCES documento_digitalizado(id_documento),
    tupla_numero INTEGER,
    datos_ocr JSONB,                   -- {col_1: "...", col_2: "...", ...}
    confianza FLOAT,
    fuente_modelo VARCHAR(50),         -- 'HTR_Sacra360' o 'EasyOCR V2'
    validado BOOLEAN DEFAULT FALSE,
    estado_validacion VARCHAR(20) DEFAULT 'pendiente'
);
```

## 🚀 Despliegue

### 1. Aplicar Migración

```bash
# En el contenedor de PostgreSQL o localmente
psql -U postgres -d sacra360 -f sql/Migration_Add_HTR_Support.sql
```

Esta migración agrega la columna `modelo_procesamiento` a `documento_digitalizado`.

### 2. Construir Imagen Docker

```bash
cd BACKEND/server-sacra360/HTR-service
docker build -t sacra360/htr-service:latest .
```

### 3. Iniciar Servicio

**Opción A: Con Docker Compose (standalone)**
```bash
docker-compose up -d --build
```

**Opción B: Integrado con docker-compose principal**
```bash
# Agregar al docker-compose.yml principal:
cd BACKEND
docker-compose up -d htr-service
```

**Opción C: Local (desarrollo)**
```bash
# 1. Instalar dependencias
pip install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env
# Editar DATABASE_URL, MINIO_ENDPOINT, etc.

# 3. Verificar
python verificar_servicio.py

# 4. Iniciar
python run_service.py
```

### 4. Verificar Integración

```bash
# 1. Health check
curl http://localhost:8004/health

# 2. Verificar que Documents-Service conoce al HTR-service
# En Documents-service/.env debe estar:
# HTR_SERVICE_URL=http://htr-service:8004

# 3. Probar procesamiento
curl -X POST http://localhost:8004/api/v1/htr/procesar-desde-bd/123

# 4. Consultar progreso
curl http://localhost:8004/api/v1/htr/progreso/123
```

## 📊 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Health check del servicio |
| POST | `/api/v1/htr/procesar-desde-bd/{id}` | Procesa documento desde BD |
| GET | `/api/v1/htr/progreso/{id}` | Consulta progreso de procesamiento |
| GET | `/docs` | Swagger UI |

## 🔧 Configuración Documents-Service

En `Documents-service/.env`:

```env
# URL del HTR Service
HTR_SERVICE_URL=http://htr-service:8004

# URL del OCR Service
OCR_SERVICE_URL=http://ocr-service:8003
```

En `Documents-service/app/services/digitalizacion_service.py`:

```python
async def procesar_documento_async(self, documento_id: int, modelo_procesamiento: str):
    """
    Procesa documento con OCR o HTR según modelo_procesamiento
    """
    if modelo_procesamiento == 'htr':
        service_url = f"{self.htr_service_url}/api/v1/htr/procesar-desde-bd/{documento_id}"
    else:
        service_url = f"{self.ocr_service_url}/api/v1/ocr/procesar-desde-bd/{documento_id}"
    
    # POST al servicio correspondiente...
```

## 🧪 Testing

### Test de Integración Completa

```bash
# 1. Subir documento con modelo_procesamiento='htr'
curl -X POST http://localhost:8002/api/v1/documentos/subir \
  -F "file=@test.pdf" \
  -F "modelo_procesamiento=htr"

# Respuesta: { "id_documento": 456 }

# 2. Verificar estado en BD
psql -U postgres -d sacra360 -c \
  "SELECT id_documento, estado_procesamiento, modelo_procesamiento, progreso_ocr 
   FROM documento_digitalizado WHERE id_documento = 456;"

# 3. Consultar resultados
psql -U postgres -d sacra360 -c \
  "SELECT tupla_numero, datos_ocr->>'col_1' as nombre, fuente_modelo 
   FROM ocr_resultado WHERE documento_id = 456 LIMIT 5;"
```

### Validar Diferenciación OCR vs HTR

```sql
-- Documentos procesados con HTR
SELECT id_documento, nombre_archivo, modelo_procesamiento, modelo_fuente
FROM documento_digitalizado
WHERE modelo_procesamiento = 'htr';

-- Documentos procesados con OCR
SELECT id_documento, nombre_archivo, modelo_procesamiento, modelo_fuente
FROM documento_digitalizado
WHERE modelo_procesamiento = 'ocr';

-- Resultados agrupados por fuente
SELECT fuente_modelo, COUNT(*) as total_tuplas
FROM ocr_resultado
GROUP BY fuente_modelo;
```

## 📦 Estructura de Datos de Salida

### Ejemplo de `datos_ocr` en `ocr_resultado`

```json
{
  "col_1": "JUAN PEREZ LOPEZ",
  "col_2": "15/03/1985",
  "col_3": "16/03/1985",
  "col_4": "20/04/1985",
  "col_5": "LA PAZ",
  "col_6": "01/01/1960",
  "col_7": "02/01/1960",
  "col_8": "15/02/1960",
  "col_9": "MARIA LOPEZ QUISPE",
  "col_10": "PARROQUIA SAN PEDRO"
}
```

**Patrón de columnas**: `[text, date, date, date, text, date, date, date, text, text]`

## 🐛 Troubleshooting

### El servicio no inicia

```bash
# Verificar logs
docker logs sacra360_htr_service

# Verificar que el puerto 8004 esté libre
netstat -tuln | grep 8004

# Verificar dependencias
docker exec sacra360_htr_service pip list
```

### EasyOCR falla

```bash
# Verificar modelos descargados
docker exec sacra360_htr_service ls -la ~/.EasyOCR/

# Verificar memoria
docker stats sacra360_htr_service

# Si falta memoria, aumentar en docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

### Poppler no disponible

```bash
# Verificar instalación
docker exec sacra360_htr_service which pdftoppm

# Si no está, reconstruir imagen
docker-compose build --no-cache htr-service
```

### Progreso no actualiza

```sql
-- Verificar última actualización
SELECT id_documento, progreso_ocr, mensaje_progreso, fecha_procesamiento
FROM documento_digitalizado
WHERE id_documento = 123;

-- Limpiar progreso bloqueado
UPDATE documento_digitalizado
SET estado_procesamiento = 'pendiente', progreso_ocr = 0
WHERE id_documento = 123;
```

## 📝 Checklist de Integración

- [ ] Migración `Migration_Add_HTR_Support.sql` aplicada
- [ ] HTR-service construido (`docker build`)
- [ ] HTR-service iniciado (`docker-compose up`)
- [ ] Variables de entorno configuradas (`.env`)
- [ ] MinIO bucket `sacra360-htr` existe
- [ ] Documents-Service tiene `HTR_SERVICE_URL` configurado
- [ ] Health check responde: `curl localhost:8004/health`
- [ ] Swagger UI accesible: `http://localhost:8004/docs`
- [ ] Procesamiento de prueba exitoso
- [ ] Resultados guardados en `ocr_resultado` con `fuente_modelo='HTR_Sacra360'`
- [ ] Diferenciación `modelo_procesamiento='htr'` funciona

## 🎯 Próximos Pasos

1. **Frontend**: Agregar opción para seleccionar modelo HTR en upload
2. **Validación**: Implementar validación específica para resultados HTR
3. **Monitoreo**: Agregar métricas de rendimiento HTR vs OCR
4. **Optimización**: Ajustar parámetros según documentos reales
5. **Scaling**: Configurar múltiples workers para procesamiento paralelo

## 📚 Referencias

- Notebook original: `models/HTR_Sacra360_Colab_Final.ipynb`
- Migración: `sql/Migration_Add_HTR_Support.sql`
- Documentación API: `http://localhost:8004/docs`
- README detallado: `BACKEND/server-sacra360/HTR-service/README.md`

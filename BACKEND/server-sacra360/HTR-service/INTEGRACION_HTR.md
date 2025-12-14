# Integración HTR Service - Sacra360

## 📋 Resumen

Este documento describe la integración del servicio HTR (Handwritten Text Recognition) en el proyecto Sacra360, especializado en el reconocimiento de texto manuscrito en documentos sacramentales históricos.

## 🎯 Objetivo

Procesar imágenes de registros sacramentales manuscritos (bautizos, confirmaciones, matrimonios) usando redes neuronales especializadas (HTR_Sacra360) para extraer información estructurada.

## 🏗️ Arquitectura

### Componentes Principales

1. **FastAPI Service** (Puerto 8004)
   - Endpoints REST para procesamiento HTR
   - Validación de archivos
   - Gestión de resultados

2. **HTR Processor**
   - Modelo HTR_Sacra360 con PyTorch
   - Procesamiento de imágenes con OpenCV
   - Extracción de texto manuscrito

3. **PostgreSQL Database** (Compartida con OCR-service)
   - Tabla `documento_digitalizado`: almacena documentos procesados (campo `modelo_procesamiento` = 'htr')
   - Tabla `ocr_resultado`: almacena resultados HTR (campo `fuente_modelo` = 'HTR_Sacra360')
   - Historial de procesamiento
   - Metadatos de documentos

4. **MinIO Object Storage** (Bucket separado)
   - **Bucket HTR**: `sacra360-htr` (exclusivo para HTR)
   - **Bucket OCR**: `sacra360-documents` (exclusivo para OCR)
   - Almacenamiento de imágenes originales
   - Imágenes preprocesadas
   - Archivos temporales

## 📁 Estructura del Proyecto

```
HTR-service/
├── app/
│   ├── main.py                    # Aplicación FastAPI
│   ├── database.py                # Configuración DB
│   ├── controllers/               # Lógica de negocio
│   ├── dto/                       # Data Transfer Objects
│   ├── entities/                  # Modelos de BD
│   ├── routers/
│   │   └── htr_router.py         # Endpoints HTR
│   ├── services/
│   │   ├── htr_processor.py      # Procesador HTR principal
│   │   └── minio_service.py      # Cliente MinIO
│   └── utils/
│       ├── config.py             # Configuración centralizada
│       └── __init__.py           # Utilidades
├── tests/                         # Tests unitarios
├── models/                        # Modelos HTR entrenados
├── requirements.txt               # Dependencias
├── Dockerfile                     # Imagen Docker
├── docker-compose.yml            # Orquestación
└── README.md                     # Documentación
```

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Base de datos (compartida con OCR-service)
DATABASE_URL=postgresql://postgres:password@localhost:5432/sacra360

# Servicio
SERVICE_PORT=8004
LOG_LEVEL=INFO

# MinIO (bucket separado para HTR)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password123
MINIO_HTR_BUCKET=sacra360-htr
MINIO_SECURE=false

# HTR Model
HTR_MODEL_PATH=./models/htr_model.pth
HTR_CONFIDENCE_THRESHOLD=0.7
```

### Diferenciación HTR vs OCR

El sistema diferencia entre procesamiento HTR y OCR mediante:

#### En la tabla `documento_digitalizado`:
- **Campo `modelo_procesamiento`**: 
  - `'htr'` para documentos procesados con HTR
  - `'ocr'` para documentos procesados con OCR
- **Campo `modelo_fuente`**: 
  - `'HTR_Sacra360'` para HTR
  - `'OCRv2_EasyOCR'` para OCR

#### En la tabla `ocr_resultado`:
- **Campo `fuente_modelo`**: 
  - `'HTR_Sacra360'` para resultados de HTR
  - `'OCRv2_EasyOCR'` para resultados de OCR

#### En MinIO:
- **Bucket `sacra360-htr`**: archivos procesados con HTR
- **Bucket `sacra360-documents`**: archivos procesados con OCR

## 🚀 Instalación y Ejecución

### Opción 1: Desarrollo Local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Ejecutar servicio
python run_service.py
```

### Opción 2: Docker Compose

```bash
# Construir y ejecutar
docker-compose up --build

# Ejecutar en background
docker-compose up -d

# Ver logs
docker-compose logs -f htr-service

# Detener
docker-compose down
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "HTR Service - Sacra360",
  "timestamp": "2024-12-11T10:30:00"
}
```

### Status Detallado
```http
GET /status
```

**Response:**
```json
{
  "service": "HTR Service - Sacra360",
  "version": "1.0.0",
  "status": "healthy",
  "config": {
    "htr_model_path": "./models/htr_model.pth",
    "confidence_threshold": 0.7,
    "max_file_size_mb": 50
  }
}
```

### Procesar Documento HTR
```http
POST /api/v1/htr/procesar
Content-Type: multipart/form-data

{
  "file": <archivo_imagen>,
  "documento_id": 123,
  "tipo_sacramento": "bautizo"
}
```

**Response:**
```json
{
  "success": true,
  "documento_id": 123,
  "texto_extraido": "...",
  "confianza": 0.85,
  "campos_extraidos": {
    "nombre_bautizado": "Juan Pérez García",
    "dia_nacimiento": "15",
    "mes_nacimiento": "marzo",
    "ano_nacimiento": "1920"
  }
}
```

### Obtener Resultados
```http
GET /api/v1/htr/resultados/{documento_id}
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest tests/

# Con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_basic.py -v
```

### Test Manual con HTTP Client
Usar el archivo `test_htr_endpoint.http` con la extensión REST Client de VS Code.

### Test con Script Python
```bash
python test_endpoint_client.py /path/to/test_image.jpg
```

## 🔄 Flujo de Procesamiento

1. **Recepción**: Cliente envía imagen vía API
2. **Validación**: Verificar formato, tamaño, tipo
3. **Almacenamiento**: Guardar en MinIO
4. **Preprocesamiento**: 
   - Conversión a escala de grises
   - Normalización
   - Eliminación de ruido
5. **HTR**: Modelo HTR_Sacra360 procesa la imagen
6. **Extracción**: Extraer campos estructurados
7. **Persistencia**: Guardar resultados en PostgreSQL
8. **Respuesta**: Devolver resultados al cliente

## 🎨 Modelo HTR_Sacra360

### Características
- **Arquitectura**: CRNN (Convolutional Recurrent Neural Network)
- **Framework**: PyTorch 2.2.0
- **Entrada**: Imágenes de texto manuscrito
- **Salida**: Texto transcrito + confianza

### Entrenamiento
El modelo fue entrenado con:
- Registros sacramentales históricos (1800-1950)
- Diferentes estilos de escritura
- Documentos envejecidos y deteriorados

### Optimizaciones
- Modelo cuantizado para CPU
- Inferencia optimizada
- Cache de predicciones frecuentes

## 📊 Métricas y Monitoreo

### Métricas Disponibles
- Tiempo de procesamiento
- Confianza promedio
- Tasa de éxito/error
- Documentos procesados

### Logs
Los logs se almacenan en formato estructurado:
```
2024-12-11 10:30:00 - HTR Service - INFO - Documento 123 procesado exitosamente
```

## 🔒 Seguridad

### Validaciones
- Tamaño máximo de archivo: 50MB
- Formatos permitidos: JPG, PNG, PDF
- Rate limiting (en producción)
- Sanitización de inputs

### Autenticación (Producción)
- Bearer token authentication
- JWT validation
- Role-based access control

## 🐛 Troubleshooting

### Problema: Servicio no inicia
**Solución**: Verificar que PostgreSQL y MinIO están corriendo
```bash
python verify_database.py
```

### Problema: Error al cargar modelo
**Solución**: Verificar ruta del modelo en `.env`
```bash
# Verificar que el archivo existe
ls -la models/htr_model.pth
```

### Problema: Baja confianza en resultados
**Solución**: 
- Verificar calidad de imagen
- Ajustar preprocesamiento
- Revisar umbral de confianza

## 📈 Mejoras Futuras

1. **Performance**
   - Soporte para GPU
   - Procesamiento por lotes
   - Cache de resultados

2. **Funcionalidad**
   - Múltiples idiomas
   - Post-procesamiento inteligente
   - Corrección ortográfica

3. **Integración**
   - Webhook notifications
   - Streaming de resultados
   - API versioning

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyTorch HTR Tutorial](https://pytorch.org/tutorials/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)

## 🤝 Contribuir

Ver [README.md](README.md) para guías de contribución.

---

**Última actualización**: Diciembre 2024  
**Versión**: 1.0.0  
**Contacto**: Equipo Sacra360

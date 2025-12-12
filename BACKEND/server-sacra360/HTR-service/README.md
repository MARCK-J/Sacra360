# HTR Service - Sacra360

Microservicio especializado en reconocimiento de texto manuscrito (Handwritten Text Recognition) para documentos sacramentales históricos.

## 🎯 Características

- **Modelo HTR_Sacra360**: Implementación exacta del notebook HTR_Sacra360_Colab_Final.ipynb
- **4 Motores de Procesamiento**:
  - **BolivianContext**: Corrector con 150+ nombres/apellidos bolivianos
  - **GridDetector**: Detección de estructura de tabla (10 columnas fijas)
  - **ManuscriptOCR**: EasyOCR con preprocesamiento CLAHE + 2.5x scale
  - **HybridHTRProcessor**: Orquestador con alternancia inteligente de filas
- **Procesamiento Inteligente**: Skipea filas de ruido/separación automáticamente
- **Integración Completa**: API REST + PostgreSQL + MinIO
- **Docker Ready**: Contenedorización completa con versiones exactas de librerías

## 📐 Arquitectura del Modelo HTR

### Patrón de Columnas Fijo

El modelo detecta **10 columnas fijas** con este patrón:

```
[text, date, date, date, text, date, date, date, text, text]
 L     N     N     N     L     N     N     N     L     L
```

- **L (text)**: Nombres, apellidos, lugares (con corrección contextual)
- **N (date)**: Fechas en formato DD/MM/YYYY

### Flujo de Procesamiento

```
PDF (bytes) → convert_to_image (3965x8038px)
            ↓
        GridDetector
            ↓
    Detectar 11 líneas verticales → 10 columnas
    Detectar N líneas horizontales → filas
            ↓
    HybridHTRProcessor (Alternancia Inteligente)
            ↓
    Para cada fila:
      - Validar altura (>20px)
      - Si expect_noise_next y altura < 75% anterior → SKIP
      - Procesar 10 celdas con ManuscriptOCR
      - Validar contenido (>3 chars totales)
      - Guardar tupla si válida
      - expect_noise_next = True
            ↓
    Lista de tuplas con datos_ocr (col_1 a col_10)
```

### Preprocesamiento de Celdas

```python
# CLAHE (Contrast Limited Adaptive Histogram Equalization)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

# Scale 2.5x para mejor resolución
scale_factor = 2.5

# Morfología para limpieza
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
binary = cv2.dilate(binary, kernel, iterations=1)
```

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- PostgreSQL 15+
- MinIO Server
- Docker y Docker Compose (para deployment)
- **Poppler 22.02+** (para pdf2image)

### Instalación Local

1. **Clonar y navegar al directorio**:
```bash
cd BACKEND/server-sacra360/HTR-service
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias del sistema** (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils libgl1 libglib2.0-0
```

4. **Instalar dependencias de Python**:
```bash
# Primero PyTorch (CPU)
pip install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cpu

# Luego el resto
pip install -r requirements.txt
```

5. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

6. **Verificar instalación**:
```bash
python test_htr_model.py
```

7. **Ejecutar el servicio**:
```bash
python run_service.py
```

El servicio estará disponible en `http://localhost:8004`

### Con Docker Compose

```bash
docker-compose up --build
```

## 📚 Documentación API

Una vez iniciado el servicio, accede a:

- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc

## 🏗️ Estructura del Proyecto

```
HTR-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── database.py          # Configuración de base de datos
│   ├── controllers/         # Lógica de negocio
│   ├── dto/                 # Data Transfer Objects
│   ├── entities/            # Modelos de base de datos
│   ├── routers/            # Endpoints de la API
│   │   └── htr_router.py
│   ├── services/           # Servicios de procesamiento
│   │   ├── htr_processor.py
│   │   └── minio_service.py
│   └── utils/              # Utilidades y configuración
│       └── config.py
├── tests/                  # Tests unitarios y de integración
├── models/                 # Modelos HTR entrenados
├── requirements.txt        # Dependencias Python
├── Dockerfile             # Imagen Docker
├── docker-compose.yml     # Orquestación de servicios
├── .env.example          # Plantilla de variables de entorno
└── README.md             # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

Consulta `.env.example` para ver todas las variables disponibles:

- `DATABASE_URL`: Conexión a PostgreSQL
- `SERVICE_PORT`: Puerto del servicio (8004)
- `MINIO_ENDPOINT`: Endpoint de MinIO
- `HTR_MODEL_PATH`: Ruta al modelo HTR entrenado
- `HTR_CONFIDENCE_THRESHOLD`: Umbral de confianza para predicciones

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/

# Con cobertura
pytest --cov=app tests/

# Ver reporte HTML
pytest --cov=app --cov-report=html tests/
```

## 📊 Endpoints Principales

### Health Check
```bash
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "HTR Service",
  "version": "1.0.0"
}
```

### Procesar Documento desde BD
```bash
POST /api/v1/htr/procesar-desde-bd/{documento_id}
```

**Descripción**: Procesa un documento ya almacenado en la BD usando el modelo HTR_Sacra360.

**Parámetros**:
- `documento_id` (path): ID del documento en `documento_digitalizado`

**Respuesta Exitosa**:
```json
{
  "estado": "success",
  "mensaje": "HTR completado exitosamente",
  "total_tuplas": 45,
  "documento_id": 123
}
```

**Ejemplo de datos extraídos**:
```json
{
  "tupla_numero": 1,
  "datos_ocr": {
    "col_1": "JUAN PEREZ",
    "col_2": "15/03/1985",
    "col_3": "16/03/1985",
    "col_4": "20/04/1985",
    "col_5": "LA PAZ",
    "col_6": "01/01/1960",
    "col_7": "02/01/1960",
    "col_8": "15/02/1960",
    "col_9": "MARIA LOPEZ",
    "col_10": "PARROQUIA SAN PEDRO"
  }
}
```

### Consultar Progreso
```bash
GET /api/v1/htr/progreso/{documento_id}
```

**Descripción**: Obtiene el progreso del procesamiento HTR.

**Respuesta**:
```json
{
  "estado": "procesando_htr",
  "progreso": 65,
  "mensaje": "Procesadas 450/700 celdas (HTR)",
  "etapa": "htr"
}
```

**Estados posibles**:
- `iniciando`: Preparando procesamiento
- `descargando`: Descargando archivo de MinIO
- `procesando_htr`: Ejecutando modelo HTR
- `guardando`: Guardando resultados en BD
- `completado`: Procesamiento finalizado
- `error`: Error durante el proceso

### Subir y Procesar Documento (Local)
```bash
POST /api/v1/htr/procesar
Content-Type: multipart/form-data

{
  "file": <archivo_imagen>,
  "documento_id": 123,
  "tipo_sacramento": "bautizo"
}
```

### Obtener Resultados
```bash
GET /api/v1/htr/resultados/{documento_id}
```

## 🔐 Seguridad

- Validación de archivos subidos
- Límite de tamaño de archivo (50MB)
- Autenticación mediante tokens (en producción)
- CORS configurado para dominios específicos

## 📝 Desarrollo

### Agregar nuevas funcionalidades

1. Crear nuevos endpoints en `app/routers/`
2. Implementar lógica en `app/services/`
3. Agregar tests en `tests/`
4. Actualizar documentación

### Modelo HTR

El modelo HTR_Sacra360 se entrena con documentos históricos manuscritos. Para actualizar:

1. Entrenar nuevo modelo
2. Guardar en `models/`
3. Actualizar `HTR_MODEL_PATH` en `.env`

## 🐛 Troubleshooting

### Error de conexión a base de datos
- Verificar que PostgreSQL esté corriendo
- Comprobar `DATABASE_URL` en `.env`

### Error al cargar modelo HTR
- Verificar que el archivo del modelo existe en `HTR_MODEL_PATH`
- Comprobar compatibilidad de versiones de PyTorch

### Problema con MinIO
- Verificar que MinIO esté corriendo
- Comprobar credenciales en `.env`

## 📦 Dependencias Principales

- FastAPI 0.104.1
- PyTorch 2.2.0 (CPU)
- EasyOCR 1.7.2
- SQLAlchemy 2.0.23
- MinIO 7.2.0

## 📄 Licencia

Proyecto Sacra360 - 2024

## 👥 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

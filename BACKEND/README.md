# 🏗️ ARQUITECTURA BACKEND SACRA360 - MICROSERVICIOS

## 📋 **RESUMEN EJECUTIVO**
Backend de microservicios para sistema de gestión y digitalización de archivos sacramentales del Arzobispado. Arquitectura modular con contenedores Docker, procesamiento de documentos OCR/HTR, inteligencia artificial para completación de texto, y APIs REST independientes.

---

## � **ESTRUCTURA GENERAL DEL PROYECTO**

### **Raíz del Proyecto**
```
SACRA360_Backend/
├── 📁 server-sacra360/          # Contenedor principal de microservicios
├── 📁 HTTP/                     # Archivos .http para testing de APIs
├── 📁 schemas/                  # Esquemas de base de datos y migraciones
├── 📁 pocketbase_data/          # Datos persistentes de PocketBase
├── 📁 sql/                      # Scripts SQL adicionales
├── 🐳 docker-compose.yml        # Orquestación de contenedores
├── 📄 requirements.txt          # Dependencias Python globales
└── 📚 README.md                 # Documentación del proyecto
```

## 🏢 **ARQUITECTURA DE MICROSERVICIOS SACRA360**

```

### 🔧 Microservicios Implementados

#### 1. **OCR Service** (`/api/v1/ocr/`)
- **Tecnología**: Tesseract + OpenCV
- **Función**: Reconocimiento de texto impreso
- **Endpoints**:
  - `POST /upload-and-process` - Subir y procesar imagen
  - `POST /process/{document_id}` - Procesar documento existente
  - `GET /status/{document_id}` - Estado del procesamiento
  - `GET /languages` - Idiomas soportados

#### 2. **HTR Service** (`/api/v1/htr/`)
- **Tecnología**: CNN + LSTM (PyTorch)
- **Función**: Reconocimiento de texto manuscrito
- **Endpoints**:
  - `POST /upload-and-process` - Subir y procesar imagen manuscrita
  - `POST /process/{document_id}` - Procesar documento existente
  - `POST /compare-with-ocr/{document_id}` - Comparar con OCR
  - `GET /models` - Modelos disponibles

#### 3. **AI Completion Service** (`/api/v1/ai-completion/`)
- **Tecnología**: BERT/RoBERTa (Transformers)
- **Función**: Complementación y corrección de texto
- **Endpoints**:
  - `POST /complete-text` - Completar y corregir texto
  - `POST /suggest-word/{word}` - Sugerir completaciones
  - `POST /combine-ocr-htr/{document_id}` - Combinar resultados
  - `GET /vocabulary` - Vocabulario sacramental

#### 4. **Document Management** (`/api/v1/documents/`)
- **Función**: Gestión integral de documentos
- **Endpoints**:
  - `POST /upload` - Subir documento con procesamiento automático
  - `GET /` - Listar documentos
  - `GET /{document_id}` - Obtener documento específico
  - `PUT /{document_id}` - Actualizar documento
  - `DELETE /{document_id}` - Eliminar documento

## 🚀 Inicio Rápido

### Opción 1: Desarrollo Local

1. **Crear entorno virtual**:
```bash
cd BACKEND
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Instalar dependencias mínimas**:
```bash
pip install -r requirements-minimal.txt
```

3. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. **Ejecutar aplicación**:
```bash
uvicorn main:app --reload
```

### Opción 2: Docker Compose (Recomendado)

1. **Ejecutar stack completo**:
```bash
docker-compose up -d
```

Esto levanta:
- **FastAPI Backend**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **MinIO**: http://localhost:9001 (consola)
- **Redis**: localhost:6379

## 📋 Dependencias Principales

### Core Framework
- **FastAPI**: Framework web asíncrono
- **SQLAlchemy**: ORM para PostgreSQL
- **Pydantic**: Validación de datos

### Procesamiento de Imágenes y ML
- **OpenCV**: Procesamiento de imágenes
- **PyTorch**: Deep learning para HTR
- **Transformers**: Modelos BERT para AI completion
- **Tesseract**: OCR tradicional

### Almacenamiento
- **MinIO**: Almacenamiento compatible con S3
- **PostgreSQL**: Base de datos principal

## 🔨 Configuración Avanzada

### Variables de Entorno Principales

```env
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/sacra360_db

# Almacenamiento de archivos
MINIO_ENDPOINT=localhost:9000
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800  # 50MB

# Configuración de OCR
TESSERACT_CMD=tesseract
OCR_LANGUAGES=spa,eng

# Modelos de IA
BERT_MODEL_NAME=dccuchile/bert-base-spanish-wwm-uncased
HTR_MODEL_PATH=./models/htr_model.pth
```

### Instalación de Dependencias del Sistema

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

#### Windows
1. Descargar Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar y configurar PATH
3. Instalar idiomas españoles

## 🧪 Pruebas

### Ejecutar pruebas unitarias
```bash
pytest tests/ -v
```

### Ejecutar con cobertura
```bash
pytest tests/ --cov=app --cov-report=html
```

### Pruebas específicas
```bash
# Solo pruebas de API
pytest tests/test_api.py

# Solo pruebas de procesadores
pytest tests/test_processors.py
```

## 📊 Monitoreo y Logs

### Endpoints de Salud
- `GET /health` - Estado general del sistema
- `GET /` - Información básica de la API

### Documentación Automática
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Estadísticas
- `GET /api/v1/stats/dashboard` - Métricas del sistema

## 🔧 Desarrollo

### Estructura de Desarrollo
```bash
# Formatear código
black app/ tests/

# Ordenar imports
isort app/ tests/

# Verificar estilo
flake8 app/ tests/

# Ejecutar pruebas
pytest
```

### Agregar Nuevo Microservicio

1. Crear directorio en `app/nuevo_servicio/`
2. Implementar `processor.py` con la lógica del servicio
3. Crear `router.py` con los endpoints FastAPI
4. Agregar `__init__.py` exportando componentes
5. Incluir router en `app/api/router.py`
6. Agregar pruebas en `tests/`

## 🚀 Despliegue

### Producción con Docker
```bash
# Construir imagen
docker build -t sacra360-backend .

# Ejecutar con docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Variables de Entorno de Producción
- Cambiar `SECRET_KEY` por valor seguro
- Configurar `DATABASE_URL` de producción
- Establecer `DEBUG=false`
- Configurar almacenamiento S3 real

## 📝 API Usage Examples

### Subir y Procesar Documento
```python
import requests

# Subir archivo con procesamiento automático
with open('documento.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/documents/upload',
        files={'file': f},
        data={
            'parish_id': 1,
            'sacrament_type_id': 1,
            'process_ocr': True,
            'process_htr': True,
            'process_ai': True
        }
    )

document_id = response.json()['document_id']
```

### Verificar Estado del Procesamiento
```python
# Obtener estado completo
response = requests.get(
    f'http://localhost:8000/api/v1/documents/{document_id}/processing-status'
)
status = response.json()
```

### Usar Servicios Individualmente
```python
# Solo OCR
response = requests.post(
    'http://localhost:8000/api/v1/ocr/upload-and-process',
    files={'file': open('image.jpg', 'rb')},
    data={'language': 'spa', 'use_preprocessing': True}
)

# Completar texto con IA
response = requests.post(
    'http://localhost:8000/api/v1/ai-completion/complete-text',
    json={
        'text': 'Texto con errores para corregir',
        'max_suggestions': 5
    }
)
```

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para reportar bugs o solicitar features, crear un issue en el repositorio de GitHub.
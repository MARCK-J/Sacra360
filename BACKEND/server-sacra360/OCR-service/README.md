# OCR Service - Sacra360

Microservicio de OCR para procesamiento de documentos sacramentales con integración a MinIO.

## 🚀 **Características**

- **Procesamiento OCR**: Extracción de texto de imágenes y PDFs
- **Integración MinIO**: Almacenamiento automático de archivos
- **Base de Datos**: PostgreSQL para persistencia
- **API REST**: FastAPI con documentación automática
- **Docker**: Despliegue containerizado completo

## 📋 **Requisitos**

- Docker y Docker Compose
- 4GB RAM mínimo
- Puertos 8003, 5432, 9000, 9001 disponibles

## ⚡ **Inicio Rápido**

```bash
# Clonar y navegar
cd OCR-service

# Levantar servicios
docker-compose up -d

# Verificar servicios
docker-compose ps
```

## 🔗 **Endpoints**

- **API OCR**: http://localhost:8003
- **Documentación**: http://localhost:8003/docs
- **MinIO Console**: http://localhost:9001 (admin/password123)
- **PostgreSQL**: localhost:5432

## 📡 **API Principal**

### Procesar Documento
```bash
POST /api/v1/ocr/procesar
Content-Type: multipart/form-data

{
  "archivo": [archivo imagen/PDF],
  "libros_id": 1,
  "tipo_sacramento": 2,
  "guardar_en_bd": true
}
```

### Health Check
```bash
GET /api/v1/ocr/health
```

## 🏗️ **Arquitectura**

```
OCR-Service/
├── app/
│   ├── main.py              # FastAPI app
│   ├── controllers/         # Endpoints REST
│   ├── services/           # Lógica de negocio
│   │   ├── ocr_service.py  # Procesamiento OCR
│   │   ├── minio_service.py # Gestión de archivos
│   │   └── database_service.py # Base de datos
│   ├── dto/                # Modelos de datos
│   ├── entities/           # Entidades de BD
│   └── utils/              # Utilidades
├── docker-compose.yml      # Orquestación
├── Dockerfile             # Imagen OCR
└── requirements.txt       # Dependencias Python
```

## 🛠️ **Configuración**

### Variables de Entorno (docker-compose.yml)
```yaml
# Base de datos
DATABASE_URL: postgresql://postgres:password@postgres:5432/sacra360

# MinIO
MINIO_ENDPOINT: minio:9000
MINIO_ACCESS_KEY: admin
MINIO_SECRET_KEY: password123
MINIO_BUCKET: sacra360-documents

# OCR
TESSERACT_PATH: /usr/bin/tesseract
LOG_LEVEL: INFO
```

## 📊 **Monitoreo**

```bash
# Logs del servicio
docker-compose logs -f ocr-service

# Estado de contenedores
docker-compose ps

# Recursos utilizados
docker stats
```

## 🔧 **Desarrollo**

### Estructura del Servicio
- **OCR Engine**: Tesseract con optimizaciones
- **Procesamiento**: OpenCV para preprocesamiento
- **Storage**: MinIO para archivos, PostgreSQL para metadata
- **API**: FastAPI con validación automática

### Flujo de Procesamiento
1. Recepción de archivo vía API
2. Subida automática a MinIO
3. Procesamiento OCR con Tesseract
4. Extracción estructurada de datos
5. Almacenamiento en PostgreSQL
6. Respuesta con resultados y métricas

## 🐳 **Docker**

### Servicios
- **ocr-service**: Aplicación FastAPI
- **postgres**: Base de datos PostgreSQL 15
- **minio**: Object storage con consola web

### Volúmenes Persistentes
- `postgres_data`: Datos de PostgreSQL
- `minio_data`: Archivos de MinIO

### Red
- `sacra360_network`: Red interna para comunicación

## 📈 **Rendimiento**

- **Tiempo típico**: 10-15 segundos por documento
- **Formatos soportados**: JPG, PNG, PDF
- **Resolución óptima**: 300-600 DPI
- **Tamaño máximo**: 50MB por archivo

## 🔐 **Seguridad**

- Variables de entorno para credenciales
- Red interna aislada
- MinIO con autenticación
- PostgreSQL con usuario dedicado

## 📞 **Soporte**

Para issues y desarrollo, ver documentación completa en `/docs` del proyecto principal.
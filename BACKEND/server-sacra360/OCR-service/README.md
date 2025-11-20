# OCR Service - Sacra360

Microservicio especializado en reconocimiento óptico de caracteres (OCR) para documentos sacramentales.

## 🎯 Descripción

Este microservicio procesa imágenes de registros sacramentales (confirmaciones, bautizos, matrimonios) y extrae información estructurada usando algoritmos OCR optimizados. Integra el algoritmo desarrollado anteriormente en Google Colab con las capas de microservicio.

## ✨ Características Principales

- **OCR Optimizado**: Algoritmo específico para registros sacramentales en formato tabular
- **Múltiples Formatos**: Soporte para JPG, PNG y PDF
- **Extracción Estructurada**: Identifica campos específicos (nombres, fechas, lugares)
- **Alta Precisión**: Correcciones post-OCR basadas en patrones observados
- **Almacenamiento BD**: Guarda resultados en PostgreSQL
- **API REST**: Endpoints FastAPI para integración completa

## 🏗️ Arquitectura

```
OCR-service/
├── app/
│   ├── main.py                 # FastAPI app principal
│   ├── controllers/
│   │   └── ocr_controller.py   # Endpoints REST
│   ├── services/
│   │   ├── ocr_service.py      # Lógica OCR principal
│   │   └── database_service.py # Operaciones BD
│   ├── dto/
│   │   └── ocr_dto.py         # DTOs Pydantic
│   ├── entities/
│   │   └── ocr_entity.py      # Modelos SQLAlchemy
│   ├── routers/
│   │   └── ocr_router.py      # Configuración routing
│   └── utils/
│       └── config.py          # Configuración
├── requirements.txt
├── run_service.py            # Script ejecución
└── test_service.py          # Tests básicos
```

## 📋 Requisitos Previos

### Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa

# Windows (con Chocolatey)
choco install tesseract

# macOS (con Homebrew)  
brew install tesseract
```

### Python
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Base de Datos
- PostgreSQL con tablas: `documento_digitalizado`, `ocr_resultado`

## 🚀 Ejecutar el Servicio

### Método 1: Script directo
```bash
cd OCR-service
python run_service.py
```

### Método 2: Uvicorn directo
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Método 3: Docker (futuro)
```bash
docker-compose up ocr-service
```

## 🔗 Endpoints Principales

### Procesar Imagen OCR
```http
POST /api/v1/ocr/procesar
Content-Type: multipart/form-data

archivo: [imagen.jpg]
libros_id: 1
tipo_sacramento: 2
guardar_en_bd: true
```

### Obtener Resultados
```http
GET /api/v1/ocr/documento/{documento_id}
```

### Health Check
```http
GET /api/v1/health
```

## 📊 Ejemplo de Uso

```python
import requests

# Procesar imagen
with open('registro_confirmacion.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8003/api/v1/ocr/procesar',
        files={'archivo': f},
        data={
            'libros_id': 1,
            'tipo_sacramento': 2,
            'guardar_en_bd': True
        }
    )

resultado = response.json()
print(f"Tuplas extraídas: {resultado['total_tuplas']}")
print(f"Calidad general: {resultado['calidad_general']:.2f}")
```

## 🧪 Testing

```bash
# Test básico del servicio
python test_service.py

# Verificar health
curl http://localhost:8003/api/v1/health

# Ver documentación
# Abrir: http://localhost:8003/docs
```

## ⚙️ Configuración

### Variables de Entorno
```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/sacra360

# Tesseract
TESSERACT_PATH=/usr/bin/tesseract  # Opcional

# Servicio
PORT=8003
HOST=0.0.0.0
LOG_LEVEL=info
```

### Configuración OCR
- **Idioma**: Español (spa)
- **Modelos**: Tesseract OEM 3
- **PSM**: Adaptativo según tipo de celda
- **Correcciones**: Post-procesamiento específico

## 🏗️ Integración Desarrollada

### Desde Google Colab Original
- ✅ Algoritmo de detección de líneas
- ✅ Segmentación de tuplas individuales  
- ✅ Extracción por celdas
- ✅ Correcciones post-OCR específicas
- ✅ Métricas de calidad

### A Microservicio
- ✅ Arquitectura FastAPI
- ✅ DTOs Pydantic
- ✅ Persistencia PostgreSQL
- ✅ Endpoints REST
- ✅ Logging estructurado
- ✅ Manejo de errores

## 🔍 Algoritmo OCR

### Pipeline de Procesamiento
1. **Preprocesado**: Binarización adaptativa
2. **Detección de Grid**: Líneas horizontales/verticales
3. **Segmentación**: Identificación de tuplas válidas
4. **Extracción**: OCR por celda individual
5. **Corrección**: Post-procesamiento específico
6. **Validación**: Métricas de calidad

### Correcciones Específicas
```python
# Lugares comunes
"SAN PEDRORO" → "SAN PEDRO"
"NUESTRA SRA O" → "NUESTRA SEÑORA"

# Nombres
"JMOSELIN" → "JHOSELIN"  
"MURANDA" → "MIRANDA"

# Años
"200" → "2004"
"208" → "2008"
```

## 📈 Métricas de Calidad

- **Calidad General**: % celdas con contenido válido
- **Tuplas Alta Calidad**: Tuplas con >70% campos completos
- **Tiempo Procesamiento**: Duración total del proceso
- **Confianza por Campo**: Score individual OCR

## ⚠️ Consideraciones

### Limitaciones Actuales
- Optimizado para registros de confirmación
- Requiere imágenes de buena calidad
- Asume estructura tabular específica

### Mejoras Futuras  
- Soporte para más tipos de sacramento
- Entrenamiento con modelos custom
- Validación inteligente de campos
- Interfaz web de corrección

## 🤝 Contribución

1. Fork del repositorio
2. Crear branch para feature
3. Implementar cambios
4. Agregar tests
5. Submit pull request

## 📞 Soporte

Para problemas con el OCR Service:
- Verificar logs en `/api/v1/health`
- Revisar configuración Tesseract
- Validar formato de imagen
- Consultar documentación en `/docs`
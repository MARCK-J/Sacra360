# 🐳 Docker Setup - OCR Service Sacra360

## Quick Start con Docker

### 1. Construir y ejecutar con Docker Compose
```bash
# Desde el directorio OCR-service
docker-compose up --build

# En background
docker-compose up -d --build
```

### 2. Solo el servicio OCR
```bash
# Construir imagen
docker build -t sacra360-ocr .

# Ejecutar contenedor
docker run -p 8003:8003 sacra360-ocr
```

## Verificar que funciona

### Endpoints disponibles
- **Servicio**: http://localhost:8003
- **Documentación**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/api/v1/health

### Pruebas rápidas
```bash
# Test básico
curl http://localhost:8003/

# Health check
curl http://localhost:8003/api/v1/health

# Test OCR
python test_ocr_completo.py
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://postgres:password@postgres:5432/sacra360` |
| `TESSERACT_PATH` | Ruta de Tesseract | `/usr/bin/tesseract` |
| `SERVICE_PORT` | Puerto del servicio | `8003` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

## Comandos útiles

```bash
# Ver logs
docker-compose logs -f ocr-service

# Parar servicios
docker-compose down

# Limpiar volúmenes
docker-compose down -v

# Reconstruir
docker-compose build --no-cache

# Acceso al contenedor
docker exec -it sacra360_ocr_service bash

# Ver base de datos
docker exec -it sacra360_postgres psql -U postgres -d sacra360
```

## Estructura de archivos Docker

```
OCR-service/
├── Dockerfile              # Imagen del servicio
├── docker-compose.yml      # Orquestación completa
├── init.sql               # Script BD inicial
├── .dockerignore          # Archivos ignorados
└── requirements.txt       # Dependencias Python
```

## Troubleshooting

### Problema: Puerto ocupado
```bash
# Verificar que nada use el puerto 8003
netstat -tulpn | grep :8003

# O cambiar puerto en docker-compose.yml
ports:
  - "8004:8003"  # Host:Container
```

### Problema: Base de datos
```bash
# Resetear BD
docker-compose down -v
docker-compose up --build
```

### Problema: Dependencias
```bash
# Reconstruir imagen
docker-compose build --no-cache ocr-service
```

## Producción

### Configuración recomendada
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  ocr-service:
    image: sacra360-ocr:latest
    ports:
      - "8003:8003"
    environment:
      DATABASE_URL: postgresql://user:pass@external-db:5432/sacra360
      LOG_LEVEL: WARNING
    restart: always
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Usar imagen externa
```bash
# Construir para producción
docker build -t sacra360-ocr:v1.0 .

# Tagear para registry
docker tag sacra360-ocr:v1.0 registry.com/sacra360-ocr:v1.0

# Subir
docker push registry.com/sacra360-ocr:v1.0
```
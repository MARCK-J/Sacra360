# 🐳 Arquitectura de Contenedores - Sacra360

## 📋 Contenido Técnico Detallado

Este documento complementa el diagrama `esquema-despliegue.puml` con información técnica detallada de cada contenedor.

---

## 🗄️ Bases de Datos

### 1. PostgreSQL (`sacra360-postgres`)

**Imagen:** `postgres:15`  
**Puerto:** `5432`  
**Red:** `sacra360_network`  
**Volumen:** `postgres_data:/var/lib/postgresql/data`

**Variables de Entorno:**
```yaml
POSTGRES_DB: sacra360
POSTGRES_USER: postgres
POSTGRES_PASSWORD: lolsito101
```

**Inicialización:**
- Script: `/docker-entrypoint-initdb.d/Database.sql`
- Tablas: 14 (usuarios, roles, sacramentos, personas, documentos, etc.)
- Índices: 25+ para optimización de consultas

**Recursos Recomendados:**
- CPU: 2 cores
- RAM: 2GB
- Storage: 10GB (inicial), 50GB (producción)

**Health Check:**
```bash
docker exec sacra360-postgres pg_isready -U postgres
```

**Backup:**
```bash
docker exec sacra360-postgres pg_dump -U postgres sacra360 > backup.sql
```

---

### 2. Redis (`sacra360_redis`)

**Imagen:** `redis:7-alpine`  
**Puerto:** `6379`  
**Red:** `sacra360_network`  
**Volumen:** `redis_data:/data`

**Configuración:**
- Modo: Cache + Sessions
- Persistencia: RDB snapshots cada 5 minutos
- TTL Cache: 300 segundos (reportes)
- Max Memory: 512MB
- Eviction Policy: `allkeys-lru`

**Uso:**
- Cache de consultas pesadas
- Sesiones de usuario
- Rate limiting
- Cache de reportes

**Health Check:**
```bash
docker exec sacra360_redis redis-cli ping
```

**Comandos Útiles:**
```bash
# Ver todas las claves
docker exec sacra360_redis redis-cli KEYS "*"

# Ver cache de reportes
docker exec sacra360_redis redis-cli GET "cache:reportes:usuarios:30d"

# Limpiar cache
docker exec sacra360_redis redis-cli FLUSHDB
```

---

### 3. MinIO (`sacra360_minio`)

**Imagen:** `minio/minio:latest`  
**Puertos:** 
- `9000`: API S3-compatible
- `9001`: Web Console

**Red:** `sacra360_network`  
**Volumen:** `minio_data:/data`

**Variables de Entorno:**
```yaml
MINIO_ROOT_USER: minioadmin
MINIO_ROOT_PASSWORD: minioadmin123
```

**Comando de Inicio:**
```bash
server /data --console-address ":9001"
```

**Buckets:**
- `sacra360` → Almacena documentos digitalizados
- Estructura: `sacra360/documentos/{año}/{mes}/{id}.jpg`

**Acceso a Consola:**
```
http://localhost:9001
Usuario: minioadmin
Password: minioadmin123
```

**Health Check:**
```bash
curl http://localhost:9000/minio/health/live
```

**Características:**
- Almacenamiento de objetos S3-compatible
- Versionado de archivos
- Políticas de acceso IAM
- Encriptación en reposo

---

## 🚀 Microservicios

### 4. API Gateway (`sacra360_gateway`)

**Imagen:** `backend-gateway` (custom)  
**Puerto:** `8000`  
**Contexto Build:** `./BACKEND/HTTP`  
**Dockerfile:** Sí

**Responsabilidades:**
- Enrutamiento centralizado
- Load balancing entre réplicas
- Rate limiting global (100 req/min)
- CORS configuration
- SSL/TLS termination
- Request logging

**Rutas:**
```
/api/v1/auth/*       → auth-service:8004
/api/v1/usuarios/*   → auth-service:8004
/api/v1/sacramentos/* → documents-service:8002
/api/v1/personas/*   → documents-service:8002
/api/v1/ocr/*        → ocr-service:8003
/api/v1/files/*      → files-service:8007
/api/v1/reports/*    → reports-service:8008
```

**Dependencias:**
- Todos los microservicios

**Health Check:**
```bash
curl http://localhost:8000/health
```

---

### 5. AuthProfiles Service (`sacra360_authprofiles_service`)

**Imagen:** `backend-authprofiles-service` (custom)  
**Puerto:** `8004`  
**Contexto Build:** `./BACKEND/server-sacra360/AuthProfiles-service`  
**Dockerfile:** Sí

**Framework:** FastAPI 0.115  
**Endpoints:** 20 (6 auth + 8 usuarios + 4 auditoría + 5 reportes)

**Variables de Entorno:**
```yaml
POSTGRES_URL: postgresql://postgres:lolsito101@postgres:5432/sacra360
REDIS_URL: redis://redis:6379
JWT_SECRET_KEY: [cambiar en producción]
JWT_ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 30
```

**Responsabilidades:**
- Autenticación JWT
- Gestión de usuarios y roles
- RBAC (144 permisos)
- Auditoría de acciones
- Generación de reportes de usuarios
- Rate limiting por IP

**Endpoints Principales:**
```
POST   /api/v1/auth/login          - Login
POST   /api/v1/auth/register       - Registro
GET    /api/v1/auth/me             - Usuario actual
POST   /api/v1/auth/logout         - Logout
POST   /api/v1/auth/refresh        - Refresh token
GET    /api/v1/usuarios            - Listar usuarios
POST   /api/v1/usuarios            - Crear usuario
PUT    /api/v1/usuarios/{id}       - Actualizar usuario
DELETE /api/v1/usuarios/{id}       - Eliminar usuario
GET    /api/v1/auditoria           - Ver auditoría
GET    /api/v1/reportes/usuarios   - Reporte usuarios
```

**Dependencias:**
- PostgreSQL (usuarios, roles, auditoría)
- Redis (cache, sessions)

**Health Check:**
```bash
curl http://localhost:8004/health
```

**Swagger Docs:**
```
http://localhost:8004/docs
```

---

### 6. Documents Service (`sacra360_documents_service`)

**Imagen:** `backend-documents-service` (custom)  
**Puerto:** `8002`  
**Contexto Build:** `./BACKEND/server-sacra360/Documents-service`

**Responsabilidades:**
- CRUD de sacramentos (bautizo, confirmación, matrimonio)
- CRUD de personas
- Búsquedas avanzadas
- Validaciones de datos
- Gestión de libros parroquiales
- Relaciones entre sacramentos

**Endpoints Principales:**
```
GET    /api/v1/sacramentos         - Listar sacramentos
POST   /api/v1/sacramentos         - Crear sacramento
GET    /api/v1/sacramentos/{id}    - Ver sacramento
PUT    /api/v1/sacramentos/{id}    - Actualizar sacramento
DELETE /api/v1/sacramentos/{id}    - Eliminar sacramento
GET    /api/v1/personas            - Listar personas
POST   /api/v1/personas            - Crear persona
GET    /api/v1/search              - Búsqueda avanzada
```

**Dependencias:**
- PostgreSQL (sacramentos, personas, libros)
- Redis (cache de búsquedas)
- AuthProfiles (validación de permisos)

**Health Check:**
```bash
curl http://localhost:8002/health
```

---

### 7. OCR Service (`sacra360_ocr_service`)

**Imagen:** `backend-ocr-service` (custom)  
**Puerto:** `8003`  
**Contexto Build:** `./BACKEND/server-sacra360/OCR-service`

**Motor:** Tesseract OCR 5.x  
**Idioma:** Español (spa)  
**Configuración:** `/app/tesseract_configs`

**Responsabilidades:**
- Procesamiento OCR de documentos impresos
- Extracción de campos estructurados
- Preprocesamiento de imágenes (binarización, deskew)
- Confianza de extracción (threshold 70%)
- Validación de resultados

**Endpoints Principales:**
```
POST   /api/v1/ocr/process         - Procesar documento
GET    /api/v1/ocr/result/{id}     - Ver resultado
POST   /api/v1/ocr/validate        - Validar OCR
GET    /api/v1/ocr/confidence/{id} - Ver confianza
```

**Proceso:**
1. Recibe ID de documento desde Files Service
2. Descarga imagen desde MinIO
3. Preprocesa imagen (filtros, rotación)
4. Ejecuta Tesseract OCR
5. Extrae campos estructurados
6. Calcula confianza por campo
7. Almacena resultado en PostgreSQL

**Dependencias:**
- PostgreSQL (resultados OCR)
- Redis (cache)
- Files Service (obtener imágenes)
- AuthProfiles (validación)

**Health Check:**
```bash
curl http://localhost:8003/health
```

---

### 8. HTR Service (`sacra360_htr_service`)

**Imagen:** `backend-htr-service` (custom)  
**Puerto:** `8005`  
**Contexto Build:** `./BACKEND/server-sacra360/HTR-service`

**Modelo:** TensorFlow Custom CNN-RNN  
**Especialización:** Manuscritos siglos XIX-XX  
**Modelos:** `/app/models`

**Responsabilidades:**
- Reconocimiento de texto manuscrito
- Procesamiento de documentos históricos
- Segmentación de líneas
- Transcripción automática

**Endpoints Principales:**
```
POST   /api/v1/htr/process         - Procesar manuscrito
GET    /api/v1/htr/result/{id}     - Ver resultado
POST   /api/v1/htr/retrain         - Re-entrenar modelo
```

**Proceso:**
1. Recibe documento manuscrito
2. Segmenta líneas de texto
3. Normaliza y preprocesa
4. Ejecuta modelo TensorFlow
5. Post-procesamiento lingüístico
6. Retorna transcripción

**Dependencias:**
- PostgreSQL (resultados HTR)
- Redis (cache)
- Files Service (obtener imágenes)
- AuthProfiles (validación)

**Recursos Recomendados:**
- CPU: 4 cores (o GPU para inferencia)
- RAM: 4GB
- GPU: Opcional (NVIDIA CUDA)

**Health Check:**
```bash
curl http://localhost:8005/health
```

---

### 9. AI Processing Service (`sacra360_ai_service`)

**Imagen:** `backend-ai-service` (custom)  
**Puerto:** `8006`  
**Contexto Build:** `./BACKEND/server-sacra360/AI-Processing-service`

**Integración:** OpenAI GPT

**Responsabilidades:**
- Procesamiento de lenguaje natural
- Extracción de entidades nombradas (NER)
- Corrección ortográfica
- Enriquecimiento de datos
- Sugerencias inteligentes

**Variables de Entorno:**
```yaml
OPENAI_API_KEY: sk-your-api-key-here
OPENAI_MODEL: gpt-4
```

**Endpoints Principales:**
```
POST   /api/v1/ai/enhance          - Mejorar datos
POST   /api/v1/ai/extract          - Extraer entidades
POST   /api/v1/ai/correct          - Corregir texto
POST   /api/v1/ai/suggest          - Sugerencias
```

**Dependencias:**
- PostgreSQL (logs de procesamiento)
- Redis (cache de respuestas)
- Documents Service (obtener datos)
- AuthProfiles (validación)

**Health Check:**
```bash
curl http://localhost:8006/health
```

---

### 10. File Storage Service (`sacra360_files_service`)

**Imagen:** `backend-files-service` (custom)  
**Puerto:** `8007`  
**Contexto Build:** `./BACKEND/server-sacra360/File-Storage-service`

**Storage Backend:** MinIO S3

**Responsabilidades:**
- Upload de archivos
- Generación de URLs firmadas
- Gestión de metadata
- Validación de formatos
- Compresión de imágenes

**Formatos Permitidos:**
- Imágenes: JPG, PNG
- Documentos: PDF
- Tamaño máximo: 10MB

**Endpoints Principales:**
```
POST   /api/v1/files/upload        - Subir archivo
GET    /api/v1/files/{id}          - Descargar archivo
DELETE /api/v1/files/{id}          - Eliminar archivo
GET    /api/v1/files/{id}/url      - URL firmada
GET    /api/v1/files/{id}/metadata - Ver metadata
```

**Proceso de Upload:**
1. Validar formato y tamaño
2. Generar ID único
3. Optimizar imagen (resize, compresión)
4. Upload a MinIO
5. Guardar metadata en PostgreSQL
6. Retornar ID y URL

**Dependencias:**
- PostgreSQL (metadata de archivos)
- Redis (cache de URLs)
- MinIO (almacenamiento)
- AuthProfiles (validación)

**Health Check:**
```bash
curl http://localhost:8007/health
```

---

### 11. Reports Service (`sacra360_reports_service`)

**Imagen:** `backend-reports-service` (custom)  
**Puerto:** `8008`  
**Contexto Build:** `./BACKEND/server-sacra360/Reports-service`

**Responsabilidades:**
- Generación de reportes PDF
- Exportación a Excel
- Gráficos y estadísticas
- Reportes programados
- Cache de reportes frecuentes

**Endpoints Principales:**
```
GET    /api/v1/reports/usuarios    - Reporte usuarios
GET    /api/v1/reports/sacramentos - Reporte sacramentos
GET    /api/v1/reports/actividad   - Reporte actividad
GET    /api/v1/reports/estadisticas - Estadísticas
POST   /api/v1/reports/custom      - Reporte personalizado
```

**Períodos Disponibles:**
- Últimos 7 días
- Últimos 30 días
- Últimos 90 días
- Último año
- Rango personalizado

**Formatos de Salida:**
- PDF (reportlab)
- Excel (openpyxl)
- CSV
- JSON

**Cache:**
- Redis TTL: 5 minutos
- Key pattern: `cache:reportes:{tipo}:{periodo}`

**Dependencias:**
- PostgreSQL (queries agregadas)
- Redis (cache)
- Documents Service (datos de sacramentos)
- AuthProfiles (validación)

**Health Check:**
```bash
curl http://localhost:8008/health
```

---

## 🌐 Red Docker

**Nombre:** `sacra360_network`  
**Driver:** `bridge`  
**Subnet:** `172.18.0.0/16`

**Características:**
- Aislamiento de red
- DNS interno (resolución por nombre de servicio)
- Comunicación inter-contenedor
- Puertos expuestos solo los necesarios

**Configuración en docker-compose.yml:**
```yaml
networks:
  sacra360_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.18.0.0/16
```

---

## 💾 Volúmenes Docker

### postgres_data
- **Mount:** `/var/lib/postgresql/data`
- **Tamaño:** ~5GB (inicial), crece según datos
- **Backup:** Diario recomendado
- **Driver:** `local`

### redis_data
- **Mount:** `/data`
- **Tamaño:** ~500MB
- **Persistencia:** RDB snapshots
- **Driver:** `local`

### minio_data
- **Mount:** `/data`
- **Tamaño:** ~50GB (producción puede crecer mucho)
- **Contenido:** Documentos digitalizados
- **Driver:** `local`

**Listar volúmenes:**
```bash
docker volume ls | grep sacra360
```

**Inspeccionar volumen:**
```bash
docker volume inspect postgres_data
```

**Backup de volumen:**
```bash
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

---

## 📊 Recursos y Límites

### Recursos Recomendados por Contenedor

| Contenedor | CPU | RAM | Disco | Prioridad |
|------------|-----|-----|-------|-----------|
| PostgreSQL | 2 cores | 2GB | 10GB | Alta |
| Redis | 1 core | 512MB | 1GB | Media |
| MinIO | 1 core | 1GB | 50GB | Alta |
| AuthProfiles | 1 core | 512MB | - | Alta |
| Documents | 1 core | 512MB | - | Alta |
| OCR | 2 cores | 2GB | - | Media |
| HTR | 4 cores | 4GB | - | Baja |
| AI Processing | 2 cores | 1GB | - | Baja |
| Files | 1 core | 512MB | - | Media |
| Reports | 1 core | 512MB | - | Media |
| Gateway | 1 core | 256MB | - | Alta |

**Total Mínimo:** 8 cores, 16GB RAM, 70GB disco

---

## 🔒 Seguridad

### Contraseñas por Defecto (⚠️ Cambiar en Producción)

```yaml
PostgreSQL:
  Usuario: postgres
  Password: lolsito101

MinIO:
  Usuario: minioadmin
  Password: minioadmin123

JWT:
  Secret: [cambiar por string seguro de 32+ caracteres]
```

### Recomendaciones de Seguridad

1. **Cambiar todas las contraseñas por defecto**
2. **Generar JWT secret key aleatorio**
3. **Usar variables de entorno para secretos**
4. **No exponer puertos innecesarios al host**
5. **Configurar firewall del servidor**
6. **Implementar SSL/TLS en producción**
7. **Habilitar autenticación en Redis**
8. **Configurar políticas IAM en MinIO**
9. **Auditar logs regularmente**
10. **Mantener imágenes actualizadas**

---

## 📈 Escalamiento

### Horizontal (Múltiples Réplicas)

```bash
# Escalar servicio a 3 réplicas
docker-compose up -d --scale auth-service=3

# Escalar múltiples servicios
docker-compose up -d --scale auth-service=3 --scale documents-service=2
```

### Vertical (Más Recursos)

Editar `docker-compose.yml`:

```yaml
services:
  auth-service:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

---

**Última actualización:** 9 de diciembre de 2025  
**Versión:** 1.0.0

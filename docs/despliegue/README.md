# 🚀 Guía de Despliegue - Sistema Sacra360

## 📑 Índice
1. [Requisitos Previos](#requisitos-previos)
2. [Arquitectura de Despliegue](#arquitectura-de-despliegue)
3. [Despliegue con Docker Compose](#despliegue-con-docker-compose)
4. [Configuración de Servicios](#configuración-de-servicios)
5. [Comandos Útiles](#comandos-útiles)
6. [Verificación del Despliegue](#verificación-del-despliegue)
7. [Troubleshooting](#troubleshooting)
8. [Monitoreo](#monitoreo)
9. [Backup y Restore](#backup-y-restore)
10. [Escalamiento](#escalamiento)

---

## 🔧 Requisitos Previos

### Software Requerido

| Software | Versión Mínima | Comando de Verificación |
|----------|----------------|-------------------------|
| **Docker** | 24.0+ | `docker --version` |
| **Docker Compose** | 2.20+ | `docker-compose --version` |
| **Git** | 2.40+ | `git --version` |
| **Node.js** (dev) | 18.0+ | `node --version` |
| **Python** (dev) | 3.11+ | `python --version` |

### Recursos del Servidor

#### Mínimos (Desarrollo)
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Disco:** 50 GB disponibles
- **SO:** Windows 10/11, Linux (Ubuntu 20.04+), macOS 12+

#### Recomendados (Producción)
- **CPU:** 8 cores
- **RAM:** 16 GB
- **Disco:** 200 GB (SSD recomendado)
- **SO:** Ubuntu Server 22.04 LTS
- **Red:** 100 Mbps mínimo

---

## 🏗️ Arquitectura de Despliegue

Ver diagrama: `esquema-despliegue.puml`

### Componentes Desplegados

#### **Contenedores (10 total)**

**Bases de Datos (3):**
1. `sacra360-postgres` - PostgreSQL 15 (:5432)
2. `sacra360_redis` - Redis 7 Alpine (:6379)
3. `sacra360_minio` - MinIO S3-compatible (:9000, :9001)

**Microservicios (7):**
4. `sacra360_gateway` - API Gateway (:8000)
5. `sacra360_authprofiles_service` - Auth & Users (:8004)
6. `sacra360_documents_service` - Documents CRUD (:8002)
7. `sacra360_ocr_service` - OCR Processing (:8003)
8. `sacra360_htr_service` - HTR Recognition (:8005)
9. `sacra360_ai_service` - AI Processing (:8006)
10. `sacra360_files_service` - File Storage (:8007)
11. `sacra360_reports_service` - Reports (:8008)

#### **Volúmenes Docker (3)**
- `postgres_data` - Datos de PostgreSQL (~5 GB)
- `redis_data` - Snapshots de Redis (~500 MB)
- `minio_data` - Documentos digitalizados (~50 GB)

#### **Red Docker**
- `sacra360_network` - Red bridge (172.18.0.0/16)

---

## 🐳 Despliegue con Docker Compose

### Paso 1: Clonar el Repositorio

```bash
# Clonar proyecto
git clone https://github.com/MARCK-J/Sacra360.git
cd Sacra360

# Cambiar a rama de desarrollo (si aplica)
git checkout Diego
```

### Paso 2: Configurar Variables de Entorno

Crear archivo `.env` en la carpeta `BACKEND/`:

```bash
cd BACKEND
cp .env.example .env
nano .env  # o usar tu editor preferido
```

**Contenido del `.env`:**

```bash
# === PostgreSQL Configuration ===
POSTGRES_DB=sacra360
POSTGRES_USER=postgres
POSTGRES_PASSWORD=lolsito101
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# === Redis Configuration ===
REDIS_URL=redis://redis:6379

# === MinIO Configuration ===
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123

# === JWT Configuration ===
JWT_SECRET_KEY=tu_clave_secreta_super_segura_de_al_menos_32_caracteres_cambiar_en_produccion
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# === OpenAI (opcional) ===
OPENAI_API_KEY=sk-your-api-key-here

# === URLs de Microservicios ===
AUTH_SERVICE_URL=http://auth-service:8004
DOCUMENTS_SERVICE_URL=http://documents-service:8002
OCR_SERVICE_URL=http://ocr-service:8003
HTR_SERVICE_URL=http://htr-service:8005
AI_SERVICE_URL=http://ai-service:8006
FILES_SERVICE_URL=http://files-service:8007
REPORTS_SERVICE_URL=http://reports-service:8008
```

### Paso 3: Construir Imágenes Docker

```bash
# Desde la carpeta BACKEND/
docker-compose build

# O construir un servicio específico
docker-compose build auth-service
docker-compose build documents-service
```

**Tiempos estimados de construcción:**
- Primera vez: 10-15 minutos
- Reconstrucción: 2-5 minutos (con cache)

### Paso 4: Inicializar la Base de Datos

El script `Database.sql` se ejecuta automáticamente en el primer inicio de PostgreSQL.

```bash
# Verificar que el script esté presente
ls -l sql/Database.sql
```

### Paso 5: Levantar los Servicios

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Levantar servicios específicos
docker-compose up -d postgres redis minio
docker-compose up -d auth-service
```

**Orden de inicio recomendado:**
1. Bases de datos: `postgres`, `redis`, `minio`
2. Servicio de autenticación: `auth-service`
3. Servicios de negocio: `documents-service`, `files-service`
4. Servicios de procesamiento: `ocr-service`, `htr-service`, `ai-service`
5. Gateway: `api-gateway`

### Paso 6: Verificar el Estado

```bash
# Ver todos los contenedores
docker-compose ps

# Verificar salud de servicios
docker ps --filter "name=sacra360"

# Ver logs de un servicio específico
docker-compose logs auth-service
```

---

## ⚙️ Configuración de Servicios

### PostgreSQL

**Puerto:** 5432  
**Base de datos:** sacra360  
**Usuario:** postgres  
**Volumen:** postgres_data

```bash
# Conectar a PostgreSQL
docker exec -it sacra360-postgres psql -U postgres -d sacra360

# Verificar tablas
\dt

# Ver usuarios
SELECT * FROM usuarios;
```

**Backup automático:**
```bash
# Configurar cron job para backup diario
0 2 * * * docker exec sacra360-postgres pg_dump -U postgres sacra360 > /backups/sacra360_$(date +\%Y\%m\%d).sql
```

---

### Redis

**Puerto:** 6379  
**Modo:** Cache + Sessions  
**TTL:** 5 minutos (reportes)  
**Volumen:** redis_data

```bash
# Conectar a Redis
docker exec -it sacra360_redis redis-cli

# Ver claves
KEYS *

# Ver cache de reportes
GET cache:reportes:usuarios:30d

# Limpiar cache
FLUSHDB
```

---

### MinIO

**Puerto API:** 9000  
**Puerto Console:** 9001  
**Usuario:** minioadmin  
**Password:** minioadmin123  
**Volumen:** minio_data

**Acceder a la consola:**
```
http://localhost:9001
```

**Crear bucket:**
```bash
# Desde la consola web o usando mc (MinIO Client)
mc alias set local http://localhost:9000 minioadmin minioadmin123
mc mb local/sacra360
```

---

### AuthProfiles Service

**Puerto:** 8004  
**Health Check:** http://localhost:8004/health  
**Swagger Docs:** http://localhost:8004/docs

```bash
# Ver logs
docker logs -f sacra360_authprofiles_service

# Reiniciar servicio
docker restart sacra360_authprofiles_service

# Entrar al contenedor
docker exec -it sacra360_authprofiles_service bash
```

**Verificar endpoints:**
```bash
# Health check
curl http://localhost:8004/health

# Login (obtener token)
curl -X POST http://localhost:8004/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sacra360.com","password":"Admin123"}'
```

---

### Frontend (Desarrollo)

**Puerto:** 5173  
**Framework:** Vite + React

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar .env
cp .env.example .env
nano .env
```

**`.env` del frontend:**
```bash
VITE_AUTH_API_URL=http://localhost:8004
VITE_DOCUMENTS_API_URL=http://localhost:8002
VITE_FILES_API_URL=http://localhost:8007
```

```bash
# Ejecutar en modo desarrollo
npm run dev

# Construir para producción
npm run build

# Preview de producción
npm run preview
```

---

## 🛠️ Comandos Útiles

### Gestión de Contenedores

```bash
# Ver todos los contenedores
docker-compose ps

# Ver solo contenedores corriendo
docker ps --filter "name=sacra360"

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ CUIDADO: borra datos)
docker-compose down -v

# Reiniciar un servicio
docker-compose restart auth-service

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de últimos 100 líneas
docker-compose logs --tail=100 auth-service

# Ver uso de recursos
docker stats
```

### Actualización de Servicios

```bash
# Reconstruir imágenes
docker-compose build --no-cache

# Recrear contenedores sin perder datos
docker-compose up -d --force-recreate

# Actualizar solo un servicio
docker-compose up -d --build auth-service
```

### Limpieza

```bash
# Limpiar imágenes no usadas
docker image prune -a

# Limpiar contenedores detenidos
docker container prune

# Limpiar volúmenes no usados
docker volume prune

# Limpieza completa (⚠️ CUIDADO)
docker system prune -a --volumes
```

---

## ✅ Verificación del Despliegue

### Checklist de Verificación

```bash
# 1. Verificar que todos los contenedores están corriendo
docker-compose ps | grep "Up"

# 2. Health check de PostgreSQL
docker exec sacra360-postgres pg_isready -U postgres

# 3. Health check de Redis
docker exec sacra360_redis redis-cli ping

# 4. Health check de MinIO
curl http://localhost:9000/minio/health/live

# 5. Health check de AuthProfiles
curl http://localhost:8004/health

# 6. Test de login
curl -X POST http://localhost:8004/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sacra360.com","password":"Admin123"}'

# 7. Verificar red Docker
docker network inspect sacra360_network

# 8. Verificar volúmenes
docker volume ls | grep sacra360
```

### Script de Verificación Automática

```bash
#!/bin/bash
# verificar-despliegue.sh

echo "🔍 Verificando despliegue de Sacra360..."

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Función de verificación
check_service() {
    if docker ps | grep -q "$1"; then
        echo -e "${GREEN}✓${NC} $1 está corriendo"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NO está corriendo"
        return 1
    fi
}

# Verificar servicios
check_service "sacra360-postgres"
check_service "sacra360_redis"
check_service "sacra360_minio"
check_service "sacra360_authprofiles_service"
check_service "sacra360_documents_service"
check_service "sacra360_ocr_service"
check_service "sacra360_files_service"

# Health checks
echo ""
echo "🏥 Verificando health checks..."

if curl -s http://localhost:8004/health | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} AuthProfiles Service - OK"
else
    echo -e "${RED}✗${NC} AuthProfiles Service - FAIL"
fi

echo ""
echo "✅ Verificación completada"
```

---

## 🐛 Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker logs sacra360_authprofiles_service

# Verificar errores en todos los servicios
docker-compose logs | grep -i "error"

# Reiniciar servicio problemático
docker-compose restart auth-service
```

### Problema: Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
docker ps | grep postgres

# Ver logs de PostgreSQL
docker logs sacra360-postgres

# Verificar conexión
docker exec sacra360-postgres pg_isready -U postgres

# Recrear contenedor
docker-compose up -d --force-recreate postgres
```

### Problema: Puerto ya en uso

```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :8004  # Windows
lsof -i :8004                 # Linux/Mac

# Cambiar puerto en docker-compose.yml
ports:
  - "8005:8004"  # Host:Container
```

### Problema: Volúmenes corruptos

```bash
# Backup de datos
docker exec sacra360-postgres pg_dump -U postgres sacra360 > backup.sql

# Eliminar volúmenes
docker-compose down -v

# Recrear desde backup
docker-compose up -d postgres
docker exec -i sacra360-postgres psql -U postgres sacra360 < backup.sql
```

### Problema: Servicio muy lento

```bash
# Verificar uso de recursos
docker stats

# Aumentar recursos en Docker Desktop
# Settings > Resources > Increase RAM/CPU

# Optimizar base de datos
docker exec sacra360-postgres psql -U postgres -d sacra360 -c "VACUUM ANALYZE;"
```

---

## 📊 Monitoreo

### Logs Centralizados

```bash
# Seguir logs de todos los servicios
docker-compose logs -f

# Filtrar por nivel de error
docker-compose logs | grep -i "error"

# Exportar logs
docker-compose logs > logs_sacra360.txt
```

### Métricas de Recursos

```bash
# Ver uso en tiempo real
docker stats

# Ver uso específico
docker stats sacra360_authprofiles_service
```

### Health Checks Automáticos

Agregar a `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8004/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 💾 Backup y Restore

### Backup de PostgreSQL

```bash
# Backup completo
docker exec sacra360-postgres pg_dump -U postgres sacra360 > backup_$(date +%Y%m%d).sql

# Backup comprimido
docker exec sacra360-postgres pg_dump -U postgres sacra360 | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup con formato custom (más rápido para restore)
docker exec sacra360-postgres pg_dump -U postgres -F c sacra360 > backup.dump
```

### Restore de PostgreSQL

```bash
# Desde SQL file
docker exec -i sacra360-postgres psql -U postgres sacra360 < backup_20251209.sql

# Desde dump comprimido
gunzip -c backup_20251209.sql.gz | docker exec -i sacra360-postgres psql -U postgres sacra360

# Desde formato custom
docker exec -i sacra360-postgres pg_restore -U postgres -d sacra360 backup.dump
```

### Backup de Volúmenes Docker

```bash
# Backup de postgres_data
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_backup.tar.gz /data

# Backup de minio_data
docker run --rm -v minio_data:/data -v $(pwd):/backup alpine tar czf /backup/minio_data_backup.tar.gz /data
```

### Restore de Volúmenes

```bash
# Restore postgres_data
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data_backup.tar.gz -C /

# Restore minio_data
docker run --rm -v minio_data:/data -v $(pwd):/backup alpine tar xzf /backup/minio_data_backup.tar.gz -C /
```

---

## 📈 Escalamiento

### Escalamiento Horizontal

```bash
# Escalar un servicio a 3 réplicas
docker-compose up -d --scale auth-service=3

# Ver réplicas corriendo
docker-compose ps
```

### Escalamiento Vertical

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

### Load Balancing

Usar nginx como load balancer:

```nginx
upstream authprofiles {
    server localhost:8004;
    server localhost:8005;
    server localhost:8006;
}

server {
    location /api/v1/auth/ {
        proxy_pass http://authprofiles;
    }
}
```

---

## 📝 Checklist de Producción

- [ ] Cambiar todas las contraseñas por defecto
- [ ] Generar JWT secret key seguro (32+ caracteres)
- [ ] Configurar HTTPS/TLS con certificados
- [ ] Configurar firewall (solo puertos necesarios)
- [ ] Implementar backup automático diario
- [ ] Configurar monitoreo (Prometheus + Grafana)
- [ ] Configurar logs centralizados (ELK Stack)
- [ ] Implementar rate limiting en nginx
- [ ] Configurar alertas (email/slack)
- [ ] Documentar procedimientos de emergencia
- [ ] Realizar pruebas de carga
- [ ] Configurar auto-scaling (Kubernetes)

---

**Última actualización:** 9 de diciembre de 2025  
**Versión:** 1.0.0  
**Soporte:** Equipo Sacra360

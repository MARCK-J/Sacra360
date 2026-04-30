# Sacra360 - Sistema de Registro de Sacramentos

Sistema integral para digitalización y validación de registros sacramentales con soporte para OCR, HTR (reconocimiento de escritura), generación de certificados y auditoría.
*Estado del Proyecto:* Desarrollo finalizado. Listo para despliegue.
*Nota de Infraestructura:* El sistema está construido bajo una arquitectura de microservicios con contenedores. Está a la espera de un equipo físico (PC) o un servidor contratado (VPS).

## 🚀 Despliegue Rápido

**Leer primero:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

Este documento contiene:
- Contexto de cambios de seguridad (credenciales → variables de entorno)
- Configuración de Vercel para frontend
- Validación de Supabase
- Docker Compose para desarrollo local
- Checklist pre-producción

## 📦 Arquitectura

```
Frontend (Vercel)  ←→  Backend Microservicios (Render/Railway)
React + Vite           FastAPI + Docker Compose
                       ↓
                    Supabase (PostgreSQL)
                    MinIO / S3 (Storage)
```

## 🔐 Seguridad

✅ Credenciales removidas de código  
✅ Variables de entorno para todos los secretos  
✅ Frontend dinámico (VITE_* vars desde Vercel)  
✅ JWT auth en endpoints protegidos  

## 📁 Estructura del Proyecto

- **BACKEND/** — Microservicios FastAPI
- **frontend/** — React + Vite (desplegable en Vercel)
- **docs/** — Diagramas y documentación
- **sql/** — Schemas y migrations
- **tests/** — Test suite

## 🛠️ Desarrollo Local

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (requiere Docker)
cd BACKEND
docker-compose up -d
```

## 📖 Documentación

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — Guía completa de despliegue
- [BACKEND/README.md](BACKEND/README.md) — Servicios backend
- [frontend/README.md](frontend/README.md) — Frontend
- [docs/](docs/) — Diagramas técnicos
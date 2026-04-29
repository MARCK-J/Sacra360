# Sacra360 - Guía de Despliegue en Vercel + Supabase

**Sesión:** 22 de abril de 2026  
**Rama de trabajo:** PRUEBA2  
**Commit actual:** 66dd141 (chore: add root vercel config for frontend subdir build)

---

## 📋 Contexto General

Sacra360 es un sistema de registro de sacramentos con arquitectura microservicios:
- **Frontend:** React + Vite, desplegable en Vercel
- **Backend:** FastAPI microservicios en Docker Compose, deployable en Render/Railway
- **Base de datos:** Supabase PostgreSQL (producción)
- **Almacenamiento:** MinIO (desarrollo) / S3 (producción)

---

## 🔐 Cambios de Seguridad Implementados

### Problema Original
El repositorio tenía **credenciales hardcodeadas** en:
- `docker-compose.yml`: URLs y contraseñas de Supabase
- `fix_auth_seed_manual.py`, `temp_supabase_check.py`: Conexiones DB directas
- Frontend: URLs localhost hardcodeadas

### Soluciones Implementadas

#### 1. **Backend - Variables de Entorno**
- Creado: `BACKEND/.env.example` con templates de producción
- Modificado: `BACKEND/docker-compose.yml` para usar `${VAR}` en lugar de valores literales
- Scripts actualizados para leer `SUPABASE_DB_URL` desde env

**Variables críticas:**
```
SUPABASE_DB_URL=postgresql://user:password@host:port/dbname
SUPABASE_DB_USER=
SUPABASE_DB_PASSWORD=
SUPABASE_DB_HOST=
SUPABASE_DB_PORT=6543
SUPABASE_DB_NAME=postgres
JWT_SECRET_KEY=
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
```

#### 2. **Frontend - Centralización de URLs**
Creado: `frontend/src/config/api.js`
```javascript
export const API_BASE_URL = trimTrailingSlash(
  import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || defaultApiBase
)

export const AUTH_API_URL = trimTrailingSlash(
  import.meta.env.VITE_AUTH_API_URL || defaultAuthBase
)

export const API_V1_URL = `${API_BASE_URL}/api/v1`
```

**Cambios en componentes:** 18 archivos (páginas + contextos) refactorizados para usar URLs desde config en lugar de hardcodeadas.

Archivos modificados:
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/context/OcrProgressContext.jsx`
- `frontend/src/pages/{Digitalizacion,RevisionOCR,Certificados,Libros,Reportes,Usuarios,Auditoria,Estadisticas,Personas,Perfil,Registros,Sacramento,Sacramentos}.jsx`
- `frontend/src/components/ValidacionOCRModal.jsx`

#### 3. **Frontend - Variables de Entorno**
Creado: `frontend/.env.example`
```
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_AUTH_API_URL=https://your-auth-service.onrender.com
VITE_API_URL=https://your-backend.onrender.com (legacy)
```

Modificado: `frontend/.gitignore`
```
.env
.env.*
!.env.example
```

Local: `frontend/.env`
```
VITE_API_BASE_URL=http://localhost:8002
VITE_AUTH_API_URL=http://localhost:8001
VITE_API_URL=http://localhost:8002
```

---

## 🗄️ Validación de Supabase

Se ejecutaron 3 pruebas de conectividad directa a Supabase:

### 1. **temp_supabase_check.py**
- ✅ Verificó credenciales de usuarios seed (admin@sacra360.com, digitalizador@sacra360.com)
- Resultado: Usuarios ya existentes, no insertados

### 2. **temp_setval_libros.py**
- ✅ Actualizó secuencia de `libros.id_libro` a 8
- Resultado: `setval_result=8`

### 3. **RW Probe (transactional)**
- ✅ Insertó registro con id_sacramento=9
- ✅ Verificó rollback automático
- Resultado: `exists_after_rollback=0` (rollback exitoso)

**Conclusión:** Supabase conecta correctamente y está listo para producción.

---

## 🚀 Configuración de Vercel

### Estado Actual
- **Problema:** Vercel estaba clonando repo incorrecto (DiegoMoron0102/sacra360) en rama main
- **Solución:** Crear proyecto nuevo apuntando a MARCK-J/Sacra360 en rama PRUEBA2

### Archivos de Configuración
Creado: `vercel.json` (raíz del repositorio)
```json
{
  "framework": null,
  "installCommand": "npm ci --prefix frontend",
  "buildCommand": "npm run build --prefix frontend",
  "outputDirectory": "frontend/dist",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

Creado: `frontend/vercel.json` (alternativa si Root Directory = frontend)
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Build Validation
```bash
npm run build --prefix frontend
```
Resultado: ✅ Construcción exitosa en 6-7 segundos, dist genera:
- index.html (0.96 KB)
- CSS bundle (48 KB)
- JS bundles (158 KB a 462 KB)

---

## 📝 Pasos para Desplegar en Vercel

### Prerequisitos
1. Acceso a cuenta Vercel (debe ser tuya, no compartida)
2. Acceso write a repositorio MARCK-J/Sacra360 (o que MARCK-J autorice)
3. Variables de producción listas

### Paso 1: Conectar Repositorio en Vercel
1. Ir a https://vercel.com/new
2. "Import Git Repository"
3. Seleccionar **MARCK-J/Sacra360** (no otro fork)
4. Authorizar acceso GitHub

### Paso 2: Configurar Build
1. **Framework:** Vite
2. **Root Directory:** `.` (raíz) — vercel.json maneja el --prefix frontend
   - *Alternativa:* Si prefieres Root = `frontend`, elimina la regla de installCommand
3. **Build Command:** `npm run build --prefix frontend`
4. **Output Directory:** `frontend/dist`

### Paso 3: Variables de Entorno
En **Settings > Environment Variables**, agregar para **Production**:

| Variable | Valor Ejemplo |
|----------|-----------|
| `VITE_API_BASE_URL` | `https://api.tubackend.onrender.com` |
| `VITE_AUTH_API_URL` | `https://auth.tubackend.onrender.com` |
| `VITE_API_URL` | `https://api.tubackend.onrender.com` (legacy) |

⚠️ **Importante:** Estos valores son **públicos** (prefijo VITE_ en Vite), visible en el navegador. No poner tokens aquí; eso va en headers de requests.

### Paso 4: Deploy
1. Hacer click **Deploy**
2. Esperar 2-3 minutos
3. Obtener URL: `https://sacra360-xxxxx.vercel.app`

---

## 🧪 Validación Post-Deploy

### 1. Verificar Frontend
```bash
# Desde la terminal o navegador:
curl https://tu-vercel-domain.vercel.app/
# Debe retornar HTML (no 404)
```

### 2. Probar Login
1. Ir a https://tu-vercel-domain.vercel.app/
2. Usar credenciales:
   - Email: `admin@sacra360.com`
   - Password: `admin123` (o la que hayas configurado en DB)
3. Verificar que auth service responde desde `VITE_AUTH_API_URL`

### 3. Probar Endpoints Clave
```javascript
// En DevTools Console:
fetch('${VITE_API_BASE_URL}/api/v1/libros')
  .then(r => r.json())
  .then(d => console.log(d))
```

---

## 🐳 Docker Compose (Desarrollo Local)

### Prerequisitos
```bash
# En BACKEND/:
cd BACKEND
cp .env.example .env
# Editar .env con credenciales locales o Supabase
```

### Ejecutar Servicios
```bash
cd BACKEND
docker-compose up -d
```

**Servicios que arrancan:**
- gateway: 8000 (proxy principal)
- auth-service: 8001
- documents-service: 8002
- ocr-service: 8003
- htr-service: 8004
- ai-service: 8005
- reports-service: 8006
- files-service: 8007
- minio: 9000 (storage)
- redis: 6379 (cache)

### Notas
- **OCR/HTR son pesados:** Builds pueden tardar 10+ minutos
- **GPU:** HTR service intenta detectar NVIDIA; sin GPU usa CPU (lento)
- **Supabase:** Remoto, requiere conectividad a internet y credenciales válidas

---

## 🔄 CI/CD Considerations

### GitHub Actions Opcional
Si quieres auto-deploy en cada push a PRUEBA2:
1. Conectar Vercel con GitHub (ya hecho en este paso)
2. Activar "Automatic deployments" en Vercel Settings

### Pre-deploy Checklist
- [ ] Variables de entorno cargadas en Vercel
- [ ] Rama correcta (PRUEBA2 o main según necesidad)
- [ ] Build compila localmente sin errores
- [ ] npm audit muestra <= 5 vulnerabilidades leves
- [ ] Supabase credenciales correctas en .env

---

## 📊 Estructura del Repositorio

```
Sacra360/
├── BACKEND/                      # Microservicios FastAPI
│   ├── docker-compose.yml        # Orquestación servicios
│   ├── .env.example              # Template variables
│   ├── app/
│   │   ├── core/                 # DTOs, utils, config
│   │   ├── services/             # Lógica de negocios
│   │   ├── ocr/                  # OCR processing
│   │   ├── htr/                  # Handwriting recognition
│   │   └── ai_completion/        # AI inference
│   ├── server-sacra360/          # Microservicios individuales
│   │   ├── AuthProfiles-service/
│   │   ├── Documents-service/
│   │   ├── OCR-service/
│   │   ├── HTR-service/
│   │   ├── Reports-service/
│   │   └── ...
│   ├── sql/                      # Schemas y migrations
│   ├── tests/                    # Test suite
│   └── requirements.txt          # Dependencies
│
├── frontend/                     # React + Vite
│   ├── src/
│   │   ├── config/api.js         # Centralización URLs
│   │   ├── context/              # Auth, OcrProgress
│   │   ├── pages/                # Rutas principales
│   │   ├── components/           # Componentes reutilizables
│   │   └── App.jsx               # Router principal
│   ├── package.json              # Dependencies
│   ├── vercel.json               # Config Vercel alternativa
│   ├── .env.example              # Template vars
│   ├── .env                      # Local dev vars
│   ├── vite.config.js            # Bundler config
│   └── tailwind.config.js        # Styling
│
├── docs/                         # Documentación
├── vercel.json                   # Config Vercel raíz
├── DEPLOYMENT_GUIDE.md           # Este archivo
└── README.md                     # Proyecto original
```

---

## 🛠️ Troubleshooting

### Frontend 404 en Vercel
**Síntoma:** Vercel builds en 500ms, sin contenido
**Causa:** Root Directory incorrecto o vercel.json no encontrado
**Solución:** 
1. Verificar `vercel.json` existe en raíz o en `frontend/`
2. Verificar Build Command incluye `--prefix frontend`
3. Output Directory = `frontend/dist`

### Auth Fallback a localhost
**Síntoma:** Login redirige a http://localhost:8001
**Causa:** `VITE_AUTH_API_URL` no configurada en Vercel
**Solución:** 
1. Ir a Vercel > Project Settings > Environment Variables
2. Añadir `VITE_AUTH_API_URL` con URL de producción
3. Redeploy

### Supabase Connection Timeout
**Síntoma:** Backend no conecta a Supabase
**Causa:** Credenciales expiradas, IP bloqueada, o URL incorrecta
**Solución:**
1. Verificar `SUPABASE_DB_URL` en `.env`
2. Probar: `python BACKEND/temp_supabase_check.py` localmente
3. Confirmar pooler URL (puerto 6543) no estándar (5432)

---

## 📚 Referencias

### Archivos Clave
- [frontend/src/config/api.js](frontend/src/config/api.js) — Centralización URLs
- [BACKEND/docker-compose.yml](BACKEND/docker-compose.yml) — Orquestación
- [vercel.json](vercel.json) — Deploy config
- [frontend/.env.example](frontend/.env.example) — Variables template

### URLs de Referencia
- Vercel Dashboard: https://vercel.com/dashboard
- Supabase Console: https://app.supabase.com
- GitHub: https://github.com/MARCK-J/Sacra360

### Comando Rápido de Deploy
```bash
# Desde raíz del repo, validar build:
npm run build --prefix frontend

# Push a PRUEBA2:
git add .
git commit -m "chore: deployment updates"
git push origin PRUEBA2

# En Vercel: Redeploy o esperar auto-deploy
```

---

## ✅ Checklist Pre-Producción

- [ ] Todas las credenciales en variables de entorno (no en código)
- [ ] Frontend compila sin errores
- [ ] Supabase validada (temp_supabase_check.py pasado)
- [ ] Variables en Vercel cargadas (VITE_*)
- [ ] Docker compose puede arrancar localmente
- [ ] Login funciona contra auth-service
- [ ] Al menos 2 endpoints de API responden en producción
- [ ] HTTPS habilitado en Vercel (automático)
- [ ] Logs de error sin secretos expuestos

---

**Última actualización:** 22 de abril de 2026, 12:30 UTC  
**Rama:** PRUEBA2 @ commit 66dd141  
**Estado:** Listo para Vercel, dependiendo de repo correcto + vars en Vercel

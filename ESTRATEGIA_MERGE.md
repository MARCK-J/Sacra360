# Estrategia de Merge - Sacra360
## Fecha: 14 de Diciembre 2025

## Ramas Involucradas

### 1. **Diego** (Rama Actual)
**Funcionalidades:**
- Gestión completa de usuarios y autenticación
- Sistema de auditoría
- Sistema de reportes
- RBAC (Role-Based Access Control)
- Tests completos de backend

**Archivos Clave:**
- `/BACKEND/app/api/auditoria.py`
- `/BACKEND/app/api/usuarios.py`
- `/BACKEND/app/api/users.py`
- `/BACKEND/app/core/security.py`
- `/BACKEND/tests/` (todos los tests)
- `/frontend/src/pages/Auditoria.jsx`
- `/frontend/src/pages/Usuarios.jsx`
- `/frontend/src/pages/Reportes.jsx`
- `/BACKEND/sql/Create_Users_All_Roles.sql`

### 2. **Marco** (OCR y HTR)
**Funcionalidades:**
- Servicios de OCR (Reconocimiento Óptico de Caracteres)
- Servicios de HTR (Reconocimiento de Escritura Manual)
- Integración con MinIO para almacenamiento
- Soporte GPU para procesamiento
- Modelos de Machine Learning

**Archivos Clave:**
- `/BACKEND/server-sacra360/OCR-service/` (todo el directorio)
- `/BACKEND/server-sacra360/HTR-service/` (todo el directorio)
- `/BACKEND/models/` (notebooks de ML)
- `/BACKEND/app/ocr/processor.py`
- `/BACKEND/app/htr/processor.py`
- Configuraciones de MinIO en docker-compose

### 3. **sE2** (Gestión de Sacramentos)
**Funcionalidades:**
- CRUD completo de sacramentos (Bautizo, Matrimonio, etc.)
- Gestión de libros y personas
- Validación de datos
- Digitalización de documentos
- Reportes de sacramentos

**Archivos Clave:**
- `/BACKEND/server-sacra360/Documents-service/app/controllers/sacramento_controller.py`
- `/BACKEND/server-sacra360/Documents-service/app/controllers/bautizo_controller.py`
- `/BACKEND/server-sacra360/Documents-service/app/controllers/matrimonio_controller.py`
- `/frontend/src/pages/Sacramento.jsx`
- `/frontend/src/pages/Sacramentos.jsx`
- `/BACKEND/sql/Migration_Add_Matrimonios_Table.sql`

## Análisis de Conflictos

### Archivos Eliminados en Marco y sE2 (presentes en Diego):
```
- BACKEND/app/main.py
- BACKEND/app/api/__init__.py
- BACKEND/app/api/auditoria.py
- BACKEND/app/api/documentos.py
- BACKEND/app/api/personas.py
- BACKEND/app/api/resources.py
- BACKEND/app/api/sacramentos.py
- BACKEND/app/api/users.py
- BACKEND/app/api/usuarios.py
- BACKEND/app/core/__init__.py
- BACKEND/app/core/config.py
- BACKEND/app/core/security.py
- BACKEND/app/schemas/__init__.py
- BACKEND/app/schemas/sacra360_schemas.py
```
⚠️ **CRÍTICO**: Estos archivos contienen la lógica de autenticación, auditoría y reportes de Diego

### Archivos Modificados en Común:
```
- BACKEND/docker-compose.yml (conflicto seguro)
- BACKEND/sql/Database.sql (conflicto probable)
- BACKEND/README.md
- FRONTEND/package.json
- FRONTEND/src/App.jsx
- FRONTEND/src/main.jsx
- FRONTEND/index.html
```

### Archivos Nuevos en Marco (OCR/HTR):
- Todos los servicios OCR y HTR
- Modelos de ML
- Configuraciones GPU
- Tests de OCR/HTR

### Archivos Nuevos en sE2 (Sacramentos):
- Controllers de sacramentos específicos
- DTOs y servicios de sacramentos
- Páginas frontend de sacramentos
- Migraciones SQL de sacramentos

## Estrategia de Merge Recomendada

### Fase 1: Preparación
1. ✅ Confirmar cambios actuales en Diego
2. ✅ Crear rama de respaldo
3. ✅ Hacer backup de base de datos

### Fase 2: Merge de Marco (OCR/HTR) → Diego
**Orden:** Marco primero porque agrega servicios nuevos sin eliminar los de Diego

**Pasos:**
1. Merge Marco en Diego
2. Resolver conflictos en:
   - `docker-compose.yml`: Combinar ambos, mantener estructura de Diego + servicios de Marco
   - `Database.sql`: Combinar esquemas
   - Mantener TODOS los archivos de `/BACKEND/app/api/` de Diego
3. Verificar que servicios de autenticación/auditoría siguen funcionando

### Fase 3: Merge de sE2 (Sacramentos) → Diego+Marco
**Orden:** sE2 después porque complementa la funcionalidad

**Pasos:**
1. Merge sE2 en Diego+Marco
2. Resolver conflictos en:
   - Controllers de Documents-service: Combinar funcionalidades
   - Frontend pages: Mantener ambas versiones
   - Migraciones SQL: Aplicar en orden cronológico
3. Verificar integración completa

### Fase 4: Integración y Arquitectura
**Unificar la arquitectura de microservicios:**

1. **AuthProfiles-service** (Puerto 8001)
   - Mantener de Diego: autenticación, usuarios, perfiles, auditoría
   
2. **Documents-service** (Puerto 8002)
   - Combinar: sacramentos (sE2) + documentos (Diego) + digitalización (Marco)
   
3. **OCR-service** (Puerto 8003)
   - De Marco: procesamiento OCR
   
4. **HTR-service** (Puerto 8004)
   - De Marco: reconocimiento manuscritos
   
5. **Reports-service** (Puerto 8005)
   - De Diego: generación de reportes
   
6. **Files-service** (Puerto 8007)
   - Compartido: almacenamiento archivos

### Fase 5: Verificación y Testing
1. Ejecutar todos los tests
2. Verificar cada funcionalidad:
   - ✓ Login y autenticación
   - ✓ Gestión de usuarios
   - ✓ Auditoría
   - ✓ OCR de documentos
   - ✓ HTR de manuscritos
   - ✓ CRUD de sacramentos
   - ✓ Generación de reportes
3. Probar integración end-to-end

## Archivos Críticos a Preservar de Diego

### Backend:
```
BACKEND/app/api/auditoria.py
BACKEND/app/api/usuarios.py
BACKEND/app/api/users.py
BACKEND/app/core/security.py
BACKEND/tests/ (todos)
BACKEND/sql/Create_Users_All_Roles.sql
```

### Frontend:
```
frontend/src/pages/Auditoria.jsx
frontend/src/pages/Usuarios.jsx
frontend/src/pages/Reportes.jsx
frontend/src/context/ (contextos de autenticación)
```

## Comandos Git para el Merge

```bash
# 1. Backup
git branch backup-Diego

# 2. Merge Marco
git merge origin/Marco --no-commit --no-ff

# 3. Resolver conflictos manualmente
# 4. Commit
git commit -m "Merge Marco (OCR/HTR) into Diego"

# 5. Merge sE2
git merge origin/sE2 --no-commit --no-ff

# 6. Resolver conflictos manualmente
# 7. Commit
git commit -m "Merge sE2 (Sacramentos) into Diego+Marco"
```

## Riesgos Identificados

1. ⚠️ **Alto**: Pérdida de archivos de autenticación/auditoría
   - **Mitigación**: Usar `git merge --no-commit` y revisar cada archivo

2. ⚠️ **Medio**: Conflictos en docker-compose.yml
   - **Mitigación**: Combinar manualmente servicios

3. ⚠️ **Medio**: Conflictos en Database.sql
   - **Mitigación**: Ejecutar migraciones en orden

4. ⚠️ **Bajo**: Conflictos en package.json
   - **Mitigación**: Combinar dependencias

## Checklist Pre-Merge

- [ ] Backup de base de datos
- [ ] Crear rama backup-Diego
- [ ] Commit de cambios locales
- [ ] Documentar estado actual
- [ ] Tener lista de archivos críticos

## Checklist Post-Merge

- [ ] Compilación exitosa del backend
- [ ] Compilación exitosa del frontend
- [ ] Tests de autenticación pasan
- [ ] Tests de sacramentos pasan
- [ ] Tests de OCR/HTR pasan
- [ ] Docker compose levanta todos los servicios
- [ ] Verificación manual de cada funcionalidad

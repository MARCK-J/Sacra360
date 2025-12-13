**Resumen**

Este documento describe cómo desplegar el proyecto Sacra360 (al menos el microservicio `documents-service` y el frontend en desarrollo) y resume el funcionamiento del modulo de gestion de documentos: `registros`, `libros`, `reportes`, `sacramentos` y `certificados`.

**Estructura y rutas principales**

- **Backend (Documents Service)**: `BACKEND/server-sacra360/Documents-service`
  - **API base**: `http://localhost:8002/api/v1`
  - Rutas destacadas:
    - `POST /api/v1/sacramentos/` — Crear sacramento
    - `GET /api/v1/sacramentos/` — Listar sacramentos (filtros: `tipo_sacramento`, `fecha_inicio`, `fecha_fin`, `sacerdote`, `id_persona`, `page`, `limit`)
    - `GET /api/v1/sacramentos/{id}` — Obtener sacramento por id
    - `PUT /api/v1/sacramentos/{id}` — Actualizar sacramento (ahora no intenta escribir `ministro` en la tabla `sacramentos`; ese campo se guarda en las tablas `detalles_*`)
    - `GET /api/v1/personas/` — Endpoints de personas (consulta/crear/actualizar)
    - `GET /api/v1/libros/` — Endpoints para libros (leer/crear/actualizar)
    - `GET /api/v1/reportes/` — Endpoints de reportes (resúmenes/estadísticas)
    - `POST /api/v1/instituciones/` — (nuevo controlador) CRUD mínimo para `institucionesparroquias` en `app/controllers/instituciones_controller.py` (no registrado por defecto en `app/main.py` salvo que lo incluyas)

- **Frontend**: `FRONTEND/`
  - Servidor dev: `http://localhost:5173`
  - Archivos relevantes modificados:
    - `FRONTEND/src/pages/Certificados.jsx` — Plantilla de certificado, estilos de impresión/export (CSS inyectado), lógica para mostrar ambos contrayentes en matrimonios, helpers `isMatrimonio()` y `getSpouseNames()`.
    - `FRONTEND/src/pages/Reportes.jsx` — Estadísticas derivadas y gráficos SVG simples (BarChart, LineSpark) y lógica para normalizar el filtro `tipo_sacramento` antes de construir la query.
    - `FRONTEND/src/pages/Registros.jsx` — Se añadió input `ministro` en la edición y el PUT envía los datos para upsert en las tablas de detalles.

**Despliegue (rápido)**

Requisitos: Docker, Docker Compose (v2+ recomendado), Node.js (para frontend si desea correr localmente)

1) Backend (docker compose) — desde la raíz del repo o la carpeta `BACKEND`:

PowerShell (desde la raíz del repo):
```powershell
docker compose -f BACKEND/docker-compose-simple.yml up -d --build
# ó si usas el compose completo:
docker compose -f BACKEND/docker-compose.yml up -d --build
```

Notas:
- Si modificas `app/main.py` para incluir el router de `instituciones_controller` (ver sección "Activar rutas nuevas"), reinicia el servicio con `--no-deps --build documents-service` para reconstruir solo ese servicio.

2) Frontend (dev):

En `FRONTEND`:
```powershell
cd FRONTEND
npm install    # si no se instalaron dependencias
npm run dev
```

3) Verificación rápida (ejemplos):

- Crear una institución (si el router está incluido):
  - POST `http://localhost:8002/api/v1/instituciones/`  Body JSON: `{ "nombre": "Parroquia San Pedro" }`
- Listar sacramentos filtrando por tipo (ejemplo):
  - GET `http://localhost:8002/api/v1/sacramentos/?tipo_sacramento=matrimonio&page=1&limit=20`
- Obtener un certificado (frontend) — usar la UI en `http://localhost:5173` y las funcionalidades de export/print en la página `Certificados`.

**Qué hace cada parte (resumen técnico)**

**Registros (Registros / `Registros.jsx`, backend: sacramentos endpoints)**
- **Frontend:** la UI de `Registros` permite buscar, editar y abrir sacramentos. La edición incluye ahora el campo `ministro` en el modal; el frontend envía los campos relevantes en el PUT.
- **Backend:** las operaciones de edición/creación guardan el registro principal en la tabla `sacramentos` y los campos tipo-ministro/padrinos/foja/numero se almacenan en tablas de detalle: `detalles_bautizo`, `detalles_confirmacion`, `detalles_matrimonio`. El controlador hace upsert en la tabla de detalles correspondiente según `tipo_id`.

**Libros**
- **Frontend:** existe una sección para listar y seleccionar `libros` cuando se asocia un sacramento.
- **Backend:** la tabla `libros` se utiliza para referenciar `libro_id` desde `sacramentos`. Si se recibe un nombre de libro que no existe, el backend intenta crear un registro de libro mínimo.

**Reportes (`Reportes.jsx`, `reportes_controller.py`)**
- **Frontend:** añadimos estadísticas derivadas y gráficos simples (barras y sparklines) para visualizar conteos por tipo y series mensuales. También se normaliza el filtro `tipo_sacramento` para enviar nombres en la consulta.
- **Backend:** el controlador de reportes agrega endpoints que devuelven agregados por tipo, periodos y otros desgloses. Observación: hubo inconsistencia en la DB donde `tipos_sacramentos.nombre` a veces guarda un código numérico como cadena; el backend fue actualizado en `sacramento_controller.py` para aceptar `tipo_sacramento` tanto por nombre textual como por código numérico o por `id_tipo`.

**Sacramentos (`sacramento_controller.py`)**
- Inserción: crea el registro en `sacramentos` y, según tipo, inserta registros en `detalles_bautizo`, `detalles_confirmacion` o `detalles_matrimonio` para almacenar `ministro`, `padrino`, `foja`, `numero_acta`, nombres de esposos, etc.
- Actualización: el `PUT` actualiza columnas permitidas en `sacramentos` (solo columnas verdaderas de la tabla) y hace upsert en la tabla de detalles correspondiente.
- Filtrado robusto: la lista ahora intenta emparejar `tipo_sacramento` por `lower(ts.nombre)=lower(:tipo)` o por `ts.nombre = :tipo_code` o por `ts.id_tipo = :tipo_num` para soportar casos donde la columna `nombre` almacena valores numéricos.

**Certificados (`Certificados.jsx`)**
- Plantilla y estilo: el componente de certificados ahora incluye un bloque de CSS (variable `CERT_CSS`) que se inyecta tanto para la vista de impresión (`window.open`) como antes de ejecutar `html2canvas` para exportar PDF, de modo que el PDF respete el estilo de impresión.
- Matrimonios: se muestra ambos contrayentes cuando la información existe (`dmt.nombre_esposo`, `dmt.nombre_esposa`).

**Decisiones y compatibilidad**

- Validaciones: se añadieron DTOs Pydantic (no destructivas) para validar payloads en `sacramento_controller.py` y `create/update` — los errores de validación se registran pero no bloquean payloads heredados (esto evita romper clientes antiguos).
- Compatibilidad DB: el código hace consultas enriquecidas con `LEFT JOIN` a las tablas de detalles, pero tiene fallback a una consulta segura si el esquema no contiene columnas de detalle.

**Ejemplos reales de requests / responses**

> Nota: las respuestas muestran la forma típica devuelta por los controladores (usando `_mapping` o DTOs). Ajusta ids según tu base de datos.

1) Personas

- Crear (POST `/api/v1/personas/`)
Request JSON:
```json
{
  "nombres": "María José",
  "apellido_paterno": "Gómez",
  "apellido_materno": "Pérez",
  "fecha_nacimiento": "1985-07-23",
  "lugar_nacimiento": "La Paz",
  "nombre_padre": "José Gómez",
  "nombre_madre": "Ana Pérez"
}
```
Response (201):
```json
{
  "id_persona": 123,
  "nombres": "María José",
  "apellido_paterno": "Gómez",
  "apellido_materno": "Pérez",
  "fecha_nacimiento": "1985-07-23",
  "lugar_nacimiento": "La Paz",
  "nombre_padre": "José Gómez",
  "nombre_madre": "Ana Pérez"
}
```

- Obtener (GET `/api/v1/personas/123`)
Response (200): same as create response object above.

- Listar (GET `/api/v1/personas/?skip=0&limit=10`)
Response (200):
```json
[
  {
    "id_persona": 123,
    "nombres": "María José",
    "apellido_paterno": "Gómez",
    "apellido_materno": "Pérez",
    "fecha_nacimiento": "1985-07-23",
    "lugar_nacimiento": "La Paz",
    "nombre_padre": "José Gómez",
    "nombre_madre": "Ana Pérez"
  }
]
```

- Actualizar (PUT `/api/v1/personas/123`)
Request JSON (parcial):
```json
{
  "lugar_nacimiento": "El Alto"
}
```
Response (200): retorna la entidad actualizada.

2) Sacramentos

- Crear bautizo (POST `/api/v1/sacramentos/`)
Request JSON ejemplo:
```json
{
  "tipo_id": 1,
  "persona_id": 123,
  "fecha_sacramento": "2020-05-10",
  "libro_id": 5,
  "ministro": "P. Juan Perez",
  "padrino": "Carlos López",
  "folio": "12",
  "numero_acta": "345"
}
```
Response (201): ejemplo parcial devuelto por el endpoint `create`:
```json
{
  "id_sacramento": 987,
  "persona_id": 123,
  "tipo_id": 1,
  "tipo_nombre": "bautizo",
  "fecha_sacramento": "2020-05-10",
  "libro_id": 5,
  "foja": "12",
  "numero_acta": "345",
  "ministro": "P. Juan Perez",
  "padrino_bautizo": "Carlos López"
}
```

- Listar (GET `/api/v1/sacramentos/?tipo_sacramento=matrimonio&page=1&limit=20`)
Response (200):
```json
[
  {
    "id_sacramento": 900,
    "persona_id": 200,
    "tipo_id": 3,
    "tipo_nombre": "matrimonio",
    "fecha_sacramento": "2018-11-03",
    "libro_id": 7,
    "nombre_esposo": "Carlos Ruiz",
    "nombre_esposa": "Ana Torres",
    "ministro": "P. Luis Morales"
  }
]
```

- Actualizar (PUT `/api/v1/sacramentos/900`)
Request JSON (ejemplo para agregar foja/numero):
```json
{
  "foja": "45",
  "numero_acta": "1200",
  "ministro": "P. Luis Morales"
}
```
Response (200): devuelve el sacramento actualizado (misma forma que GET `/sacramentos/{id}`).

3) Libros

- Crear (POST `/api/v1/libros/`)
Request JSON:
```json
{
  "nombre": "Libro de Matrimonios 2018-2022",
  "fecha_inicio": "2018-01-01",
  "fecha_fin": "2022-12-31",
  "observaciones": "Digitalizado parcialmente"
}
```
Response (201): ejemplo:
```json
{
  "id_libro": 7,
  "nombre": "Libro de Matrimonios 2018-2022",
  "fecha_inicio": "2018-01-01",
  "fecha_fin": "2022-12-31",
  "observaciones": "Digitalizado parcialmente"
}
```

4) Reportes

- Conteo por tipo (GET `/api/v1/reportes/count-by-type`)
Response (200):
```json
{
  "counts": [
    {"tipo": "bautizo", "total": 120},
    {"tipo": "matrimonio", "total": 80}
  ]
}
```

- Resumen (GET `/api/v1/reportes/summary`)
Response (200):
```json
{
  "total": 300,
  "by_type": [
    {"tipo": "bautizo", "total": 120},
    {"tipo": "matrimonio", "total": 80}
  ]
}
```

5) Certificados (frontend)

- La generación/impresión se hace desde la UI en `http://localhost:5173`.
- Para exportar PDF la app inyecta estilos (`CERT_CSS`) antes de ejecutar `html2canvas` y genera el PDF con `jspdf`.

6) Instituciones (nuevo controlador)

- Crear (POST `/api/v1/instituciones/`)
Request JSON:
```json
{
  "nombre": "Parroquia San Pedro"
}
```
Response (201):
```json
{
  "id_institucion": 11,
  "nombre": "Parroquia San Pedro"
}
```

**Activar el nuevo controlador de instituciones (opcional)**

Si quieres exponer las rutas de `instituciones_controller.py`, registra su router en `app/main.py` (buscar la sección "Incluir routers") y añade:

```python
from app.controllers.instituciones_controller import router as instituciones_router
app.include_router(instituciones_router, prefix="/api/v1")
```

Luego reinicia el servicio `documents-service` con Docker Compose como se indica en la sección de despliegue.

**Pruebas y verificación**

- Usa `curl` o Postman para probar los endpoints listados. Ejemplo con `curl` (PowerShell compatible):
```powershell
curl -X GET "http://localhost:8002/api/v1/sacramentos/?limit=10" -H "Accept: application/json"
curl -X POST "http://localhost:8002/api/v1/instituciones/" -H "Content-Type: application/json" -d '{"nombre":"Parroquia Demo"}'
```

**Notas finales / riesgos conocidos**

- La tabla `tipos_sacramentos` en la DB tiene valores mixtos (a veces el `nombre` contiene un número en forma de cadena). Por eso se añadió tolerancia en los filtros; considera normalizar datos en BD para evitar ambigüedades.
- El controlador de instituciones fue añadido pero no registrado por defecto: no cambia la funcionalidad existente hasta que lo registres en `app/main.py`.
- Cualquier cambio en esquemas (nombres de columnas) debe probarse en un entorno de staging antes de aplicar en producción.

Si quieres, actualizo este documento para añadir ejemplos concretos de requests/responses, o genero una colección Postman / HTTPie con las rutas principales.

-- Fin

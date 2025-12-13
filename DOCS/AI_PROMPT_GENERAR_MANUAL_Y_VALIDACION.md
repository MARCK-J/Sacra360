# Prompt para otra IA — Generar Manual Formal + Pruebas y Capturas

Contexto breve:
Soy parte del proyecto Sacra360 (sistema de gestión y digitalización de archivos sacramentales). Hay un pseudo manual creado en `DOCS/README_DIGITALIZACION.md` que describe el flujo de digitalización: formulario de metadatos, subida de archivos (PDF/JPG/PNG), almacenamiento en MinIO, procesamiento en background con OCR o HTR, y revisión de resultados por parte de un usuario. El frontend usa la página `Digitalizacion.jsx` y muestra un modal de progreso; el backend orquesta con `Documents-service`, y hay servicios `OCR-service` y `HTR-service` que realizan el procesamiento.

Objetivo del prompt:
Pedir a la IA que genere un manual formal y visual (PDF y Markdown), y además entregue una guía de pruebas y un pequeño reporte/checklist para validar el flujo de digitalización (subida, procesamiento, progreso, revisión). El resultado debe ser listo para entregar a usuarios y equipo de QA.

Requerimientos de salida (entregables):
- `manual_digitalizacion.pdf` — Manual de usuario formal y visual en PDF.
- `manual_digitalizacion.md` — Mismo contenido en Markdown con enlaces a las capturas.
- `pruebas_digitalizacion_checklist.md` — Checklist de pruebas paso a paso y resultados esperados.
- `reporte_pruebas.json` — Plantilla JSON con campos para completar resultados (fecha, tester, entorno, lista de casos, estado, comentarios, ids de documentos generados).

Instrucciones detalladas para la IA (qué hacer):
1. Basarse en `DOCS/README_DIGITALIZACION.md` como fuente principal de contenido y estructura.
2. Generar un manual formal en español que incluya:
   - Portada (título, versión, fecha, autor).
   - Índice automático.
   - Introducción y alcance (qué hace el módulo, público objetivo).
   - Requisitos previos (credenciales, formatos, límites: PDF/JPG/PNG, máx 50MB).
   - Guía paso a paso (números, capturas sugeridas y textos para cada captura).
   - Resolución de problemas frecuentes y acciones recomendadas.
   - Apéndice técnico con endpoints principales: `POST /api/v1/digitalizacion/upload`, `GET /api/v1/digitalizacion/progreso/{documento_id}`, `GET /api/v1/digitalizacion/documentos` y lista de servicios implicados (Documents-service, OCR-service, HTR-service, MinIO, Postgres).
   - Glosario (OCR, HTR, MinIO, documento, tupla).
3. Usar las capturas que se colocarán en `DOCS/screenshots/` con los nombres exactos listados en el pseudo manual. Para cada captura, generar un pie de foto breve y puntual indicando qué resalta la imagen (ej. "Botón Subir resaltado — paso 6").
4. Formatear las secciones de la guía paso a paso para que cada paso incluya:
   - Texto (1–3 frases claras y accionables).
   - Captura recomendada (archivo de `DOCS/screenshots/`), si no existe, dejar una nota "[CAPTURA FALTANTE: 01_formulario_metadatos.png]".
   - Resultado esperado y posibles mensajes de error.
5. Generar `pruebas_digitalizacion_checklist.md` con casos de prueba mínimos y resultados esperados, por ejemplo:
   - Caso 1: Subir PDF válido + seleccionar sacramento/libro + modelo OCR → espera: respuesta 200, modal de progreso y documento listado en "Documentos Procesados".
   - Caso 2: Subir imagen JPG mayor a 50MB → espera: error de tamaño y mensaje amigable.
   - Caso 3: Cambiar modelo a HTR y reprocesar documento existente → espera: re-procesamiento en background y progreso observable.
   - Caso 4: Consultar progreso con `GET /api/v1/digitalizacion/progreso/{documento_id}` → respuesta JSON con `estado`, `progreso`, `mensaje`.
   Para cada caso, incluir pasos concretos para ejecutar en UI y API, datos de entrada de ejemplo, y criterios de aceptación.
6. Producir `reporte_pruebas.json` como plantilla (vacía pero con campos): `tester`, `fecha`, `entorno`, `casos: [{id, descripcion, estado, evidencia: [ruta_imagen], comentarios}]`.
7. Incluir una sección corta que explique cómo automatizar la verificación básica (opcional): comandos `curl` para los endpoints, y un script de ejemplo (bash/PowerShell) que suba un archivo de prueba y consulte progreso.
8. Mantener lenguaje accesible y profesional; evitar tecnicismos sin explicación.

Datos y rutas útiles (para la IA):
- Pseudo manual fuente: `DOCS/README_DIGITALIZACION.md`
- Ruta sugerida para capturas: `DOCS/screenshots/` (nombres esperados: `01_formulario_metadatos.png`, `02_zona_carga.png`, `03_lista_archivos.png`, `04_subiendo_modal.png`, `05_documentos_procesados.png`, `06_revision_ocr.png`).
- Entorno API base (ejemplo): `http://localhost:8002` (Documents-service). OCR en `http://localhost:8003`, HTR en `http://localhost:8004`. MinIO bucket: `sacra360-documents`.

Instrucción final y formato de respuesta:
Devuelve un ZIP o un listado de archivos con contenido listo (o enlaces a los ficheros generados). Si no puede crear un PDF directamente, devuelve el Markdown final (`manual_digitalizacion.md`) con instrucciones precisas para convertir a PDF (comando `pandoc` o similar) y una carpeta `assets/` con las rutas de las capturas esperadas.

Prompt corto listo para usar (versión resumida):
"Toma `DOCS/README_DIGITALIZACION.md` y las capturas en `DOCS/screenshots/` y genera: 1) un manual formal en PDF y Markdown; 2) un checklist de pruebas de QA; 3) una plantilla JSON para el reporte de pruebas; 4) un breve script de ejemplo para subir y consultar progreso. Incluye pies de foto para cada captura, pasos de aceptación y comandos `curl` para validar endpoints. Entrega los archivos: `manual_digitalizacion.pdf`, `manual_digitalizacion.md`, `pruebas_digitalizacion_checklist.md`, `reporte_pruebas.json`. Si no puedes generar PDF, entrega el Markdown listo para conversión y las instrucciones para convertir a PDF." 

---

Si quieres que ejecute este prompt con una IA que tengas disponible, dime cuál servicio usar (por ejemplo: OpenAI + capacidad de subir archivos, o una IA local) y preparo la llamada; si no, puedo ajustar el prompt o generar el Markdown aquí mismo usando la información disponible.

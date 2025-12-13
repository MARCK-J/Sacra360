# Módulo de Digitalización — Pseudo Manual de Usuario

Este documento es un pseudo manual orientado al usuario final del módulo de digitalización. Está escrito de forma simple para que lo entiendan los usuarios (p. ej. digitalizadores) y contiene pautas para completar con capturas de pantalla. También incluye instrucciones para pasar este contenido a otra IA y generar un manual formal.

## Resumen del flujo (visión general)
- 1) El usuario accede a la página "Digitalización" desde el Frontend.
- 2) Completa los metadatos obligatorios: *Sacramento* y *Libro*.
- 3) Selecciona el tipo de procesamiento: **OCR** (texto mecanografiado) o **HTR** (texto manuscrito).
- 4) Arrastra o selecciona uno o varios archivos (PDF/JPG/PNG), máximo 50MB por archivo.
- 5) Presiona "Subir". El sistema sube el archivo al almacenamiento (MinIO) y lo guarda en la base de datos.
- 6) Si se habilita el procesamiento automático, el documento se procesa en background con OCR o HTR.
- 7) Durante el procesamiento aparece un modal de progreso que muestra porcentaje, etapa y mensajes.
- 8) Al completarse, el usuario puede ir a la pantalla de "Revisión OCR" para validar y corregir los resultados.

## Pasos de uso (guía paso a paso — usuario no técnico)
1. Ir a la opción "Digitalización" en el menú principal.
2. En "Información del Documento": elegir el tipo de sacramento (p. ej. Bautismo) y el libro correspondiente.
3. Elegir "Tipo de Texto": seleccione "OCR" para textos impresos o "HTR" para manuscritos.
4. En la zona "Subir Documentos": arrastre sus archivos o use "Seleccionar archivos".
   - Tipos permitidos: PDF, JPG, JPEG, PNG.
   - Tamaño máximo: 50MB por archivo.
5. Revise la lista de archivos seleccionados y elimine los que no quiera antes de subir.
6. Pulse el botón "Subir N archivo(s)".
7. Verá un modal de progreso: espere a que llegue a 100% y cierre automáticamente.
8. Al finalizar, haga clic en "Ir a Revisión OCR" para validar las tuplas extraídas.

## Qué espera el usuario ver en pantalla
- Formulario con campos: *Sacramento*, *Libro*, *Tipo de Texto*.
- Zona de arrastrar/soltar con botón "Seleccionar archivos".
- Lista de archivos con miniaturas (para imágenes) y tamaño.
- Botón claro de "Subir" que muestra estado (Subiendo... / Subido).
- Modal de progreso con porcentaje, estado y mensaje.
- Sección "Documentos Procesados" con lista y links a revisión.

## Errores comunes y acciones recomendadas
- Archivo rechazado por tipo: subir un PDF o imagen compatible.
- Archivo demasiado grande: dividir o reducir resolución y volver a subir.
- Error en procesamiento (modal muestra error): reintentar reprocesar desde la lista de documentos o contactar soporte con el ID del documento.
- Si el progreso no avanza: comprobar conectividad o que los servicios OCR/HTR estén activos.

## Información útil para el operario
- Usuario de prueba (si está cargado en la BD de ejemplo): digitalizador@sacra360.com / admin123
- Los archivos subidos se guardan en el almacenamiento MinIO (bucket: `sacra360-documents`).
- El procesamiento puede tardar varios minutos según el tamaño y el modelo (OCR suele ser más rápido que HTR).

## Dónde y cómo adjuntar capturas de pantalla
Para crear un manual visual completo, capture las siguientes pantallas y guárdelas con los nombres sugeridos debajo de la carpeta `DOCS/screenshots/`:

- 01_formulario_metadatos.png — Formulario "Información del Documento" con sacramento, libro y tipo de texto seleccionados.
- 02_zona_carga.png — Zona de arrastrar/soltar mostrando archivos seleccionados.
- 03_lista_archivos.png — Lista de archivos antes de subir (con miniaturas o etiquetas PDF).
- 04_subiendo_modal.png — Modal de progreso mostrado mientras se procesa (mostrar porcentaje visible).
- 05_documentos_procesados.png — Sección "Documentos Procesados" con documento subido y su ID.
- 06_revision_ocr.png — Pantalla de revisión OCR mostrando algunas tuplas y controles de validación.

Pautas de captura:
- Tomar la captura con el estado más informativo (p. ej. modal de progreso al 40% o 75%).
- Anotar con flechas o recuadros las áreas importantes (botón subir, ID del documento, mensajes de error).
- Guardar las imágenes en formato PNG, nombradas siguiendo el patrón `NN_descripcion.png`.

## Pautas para pasar a otra IA (para generar un manual formal)
Si deseas que otra IA convierta este pseudo manual en un manual formal, pásale lo siguiente:

1. Objetivo: "Generar un manual de usuario formal y visual para el módulo de digitalización del sistema Sacra360. Público: personal de digitalización sin conocimientos técnicos."
2. Estructura requerida (sugerida):
   - Portada: Título, versión, fecha, autor.
   - Índice.
   - Introducción (qué hace el módulo y beneficios).
   - Requisitos previos (credenciales, formatos de archivo, límites).
   - Guía paso a paso con capturas (usar archivos en `DOCS/screenshots/`).
   - Sección de resolución de problemas frecuentes.
   - Glosario de términos (OCR, HTR, MinIO, documento, tupla).
   - Apéndice: direcciones de endpoints y usuarios de prueba (opcional, técnico).
3. Para cada paso en la guía paso a paso, incluir:
   - Texto breve y claro (1–3 frases).
   - Captura de pantalla correspondiente (usar el nombre de archivo indicado más arriba).
   - Señalar campos obligatorios con ejemplos (p. ej. seleccionar "Bautismo" y libro "Bautismos 2024").
4. Formato de salida deseado: `PDF` y `Markdown` (ambos). Incluir tabla de contenidos y números de página.
5. Tonalidad: Profesional, accesible, con instrucciones numeradas y recomendaciones de seguridad simples (no compartir credenciales).

Ejemplo de prompt compacto para otra IA:
"Toma este pseudo manual y las capturas en `DOCS/screenshots/` y genera un manual de usuario en PDF y Markdown. Público: digitalizadores. Incluir portada, índice, pasos con capturas y resolución de problemas. Mantén un lenguaje claro y conciso." 

## Apéndice (resumen técnico breve — opcional para incluir en el manual técnico)
- Endpoints principales usados por el Frontend:
  - `POST /api/v1/digitalizacion/upload` — subir archivo y lanzar procesamiento.
  - `GET /api/v1/digitalizacion/progreso/{documento_id}` — consultar progreso de procesamiento.
  - `GET /api/v1/digitalizacion/documentos` — listar documentos procesados/pendientes.
- Servicios involucrados: `Documents-service` (orquestador), `OCR-service`, `HTR-service`, `MinIO` (almacenamiento de archivos), PostgreSQL (metadatos y resultados OCR).

## Próximos pasos sugeridos
- Crear la carpeta `DOCS/screenshots/` y añadir las capturas listadas.
- Ejecutar una subida de prueba y obtener al menos 4 capturas representativas.
- Pasar este archivo y las capturas a una IA para que genere el manual formal en PDF.

---

Si quieres, puedo generar el archivo PDF/Markdown final usando tus capturas o puedo crear el archivo Markdown ahora en el repositorio. ¿Cómo deseas proceder?

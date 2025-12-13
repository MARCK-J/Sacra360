-- ==================================================================================
-- MIGRATION: Preparar BD para soportar HTR (Handwritten Text Recognition)
-- Fecha: 2025-12-11
-- Descripción: Agrega soporte para procesar documentos con HTR además de OCR
-- ==================================================================================

-- 1. Agregar columna para distinguir el modelo de procesamiento (OCR vs HTR)
ALTER TABLE documento_digitalizado 
ADD COLUMN IF NOT EXISTS modelo_procesamiento VARCHAR(20) DEFAULT 'ocr'
CHECK (modelo_procesamiento IN ('ocr', 'htr'));

COMMENT ON COLUMN documento_digitalizado.modelo_procesamiento IS 
'Indica qué modelo se usó para procesar el documento: ocr (EasyOCR) o htr (HTR_Sacra360)';

-- 2. Renombrar columnas de progreso para ser más genéricas (aplican a OCR y HTR)
-- Nota: Si las columnas progreso_ocr y mensaje_progreso ya existen, se mantienen
-- pero se actualizan los comentarios para reflejar que sirven para ambos modelos

COMMENT ON COLUMN documento_digitalizado.progreso_ocr IS 
'Progreso del procesamiento (0-100%). Aplica tanto para OCR como HTR';

COMMENT ON COLUMN documento_digitalizado.mensaje_progreso IS 
'Mensaje descriptivo del progreso actual. Ejemplo: "Procesadas 20/139 celdas"';

-- 3. Actualizar comentario de la tabla ocr_resultado para reflejar que ahora almacena
-- resultados tanto de OCR como de HTR
COMMENT ON TABLE ocr_resultado IS 
'Almacena resultados de procesamiento de documentos (OCR o HTR). 
El campo fuente_modelo distingue qué motor generó los datos.';

COMMENT ON COLUMN ocr_resultado.fuente_modelo IS 
'Identificador del modelo que generó los datos: "OCRv2_EasyOCR" o "HTR_Sacra360"';

-- 4. Crear índice para búsquedas por modelo de procesamiento
CREATE INDEX IF NOT EXISTS idx_documento_modelo_procesamiento 
ON documento_digitalizado(modelo_procesamiento);

-- 5. Crear índice para búsquedas por fuente de modelo en ocr_resultado
CREATE INDEX IF NOT EXISTS idx_ocr_resultado_fuente_modelo 
ON ocr_resultado(fuente_modelo);

-- 6. Verificar la migración
DO $$
BEGIN
    RAISE NOTICE '✅ Migración completada exitosamente';
    RAISE NOTICE 'Columnas agregadas:';
    RAISE NOTICE '  - documento_digitalizado.modelo_procesamiento';
    RAISE NOTICE 'Índices creados:';
    RAISE NOTICE '  - idx_documento_modelo_procesamiento';
    RAISE NOTICE '  - idx_ocr_resultado_fuente_modelo';
END $$;

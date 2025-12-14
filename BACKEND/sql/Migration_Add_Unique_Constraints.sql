-- Migration: Agregar constraints UNIQUE para validación de duplicados
-- Fecha: 2025-11-28
-- Descripción: Agrega constraints únicos en personas y sacramentos para evitar registros duplicados

-- ============================================
-- TABLA: personas
-- ============================================
-- Evitar personas duplicadas con mismos datos básicos
-- Una persona es única por: nombres + apellidos + fecha de nacimiento
ALTER TABLE personas 
ADD CONSTRAINT personas_datos_basicos_unique 
UNIQUE (nombres, apellido_paterno, apellido_materno, fecha_nacimiento);

-- Índice para búsquedas rápidas de duplicados
CREATE INDEX idx_personas_busqueda_duplicados 
ON personas (apellido_paterno, apellido_materno, nombres, fecha_nacimiento);

-- ============================================
-- TABLA: sacramentos
-- ============================================
-- Evitar registrar el mismo sacramento dos veces
-- Un sacramento es único por: persona + tipo + fecha + libro
ALTER TABLE sacramentos 
ADD CONSTRAINT sacramentos_unico_por_registro 
UNIQUE (persona_id, tipo_id, fecha_sacramento, libro_id);

-- Índice para búsqueda de sacramentos duplicados
CREATE INDEX idx_sacramentos_busqueda_duplicados 
ON sacramentos (persona_id, tipo_id, fecha_sacramento);

-- ============================================
-- ÍNDICES ADICIONALES PARA RENDIMIENTO
-- ============================================
-- Índice para búsqueda de documentos por estado (sin constraint único)
CREATE INDEX IF NOT EXISTS idx_documento_estado_procesamiento 
ON documento_digitalizado (estado_procesamiento);

-- ============================================
-- COMENTARIOS EN LA BASE DE DATOS
-- ============================================
COMMENT ON CONSTRAINT personas_datos_basicos_unique ON personas 
IS 'Evita registrar la misma persona con los mismos datos básicos';

COMMENT ON CONSTRAINT sacramentos_unico_por_registro ON sacramentos 
IS 'Evita registrar el mismo sacramento dos veces para la misma persona';

-- End of migration

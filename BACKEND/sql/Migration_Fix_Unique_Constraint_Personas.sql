-- Migration: Corregir constraint UNIQUE en tabla personas
-- Fecha: 2025-12-12
-- Descripción: Actualiza el constraint único para incluir fecha_bautismo
--              Esto evita registrar la misma persona dos veces considerando también
--              su fecha de bautizo, no solo nombre y fecha de nacimiento

-- ============================================
-- 1. ELIMINAR CONSTRAINT ANTERIOR
-- ============================================
ALTER TABLE personas 
DROP CONSTRAINT IF EXISTS personas_datos_basicos_unique;

-- ============================================
-- 2. CREAR NUEVO CONSTRAINT INCLUYENDO FECHA_BAUTISMO
-- ============================================
ALTER TABLE personas 
ADD CONSTRAINT personas_datos_basicos_unique 
UNIQUE (nombres, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_bautismo);

-- ============================================
-- 3. ACTUALIZAR ÍNDICE DE BÚSQUEDA
-- ============================================
-- Eliminar índice anterior
DROP INDEX IF EXISTS idx_personas_busqueda_duplicados;

-- Crear índice actualizado
CREATE INDEX idx_personas_busqueda_duplicados 
ON personas (apellido_paterno, apellido_materno, nombres, fecha_nacimiento, fecha_bautismo);

-- ============================================
-- 4. COMENTARIOS
-- ============================================
COMMENT ON CONSTRAINT personas_datos_basicos_unique ON personas 
IS 'Evita registrar la misma persona con los mismos datos básicos (nombres, apellidos, fecha nacimiento y fecha bautismo)';

-- End of migration

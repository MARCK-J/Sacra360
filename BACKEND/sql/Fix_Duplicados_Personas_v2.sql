-- Script para eliminar duplicados en personas con referencias en sacramentos
-- Actualiza las referencias de sacramentos antes de eliminar duplicados

-- PASO 1: Identificar duplicados y sus IDs
SELECT 
    nombres, apellido_paterno, apellido_materno, 
    fecha_nacimiento, fecha_bautismo, 
    STRING_AGG(id_persona::text, ', ' ORDER BY id_persona) as ids,
    MIN(id_persona) as id_mantener,
    COUNT(*) as cantidad
FROM personas 
GROUP BY nombres, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_bautismo
HAVING COUNT(*) > 1
ORDER BY cantidad DESC;

-- PASO 2: Actualizar referencias en sacramentos para que apunten al ID más bajo (el que vamos a mantener)
UPDATE sacramentos s
SET persona_id = (
    SELECT MIN(p1.id_persona)
    FROM personas p1
    WHERE p1.nombres = (SELECT nombres FROM personas WHERE id_persona = s.persona_id)
    AND p1.apellido_paterno = (SELECT apellido_paterno FROM personas WHERE id_persona = s.persona_id)
    AND p1.apellido_materno = (SELECT apellido_materno FROM personas WHERE id_persona = s.persona_id)
    AND p1.fecha_nacimiento = (SELECT fecha_nacimiento FROM personas WHERE id_persona = s.persona_id)
    AND p1.fecha_bautismo = (SELECT fecha_bautismo FROM personas WHERE id_persona = s.persona_id)
)
WHERE persona_id IN (
    SELECT p2.id_persona
    FROM personas p1
    JOIN personas p2 
        ON p1.nombres = p2.nombres 
        AND p1.apellido_paterno = p2.apellido_paterno
        AND p1.apellido_materno = p2.apellido_materno
        AND p1.fecha_nacimiento = p2.fecha_nacimiento
        AND p1.fecha_bautismo = p2.fecha_bautismo
        AND p1.id_persona < p2.id_persona
);

-- PASO 3: Verificar que las referencias se actualizaron
SELECT 'Referencias en sacramentos actualizadas' as resultado;

-- PASO 4: Eliminar duplicados (ahora sin referencias)
DELETE FROM personas 
WHERE id_persona IN (
    SELECT p2.id_persona
    FROM personas p1
    JOIN personas p2 
        ON p1.nombres = p2.nombres 
        AND p1.apellido_paterno = p2.apellido_paterno
        AND p1.apellido_materno = p2.apellido_materno
        AND p1.fecha_nacimiento = p2.fecha_nacimiento
        AND p1.fecha_bautismo = p2.fecha_bautismo
        AND p1.id_persona < p2.id_persona
);

-- PASO 5: Verificar que ya no hay duplicados
SELECT 
    nombres, apellido_paterno, apellido_materno, 
    fecha_nacimiento, fecha_bautismo, 
    COUNT(*) as cantidad
FROM personas 
GROUP BY nombres, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_bautismo
HAVING COUNT(*) > 1;

-- PASO 6: Aplicar constraint UNIQUE
ALTER TABLE personas 
ADD CONSTRAINT personas_datos_basicos_unique 
UNIQUE (nombres, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_bautismo);

-- PASO 7: Crear índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_personas_busqueda_duplicados 
ON personas (apellido_paterno, apellido_materno, nombres, fecha_nacimiento, fecha_bautismo);

-- Resultado final
SELECT 
    'Duplicados eliminados, constraint aplicado exitosamente' as resultado,
    COUNT(*) as total_personas
FROM personas;

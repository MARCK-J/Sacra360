-- Script para eliminar registros duplicados en la tabla personas
-- Mantiene el registro más antiguo (menor id_persona) y elimina los duplicados

-- 1. Ver duplicados antes de eliminar (para verificación)
SELECT 
    nombres, apellido_paterno, apellido_materno, 
    fecha_nacimiento, fecha_bautismo, 
    COUNT(*) as cantidad,
    STRING_AGG(id_persona::text, ', ' ORDER BY id_persona) as ids
FROM personas 
GROUP BY nombres, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_bautismo
HAVING COUNT(*) > 1
ORDER BY cantidad DESC;

-- 2. Eliminar duplicados manteniendo solo el registro con el id_persona más bajo
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

-- 3. Verificar que ya no hay duplicados
SELECT 
    nombres, apellido_paterno, apellido_materno, 
    fecha_nacimiento, fecha_bautismo, 
    COUNT(*) as cantidad
FROM personas 
GROUP BY nombres, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_bautismo
HAVING COUNT(*) > 1;

-- 4. Aplicar constraint UNIQUE
ALTER TABLE personas 
ADD CONSTRAINT personas_datos_basicos_unique 
UNIQUE (nombres, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_bautismo);

-- 5. Crear índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_personas_busqueda_duplicados 
ON personas (apellido_paterno, apellido_materno, nombres, fecha_nacimiento, fecha_bautismo);

-- Resultado: tabla limpia con constraint aplicado
SELECT 'Duplicados eliminados y constraint aplicado exitosamente' as resultado;

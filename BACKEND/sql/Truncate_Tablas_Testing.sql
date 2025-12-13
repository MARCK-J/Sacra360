-- Script para limpiar tablas del sistema (SOLO PARA TESTING)
-- ADVERTENCIA: Este script elimina TODOS los datos de las tablas especificadas
-- Usar solo en ambiente de desarrollo/testing

-- Deshabilitar temporalmente los triggers para evitar problemas
SET session_replication_role = 'replica';

-- TRUNCATE en orden inverso de dependencias (primero las que dependen, luego las principales)
-- Usamos CASCADE para eliminar automáticamente registros relacionados

TRUNCATE TABLE validacion_tuplas RESTART IDENTITY CASCADE;
TRUNCATE TABLE ocr_resultado RESTART IDENTITY CASCADE;
TRUNCATE TABLE sacramentos RESTART IDENTITY CASCADE;
TRUNCATE TABLE documento_digitalizado RESTART IDENTITY CASCADE;
TRUNCATE TABLE personas RESTART IDENTITY CASCADE;

-- Rehabilitar triggers
SET session_replication_role = 'origin';

-- Verificar que las tablas están vacías
SELECT 
    'personas' as tabla, COUNT(*) as registros FROM personas
UNION ALL
SELECT 'sacramentos', COUNT(*) FROM sacramentos
UNION ALL
SELECT 'documento_digitalizado', COUNT(*) FROM documento_digitalizado
UNION ALL
SELECT 'ocr_resultado', COUNT(*) FROM ocr_resultado
UNION ALL
SELECT 'validacion_tuplas', COUNT(*) FROM validacion_tuplas;

-- Mensaje de confirmación
SELECT 'Tablas limpiadas exitosamente. Todos los registros eliminados y secuencias reiniciadas.' as resultado;

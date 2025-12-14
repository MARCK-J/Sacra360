-- ========================================
-- SCRIPT DE INSERCIÓN DE ROLES Y USUARIOS
-- Sistema Sacra360
-- Fecha: Diciembre 2025
-- ========================================
-- 
-- INSTRUCCIONES:
-- 1. Ejecutar este script DESPUÉS de crear las tablas (Database.sql)
-- 2. Las contraseñas ya están hasheadas con bcrypt
-- 3. Todos los usuarios tienen contraseñas seguras pre-configuradas
--
-- CONTRASEÑAS (para referencia):
-- Las contraseñas originales fueron hasheadas con bcrypt (12 rounds)
-- Para crear nuevas contraseñas, usar Python:
--   from passlib.hash import bcrypt
--   hash = bcrypt.hash("tu_contraseña")
-- ========================================

-- ========================================
-- 1. LIMPIAR DATOS EXISTENTES (OPCIONAL)
-- ========================================
-- Descomenta las siguientes líneas si quieres limpiar antes de insertar
-- TRUNCATE TABLE auditoria CASCADE;
-- TRUNCATE TABLE usuarios CASCADE;
-- TRUNCATE TABLE roles CASCADE;

-- ========================================
-- 2. INSERTAR ROLES
-- ========================================
-- Se reinicia la secuencia para asegurar IDs correctos
SELECT setval('roles_id_rol_seq', 1, false);

INSERT INTO roles (id_rol, nombre, descripcion) VALUES
(1, 'Administrador', 'Acceso completo al sistema'),
(2, 'Digitalizador', 'Puede digitalizar y cargar documentos'),
(3, 'Validador', 'Puede validar documentos OCR'),
(4, 'Usuario', 'Acceso de solo lectura')
ON CONFLICT (id_rol) DO NOTHING;

-- Resetear la secuencia de roles al valor actual máximo
SELECT setval('roles_id_rol_seq', (SELECT MAX(id_rol) FROM roles));

-- ========================================
-- 3. INSERTAR USUARIOS
-- ========================================
-- Se reinicia la secuencia para asegurar IDs correctos
SELECT setval('usuarios_id_usuario_seq', 1, false);

INSERT INTO usuarios (id_usuario, nombre, apellido_paterno, apellido_materno, email, contrasenia, rol_id, activo, fecha_creacion) VALUES
-- Usuario 5: Carlos Moron (Administrador)
(5, 'Carlos', 'Moron', 'Carrasco', 'admin@sacra360.com', 
 '$2b$12$./lAbpEl7qU31XSH1f2btOP2OPKItxDjQD0d9EgRlAjkZGtaWqdbm', 
 1, true, '2025-11-28'),

-- Usuario 6: Pepe Pérez (Validador)
(6, 'Pepe', 'Pérez', 'García', 'digitalizador@sacra360.com', 
 '$2b$12$FDopJ1zQeRl7nQLgX4OcMO1EL4HKH6.ldpglx4ewrf/vqJwHETLiG', 
 3, true, '2025-11-28'),

-- Usuario 7: Ana Rodríguez (Digitalizador)
(7, 'Ana', 'Rodríguez', 'Martínez', 'revisor@sacra360.com', 
 '$2b$12$CAsfuEBMFz1dSXeDiEw1j.v0MqdYVn7XnHGMxXe079.AAViEDSEcK', 
 2, true, '2025-11-28'),

-- Usuario 8: Sofía Gómez (Usuario de solo lectura)
(8, 'Sofía', 'Gómez', 'Torres', 'consultor@sacra360.com', 
 '$2b$12$gnGJFCY3YNsD1kCMctwI7..sWV1sFUWdmyEZVMqdHAxA9K8STfk9C', 
 4, true, '2025-11-28'),

-- Usuario 9: Diego Moron (Administrador)
(9, 'Diego', 'Moron', 'Mejia', 'diego.moron@ucb.edu.bo', 
 '$2b$12$VABwTwA3viQs3YZzc87hPO1XB2erCyvQaJDD/Yq1HN8T1gf26L5AO', 
 1, true, '2025-11-28'),

-- Usuario 10: Ramon Gómez (Digitalizador)
(10, 'Ramon', 'Gómez', 'Torres', 'intento@sacra.com', 
 '$2b$12$TfIYd0bFC81svbcSLQ1naOHY8yZWAmqi2gt3IB/8LJzDCEc5M2oJC', 
 2, true, '2025-12-12'),

-- Usuario 11: Pepe Moron (Administrador)
(11, 'Pepe', 'Moron', 'Mejia', 'diego.moras@gmail.com', 
 '$2b$12$pEyujaqJEXtrEAk1p/dfNOQGy2K8Lvj9gRRqahKMlt4L4cA5/D2Y.', 
 1, true, '2025-12-12'),

-- Usuario 12: María González (Administrador)
(12, 'María', 'González', 'López', 'superadmin@sacra360.com', 
 '$2b$12$WzBHX.1fX.mxWutFaGFgnedLCCddV4mWgGPiRYVHPHbv1mFkjxmgm', 
 1, true, '2025-12-12'),

-- Usuario 13: Carlos Rodríguez (Usuario - INACTIVO)
(13, 'Carlos', 'Rodríguez', 'Torres', 'admin4@sacra360.com', 
 '$2b$12$tCyCyf8H4aBmwn77.H1jFOzUnrMT8IEpLBfQg0rOhKXXuqwV6tUVy', 
 4, false, '2025-12-12'),

-- Usuario 14: Orlando Rivera (Digitalizador)
(14, 'Orlando', 'RIvera', NULL, 'consultor1@sacra360.com', 
 '$2b$12$FYKBwApsuaWdV/iFDbfBk.U4N6p80VrNToyyOuut1fEtUh1NIPNpu', 
 2, true, '2025-12-12')

ON CONFLICT (email) DO NOTHING;

-- Resetear la secuencia de usuarios al valor actual máximo
SELECT setval('usuarios_id_usuario_seq', (SELECT MAX(id_usuario) FROM usuarios));

-- ========================================
-- 4. VERIFICACIÓN
-- ========================================
-- Mostrar resumen de datos insertados
SELECT 
    'ROLES INSERTADOS' as tipo,
    COUNT(*) as total
FROM roles
UNION ALL
SELECT 
    'USUARIOS ACTIVOS' as tipo,
    COUNT(*) as total
FROM usuarios
WHERE activo = true
UNION ALL
SELECT 
    'USUARIOS INACTIVOS' as tipo,
    COUNT(*) as total
FROM usuarios
WHERE activo = false
UNION ALL
SELECT 
    'TOTAL USUARIOS' as tipo,
    COUNT(*) as total
FROM usuarios;

-- Mostrar distribución de usuarios por rol
SELECT 
    r.nombre as rol,
    COUNT(u.id_usuario) as cantidad_usuarios,
    STRING_AGG(u.email, ', ' ORDER BY u.email) as emails
FROM roles r
LEFT JOIN usuarios u ON r.id_rol = u.rol_id
GROUP BY r.id_rol, r.nombre
ORDER BY r.id_rol;

-- ========================================
-- NOTAS IMPORTANTES:
-- ========================================
-- 
-- USUARIOS POR ROL:
-- - Administradores (4): admin@sacra360.com, diego.moron@ucb.edu.bo, 
--                        diego.moras@gmail.com, superadmin@sacra360.com
-- - Digitalizadores (3): revisor@sacra360.com, intento@sacra.com, 
--                        consultor1@sacra360.com
-- - Validadores (1): digitalizador@sacra360.com
-- - Usuarios (2): consultor@sacra360.com, admin4@sacra360.com (inactivo)
--
-- SEGURIDAD:
-- - Todas las contraseñas están hasheadas con bcrypt (12 rounds)
-- - Los hashes son seguros y no pueden revertirse
-- - Para resetear contraseñas, generar nuevos hashes con bcrypt
--
-- PARA TESTING:
-- Puedes usar cualquiera de estos emails con sus contraseñas originales
-- (contactar al administrador del sistema para obtener las contraseñas)
--
-- ========================================

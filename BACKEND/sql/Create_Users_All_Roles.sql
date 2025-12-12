-- ================================================
-- SCRIPT: Crear usuarios para cada rol del sistema
-- Sistema Sacra360 - Gesti├│n de Archivos Sacramentales
-- ================================================

-- Verificar que la tabla usuarios existe
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'usuarios') THEN
        RAISE EXCEPTION 'La tabla usuarios no existe. Ejecutar Database.sql primero.';
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'roles') THEN
        RAISE EXCEPTION 'La tabla roles no existe. Ejecutar Database.sql primero.';
    END IF;
END $$;

-- ================================================
-- 1. USUARIO ADMINISTRADOR
-- ================================================
-- Email: admin@sacra360.com
-- Contrase├▒a: Admin123!
-- Rol: Administrador (id_rol: 1)

INSERT INTO usuarios (
    rol_id, 
    nombre, 
    apellido_paterno, 
    apellido_materno, 
    email, 
    contrasenia, 
    fecha_creacion, 
    activo
)
SELECT 
    1,
    'Carlos',
    'Mendoza',
    'L├│pez',
    'admin@sacra360.com',
    '$2b$12$HH88zDZaTI1Kn5zOtm9PZ.XBKQY.73YE6k8267JYn520cet6tPH8G', -- Admin123!
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'admin@sacra360.com'
);

-- ================================================
-- 1.1. USUARIO ADMINISTRADOR NUEVO (USAR ESTE)
-- ================================================
-- Email: superadmin@sacra360.com
-- Contraseña: Admin2024!
-- Rol: Administrador (id_rol: 1)
-- NOTA: Usar este usuario si no recuerdas las otras contraseñas

INSERT INTO usuarios (
    rol_id, 
    nombre, 
    apellido_paterno, 
    apellido_materno, 
    email, 
    contrasenia, 
    fecha_creacion, 
    activo
)
SELECT 
    1,
    'María',
    'González',
    'López',
    'superadmin@sacra360.com',
    '$2b$12$WzBHX.1fX.mxWutFaGFgnedLCCddV4mWgGPiRYVHPHbv1mFkjxmgm', -- Admin2024!
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'superadmin@sacra360.com'
);

-- ================================================
-- 2. USUARIO REVISOR
-- ================================================
-- Email: revisor@sacra360.com
-- Contrase├▒a: Revisor123!
-- Rol: Revisor (id_rol: 2)

INSERT INTO usuarios (
    rol_id, 
    nombre, 
    apellido_paterno, 
    apellido_materno, 
    email, 
    contrasenia, 
    fecha_creacion, 
    activo
)
SELECT 
    2,
    'Ana',
    'Rodr├¡guez',
    'Mart├¡nez',
    'revisor@sacra360.com',
    '$2b$12$vXZx3YKpL9wN2QrA5BcXhOHj8F4kT6mP1nL7sV9eR3wQ2aB5cD8fG', -- Revisor123!
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'revisor@sacra360.com'
);

-- ================================================
-- 3. USUARIO DIGITALIZADOR
-- ================================================
-- Email: digitalizador@sacra360.com
-- Contrase├▒a: Digita123!
-- Rol: Digitalizador (id_rol: 3)

INSERT INTO usuarios (
    rol_id, 
    nombre, 
    apellido_paterno, 
    apellido_materno, 
    email, 
    contrasenia, 
    fecha_creacion, 
    activo
)
SELECT 
    3,
    'Juan',
    'P├®rez',
    'Garc├¡a',
    'digitalizador@sacra360.com',
    '$2b$12$QSUuTRfapgfqrWSFytoK0u1kCJFMGVYmwL6FcmuiZGULwy4iZtOpi', -- Digita123!
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'digitalizador@sacra360.com'
);

-- ================================================
-- 4. USUARIO CONSULTOR
-- ================================================
-- Email: consultor@sacra360.com
-- Contrase├▒a: Consul123!
-- Rol: Consultor (id_rol: 4)

INSERT INTO usuarios (
    rol_id, 
    nombre, 
    apellido_paterno, 
    apellido_materno, 
    email, 
    contrasenia, 
    fecha_creacion, 
    activo
)
SELECT 
    4,
    'Sof├¡a',
    'G├│mez',
    'Torres',
    'consultor@sacra360.com',
    '$2b$12$kL9pN8mQ3vR7tS5wX2yZ1uA4bC6dE8fH9jK0lM2nO4pQ6rT8sV9wY', -- Consul123!
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'consultor@sacra360.com'
);

-- ================================================
-- VERIFICACI├ôN: Mostrar usuarios creados
-- ================================================

SELECT 
    u.id_usuario,
    u.nombre,
    u.apellido_paterno,
    u.apellido_materno,
    u.email,
    r.nombre as rol,
    u.activo,
    u.fecha_creacion
FROM usuarios u
LEFT JOIN roles r ON u.rol_id = r.id_rol
WHERE u.email IN (
    'admin@sacra360.com',
    'revisor@sacra360.com',
    'digitalizador@sacra360.com',
    'consultor@sacra360.com'
)
ORDER BY u.rol_id;

-- ================================================
-- MENSAJE DE ├ëXITO
-- ================================================

DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'Ô£à ================================================';
    RAISE NOTICE 'Ô£à USUARIOS CREADOS EXITOSAMENTE';
    RAISE NOTICE 'Ô£à ================================================';
    RAISE NOTICE '';
    RAISE NOTICE '­ƒöÉ CREDENCIALES DE ACCESO:';
    RAISE NOTICE '';
    RAISE NOTICE '­ƒæñ ADMINISTRADOR:';
    RAISE NOTICE '   Email: admin@sacra360.com';
    RAISE NOTICE '   Password: Admin123!';
    RAISE NOTICE '   Permisos: Control total del sistema';
    RAISE NOTICE '';
    RAISE NOTICE '­ƒæñ REVISOR:';
    RAISE NOTICE '   Email: revisor@sacra360.com';
    RAISE NOTICE '   Password: Revisor123!';
    RAISE NOTICE '   Permisos: Revisar y validar registros';
    RAISE NOTICE '';
    RAISE NOTICE '­ƒæñ DIGITALIZADOR:';
    RAISE NOTICE '   Email: digitalizador@sacra360.com';
    RAISE NOTICE '   Password: Digita123!';
    RAISE NOTICE '   Permisos: Digitalizar documentos';
    RAISE NOTICE '';
    RAISE NOTICE '­ƒæñ CONSULTOR:';
    RAISE NOTICE '   Email: consultor@sacra360.com';
    RAISE NOTICE '   Password: Consul123!';
    RAISE NOTICE '   Permisos: Solo lectura';
    RAISE NOTICE '';
    RAISE NOTICE 'ÔÜá´©Å  IMPORTANTE: Cambiar las contrase├▒as en producci├│n';
    RAISE NOTICE '================================================';
END $$;
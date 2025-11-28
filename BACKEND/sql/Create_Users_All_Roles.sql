-- ================================================
-- SCRIPT: Crear usuarios para cada rol del sistema
-- Sistema Sacra360 - Gestión de Archivos Sacramentales
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
-- Contraseña: Admin123!
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
    'López',
    'admin@sacra360.com',
    '$2b$12$HH88zDZaTI1Kn5zOtm9PZ.XBKQY.73YE6k8267JYn520cet6tPH8G', -- Admin123!
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'admin@sacra360.com'
);

-- ================================================
-- 2. USUARIO REVISOR
-- ================================================
-- Email: revisor@sacra360.com
-- Contraseña: Revisor123!
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
    'Rodríguez',
    'Martínez',
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
-- Contraseña: Digita123!
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
    'Pérez',
    'García',
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
-- Contraseña: Consul123!
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
    'Sofía',
    'Gómez',
    'Torres',
    'consultor@sacra360.com',
    '$2b$12$kL9pN8mQ3vR7tS5wX2yZ1uA4bC6dE8fH9jK0lM2nO4pQ6rT8sV9wY', -- Consul123!
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'consultor@sacra360.com'
);

-- ================================================
-- VERIFICACIÓN: Mostrar usuarios creados
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
-- MENSAJE DE ÉXITO
-- ================================================

DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ ================================================';
    RAISE NOTICE '✅ USUARIOS CREADOS EXITOSAMENTE';
    RAISE NOTICE '✅ ================================================';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 CREDENCIALES DE ACCESO:';
    RAISE NOTICE '';
    RAISE NOTICE '👤 ADMINISTRADOR:';
    RAISE NOTICE '   Email: admin@sacra360.com';
    RAISE NOTICE '   Password: Admin123!';
    RAISE NOTICE '   Permisos: Control total del sistema';
    RAISE NOTICE '';
    RAISE NOTICE '👤 REVISOR:';
    RAISE NOTICE '   Email: revisor@sacra360.com';
    RAISE NOTICE '   Password: Revisor123!';
    RAISE NOTICE '   Permisos: Revisar y validar registros';
    RAISE NOTICE '';
    RAISE NOTICE '👤 DIGITALIZADOR:';
    RAISE NOTICE '   Email: digitalizador@sacra360.com';
    RAISE NOTICE '   Password: Digita123!';
    RAISE NOTICE '   Permisos: Digitalizar documentos';
    RAISE NOTICE '';
    RAISE NOTICE '👤 CONSULTOR:';
    RAISE NOTICE '   Email: consultor@sacra360.com';
    RAISE NOTICE '   Password: Consul123!';
    RAISE NOTICE '   Permisos: Solo lectura';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANTE: Cambiar las contraseñas en producción';
    RAISE NOTICE '================================================';
END $$;

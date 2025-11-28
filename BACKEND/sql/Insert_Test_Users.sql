-- ================================================
-- SCRIPT: Crear usuario administrador de prueba
-- ================================================

-- Verificar que la tabla usuarios existe
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'usuarios') THEN
        RAISE EXCEPTION 'La tabla usuarios no existe. Ejecutar Database.sql primero.';
    END IF;
END $$;

-- Insertar usuario administrador si no existe
-- Email: admin@sacra360.com
-- Contraseña: admin123 (hash bcrypt)
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
    1, -- rol_id (Administrador)
    'Admin',
    'Sistema',
    'Sacra360',
    'admin@sacra360.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyJJb3hA7YDe', -- admin123
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'admin@sacra360.com'
);

-- Insertar usuario de prueba digitalizador
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
    3, -- rol_id (Digitalizador)
    'Juan',
    'Pérez',
    'García',
    'digitalizador@sacra360.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyJJb3hA7YDe', -- admin123
    CURRENT_DATE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'digitalizador@sacra360.com'
);

-- Verificar usuarios creados
SELECT 
    id_usuario,
    nombre,
    apellido_paterno,
    apellido_materno,
    email,
    rol_id,
    activo
FROM usuarios
WHERE email IN ('admin@sacra360.com', 'digitalizador@sacra360.com');

-- Mensaje de éxito
DO $$ 
BEGIN
    RAISE NOTICE '✅ Usuarios de prueba creados exitosamente';
    RAISE NOTICE 'Email: admin@sacra360.com | Contraseña: admin123';
    RAISE NOTICE 'Email: digitalizador@sacra360.com | Contraseña: admin123';
END $$;

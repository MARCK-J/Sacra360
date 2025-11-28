-- =====================================================
-- SCHEMA DE AUTENTICACIÓN Y USUARIOS - SACRA360
-- =====================================================

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    rol VARCHAR(20) DEFAULT 'usuario' CHECK (rol IN ('administrador', 'digitalizador', 'validador', 'usuario')),
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Perfiles (información adicional del usuario)
CREATE TABLE IF NOT EXISTS perfiles (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    telefono VARCHAR(20),
    direccion TEXT,
    foto_perfil VARCHAR(255),
    biografia TEXT,
    fecha_nacimiento DATE,
    genero VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Sesiones (para gestionar tokens y sesiones activas)
CREATE TABLE IF NOT EXISTS sesiones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    refresh_token VARCHAR(500),
    ip_address VARCHAR(45),
    user_agent TEXT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Auditoría de Accesos
CREATE TABLE IF NOT EXISTS auditoria_accesos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    accion VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    exitoso BOOLEAN DEFAULT TRUE,
    mensaje TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_sesiones_token ON sesiones(token);
CREATE INDEX IF NOT EXISTS idx_sesiones_usuario ON sesiones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria_accesos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria_accesos(fecha);

-- Trigger para actualizar fecha_actualizacion
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_perfiles_updated_at BEFORE UPDATE ON perfiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Usuario administrador por defecto (password: admin123)
-- Hash generado con bcrypt
INSERT INTO usuarios (username, email, password_hash, nombre, apellido, rol, estado)
VALUES (
    'admin',
    'admin@sacra360.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyJJb3hA7YDe',
    'Administrador',
    'Sistema',
    'administrador',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Crear perfil para el administrador
INSERT INTO perfiles (usuario_id)
SELECT id FROM usuarios WHERE username = 'admin'
ON CONFLICT DO NOTHING;

-- Comentarios en las tablas
COMMENT ON TABLE usuarios IS 'Tabla principal de usuarios del sistema';
COMMENT ON TABLE perfiles IS 'Información adicional del perfil de usuario';
COMMENT ON TABLE sesiones IS 'Gestión de sesiones y tokens activos';
COMMENT ON TABLE auditoria_accesos IS 'Registro de auditoría de accesos al sistema';

COMMENT ON COLUMN usuarios.rol IS 'Roles: administrador, digitalizador, validador, usuario';
COMMENT ON COLUMN usuarios.estado IS 'TRUE = activo, FALSE = desactivado';

-- Script de inicialización para PostgreSQL - Sacra360 Microservicios
-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================
-- ESQUEMAS POR MICROSERVICIO
-- ==========================

-- Esquema para AuthProfiles Service
CREATE SCHEMA IF NOT EXISTS auth;

-- Esquema para Documents Service  
CREATE SCHEMA IF NOT EXISTS documents;

-- Esquema para File Storage Service
CREATE SCHEMA IF NOT EXISTS files;

-- Esquema para procesamiento (OCR, HTR, AI)
CREATE SCHEMA IF NOT EXISTS processing;

-- Esquema para Reports Service
CREATE SCHEMA IF NOT EXISTS reports;

-- ==========================
-- TABLAS AUTH SERVICE
-- ==========================

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sesiones
CREATE TABLE IF NOT EXISTS auth.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Tabla de permisos
CREATE TABLE IF NOT EXISTS auth.permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de roles y permisos
CREATE TABLE IF NOT EXISTS auth.role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role VARCHAR(50) NOT NULL,
    permission_id UUID REFERENCES auth.permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role, permission_id)
);

-- ==========================
-- TABLAS DOCUMENTS SERVICE
-- ==========================

-- Tabla de personas
CREATE TABLE IF NOT EXISTS documents.persons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(200) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    document_number VARCHAR(20) NOT NULL,
    document_type VARCHAR(20) DEFAULT 'cedula',
    birth_date DATE NOT NULL,
    birth_place VARCHAR(200) NOT NULL,
    nationality VARCHAR(100) DEFAULT 'Colombiana',
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_number, document_type)
);

-- Tabla de diócesis
CREATE TABLE IF NOT EXISTS documents.dioceses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    bishop_name VARCHAR(200),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    founded_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de parroquias
CREATE TABLE IF NOT EXISTS documents.parishes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    diocese_id UUID REFERENCES documents.dioceses(id),
    founded_date DATE,
    patron_saint VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sacerdotes
CREATE TABLE IF NOT EXISTS documents.priests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- Referencia a auth.users
    person_id UUID REFERENCES documents.persons(id),
    ordination_date DATE NOT NULL,
    parish_id UUID REFERENCES documents.parishes(id),
    diocese_id UUID REFERENCES documents.dioceses(id),
    rank VARCHAR(50) DEFAULT 'priest',
    specializations TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla principal de documentos
CREATE TABLE IF NOT EXISTS documents.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    parish_id UUID REFERENCES documents.parishes(id),
    priest_id UUID REFERENCES documents.priests(id),
    diocese_id UUID REFERENCES documents.dioceses(id),
    sacrament_type VARCHAR(50),
    sacrament_date TIMESTAMP WITH TIME ZONE,
    book_number VARCHAR(20),
    page_number VARCHAR(20),
    record_number VARCHAR(20),
    participants UUID[],
    metadata JSONB DEFAULT '{}',
    file_paths TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    last_modified_by UUID,
    reviewed_by UUID,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE
);

-- Tablas específicas de sacramentos
CREATE TABLE IF NOT EXISTS documents.baptisms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents.documents(id) ON DELETE CASCADE,
    person_id UUID REFERENCES documents.persons(id),
    father_id UUID REFERENCES documents.persons(id),
    mother_id UUID REFERENCES documents.persons(id),
    godfather_id UUID REFERENCES documents.persons(id),
    godmother_id UUID REFERENCES documents.persons(id),
    baptism_date TIMESTAMP WITH TIME ZONE NOT NULL,
    baptism_place VARCHAR(200) NOT NULL,
    book_number VARCHAR(20) NOT NULL,
    page_number VARCHAR(20) NOT NULL,
    record_number VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents.marriages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents.documents(id) ON DELETE CASCADE,
    groom_id UUID REFERENCES documents.persons(id),
    bride_id UUID REFERENCES documents.persons(id),
    marriage_date TIMESTAMP WITH TIME ZONE NOT NULL,
    marriage_place VARCHAR(200) NOT NULL,
    civil_marriage_date DATE,
    civil_marriage_place VARCHAR(200),
    witness_1_id UUID REFERENCES documents.persons(id),
    witness_2_id UUID REFERENCES documents.persons(id),
    book_number VARCHAR(20) NOT NULL,
    page_number VARCHAR(20) NOT NULL,
    record_number VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents.deaths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents.documents(id) ON DELETE CASCADE,
    person_id UUID REFERENCES documents.persons(id),
    death_date TIMESTAMP WITH TIME ZONE NOT NULL,
    death_place VARCHAR(200) NOT NULL,
    death_cause TEXT,
    marital_status VARCHAR(50),
    spouse_id UUID REFERENCES documents.persons(id),
    burial_date DATE,
    cemetery VARCHAR(200),
    informant_name VARCHAR(200),
    informant_relationship VARCHAR(100),
    book_number VARCHAR(20) NOT NULL,
    page_number VARCHAR(20) NOT NULL,
    record_number VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- TABLAS FILE STORAGE SERVICE
-- ==========================

CREATE TABLE IF NOT EXISTS files.document_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    is_original BOOLEAN DEFAULT false,
    is_processed BOOLEAN DEFAULT false,
    ocr_text TEXT,
    htr_text TEXT,
    ai_metadata JSONB DEFAULT '{}',
    uploaded_by UUID,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- TABLAS PROCESSING SERVICES
-- ==========================

CREATE TABLE IF NOT EXISTS processing.ocr_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES files.document_files(id),
    status VARCHAR(50) DEFAULT 'pending',
    language VARCHAR(10) DEFAULT 'spa',
    confidence_threshold DECIMAL(3,2) DEFAULT 0.80,
    extracted_text TEXT,
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS processing.htr_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES files.document_files(id),
    model_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    extracted_text TEXT,
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS processing.ai_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES files.document_files(id),
    job_type VARCHAR(50) NOT NULL, -- completion, analysis, extraction
    model_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ==========================
-- ÍNDICES PARA RENDIMIENTO
-- ==========================

-- Índices para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON auth.users(username);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON auth.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON auth.user_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_persons_document ON documents.persons(document_number, document_type);
CREATE INDEX IF NOT EXISTS idx_persons_full_name ON documents.persons USING gin(full_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents.documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents.documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_parish ON documents.documents(parish_id);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents.documents(created_at);

CREATE INDEX IF NOT EXISTS idx_files_document_id ON files.document_files(document_id);
CREATE INDEX IF NOT EXISTS idx_files_type ON files.document_files(file_type);

-- ==========================
-- DATOS INICIALES
-- ==========================

-- Insertar permisos básicos
INSERT INTO auth.permissions (name, description, resource, action) VALUES 
('documents_read_all', 'Leer todos los documentos', 'documents', 'read'),
('documents_write_all', 'Escribir todos los documentos', 'documents', 'write'),
('documents_delete_all', 'Eliminar todos los documentos', 'documents', 'delete'),
('users_manage', 'Gestionar usuarios', 'users', 'manage'),
('reports_read', 'Ver reportes', 'reports', 'read'),
('system_admin', 'Administración del sistema', 'system', 'admin')
ON CONFLICT (name) DO NOTHING;

-- Insertar diócesis por defecto
INSERT INTO documents.dioceses (name, bishop_name, address) VALUES 
('Arzobispado Metropolitano', 'Mons. Juan Carlos Pérez', 'Carrera 7 # 10-20, Centro Histórico')
ON CONFLICT DO NOTHING;

-- Insertar parroquia por defecto
INSERT INTO documents.parishes (name, address, diocese_id) VALUES 
('Parroquia San José', 'Calle Principal 123, Barrio Centro', 
 (SELECT id FROM documents.dioceses WHERE name = 'Arzobispado Metropolitano' LIMIT 1))
ON CONFLICT DO NOTHING;

-- Insertar usuario administrador por defecto
INSERT INTO auth.users (email, username, hashed_password, full_name, role, is_superuser) VALUES 
('admin@sacra360.com', 'admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Administrador del Sistema', 'archbishop', true)
ON CONFLICT (email) DO NOTHING;
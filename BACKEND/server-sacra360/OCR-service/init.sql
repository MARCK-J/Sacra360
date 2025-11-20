-- Script de inicialización de base de datos para OCR Service
-- Se ejecuta automáticamente al crear el contenedor de PostgreSQL

-- Crear tablas necesarias para OCR Service
CREATE TABLE IF NOT EXISTS documento_digitalizado (
    id_documento SERIAL PRIMARY KEY,
    libros_id INTEGER NOT NULL,
    tipo_sacramento INTEGER,
    imagen_url TEXT NOT NULL,
    ocr_texto TEXT NOT NULL,
    modelo_fuente VARCHAR(100) NOT NULL,
    confianza DECIMAL(4,3) NOT NULL,
    fecha_procesamiento TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ocr_resultado (
    id_ocr SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documento_digitalizado(id_documento),
    campo VARCHAR(50) NOT NULL,
    valor_extraido TEXT NOT NULL,
    confianza DECIMAL(4,3) NOT NULL,
    fuente_modelo VARCHAR(100) NOT NULL,
    validado BOOLEAN NOT NULL DEFAULT FALSE
);

-- Insertar datos de prueba
INSERT INTO documento_digitalizado (libros_id, tipo_sacramento, imagen_url, ocr_texto, modelo_fuente, confianza, fecha_procesamiento)
VALUES (1, 2, 'test_image.jpg', '{"test": "data"}', 'Test_Model', 0.95, NOW())
ON CONFLICT DO NOTHING;

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_documento_libros ON documento_digitalizado(libros_id);
CREATE INDEX IF NOT EXISTS idx_ocr_documento ON ocr_resultado(documento_id);
CREATE INDEX IF NOT EXISTS idx_ocr_campo ON ocr_resultado(campo);

-- Comentarios
COMMENT ON TABLE documento_digitalizado IS 'Documentos procesados por OCR';
COMMENT ON TABLE ocr_resultado IS 'Campos individuales extraídos por OCR';
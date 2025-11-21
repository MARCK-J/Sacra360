-- Migración para agregar soporte de validación de tuplas OCR
-- Fecha: 2025-11-20
-- Descripción: Agrega campos para rastrear tuplas y su proceso de validación

-- 1. Agregar columnas a ocr_resultado para tuplas
ALTER TABLE ocr_resultado 
ADD COLUMN tupla_numero int NOT NULL DEFAULT 1,
ADD COLUMN estado_validacion varchar(20) NOT NULL DEFAULT 'pendiente',
ADD COLUMN sacramento_id int NULL;

-- 2. Crear tabla validacion_tuplas
CREATE TABLE validacion_tuplas (
    id_validacion serial NOT NULL,
    documento_id int NOT NULL,
    tupla_numero int NOT NULL,
    estado varchar(20) NOT NULL DEFAULT 'pendiente',
    usuario_validador_id int NULL,
    fecha_validacion timestamp NULL,
    sacramento_registrado_id int NULL,
    observaciones text NULL,
    CONSTRAINT validacion_tuplas_pk PRIMARY KEY (id_validacion)
);

-- 3. Agregar foreign keys
ALTER TABLE ocr_resultado 
ADD CONSTRAINT ocr_resultado_sacramentos
    FOREIGN KEY (sacramento_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE;

ALTER TABLE validacion_tuplas 
ADD CONSTRAINT validacion_tuplas_documento
    FOREIGN KEY (documento_id)
    REFERENCES documento_digitalizado (id_documento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE;

ALTER TABLE validacion_tuplas 
ADD CONSTRAINT validacion_tuplas_usuario
    FOREIGN KEY (usuario_validador_id)
    REFERENCES usuarios (id_usuario)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE;

ALTER TABLE validacion_tuplas 
ADD CONSTRAINT validacion_tuplas_sacramento
    FOREIGN KEY (sacramento_registrado_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE;

-- 4. Crear índices para mejorar rendimiento
CREATE INDEX idx_ocr_resultado_tupla ON ocr_resultado(documento_id, tupla_numero);
CREATE INDEX idx_ocr_resultado_estado ON ocr_resultado(estado_validacion);
CREATE INDEX idx_validacion_tuplas_documento ON validacion_tuplas(documento_id);
CREATE INDEX idx_validacion_tuplas_estado ON validacion_tuplas(estado);

-- 5. Actualizar datos existentes
-- Agrupar resultados OCR existentes por tuplas basándose en el patrón de nombres
-- Los campos que terminan en "_tupla_X" ya tienen el número de tupla
UPDATE ocr_resultado 
SET tupla_numero = COALESCE(
    CAST(SUBSTRING(campo FROM '_tupla_([0-9]+)$') AS INTEGER), 
    1
);

-- 6. Crear registros en validacion_tuplas para documentos existentes
INSERT INTO validacion_tuplas (documento_id, tupla_numero, estado)
SELECT DISTINCT 
    documento_id, 
    tupla_numero,
    'pendiente'
FROM ocr_resultado 
WHERE documento_id IS NOT NULL
ON CONFLICT DO NOTHING;

-- 7. Comentarios sobre estados
COMMENT ON COLUMN ocr_resultado.estado_validacion IS 'Estados: pendiente, validado, corregido, registrado';
COMMENT ON COLUMN validacion_tuplas.estado IS 'Estados: pendiente, en_validacion, validado, registrado, rechazado';
COMMENT ON TABLE validacion_tuplas IS 'Tabla para gestionar el proceso de validación tupla por tupla de resultados OCR';
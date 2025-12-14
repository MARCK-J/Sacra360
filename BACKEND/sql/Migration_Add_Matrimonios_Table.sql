-- Migración: Agregar tabla matrimonios para soportar registro de matrimonios
-- Fecha: 2024-11-30

BEGIN;

-- Crear tabla matrimonios
CREATE TABLE IF NOT EXISTS matrimonios (
    id_matrimonio serial  NOT NULL,
    sacramento_id int  NOT NULL,
    esposo_id int  NOT NULL,
    esposa_id int  NOT NULL,
    nombre_padre_esposo varchar(100)  NOT NULL,
    nombre_madre_esposo varchar(100)  NOT NULL,
    nombre_padre_esposa varchar(100)  NOT NULL,
    nombre_madre_esposa varchar(100)  NOT NULL,
    testigos varchar(200)  NOT NULL,
    CONSTRAINT matrimonios_pk PRIMARY KEY (id_matrimonio),
    CONSTRAINT matrimonios_sacramento_unico UNIQUE (sacramento_id)
);

-- Agregar foreign keys
ALTER TABLE matrimonios ADD CONSTRAINT matrimonios_sacramentos
    FOREIGN KEY (sacramento_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

ALTER TABLE matrimonios ADD CONSTRAINT matrimonios_esposo
    FOREIGN KEY (esposo_id)
    REFERENCES personas (id_persona)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

ALTER TABLE matrimonios ADD CONSTRAINT matrimonios_esposa
    FOREIGN KEY (esposa_id)
    REFERENCES personas (id_persona)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

COMMIT;

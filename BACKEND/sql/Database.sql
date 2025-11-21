-- Created by Redgate Data Modeler (https://datamodeler.redgate-platform.com)
-- Last modification date: 2025-09-24 21:23:56.179

-- tables
-- Table: Auditoria
CREATE TABLE Auditoria (
    id_auditoria serial  NOT NULL,
    usuario_id int  NOT NULL,
    accion text  NOT NULL,
    registro_afectado text  NOT NULL,
    Id_registro int  NOT NULL,
    fecha timestamp  NOT NULL,
    CONSTRAINT Auditoria_pk PRIMARY KEY (id_auditoria)
);

-- Table: InstitucionesParroquias
CREATE TABLE InstitucionesParroquias (
    id_institucion serial  NOT NULL,
    nombre varchar(100)  NOT NULL,
    direccion varchar(150)  NULL,
    telefono varchar(15)  NULL,
    email varchar(100)  NULL,
    CONSTRAINT InstitucionesParroquias_pk PRIMARY KEY (id_institucion)
);

-- Table: Roles
CREATE TABLE Roles (
    id_rol serial  NOT NULL,
    nombre varchar(50)  NOT NULL,
    descripcion text  NULL,
    CONSTRAINT Roles_pk PRIMARY KEY (id_rol)
);

-- Table: correccion_documento
CREATE TABLE correccion_documento (
    id_correccion serial  NOT NULL,
    ocr_resultado_id int  NOT NULL,
    usuario_id int  NOT NULL,
    valor_original text  NOT NULL,
    valor_corregido text  NOT NULL,
    fecha timestamp  NOT NULL,
    CONSTRAINT correccion_documento_pk PRIMARY KEY (id_correccion)
);

-- Table: detalles_bautizo
CREATE TABLE detalles_bautizo (
    id_bautizo serial  NOT NULL,
    sacramento_id int  NOT NULL,
    padrino varchar(100)  NOT NULL,
    ministro varchar(100)  NOT NULL,
    foja varchar(10)  NOT NULL,
    numero varchar(10)  NOT NULL,
    fecha_bautizo date  NOT NULL,
    CONSTRAINT Detalle_bautizo_pk PRIMARY KEY (id_bautizo)
);

-- Table: detalles_confirmacion
CREATE TABLE detalles_confirmacion (
    id_confirmacion serial  NOT NULL,
    sacramento_id int  NOT NULL,
    padrino varchar(100)  NOT NULL,
    ministro varchar(100)  NOT NULL,
    foja varchar(10)  NOT NULL,
    numero varchar(10)  NOT NULL,
    fecha_confirmacion date  NOT NULL,
    CONSTRAINT Detalle_confirmacion_pk PRIMARY KEY (id_confirmacion)
);

-- Table: detalles_matrimonio
CREATE TABLE detalles_matrimonio (
    id_matrimonio serial  NOT NULL,
    sacramento_id int  NOT NULL,
    nombre_esposo varchar(100)  NOT NULL,
    nombre_esposa varchar(100)  NOT NULL,
    apellido_peterno_esposo varchar(50)  NOT NULL,
    apellido_materno_esposo varchar(50)  NOT NULL,
    apellido_peterno_esposa varchar(50)  NOT NULL,
    apellido_materno_esposa varchar(50)  NOT NULL,
    nombre_padre_esposo varchar(100)  NOT NULL,
    nombre_madre_esposo varchar(100)  NOT NULL,
    nombre_padre_esposa varchar(100)  NOT NULL,
    nombre_madre_esposa varchar(100)  NOT NULL,
    padrino varchar(100)  NOT NULL,
    ministro varchar(100)  NOT NULL,
    foja varchar(10)  NOT NULL,
    numero varchar(10)  NOT NULL,
    reg_civil varchar(100)  NOT NULL,
    fecha_matrimonio date  NOT NULL,
    lugar_matrimonio varchar(100)  NOT NULL,
    CONSTRAINT Detalle_matrimonio_pk PRIMARY KEY (id_matrimonio)
);

-- Table: documento_digitalizado
CREATE TABLE documento_digitalizado (
    id_documento serial  NOT NULL,
    libros_id int  NOT NULL,
    tipo_sacramento int  NULL,
    imagen_url text  NOT NULL,
    ocr_texto text  NOT NULL,
    modelo_fuente varchar(100)  NOT NULL,
    confianza decimal(4,3)  NOT NULL,
    fecha_procesamiento timestamp  NOT NULL,
    CONSTRAINT documento_digitalizado_pk PRIMARY KEY (id_documento)
);

-- Table: libros
CREATE TABLE libros (
    id_libro serial  NOT NULL,
    nombre varchar(50)  NOT NULL,
    fecha_inicio date  NOT NULL,
    fecha_fin date  NOT NULL,
    observaciones text  NULL,
    CONSTRAINT Libros_pk PRIMARY KEY (id_libro)
);

-- Table: ocr_resultado
CREATE TABLE ocr_resultado (
    id_ocr serial  NOT NULL,
    documento_id int  NOT NULL,
    campo varchar(50)  NOT NULL,
    valor_extraido text  NOT NULL,
    confianza decimal(4,3)  NOT NULL,
    fuente_modelo varchar(100)  NOT NULL,
    validado boolean  NOT NULL,
    tupla_numero int  NOT NULL DEFAULT 1,
    estado_validacion varchar(20)  NOT NULL DEFAULT 'pendiente',
    sacramento_id int  NULL,
    CONSTRAINT ocr_resultado_pk PRIMARY KEY (id_ocr)
);

-- Table: personas
CREATE TABLE personas (
    id_persona serial  NOT NULL,
    nombres varchar(100)  NOT NULL,
    apellido_paterno varchar(50)  NOT NULL,
    apellido_materno varchar(50)  NOT NULL,
    fecha_nacimiento date  NOT NULL,
    lugar_nacimiento varchar(100)  NOT NULL,
    nombre_padre varchar(100)  NOT NULL,
    nombre_madre varchar(100)  NOT NULL,
    CONSTRAINT personas_pk PRIMARY KEY (id_persona)
);

-- Table: sacramentos
CREATE TABLE sacramentos (
    id_sacramento serial  NOT NULL,
    persona_id int  NOT NULL,
    tipo_id int  NOT NULL,
    usuario_id int  NOT NULL,
    institucion_id int  NOT NULL,
    libro_id int  NOT NULL,
    fecha_sacramento date  NOT NULL,
    fecha_registro timestamp  NOT NULL,
    fecha_actualizacion timestamp  NOT NULL,
    CONSTRAINT sacramentos_pk PRIMARY KEY (id_sacramento)
);

-- Table: tipos_sacramentos
CREATE TABLE tipos_sacramentos (
    id_tipo serial  NOT NULL,
    nombre varchar(50)  NOT NULL,
    descripcion text  NULL,
    CONSTRAINT Tipos_sacramentos_pk PRIMARY KEY (id_tipo)
);

-- Table: usuarios
CREATE TABLE usuarios (
    id_usuario serial  NOT NULL,
    rol_id int  NOT NULL,
    nombre varchar(50)  NOT NULL,
    apellido_paterno varchar(50)  NOT NULL,
    apellido_materno varchar(50)  NOT NULL,
    email varchar(100)  NOT NULL,
    contrasenia text  NOT NULL,
    fecha_creacion date  NOT NULL,
    activo boolean  NOT NULL,
    CONSTRAINT Usuarios_pk PRIMARY KEY (id_usuario)
);

-- Table: validacion_tuplas
CREATE TABLE validacion_tuplas (
    id_validacion serial  NOT NULL,
    documento_id int  NOT NULL,
    tupla_numero int  NOT NULL,
    estado varchar(20)  NOT NULL DEFAULT 'pendiente',
    usuario_validador_id int  NULL,
    fecha_validacion timestamp  NULL,
    sacramento_registrado_id int  NULL,
    observaciones text  NULL,
    CONSTRAINT validacion_tuplas_pk PRIMARY KEY (id_validacion)
);

-- foreign keys
-- Reference: Auditoria_Usuarios (table: Auditoria)
ALTER TABLE Auditoria ADD CONSTRAINT Auditoria_Usuarios
    FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id_usuario)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Detalle_confirmacion_sacramentos (table: detalles_confirmacion)
ALTER TABLE detalles_confirmacion ADD CONSTRAINT Detalle_confirmacion_sacramentos
    FOREIGN KEY (sacramento_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Detalle_matrimonio_sacramentos (table: detalles_matrimonio)
ALTER TABLE detalles_matrimonio ADD CONSTRAINT Detalle_matrimonio_sacramentos
    FOREIGN KEY (sacramento_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: correccion_documento_ocr_resultado (table: correccion_documento)
ALTER TABLE correccion_documento ADD CONSTRAINT correccion_documento_ocr_resultado
    FOREIGN KEY (ocr_resultado_id)
    REFERENCES ocr_resultado (id_ocr)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: correccion_documento_usuarios (table: correccion_documento)
ALTER TABLE correccion_documento ADD CONSTRAINT correccion_documento_usuarios
    FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id_usuario)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: detalles_bautizo_sacramentos (table: detalles_bautizo)
ALTER TABLE detalles_bautizo ADD CONSTRAINT detalles_bautizo_sacramentos
    FOREIGN KEY (sacramento_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: documento_digitalizado_libros (table: documento_digitalizado)
ALTER TABLE documento_digitalizado ADD CONSTRAINT documento_digitalizado_libros
    FOREIGN KEY (libros_id)
    REFERENCES libros (id_libro)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: ocr_resultado_documento_digitalizado (table: ocr_resultado)
ALTER TABLE ocr_resultado ADD CONSTRAINT ocr_resultado_documento_digitalizado
    FOREIGN KEY (documento_id)
    REFERENCES documento_digitalizado (id_documento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: sacramentos_InstitucionesParroquias (table: sacramentos)
ALTER TABLE sacramentos ADD CONSTRAINT sacramentos_InstitucionesParroquias
    FOREIGN KEY (institucion_id)
    REFERENCES InstitucionesParroquias (id_institucion)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: sacramentos_libros (table: sacramentos)
ALTER TABLE sacramentos ADD CONSTRAINT sacramentos_libros
    FOREIGN KEY (libro_id)
    REFERENCES libros (id_libro)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: sacramentos_personas (table: sacramentos)
ALTER TABLE sacramentos ADD CONSTRAINT sacramentos_personas
    FOREIGN KEY (persona_id)
    REFERENCES personas (id_persona)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: sacramentos_tipos_sacramentos (table: sacramentos)
ALTER TABLE sacramentos ADD CONSTRAINT sacramentos_tipos_sacramentos
    FOREIGN KEY (tipo_id)
    REFERENCES tipos_sacramentos (id_tipo)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: sacramentos_usuarios (table: sacramentos)
ALTER TABLE sacramentos ADD CONSTRAINT sacramentos_usuarios
    FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id_usuario)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: usuarios_Roles (table: usuarios)
ALTER TABLE usuarios ADD CONSTRAINT usuarios_Roles
    FOREIGN KEY (rol_id)
    REFERENCES Roles (id_rol)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: ocr_resultado_sacramentos (table: ocr_resultado)
ALTER TABLE ocr_resultado ADD CONSTRAINT ocr_resultado_sacramentos
    FOREIGN KEY (sacramento_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: validacion_tuplas_documento (table: validacion_tuplas)
ALTER TABLE validacion_tuplas ADD CONSTRAINT validacion_tuplas_documento
    FOREIGN KEY (documento_id)
    REFERENCES documento_digitalizado (id_documento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: validacion_tuplas_usuario (table: validacion_tuplas)
ALTER TABLE validacion_tuplas ADD CONSTRAINT validacion_tuplas_usuario
    FOREIGN KEY (usuario_validador_id)
    REFERENCES usuarios (id_usuario)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: validacion_tuplas_sacramento (table: validacion_tuplas)
ALTER TABLE validacion_tuplas ADD CONSTRAINT validacion_tuplas_sacramento
    FOREIGN KEY (sacramento_registrado_id)
    REFERENCES sacramentos (id_sacramento)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.


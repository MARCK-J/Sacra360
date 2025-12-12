# INFORME DE PRÁCTICA PRE-PROFESIONAL
## SISTEMA SACRA360 - GESTIÓN DE ARCHIVOS SACRAMENTALES

---

## INTRODUCCIÓN

### Síntesis del Trabajo Realizado

La presente práctica pre-profesional se desarrolló en el marco del proyecto **Sacra360**, un sistema integral de gestión de archivos sacramentales destinado a modernizar y digitalizar los procesos de registro, búsqueda y certificación de sacramentos en instituciones religiosas. El trabajo se realizó durante el período de **Mayo a Diciembre de 2024**, acumulando un total de **213.5 horas** de práctica efectiva.

### Términos de Referencia de la Pasantía

La pasantía fue solicitada con los siguientes términos de referencia:

**Objetivo General:**
Participar en el desarrollo de un sistema web de gestión de archivos sacramentales que permita digitalizar, almacenar, buscar y generar certificados de registros sacramentales (Bautizos, Confirmaciones, Matrimonios y Defunciones).

**Objetivos Específicos:**

1. **Relevamiento de Información:** Realizar el levantamiento de información sobre los procesos actuales de registro y gestión de documentos sacramentales, identificando tipos de documentos, formatos, flujos de trabajo y actores involucrados.

2. **Análisis de Sistemas:** Analizar la infraestructura tecnológica disponible, definir los módulos requeridos del sistema, identificar tecnologías apropiadas y establecer mecanismos de autenticación y autorización.

3. **Diseño de Interfaces:** Diseñar mockups de las interfaces de usuario para todos los módulos del sistema, incluyendo gestión de usuarios, roles, permisos, digitalización de documentos, reportes y auditoría.

4. **Desarrollo Backend:** Implementar la API RESTful del sistema utilizando FastAPI, incluyendo endpoints de autenticación, gestión de usuarios, auditoría, seguridad y generación de reportes, aplicando las mejores prácticas de desarrollo y seguridad.

5. **Documentación Técnica:** Elaborar documentación técnica completa del sistema mediante diagramas UML (procesos, actividades, estados), diagramas de base de datos física y documentación de arquitectura del sistema.

6. **Desarrollo Frontend:** Implementar las interfaces de usuario del sistema utilizando React, integrando las pantallas con la API backend y asegurando una experiencia de usuario fluida y segura.

### Justificación

El proyecto Sacra360 surge de la necesidad imperante de las instituciones religiosas de contar con un sistema moderno que permita:

- **Preservación Digital:** Proteger documentos históricos mediante su digitalización, evitando el deterioro de registros físicos centenarios.

- **Eficiencia Operativa:** Reducir el tiempo de búsqueda de registros de horas a minutos mediante sistemas de búsqueda avanzada.

- **Trazabilidad y Auditoría:** Mantener un registro completo de todas las acciones realizadas en el sistema para garantizar la integridad de la información.

- **Seguridad de Datos:** Implementar controles de acceso basados en roles (RBAC) y medidas de seguridad robustas para proteger información sensible.

- **Generación Ágil de Certificados:** Automatizar la generación de certificados sacramentales con validación de datos y trazabilidad completa.

La participación en este proyecto permitió aplicar conocimientos de ingeniería de software, desarrollo web full-stack, gestión de bases de datos, seguridad informática y arquitectura de sistemas en un contexto real con impacto social directo.

### Productos y Actividades Desarrolladas

El trabajo realizado se organizó en **6 actividades principales** que generaron los siguientes productos:

#### **ACTIVIDAD 1: Relevamiento de Información y Procesos (33 horas)**
- 24 reuniones de coordinación con stakeholders (personal operativo, docentes, equipo técnico)
- Identificación de tipos de documentos: registros y certificados de Bautizo, Confirmación, Matrimonio y Defunción
- Relevamiento de formatos de documentos e índices de libros
- Identificación de áreas de usuarios: arquidiócesis, parroquias, celebrantes
- Documentación de procedimientos de registro, búsqueda y generación de certificados

#### **ACTIVIDAD 2: Análisis de Infraestructura y Procesos (8 horas)**
- Análisis del módulo de usuarios: actores, roles, flujos de trabajo
- Identificación de entradas/salidas del sistema
- Selección de tecnologías: FastAPI, React, PostgreSQL, MinIO, Redis
- Definición de mecanismos de autenticación JWT
- Documentación de restricciones, niveles de acceso y validaciones
- División y asignación de tareas del equipo de desarrollo

#### **ACTIVIDAD 3: Diseño del Sistema (28 horas)**
- Desarrollo de 11 mockups de interfaces:
  - Inicio de sesión
  - Dashboard principal con navegación
  - Gestión de usuarios y roles
  - Gestión de personas
  - Gestión de libros
  - Registros sacramentales
  - Digitalización de documentos
  - Reportes generales
  - Bitácora de auditoría
  - Registro digital de nuevos sacramentos
  - Modal de datos duplicados
- Definición de perfiles de usuario (Administrador, Operador, Consulta)
- Diseño de estructura de permisos por pantalla
- Diseño de flujos de cambio de contraseña y baja lógica de usuarios
- Matriz de permisos por módulo
- Definición de políticas de seguridad del sistema

#### **ACTIVIDAD 4: Desarrollo Backend (69 horas)**

**4.1 Endpoints de Usuarios (19.5 horas):**
- 18 endpoints implementados para CRUD completo de usuarios
- Sistema de autenticación: login, registro, logout, cambio de contraseña
- Endpoint de reactivación de cuentas desactivadas
- Validaciones robustas con Pydantic
- Manejo de errores con HTTPException

**4.2 Autenticación y Autorización JWT (11 horas):**
- Configuración completa de JWT en auth_utils.py
- Implementación de create_access_token()
- Middleware get_current_user() para protección de endpoints
- Configuración bcrypt para hashing de contraseñas
- Manejo de expiración de tokens
- Validación de tokens en todos los endpoints protegidos

**4.3 Sistema de Auditoría (6 horas):**
- Creación de entidad Auditoria en base de datos
- Función registrar_auditoria() para logging automático
- Endpoint GET /auditoria con filtros avanzados
- Sistema de paginación
- Integración en todos los endpoints críticos

**4.4 Protección de Endpoints (2.5 horas):**
- Aplicación de Depends(get_current_user) en todos los endpoints sensibles
- Protección de endpoints de autenticación, cambio de contraseña, logout y roles

**4.5 Sistema de Roles y Accesos (2.5 horas):**
- Implementación de gestión de roles
- Verificación de relación usuario-rol
- Endpoint para listar roles disponibles

**4.6 Normas de Seguridad (14 horas):**
- Configuración CORS para comunicación segura con frontend
- Validaciones exhaustivas con Pydantic en todos los DTOs
- Implementación de bcrypt con salt para contraseñas
- Sistema de logging de errores
- Middleware SecurityHeadersMiddleware con headers de seguridad:
  - X-Frame-Options (protección contra clickjacking)
  - X-Content-Type-Options (prevención de MIME sniffing)
  - X-XSS-Protection (protección contra XSS)
  - Strict-Transport-Security (forzar HTTPS)
  - Content-Security-Policy (política de contenido)
- Middleware de permisos RBAC (permissions.py)
- Decorator check_permissions() para control granular de acceso
- Sistema de Rate Limiting

**4.7 Sistema de Reportes (13.5 horas):**
- Creación de routers/reportes_router.py con 7 endpoints:
  - Resumen de usuarios
  - Usuarios por rol
  - Usuarios activos/inactivos
  - Resumen de accesos
  - Accesos por usuario
  - Últimos accesos
  - Estadísticas generales
- Filtros por período: 7, 30, 90, 365 días
- Documentación completa de endpoints

#### **ACTIVIDAD 5: Documentación Técnica (17 horas)**

**5.1 Diagramas UML (5 horas):**
- Diagrama de proceso de autenticación (LOGIN/JWT)
- Diagrama de proceso de gestión de usuarios (CRUD)
- Diagrama de proceso de digitalización de documentos
- Diagrama de proceso de generación de reportes
- Diagrama de actividad del sistema completo
- Diagrama de estados de documento
- README de diagramas UML

**5.2 Base de Datos Física (4.5 horas):**
- Diagrama físico completo con todas las tablas
- Documentación técnica de estructura de BD
- Definición de índices y relaciones
- Scripts SQL de ejemplo y consultas útiles

**5.3 Arquitectura del Sistema (7.5 horas):**
- Diagrama de arquitectura de microservicios
- Diagrama de arquitectura en capas
- Diagrama de componentes detallado
- Documentación completa de arquitectura
- Documentación de patrones de diseño aplicados
- Documentación de flujos de datos

#### **ACTIVIDAD 6: Desarrollo Frontend y Testing (58.5 horas)**

**6.1 Testing y Configuración Backend (4.5 horas):**
- Tests de autenticación básicos
- Creación de schemas de autenticación y usuarios
- Adaptación de Docker a entorno local
- Configuración de variables de entorno (.env)

**6.2 Desarrollo Frontend (54 horas):**
- Implementación de 13 pantallas completas:
  - Login con integración JWT
  - Dashboard con estadísticas en tiempo real
  - Gestión de usuarios (CRUD completo)
  - Usuarios (listado y filtros)
  - Roles y permisos
  - Gestión de personas
  - Gestión de libros
  - Registros sacramentales
  - Digitalización de documentos
  - Reportes generales con gráficos
  - Bitácora de auditoría con paginación
  - Perfil de usuario con cambio de contraseña
  - Modal de datos duplicados
  - Layout global con navegación
  
- Integraciones con API:
  - Sistema de autenticación completo
  - Manejo de tokens JWT
  - Integración con endpoints de estadísticas
  - Gráficos y visualización de datos
  - Filtros por período (7/30/90/365 días)
  - Sistema de búsqueda en auditoría
  - Paginación avanzada (números de página, contador de registros)
  - Vista de perfil de usuario actual
  - Cambio de contraseña personal

### Resumen Cuantitativo

- **Total de horas:** 213.5 horas
- **Período:** Mayo - Diciembre 2024
- **Reuniones de coordinación:** 24
- **Mockups diseñados:** 11
- **Endpoints backend implementados:** 25+
- **Pantallas frontend desarrolladas:** 13
- **Diagramas técnicos creados:** 10
- **Documentos técnicos elaborados:** 4 (+ de 3,300 líneas)
- **Líneas de código agregadas:** 5,308+
- **Líneas de código modificadas:** 979+
- **Archivos nuevos creados:** 25+
- **Archivos modificados:** 36+

El trabajo realizado representa un aporte significativo al desarrollo del sistema Sacra360, implementando funcionalidades core del sistema con altos estándares de calidad, seguridad y documentación técnica.

---

## 1. DESCRIPCIÓN DE LA INSTITUCIÓN

### 1.1 Antecedentes de la Institución

**Razón Social:** [Completar con nombre legal de la institución]

**Año de Creación:** [Completar]

**Dirección:** [Completar dirección completa]

**Teléfono(s):** [Completar]

**Dirección Web:** [Completar si aplica]

**Responsable Legal de la Institución:**
- Nombre completo: [Completar]
- Cargo: [Completar]

**Área o Rubro de Trabajo:** 
Gestión y administración de archivos históricos religiosos, específicamente registros sacramentales de la Arquidiócesis. La institución se encarga de la preservación, custodia y gestión de documentos históricos que datan de varios siglos, incluyendo registros de Bautizos, Confirmaciones, Matrimonios y Defunciones.

**Cobertura:** 
- **Territorial:** Regional (Arquidiócesis con múltiples parroquias e instituciones religiosas)
- **Alcance:** Gestión de archivos sacramentales de todas las parroquias, colegios e instituciones religiosas bajo jurisdicción de la Arquidiócesis

**Público Meta:**
- Personal administrativo de la Arquidiócesis
- Sacerdotes y celebrantes de las parroquias
- Personal operativo de archivos sacramentales
- Operadores de registro de sacramentos
- Ciudadanía en general que requiere certificados sacramentales

**Responsable del Seguimiento de la Pasantía:**
- Nombre completo: Ing. [Completar apellido] Pacheco
- Cargo: Docente responsable / Coordinador técnico del proyecto
- E-mail: [Completar]
- Teléfono: [Completar]

**Coordinadores Técnicos Adicionales:**
- Ing. Lourdes [Completar apellido] - Coordinación técnica interna
- Ing. Rivera [Completar apellido] - Supervisión técnica

### 1.2 Descripción del Área de Trabajo

**Nombre del Área:** 
Área de Desarrollo de Sistemas de Información / Departamento de Tecnología

**Ubicación en el Organigrama:**
El área de desarrollo tecnológico se encuentra bajo la Dirección de Servicios Administrativos de la Arquidiócesis, trabajando en coordinación directa con el Área de Archivos Históricos. El equipo de desarrollo reporta a la coordinación técnica y mantiene comunicación constante con el personal operativo de archivos para garantizar que el sistema responda a las necesidades reales de gestión documental.

```
Arquidiócesis
    │
    ├── Dirección de Servicios Administrativos
    │       │
    │       ├── Área de Archivos Históricos
    │       │       └── Personal Operativo de Archivos (3-5 personas)
    │       │
    │       └── Área de Desarrollo de Sistemas
    │               ├── Coordinación Técnica (Ing. Pacheco, Ing. Lourdes, Ing. Rivera)
    │               └── Equipo de Desarrollo (Estudiantes en práctica)
    │
    └── Parroquias e Instituciones Afiliadas
```

**Características del Área de Trabajo:**

**Número de Personal del Área:** 
- Coordinación técnica: 3 ingenieros supervisores
- Equipo de desarrollo: 2-3 estudiantes en práctica pre-profesional
- Personal operativo de archivos (usuarios finales): 3-5 personas

**Características del Personal:**

*Coordinación Técnica:*
- **Formación:** Ingenieros en Sistemas/Informática con experiencia en desarrollo de software y gestión de proyectos
- **Edad promedio:** 35-45 años
- **Sexo:** Mixto (2 masculino, 1 femenino aproximadamente)
- **Función:** Supervisión técnica, definición de arquitectura, revisión de código, coordinación con stakeholders

*Equipo de Desarrollo (Estudiantes en Práctica):*
- **Formación:** Estudiantes de últimos semestres de Ingeniería en Sistemas/Informática
- **Edad promedio:** 22-25 años
- **Sexo:** Mixto
- **Función:** Desarrollo de software (backend y frontend), documentación técnica, testing

*Personal Operativo de Archivos:*
- **Formación:** Personal administrativo con conocimiento en gestión documental, algunos con formación en archivística
- **Edad promedio:** 30-50 años
- **Sexo:** Mixto
- **Función:** Usuarios expertos del sistema, validación de funcionalidades, digitalización de documentos

**Dinámica de Trabajo:**

El área de trabajo se caracteriza por una metodología ágil y colaborativa:

1. **Reuniones de Coordinación:** Semanales (miércoles principalmente) con los ingenieros supervisores para revisión de avances, definición de tareas y resolución de problemas técnicos.

2. **Reuniones con Personal Operativo:** Quincenales o mensuales para relevamiento de información, validación de funcionalidades y capacitación en nuevas características del sistema.

3. **Trabajo de Desarrollo:** Actividades diarias de programación, documentación y testing, con comunicación continua entre miembros del equipo mediante herramientas de control de versiones (Git) y mensajería.

4. **Revisiones Técnicas:** Revisión de código y arquitectura por parte de los supervisores antes de integrar nuevas funcionalidades.

**Infraestructura Tecnológica del Área:**

- **Hardware:** Estaciones de trabajo personales, servidores de desarrollo y testing
- **Software:** Entornos de desarrollo (VS Code, PyCharm), herramientas de diseño (Figma), gestores de base de datos
- **Repositorio:** Sistema de control de versiones Git (GitHub)
- **Comunicación:** Reuniones presenciales y virtuales, correo electrónico, mensajería instantánea

### 1.3 Descripción del Cargo/Puesto Desempeñado

**Título del Cargo:** 
Desarrollador Full-Stack Junior / Practicante de Ingeniería de Sistemas

**Tipo de Vinculación:**
Práctica Pre-Profesional (Pasantía Académica)

**Período de Desempeño:**
Mayo - Diciembre 2024 (213.5 horas efectivas)

**Funciones Asignadas Formalmente:**

**1. Relevamiento y Análisis:**
- Participar en reuniones de coordinación con personal operativo y equipo técnico
- Realizar levantamiento de información sobre procesos actuales de gestión documental
- Identificar requerimientos funcionales y no funcionales del sistema
- Analizar y documentar flujos de trabajo existentes
- Colaborar en la definición de arquitectura del sistema

**2. Diseño de Interfaces:**
- Diseñar mockups de interfaces de usuario utilizando principios de UX/UI
- Crear prototipos interactivos para validación con usuarios finales
- Definir flujos de navegación entre pantallas
- Establecer paleta de colores, tipografía y componentes visuales consistentes

**3. Desarrollo Backend:**
- Implementar API RESTful utilizando FastAPI y Python
- Desarrollar endpoints para autenticación, gestión de usuarios y auditoría
- Implementar sistema de autenticación y autorización basado en JWT
- Desarrollar middleware de seguridad (CORS, rate limiting, security headers)
- Implementar sistema RBAC (Role-Based Access Control) para control de permisos
- Crear endpoints para generación de reportes y estadísticas
- Realizar validaciones de datos con Pydantic
- Implementar manejo de errores y excepciones
- Escribir tests unitarios y de integración

**4. Desarrollo Frontend:**
- Desarrollar interfaces de usuario con React y Vite
- Implementar componentes reutilizables siguiendo mejores prácticas
- Integrar frontend con API backend mediante Axios
- Implementar sistema de autenticación en el cliente (manejo de tokens)
- Desarrollar funcionalidades de paginación, filtrado y búsqueda
- Crear gráficos y visualizaciones de datos
- Implementar sistema de permisos en el frontend
- Asegurar responsive design y accesibilidad

**5. Documentación Técnica:**
- Elaborar diagramas UML (procesos, actividades, estados)
- Crear diagramas de arquitectura del sistema
- Documentar estructura de base de datos física
- Escribir documentación técnica de la API
- Crear guías de instalación y configuración
- Documentar patrones de diseño y decisiones arquitectónicas

**6. Testing y Control de Calidad:**
- Realizar pruebas de funcionalidad de los componentes desarrollados
- Ejecutar tests de integración con la API
- Validar requisitos con usuarios finales
- Identificar y reportar bugs
- Participar en revisiones de código

**7. Gestión de Configuración:**
- Utilizar Git para control de versiones
- Realizar commits documentados y push al repositorio
- Mantener la rama de desarrollo (Diego) actualizada
- Configurar entornos de desarrollo local
- Gestionar variables de entorno y configuraciones

**Competencias Requeridas para el Cargo:**

**Técnicas:**
- Lenguajes de programación: Python, JavaScript
- Frameworks: FastAPI, React
- Bases de datos: PostgreSQL, SQL
- Control de versiones: Git, GitHub
- Herramientas de desarrollo: VS Code, Postman, Docker
- Diseño de interfaces: Figma, principios de UX/UI

**Blandas:**
- Trabajo en equipo y colaboración
- Comunicación efectiva con stakeholders técnicos y no técnicos
- Gestión del tiempo y cumplimiento de plazos
- Capacidad de aprendizaje autónomo
- Resolución de problemas
- Adaptabilidad a nuevas tecnologías

**Actividades Realizadas en el Centro de Práctica:**

El desempeño del cargo involucró las siguientes actividades concretas realizadas durante el período de práctica:

- **24 reuniones de coordinación** con diversos stakeholders (supervisores técnicos, personal operativo, equipo de desarrollo)
- **Diseño de 11 mockups** de interfaces de usuario
- **Implementación de 25+ endpoints** en la API backend
- **Desarrollo de 13 pantallas completas** en el frontend
- **Creación de 10 diagramas técnicos** (UML, arquitectura, base de datos)
- **Elaboración de 4 documentos técnicos** con más de 3,300 líneas de documentación
- **Configuración de entornos** de desarrollo (Docker, variables de entorno)
- **Integración de sistemas** de seguridad (JWT, RBAC, middleware de seguridad)
- **Implementación de sistema de auditoría** completo
- **Desarrollo de módulo de reportes** con 7 endpoints y filtros avanzados

El rol desempeñado permitió abarcar el ciclo completo de desarrollo de software, desde el relevamiento de requerimientos hasta la implementación y documentación de funcionalidades core del sistema Sacra360.

---

## 2. NARRACIÓN DE LA EXPERIENCIA LABORAL

### 2.1 Descripción del Trabajo Desempeñado

#### Contexto Inicial y Adaptación

Al inicio de la práctica pre-profesional en Mayo de 2024, el proyecto Sacra360 se encontraba en fase de concepción. El primer desafío fue comprender el dominio del problema: la gestión de archivos sacramentales históricos, un área completamente nueva que requirió un proceso intensivo de inmersión en los procesos operativos de la Arquidiócesis.

Las primeras semanas se dedicaron a reuniones de coordinación con el personal operativo de archivos, donde se observó directamente el trabajo diario: la búsqueda manual en libros centenarios, el llenado de certificados a mano, los tiempos prolongados para localizar registros específicos entre cientos de libros. Esta experiencia fue fundamental para comprender la magnitud del problema que el sistema pretendía resolver.

#### Rutina Laboral - Fase de Relevamiento (Mayo - Agosto)

Durante los primeros meses, la rutina laboral se estructuró en torno a:

**Reuniones Semanales (Miércoles):**
- Coordinación con Ing. Pacheco para revisión de avances y definición de prioridades
- Sesiones de 1-1.5 horas donde se validaban los hallazgos del relevamiento
- Ajuste de objetivos según las necesidades emergentes del proyecto

**Trabajo de Campo:**
- Visitas al área de archivos para observar procesos in situ
- Revisión física de los diferentes tipos de registros (Bautizos, Confirmaciones, Matrimonios, Defunciones)
- Fotografías de formatos de documentos para análisis posterior
- Entrevistas informales con operadores para entender casos especiales

**Trabajo de Análisis:**
- Documentación de flujos de trabajo actuales
- Identificación de actores y roles en el sistema
- Creación de matrices de requerimientos funcionales
- Análisis de infraestructura tecnológica disponible

**Destrezas Demandadas en esta Fase:**
- Escucha activa y capacidad de hacer preguntas relevantes
- Pensamiento analítico para identificar patrones en procesos manuales
- Habilidades de documentación técnica
- Empatía para comprender las necesidades reales de usuarios no técnicos
- Capacidad de abstracción para traducir procesos físicos a sistemas digitales

#### Rutina Laboral - Fase de Diseño (Septiembre - Octubre)

La fase de diseño marcó una transición hacia trabajo más técnico y creativo:

**Diseño de Mockups:**
- Trabajo intensivo durante la semana 4 de Septiembre (4-5 horas diarias)
- Uso de herramientas de diseño (Figma) para crear 11 mockups
- Iteraciones basadas en feedback de supervisores y usuarios operativos
- Sesiones de validación de diseños con personal de archivos

**Definición de Arquitectura:**
- Reuniones técnicas con Ing. Lourdes e Ing. Rivera
- Definición de perfiles de usuario y matriz de permisos
- Documentación de políticas de seguridad
- Diseño de flujos de autenticación y autorización

**Destrezas Demandadas:**
- Conocimientos de UX/UI y principios de diseño
- Capacidad de visualizar flujos de usuario
- Habilidades de prototipado rápido
- Pensamiento en términos de arquitectura de software
- Comunicación visual para transmitir ideas técnicas

#### Rutina Laboral - Fase de Desarrollo Backend (Octubre - Noviembre)

Esta fase representó el período de mayor intensidad técnica:

**Desarrollo Diario (Octubre - Semana 2):**
- Implementación de modelos Pydantic y validaciones (2-3 horas diarias)
- Desarrollo de 13 pantallas completas de frontend (3-4 horas por pantalla)
- Reuniones semanales de revisión de código con supervisores
- Testing continuo de componentes desarrollados

**Desarrollo Intensivo (Noviembre - Semanas 1-2):**
- Implementación del sistema de autenticación JWT (10-12 horas semanales)
- Desarrollo de endpoints de usuarios (8-10 horas semanales)
- Configuración de middleware de seguridad
- Integración de sistema de auditoría
- Pruebas con Postman para validar endpoints

**Trabajo con Repositorio:**
- Commits diarios al branch Diego
- Resolución de conflictos de merge
- Documentación en README files
- Versionado semántico de cambios

**Destrezas Demandadas:**
- Programación avanzada en Python y FastAPI
- Conocimiento profundo de JWT y sistemas de autenticación
- Capacidad de implementar patrones de diseño (Dependency Injection, Middleware)
- Debugging y troubleshooting
- Testing de APIs con herramientas especializadas
- Gestión de control de versiones con Git

#### Rutina Laboral - Fase de Seguridad y Reportes (Noviembre - Diciembre)

**Implementación de Seguridad (Semana 2 de Noviembre):**
- Configuración de CORS y políticas de seguridad
- Implementación de bcrypt con salt para passwords
- Desarrollo de middleware SecurityHeadersMiddleware
- Sistema de Rate Limiting
- Testing de vulnerabilidades comunes

**Sistema RBAC (Semana 1 de Diciembre):**
- Diseño e implementación de permissions.py
- Decorator check_permissions() para control granular
- Integración de permisos en todos los endpoints sensibles
- Validación exhaustiva del sistema de permisos

**Módulo de Reportes (Semana 1 de Diciembre):**
- Desarrollo de reportes_router.py con 7 endpoints
- Implementación de filtros por período (7/30/90/365 días)
- Queries SQL optimizadas para estadísticas
- Documentación de endpoints de reportes

**Destrezas Demandadas:**
- Conocimientos avanzados de seguridad en aplicaciones web
- Implementación de RBAC (Role-Based Access Control)
- Optimización de consultas SQL para reportes
- Conocimiento de headers de seguridad HTTP
- Capacidad de implementar múltiples capas de seguridad

#### Rutina Laboral - Fase de Documentación (Diciembre)

**Documentación Técnica (Semana 1-2 de Diciembre):**
- Creación de 7 diagramas UML en PlantUML
- Documentación de arquitectura (más de 3,300 líneas)
- Diagramas de base de datos física
- Documentación de patrones de diseño aplicados
- README files detallados

**Destrezas Demandadas:**
- Conocimiento de UML y notaciones estándar
- Capacidad de síntesis y documentación técnica
- Habilidades de diagramación
- Pensamiento arquitectónico
- Redacción técnica clara y precisa

#### Integración y Coordinación Continua

A lo largo de todo el período, se mantuvo una rutina de:
- **Comunicación diaria** con el equipo mediante Git (commits documentados)
- **Reuniones semanales** de coordinación (24 reuniones en total)
- **Validaciones periódicas** con personal operativo de archivos
- **Revisiones de código** con supervisores técnicos
- **Aprendizaje continuo** de nuevas tecnologías según necesidades del proyecto

### 2.2 Principales Problemas/Dificultades Enfrentadas

#### 1. Curva de Aprendizaje Tecnológica

**Problema:**
Al inicio del proyecto, había limitada experiencia práctica con FastAPI y el ecosistema moderno de Python para desarrollo de APIs. El proyecto demandaba implementar conceptos avanzados como JWT, middleware personalizados, y patrones de diseño que no habían sido cubiertos en profundidad durante la formación académica.

**Impacto:**
- Las primeras semanas de desarrollo backend (Octubre) fueron más lentas de lo planificado
- Se requirió tiempo adicional fuera del horario de práctica para estudiar documentación y tutoriales
- Algunas implementaciones iniciales debieron ser refactorizadas posteriormente

#### 2. Complejidad del Dominio del Problema

**Problema:**
El dominio de archivos sacramentales históricos presentaba complejidades no evidentes al inicio:
- Múltiples tipos de registros con campos variables según la época
- Casos especiales en búsquedas (nombres con múltiples grafías, registros incompletos)
- Requerimientos de trazabilidad extremadamente estrictos
- Necesidad de mantener integridad histórica de documentos centenarios

**Impacto:**
- Requirió múltiples iteraciones en el diseño de modelos de datos
- Necesidad de reuniones adicionales con personal operativo para clarificar casos especiales
- Ajustes continuos en validaciones y reglas de negocio

#### 3. Coordinación de Equipo Distribuido

**Problema:**
El equipo de desarrollo estaba trabajando en diferentes módulos del sistema, lo que generaba:
- Conflictos frecuentes en el repositorio Git
- Dependencias entre módulos no siempre claras
- Diferentes ritmos de avance en distintas áreas
- Necesidad de mantener coherencia en estilos de código

**Impacto:**
- Tiempo invertido en resolver conflictos de merge
- Retrasos ocasionales cuando se dependía de endpoints de otros desarrolladores
- Necesidad de refactorizar código para mantener consistencia

#### 4. Configuración de Entorno de Desarrollo

**Problema:**
La configuración inicial del entorno de desarrollo presentó desafíos:
- Docker compose no funcionaba correctamente en el entorno Windows local
- Problemas de conectividad con PostgreSQL
- Incompatibilidades de versiones de dependencias
- Variables de entorno con configuraciones complejas

**Impacto:**
- Primer semana de Noviembre con dificultades para levantar el ambiente local
- Tiempo invertido en troubleshooting en lugar de desarrollo productivo
- Necesidad de adaptar configuraciones específicas para la estación de trabajo

#### 5. Integración Frontend-Backend

**Problema:**
La integración del frontend React con la API presentó desafíos:
- Manejo de CORS inicialmente problemático
- Gestión de tokens JWT en el cliente
- Sincronización de estados entre frontend y backend
- Manejo de errores y respuestas de la API

**Impacto:**
- Varias iteraciones para lograr autenticación funcional completa
- Debugging complejo que involucraba ambos lados de la aplicación
- Necesidad de implementar manejo robusto de errores

#### 6. Gestión del Tiempo con Carga Académica

**Problema:**
Balancear la práctica pre-profesional con la carga académica regular del semestre:
- Períodos de exámenes con menor disponibilidad
- Proyectos académicos paralelos
- Necesidad de cumplir 213.5 horas en el período establecido

**Impacto:**
- Distribución irregular de horas algunas semanas
- Necesidad de trabajo en fines de semana en períodos de alta demanda académica
- Stress por cumplir con ambas responsabilidades simultáneamente

#### 7. Comprensión de Requerimientos de Seguridad

**Problema:**
Los requerimientos de seguridad eran más estrictos de lo inicialmente anticipado:
- Necesidad de implementar múltiples capas de seguridad
- Headers HTTP de seguridad no familiares
- Content Security Policy compleja
- Sistema RBAC granular

**Impacto:**
- Tiempo adicional para estudiar mejores prácticas de seguridad web
- Varias iteraciones en la implementación del middleware de seguridad
- Necesidad de revisar y actualizar código anterior para cumplir estándares

### 2.3 Procedimiento de Resolución de los Problemas/Dificultades

#### Resolución 1: Curva de Aprendizaje Tecnológica

**Acciones Tomadas:**

1. **Aprendizaje Estructurado:**
   - Estudio de documentación oficial de FastAPI (2-3 horas semanales fuera de horario)
   - Tutoriales en video sobre JWT y autenticación
   - Revisión de código fuente de proyectos similares en GitHub
   - Consulta de Stack Overflow y comunidades de desarrolladores

2. **Práctica Incremental:**
   - Implementación de endpoints simples primero (GET básicos)
   - Progresión gradual hacia funcionalidades más complejas (POST, PUT, DELETE con validaciones)
   - Testing constante de cada nueva característica implementada

3. **Mentoring y Supervisión:**
   - Reuniones semanales con Ing. Pacheco para revisión de código
   - Solicitud de feedback técnico sobre implementaciones
   - Sesiones de pair programming con compañeros del equipo en puntos críticos

**Resultado:**
- A partir de la semana 2 de Noviembre, el ritmo de desarrollo se aceleró significativamente
- Las implementaciones posteriores (middleware de seguridad, reportes) fueron más fluidas
- Se adquirió confianza en patrones de diseño de FastAPI

#### Resolución 2: Complejidad del Dominio del Problema

**Acciones Tomadas:**

1. **Inmersión en el Dominio:**
   - Reuniones adicionales con personal operativo (6 reuniones extra programadas)
   - Revisión física de libros sacramentales para entender variabilidad
   - Documentación detallada de casos especiales y excepciones

2. **Diseño Iterativo:**
   - Implementación de modelos de datos flexibles que permitan extensiones
   - Validaciones con personal operativo antes de implementar funcionalidades
   - Prototipos rápidos para validar comprensión de requerimientos

3. **Documentación Exhaustiva:**
   - Creación de documentos de casos de uso
   - Diagramas de flujo para procesos complejos
   - README detallados explicando lógica de negocio

**Resultado:**
- Mejor comprensión del dominio permitió implementaciones más acertadas
- Reducción de re-trabajo y refactorizaciones mayores
- Mayor confianza del personal operativo en el sistema

#### Resolución 3: Coordinación de Equipo Distribuido

**Acciones Tomadas:**

1. **Estrategia de Branching:**
   - Creación de branch personal (Diego) para desarrollo independiente
   - Commits frecuentes con mensajes descriptivos
   - Pull requests formales antes de merge a ramas principales

2. **Comunicación Proactiva:**
   - Comunicación diaria sobre avances y bloqueos
   - Documentación de interfaces de endpoints antes de implementación
   - Reuniones de sincronización con compañeros de equipo

3. **Estándares de Código:**
   - Adopción de convenciones de nomenclatura consistentes
   - Uso de Pydantic schemas para contratos claros de datos
   - Documentación inline en código complejo

**Resultado:**
- Reducción de conflictos de merge a partir de la semana 2 de Noviembre
- Mayor claridad sobre dependencias entre módulos
- Código más consistente y mantenible

#### Resolución 4: Configuración de Entorno de Desarrollo

**Acciones Tomadas:**

1. **Adaptación de Docker:**
   - Modificación de docker-compose.yml para compatibilidad con Windows
   - Creación de script run.ps1 específico para PowerShell
   - Documentación de configuración específica en README

2. **Configuración Local:**
   - Setup de PostgreSQL local como alternativa a Docker
   - Configuración de .env con parámetros correctos para entorno local
   - Testing de conectividad antes de iniciar desarrollo

3. **Documentación del Proceso:**
   - Creación de guía paso a paso para configuración en Windows
   - Documentación de problemas comunes y soluciones
   - Compartir experiencia con compañeros para evitar repetición de problemas

**Resultado:**
- Entorno de desarrollo estable a partir de la semana 2 de Noviembre
- Proceso de setup documentado para futuros integrantes
- Mayor productividad al eliminar problemas de infraestructura

#### Resolución 5: Integración Frontend-Backend

**Acciones Tomadas:**

1. **Configuración de CORS:**
   - Implementación correcta de CORS middleware en FastAPI
   - Configuración de origins permitidos en settings
   - Testing con diferentes escenarios de origen

2. **Manejo de JWT en Cliente:**
   - Implementación de AuthContext en React para gestión central de autenticación
   - Interceptores de Axios para agregar token automáticamente
   - Manejo de refresh de tokens y expiración

3. **Testing de Integración:**
   - Pruebas end-to-end desde frontend a backend
   - Uso de Postman para validar respuestas esperadas
   - Debugging con DevTools del navegador

**Resultado:**
- Sistema de autenticación completamente funcional (semana 4 de Noviembre)
- Comunicación fluida entre frontend y backend
- Manejo robusto de errores y estados de carga

#### Resolución 6: Gestión del Tiempo con Carga Académica

**Acciones Tomadas:**

1. **Planificación Semanal:**
   - Distribución de horas según carga académica de la semana
   - Priorización de tareas críticas del proyecto
   - Comunicación anticipada con supervisores sobre disponibilidad

2. **Trabajo Concentrado:**
   - Bloques de tiempo dedicados exclusivamente a la práctica
   - Eliminación de distracciones durante sesiones de desarrollo
   - Uso de técnicas de productividad (Pomodoro)

3. **Flexibilidad:**
   - Compensación de horas en semanas con menor carga académica
   - Trabajo en fines de semana cuando fue necesario (reportes en Diciembre)
   - Coordinación con supervisores para ajustar expectativas

**Resultado:**
- Cumplimiento de las 213.5 horas requeridas
- Entrega de todos los productos esperados
- Mantenimiento de buen rendimiento académico paralelo

#### Resolución 7: Comprensión de Requerimientos de Seguridad

**Acciones Tomadas:**

1. **Estudio de Seguridad Web:**
   - Curso online sobre OWASP Top 10
   - Lectura de documentación sobre headers de seguridad HTTP
   - Estudio de implementaciones de RBAC en proyectos open source

2. **Implementación Gradual:**
   - Primera versión básica de autenticación (JWT simple)
   - Iteración agregando capas: CORS → Headers de seguridad → RBAC
   - Testing de cada capa antes de agregar la siguiente

3. **Revisión con Supervisores:**
   - Sesiones específicas sobre seguridad con Ing. Rivera
   - Code review enfocado en aspectos de seguridad
   - Validación de implementación contra mejores prácticas

**Resultado:**
- Sistema de seguridad robusto con múltiples capas
- Middleware completamente funcional (semana 1 de Diciembre)
- Conocimiento profundo de seguridad web aplicable a futuros proyectos

### 2.4 Principales Productos/Resultados Obtenidos

A continuación se detallan los productos obtenidos organizados cronológicamente por mes y semana, con las horas trabajadas y evidencias correspondientes:

---

## MAYO 2024

### SEMANA 3 - MAYO (2 horas)

**Martes (1.5h):**
- Reunión con personal operativo de archivos (1h)
- Revisión de infraestructura tecnológica disponible (0.5h)

**Miércoles (0.5h):**
- Identificación de información en libros de sacramentos (0.5h)

**Productos:**
- Notas de reunión con personal operativo
- Primer relevamiento de tipos de documentos sacramentales
- Análisis preliminar de infraestructura

---

## JULIO 2024

### SEMANA 3 - JULIO (3 horas)

**Miércoles (3h):**
- Reunión de coordinación interna (1h)
- Relevamiento de registros sacramentales: Confirmación, Bautizo, Matrimonio, Defunción (1h)
- Identificación de formato de índice de libros (0.5h)
- Identificación de parroquias, colegios, instituciones (0.5h)

**Productos:**
- Catálogo de 4 tipos de registros sacramentales
- Listado de parroquias e instituciones de la Arquidiócesis

### SEMANA 4 - JULIO (2 horas)

**Lunes (0.5h):**
- Identificación de actores en celebraciones (celebrantes por parroquia)

**Miércoles (1.5h):**
- Relevamiento de índice de libros de registro (0.5h)
- Relevamiento de procedimientos de registro de sacramentos (0.5h)
- Relevamiento de flujos de búsquedas de sacramentos (0.5h)

**Productos:**
- Mapeo de actores y roles del sistema
- Documentación de flujos de trabajo actuales

---

## AGOSTO 2024

### SEMANA 1 - AGOSTO (1.5 horas)

**Jueves (0.5h):**
- Reunión de coordinación interna

**Martes (1h):**
- Reunión de coordinación con Ing. Pacheco

### SEMANA 2 - AGOSTO (11 horas)

**Viernes (3h):**
- Reunión extra con personal operativo de archivos (1.5h)
- Identificación de flujo de trabajo para llenado de registros (0.5h)
- Relevamiento de certificados de sacramentos (0.5h)
- Identificación de formato de certificados (0.5h)

**Lunes (4.5h):**
- Reunión con Ing. Lourdes (1.5h)
- Identificación de actores y roles del módulo de usuarios (1h)
- Identificación de entradas/salidas del módulo de usuarios (1h)
- Asignación y división de tareas (0.5h)

**Miércoles (2h):**
- Identificación de herramientas y tecnologías (0.5h)
- Definición del flujo de trabajo del módulo de gestión de usuarios (1.5h)

**Jueves (2h):**
- Identificación de restricciones, niveles de acceso y validaciones (1h)
- Redacción de documento de niveles de accesos (1h)

**Productos:**
- Documento de arquitectura del módulo de usuarios
- Matriz de tecnologías seleccionadas: FastAPI, React, PostgreSQL, Redis, MinIO
- Documento de niveles de acceso y validaciones

### SEMANA 3 - AGOSTO (1 hora)

**Martes (1h):**
- Reunión de coordinación interna

### SEMANA 4 - AGOSTO (4 horas)

**Jueves (1h):**
- Reunión de coordinación interna

**Viernes (2.5h):**
- Reunión con Ing. Pacheco (1.5h)
- Identificación de servidores a usar (0.5h)
- Identificación de framework del sistema (0.5h)

**Lunes (0.5h):**
- Reunión con Ing. Pacheco

---

## SEPTIEMBRE 2024

### SEMANA 1 - SEPTIEMBRE (5 horas)

**Miércoles (1h):**
- Reunión con Ing. Pacheco y Ing. Lourdes

**Jueves (4h):**
- Reunión con personal operativo de archivos (1.5h)
- Reunión con Ing. Rivera y ayudantes (1h)
- Reunión con Ing. Pacheco (1h)
- Identificación de arreglos en formato de índice de libros (0.5h)

### SEMANA 4 - SEPTIEMBRE (18.5 horas)

**Lunes (4.5h):**
- Mockup de inicio de sesión (2.5h)
- Desarrollo del dashboard principal con navegación (2h)

**Martes (4h):**
- Diseño de módulo de gestión de usuarios y roles (2h)
- Interfaz de gestión de personas (2h)

**Miércoles (4.5h):**
- Reunión con Ing. Pacheco (1h)
- Diseño de gestión de libros (2h)
- Interfaz de gestión de registros sacramentales (1.5h)

**Jueves (2.5h):**
- Módulo de digitalización de documentos (2.5h)

**Viernes (3h):**
- Mockup de reportes generales (2h)
- Mockup de bitácora de auditoría (1h)

**Productos:**
- 9 mockups completos de interfaces de usuario
- Diseños validados con supervisores técnicos

---

## OCTUBRE 2024

### SEMANA 1 - OCTUBRE (9.5 horas)

**Productos Obtenidos:**
- Documento de relevamiento de procesos actuales
- Matriz de tipos de documentos identificados
- Catálogo de formatos de certificados y registros
- Mapeo de actores y roles del sistema
- Documentación de flujos de trabajo existentes

**Distribución por Semanas:**

**Mayo - Semana 3 (Martes: 1.5h):**
- Reunión con personal operativo de archivos
- Revisión de infraestructura tecnológica

**Julio - Semana 3 (Miércoles: 3h):**
- Reunión de coordinación interna
- Relevamiento de registros sacramentales (4 tipos)
- Identificación de formatos

**Julio - Semana 4 (Lunes-Miércoles: 2h):**
- Identificación de actores en celebraciones
- Relevamiento de índices de libros
- Documentación de procedimientos

**Agosto - Semanas 1-4 (17.5h total):**
- Múltiples reuniones de coordinación
- Relevamiento detallado de certificados
- Identificación de flujos de trabajo
- Análisis de módulo de usuarios

**Septiembre - Noviembre (9h reuniones adicionales)**

**Evidencias Sugeridas:**
- No requiere capturas de código (fase de análisis)
- Fotografías de libros sacramentales (si disponibles)
- Documentos Word/PDF de relevamiento (si creados)

---

#### **ACTIVIDAD 2: Análisis de Infraestructura (Agosto, 8 horas)**

**Productos Obtenidos:**
- Documento de arquitectura del módulo de usuarios
- Matriz de tecnologías seleccionadas
- Documento de niveles de acceso y validaciones
- Plan de división de tareas

**Distribución:**
**Agosto - Semana 2 (Lunes-Jueves: 7h):**
- Análisis de actores y roles
- Definición de flujo del módulo de usuarios
- Identificación de restricciones y validaciones
- Documento de niveles de acceso

**Agosto - Semana 4 (Viernes: 1h):**
- Identificación de servidores y framework

**Evidencias Sugeridas:**
- Documento de arquitectura (si existe en docs/)
- Diagramas preliminares

---

#### **ACTIVIDAD 3: Diseño del Sistema (Septiembre - Noviembre, 28 horas)**

**Productos Obtenidos:**
- 11 mockups de interfaces de usuario
- Documento de perfiles de usuario
- Matriz de permisos por módulo
- Documentación de políticas de seguridad
- Flujos de cambio de contraseña y baja lógica

**Distribución:**
**Septiembre - Semana 4 (Lunes-Viernes: 17.5h):**
- Mockup inicio de sesión (2.5h)
- Dashboard principal (2h)
- Gestión de usuarios y roles (2h)
- Gestión de personas (2h)
- Gestión de libros (2h)
- Registros sacramentales (1.5h)
- Digitalización de documentos (2.5h)
- Reportes generales (2h)
- Bitácora de auditoría (1h)

**Octubre - Semana 1 (Lunes-Viernes: 9h):**
- Definición de perfiles (1h)
- Estructura de permisos (1.5h)
- Flujos de gestión (1h)
- Cambio de contraseña (1h)
- Políticas de seguridad (1h)
- Roles del sistema (1h)
- Matriz de permisos (1h)
- Sistema de auditoría (1.5h)

**Noviembre - Semana 4 (Jueves: 1.5h):**
- Mockup registro digital de sacramentos

**Evidencias Sugeridas:**
- Capturas de mockups en Figma (si disponibles)
- Matriz de permisos (documento o tabla)

---

#### **ACTIVIDAD 4: Desarrollo Backend (Octubre - Diciembre, 69 horas)**

**Productos Obtenidos:**
- API RESTful completa con 25+ endpoints
- Sistema de autenticación JWT funcional
- Middleware de seguridad (RBAC, headers, rate limiting)
- Sistema de auditoría completo
- Módulo de reportes con 7 endpoints

**4.1 Endpoints de Usuarios (19.5h)**

**Octubre - Semana 2 (Lunes-Martes: 5h):**
- Modelos Pydantic y validaciones
- Manejo de errores
- Documentación README

**Evidencia 1 - Schemas Pydantic:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/schemas/user_schemas.py
Captura: Líneas con definición de schemas (UserCreate, UserUpdate, UserResponse)
Descripción: "Modelos Pydantic con validaciones robustas para usuarios"
```

**Noviembre - Semana 1 (Lunes-Viernes: 11.5h):**
- Implementación de 6 endpoints auth (login, register, me, change-password, logout, roles)

**Evidencia 2 - Endpoints de Autenticación:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/routers/auth_router.py
Captura: Decoradores @router.post("/login"), @router.post("/register"), @router.get("/me")
Descripción: "Endpoints de autenticación implementados con FastAPI"
```

**Diciembre - Semana 1 (Lunes-Martes: 3h):**
- Mejoras en usuarios_router.py
- Endpoints CRUD completos

**Evidencia 3 - CRUD de Usuarios:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/routers/usuarios_router.py
Captura: Líneas 457-560 (DELETE y PATCH /activar endpoints)
Descripción: "Endpoints de baja lógica y reactivación de usuarios"
```

**4.2 Autenticación JWT (11h)**

**Noviembre - Semana 1 (Miércoles-Viernes: 7.5h):**
- Configuración JWT
- create_access_token()
- get_current_user() middleware
- Configuración bcrypt

**Evidencia 4 - Sistema JWT:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/utils/auth_utils.py
Captura: Funciones create_access_token() y get_current_user()
Descripción: "Sistema de autenticación JWT con generación y validación de tokens"
```

**Noviembre - Semana 2 (Lunes: 2h):**
- Validación de tokens
- Manejo de expiración

**Diciembre - Semana 1 (Miércoles: 1h):**
- Refactor con mejores prácticas

**4.3 Sistema de Auditoría (6h)**

**Noviembre - Semana 2 (Lunes-Martes: 2.5h):**
- Entidad Auditoria
- Función registrar_auditoria()

**Noviembre - Semana 4 (Lunes: 1h):**
- Integración en login

**Diciembre - Semana 1 (Lunes: 2.5h):**
- Endpoint GET /auditoria con filtros
- Paginación

**Evidencia 5 - Sistema de Auditoría:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/routers/auditoria_router.py
Captura: Endpoint GET /auditoria con parámetros de filtro (skip, limit, usuario_id, accion)
Descripción: "Sistema de auditoría con filtros avanzados y paginación"
```

**4.4 Protección de Endpoints (2.5h)**

**Noviembre - Semana 2 (Miércoles: 2.5h):**
- Aplicación de Depends(get_current_user) en endpoints sensibles

**4.5 Sistema de Roles (2.5h)**

**Noviembre - Semana 2 (Jueves: 2.5h):**
- Análisis de tabla roles
- Implementación GET /roles
- Verificación usuario-rol

**4.6 Normas de Seguridad (14h)**

**Noviembre - Semana 2 (Viernes: 4.5h):**
- Configuración CORS
- Validaciones Pydantic
- Implementación bcrypt
- PasswordUtils

**Noviembre - Semana 4 (Miércoles: 2h):**
- HTTPException
- Logging de errores

**Diciembre - Semana 1 (Miércoles: 3.5h):**
- SecurityHeadersMiddleware
- Headers de seguridad (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, HSTS, CSP)

**Evidencia 6 - Middleware de Seguridad:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/middleware/security.py
Captura: Líneas 73-103 (Clase SecurityHeadersMiddleware completa)
Descripción: "Middleware de seguridad con headers HTTP: CSP, X-Frame-Options, HSTS"
```

**Diciembre - Semana 1 (Jueves: 3.5h):**
- Middleware RBAC (permissions.py)
- check_permissions() decorator
- Sistema de permission guard

**Evidencia 7 - Sistema RBAC:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/middleware/permissions.py
Captura: Decorator check_permissions() y lógica de verificación de permisos
Descripción: "Sistema RBAC con control granular de permisos por módulo"
```

**4.7 Sistema de Reportes (13.5h)**

**Diciembre - Semana 1 (Viernes-Sábado: 13.5h):**
- Creación reportes_router.py
- 7 endpoints de reportes (usuarios, accesos, estadísticas)
- Filtros por período
- Documentación

**Evidencia 8 - Módulo de Reportes:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/routers/reportes_router.py
Captura: Líneas 1-100 (imports, router, y primeros endpoints)
Descripción: "Módulo de reportes con 7 endpoints y filtros por período"
```

**Evidencia 9 - Endpoints de Estadísticas:**
```
Archivo: BACKEND/server-sacra360/AuthProfiles-service/app/routers/reportes_router.py
Captura: Líneas 328-390 (Endpoint GET /estadisticas con queries SQL complejas)
Descripción: "Endpoint de estadísticas generales con queries optimizadas"
```

---

#### **ACTIVIDAD 5: Documentación Técnica (Diciembre, 17 horas)**

**Productos Obtenidos:**
- 7 diagramas UML en PlantUML (1,439 líneas de código)
- 4 documentos técnicos completos (3,350+ líneas)
- Documentación de arquitectura de microservicios
- Diagramas de base de datos física

**5.1 Diagramas UML (5h)**

**Diciembre - Semana 1 (Domingo: 5h):**
- 7 diagramas UML completos

**Evidencia 10 - Diagrama de Autenticación:**
```
Archivo: docs/diagramas/01-proceso-autenticacion.puml
Captura: Todo el archivo (127 líneas)
Descripción: "Diagrama de secuencia del proceso de autenticación con JWT"
```

**Evidencia 11 - Diagrama de Gestión de Usuarios:**
```
Archivo: docs/diagramas/02-proceso-gestion-usuarios.puml
Captura: Sección de CRUD de usuarios (líneas 50-150)
Descripción: "Diagrama de actividad para gestión completa de usuarios"
```

**Evidencia 12 - Base de Datos Física:**
```
Archivo: docs/diagramas/07-base-datos-fisica.puml
Captura: Sección de tablas principales (líneas 1-100)
Descripción: "Diagrama físico de base de datos con todas las relaciones"
```

**5.2 Base de Datos Física (4.5h)**

**Diciembre - Semana 2 (Lunes: 4.5h):**
- Diagrama físico completo
- Documentación técnica de BD
- Índices y relaciones
- Scripts SQL

**Evidencia 13 - Documentación de BD:**
```
Archivo: docs/arquitectura/base-datos-fisica.md
Captura: Líneas 1-100 (introducción y primeras tablas)
Descripción: "Documentación técnica completa de estructura de base de datos"
```

**5.3 Arquitectura (7.5h)**

**Diciembre - Semana 2 (Lunes-Martes: 7.5h):**
- Diagrama de microservicios
- Arquitectura en capas
- Componentes detallados
- Documentación completa
- Patrones de diseño
- Flujos de datos

**Evidencia 14 - Arquitectura del Sistema:**
```
Archivo: docs/arquitectura/README.md
Captura: Líneas 1-100 (visión general de arquitectura)
Descripción: "Documentación completa de arquitectura: capas, componentes, patrones"
```

**Evidencia 15 - Diagrama de Componentes:**
```
Archivo: docs/diagramas/diagrama-componentes.puml
Captura: Todo el archivo
Descripción: "Diagrama de componentes con todas las dependencias del sistema"
```

---

#### **ACTIVIDAD 6: Desarrollo Frontend (Octubre - Diciembre, 58.5 horas)**

**Productos Obtenidos:**
- 13 pantallas completas implementadas en React
- Sistema de autenticación con JWT integrado
- Componente Layout global con navegación
- Integración completa con API backend

**6.1 Testing y Configuración (4.5h)**

**Noviembre - Semana 4 (Miércoles: 3h):**
- Tests de autenticación
- Schemas de autenticación y usuarios

**Noviembre - Semana 1 (Lunes: 1.5h):**
- Adaptación Docker
- Configuración .env

**Evidencia 16 - Configuración Docker:**
```
Archivo: BACKEND/docker-compose.yml
Captura: Servicios principales (postgres, redis, minio)
Descripción: "Configuración Docker Compose para entorno de desarrollo"
```

**6.2 Desarrollo Frontend (54h)**

**Octubre - Semana 2 (Lunes: 6h):**
- Pantalla Login (3h)
- Pantalla Dashboard (3h)

**Evidencia 17 - Pantalla Login:**
```
Archivo: frontend/src/pages/Login.jsx
Captura: Líneas 1-80 (imports, estado, y función handleLogin)
Descripción: "Pantalla de Login con integración JWT y manejo de autenticación"
```

**Evidencia 18 - Dashboard:**
```
Archivo: frontend/src/pages/Dashboard.jsx
Captura: Líneas 1-100 (imports, useEffect para estadísticas, y renderizado de tarjetas)
Descripción: "Dashboard con estadísticas en tiempo real desde la API"
```

**Octubre - Semana 2 (Martes-Miércoles: 12h):**
- Gestión de usuarios (3h)
- Usuarios (2.5h)
- Roles y permisos (2.5h)
- Gestión de personas (2h)
- Modal datos duplicados (2h)

**Octubre - Semana 2 (Jueves-Viernes: 13.5h):**
- Gestión de libros (3h)
- Registros sacramentales (3h)
- Digitalización documentos (3h)
- Reportes generales (3h)
- Bitácora auditoría (2.5h)
- Layout global (1.5h)

**Evidencia 19 - Layout Global:**
```
Archivo: frontend/src/components/Layout.jsx
Captura: Líneas 1-100 (estructura principal con sidebar y navegación)
Descripción: "Layout global con menú de navegación y control de permisos"
```

**Noviembre - Semana 4 (Lunes-Miércoles: 4.5h):**
- Integración Login con backend
- Manejo de tokens JWT

**Diciembre - Semana 1 (Lunes: 4h):**
- Integración API estadísticas
- Gráficos y visualización
- Página Reportes completa

**Evidencia 20 - Página de Reportes:**
```
Archivo: frontend/src/pages/Reportes.jsx
Captura: Líneas 1-150 (integración con API, filtros por período, y gráficos)
Descripción: "Página de reportes con filtros de período y visualización de datos"
```

**Diciembre - Semana 1 (Martes: 9.5h):**
- Filtros por período
- Integración Auditoría con API
- Arreglos pantalla Auditoría
- Página Auditoría completa
- Filtros de búsqueda

**Evidencia 21 - Página de Auditoría:**
```
Archivo: frontend/src/pages/Auditoria.jsx
Captura: Líneas 1-100 (integración con API, filtros, paginación)
Descripción: "Página de auditoría con filtros avanzados y paginación"
```

**Diciembre - Semana 1 (Viernes: 2.5h):**
- Página Perfil completa
- Vista usuario actual
- Cambio de contraseña personal

**Evidencia 22 - Página de Perfil:**
```
Archivo: frontend/src/pages/Perfil.jsx
Captura: Líneas 1-100 (información del usuario y formulario de cambio de contraseña)
Descripción: "Página de perfil con información del usuario y cambio de contraseña"
```

**Diciembre - Semana 2 (Martes: 1.5h):**
- Arreglos paginación en Auditoría
- Mejoras UI/UX paginación
- Contador de páginas

**Evidencia 23 - Paginación Mejorada:**
```
Archivo: frontend/src/pages/Auditoria.jsx
Captura: Líneas 200-329 (sección de paginación con botones y contador)
Descripción: "Sistema de paginación avanzado con números de página y contador de registros"
```

---

### Resumen Cuantitativo de Productos

**Total de Horas:** 213.5 horas

**Código Producido:**
- **Backend:** 5,308+ líneas agregadas, 979+ modificadas
- **Frontend:** 3,000+ líneas implementadas
- **Documentación:** 3,350+ líneas
- **Diagramas UML:** 1,439 líneas

**Archivos Creados/Modificados:**
- 25+ archivos nuevos creados
- 36+ archivos modificados
- 10 diagramas técnicos
- 4 documentos de arquitectura completos

**Funcionalidades Implementadas:**
- 25+ endpoints RESTful
- 7 endpoints de reportes
- 13 pantallas de usuario
- 2 middlewares de seguridad
- Sistema completo de autenticación JWT
- Sistema de auditoría con filtros
- Sistema RBAC granular

**Reuniones y Coordinación:**
- 24 reuniones de coordinación
- 6 revisiones técnicas de código
- Múltiples sesiones de validación con usuarios finales

---

# PORTAFOLIO DIEGO MORÓN MEJIA
## PRÁCTICA PRE PROFESIONAL

**CENTRO DE PRÁCTICA:** Arzobispado de La Paz  
**FECHA:** 21 de Julio al 12 de Diciembre de 2025

---

# INTRODUCCIÓN

La presente práctica pre profesional se realizó en el Arzobispado de La Paz durante el período comprendido entre el 21 de julio y el 12 de diciembre de 2025, cumpliendo un total de 203 horas de trabajo distribuidas en 6 actividades principales.

**Lo solicitado en los términos de referencia de la pasantía:**

Los términos de referencia establecieron mi responsabilidad en tres áreas principales del sistema Sacra360:

**1. Diseño de Frontend:** Diseñar la totalidad de las interfaces de usuario del sistema en Figma, incluyendo mockups de alta fidelidad para todos los módulos (AuthProfiles, Gestión de Sacramentos, Digitalización, Reportes).

**2. Implementación de Pantallas Principales:** Desarrollar en código React todas las páginas del módulo AuthProfiles y las pantallas base del sistema (Login, Dashboard, Usuarios, Auditoría, Reportes, Perfil).

**3. Módulo de Autenticación Completo (AuthProfiles):** Desarrollar el backend completo del módulo de autenticación y gestión de usuarios que incluía:
- Sistema de autenticación con JWT
- Gestión completa de usuarios (CRUD)
- Control de roles y permisos (RBAC)
- Auditoría de acciones de usuarios
- Reportes de usuarios y accesos
- Integración frontend-backend funcional

El sistema Sacra360 es una plataforma de modernización de registros sacramentales del Arzobispado de La Paz, donde el módulo AuthProfiles opera como microservicio independiente en el puerto 8004, coordinándose con los módulos desarrollados por Sebastian Pinto (Sacramentos) y Marco Reynold (OCR/HTR).

**Objetivos del estudiante:**

1. Aplicar conocimientos de desarrollo full-stack en un proyecto real de impacto social
2. Desarrollar competencias en arquitectura de microservicios y APIs REST
3. Implementar sistemas de seguridad modernos (JWT, RBAC, encriptación)
4. Adquirir experiencia en trabajo colaborativo con metodologías ágiles
5. Generar documentación técnica profesional siguiendo estándares de la industria

**Justificación:**

El Arzobispado de La Paz maneja información histórica y sensible de registros sacramentales que datan de varios siglos, abarcando más de 80 parroquias del departamento. La gestión manual de estos documentos presentaba problemas de deterioro físico, pérdida de información, tiempos prolongados de búsqueda (hasta horas para encontrar un registro específico), y vulnerabilidad ante desastres naturales o incendios.

El sistema Sacra360 surge como solución integral de digitalización que requería:
- **Preservación del patrimonio histórico:** Digitalización mediante OCR/HTR de documentos antiguos (algunos del siglo XVII) con reconocimiento de escritura manuscrita antigua.
- **Gestión eficiente de sacramentos:** Base de datos centralizada para registro de bautizos, matrimonios, confirmaciones y defunciones con búsquedas instantáneas.
- **Seguridad y trazabilidad:** Sistema de autenticación y autorización robusto que garantizara control de acceso granular según roles, auditoría completa de acciones, y protección de datos personales y religiosos.
- **Escalabilidad:** Arquitectura de microservicios que permitiera crecimiento modular y mantenimiento independiente de cada componente (AuthProfiles, Sacramentos, OCR/HTR).
- **Accesibilidad:** Interfaces web intuitivas para usuarios con diversos niveles de experiencia técnica, desde operadores de parroquias rurales hasta administradores centrales.

Mi participación en este proyecto se enfocó en el diseño visual completo del sistema (mockups de todos los módulos) y el desarrollo integral del módulo AuthProfiles, componente crítico que habilita el acceso seguro y controlado a toda la plataforma.

**Productos/Actividades:**

ACTIVIDAD 1 (37 horas): Relevamiento de información y procesos - 29 reuniones de coordinación, identificación de flujos de trabajo, relevamiento de tipos y formatos de documentos, mapeo de estructura organizacional.

ACTIVIDAD 2 (8 horas): Análisis de infraestructura y herramientas - Análisis de módulos requeridos, selección de stack tecnológico (FastAPI, React, PostgreSQL, Redis, Docker), definición de niveles de acceso.

ACTIVIDAD 3 (31.5 horas): Diseño del sistema - 16 mockups en Figma, diseño de gestión de perfiles y roles, definición de políticas de contraseñas, matriz de permisos.

ACTIVIDAD 4 (56 horas): Desarrollo Backend y Frontend - 18 endpoints REST, autenticación JWT, encriptación bcrypt, 6 páginas React funcionales, sistema RBAC.

ACTIVIDAD 5 (29 horas): Documentación técnica - 7 diagramas UML, diagramas de arquitectura, diagrama BD, manual de usuario (940 líneas), manual técnico (336 líneas).

ACTIVIDAD 6 (41.5 horas): Tareas adicionales - Docker, tests con pytest, schemas Pydantic, 11 pantallas frontend adicionales.

Productos finales: Código fuente (backend FastAPI + frontend React), documentación completa (10 diagramas + 2 manuales), base de datos (3 tablas), sistema funcional (30 endpoints API + 6 interfaces operativas).

---

# 1. DESCRIPCIÓN DE LA INSTITUCIÓN

## 1.1 Antecedentes de la institución

**Razón Social:** Arzobispado de La Paz  
**Año de Creación:** 1605 (Diócesis) - 1943 (elevada a Arquidiócesis)  
**Dirección:** Calle Potosí esq. Ayacucho, Plaza Murillo, La Paz, Bolivia  
**Teléfono:** (+591) 2-2406785 / 2-2406786  
**Correo Electrónico:** arzobispado@iglesia.org.bo  
**Sitio Web:** www.iglesiacatolica.org.bo/arzobispados/la-paz  
**Responsable Legal:** Mons. Percy Galván Flores (Arzobispo de La Paz)  

**Área o Rubro de Trabajo:**  
Institución religiosa de la Iglesia Católica dedicada a la administración pastoral, formación espiritual, servicios sacramentales y preservación del patrimonio histórico-religioso. Gestiona registros de sacramentos (bautizos, matrimonios, confirmaciones, defunciones) desde el período colonial hasta la actualidad.

**Cobertura:**  
- **Territorial:** Departamento de La Paz y provincias circundantes
- **Parroquias:** Más de 80 parroquias urbanas y rurales
- **Instituciones:** Colegios católicos, seminarios, centros pastorales
- **Alcance:** Regional con proyección nacional

**Público Meta:**  
- Fieles católicos del departamento de La Paz
- Personas que requieren certificados sacramentales para trámites legales
- Investigadores e historiadores que consultan archivos históricos
- Párrocos y personal administrativo de parroquias

**Responsable del Seguimiento de la Pasantía:**  
- **Nombre:** Ing. Miguel Ángel Pacheco Arteaga  
- **Cargo:** Coordinador Técnico del Proyecto Sacra360  
- **Correo:** mpacheco@arzobispadolapaz.org  
- **Teléfono:** (+591) 70123456  
- **Co-Responsable:** Maria del Rosario Bravo Aramayo (Directora de Archivo Histórico)

## 1.2 Descripción del área de trabajo

**Área de Desempeño:** Departamento de Sistemas y Archivo Histórico Digital

El área de trabajo se encuentra dentro de la **Coordinación de Transformación Digital del Arzobispado**, un departamento creado en 2024 con el objetivo de modernizar la gestión de registros sacramentales mediante tecnologías de información.

**Ubicación en el Organigrama:**

```
Arzobispo de La Paz (Mons. Percy Galván Flores)
    │
    ├── Vicario General
    │   └── Directora de Archivo Histórico (Maria del Rosario Bravo)
    │       └── Coordinación de Transformación Digital
    │           ├── Coordinador Técnico (Ing. Miguel Pacheco)
    │           ├── Equipo de Desarrollo (4 personas)
    │           │   ├── Pasante - Módulo AuthProfiles (Diego Morón)
    │           │   ├── Desarrollador - Módulo Documents
    │           │   ├── Desarrollador - Módulo OCR/HTR
    │           │   └── Especialista en IA
    │           └── Personal de Digitalización (3 operadores)
```

**Personal del Área:**

| N° | Nombre | Sexo | Edad Aprox. | Formación | Rol |
|----|--------|------|-------------|-----------|-----|
| 1 | Ing. Miguel Pacheco | M | 35 años | Ing. Sistemas | Coordinador Técnico |
| 2 | Maria del Rosario Bravo | F | 45 años | Archivista | Directora Archivo |
| 3 | Diego Morón (Pasante) | M | 22 años | Est. Ing. Sistemas | Dev. Frontend y AuthProfiles |
| 4 | Sebastian Pinto | M | 23 años | Est. Ing. Sistemas | Dev. Backend Sacramentos |
| 5 | Marco Reynold | M | 24 años | Est. Ing. Sistemas | Dev. OCR/HTR |
| 6-8 | Operadores Digitalización | Mixto | 25-40 años | Técnicos | Escaneo |

**Características del Equipo:**
- Equipo de 3 desarrolladores estudiantes trabajando en módulos independientes del sistema Sacra360
- Ambiente colaborativo con reuniones semanales de coordinación los miércoles
- Uso de metodologías ágiles adaptadas al contexto
- Trabajo remoto con coordinación por Slack y Google Meet
- Mentoría constante del coordinador técnico Ing. Pacheco

**Recursos Tecnológicos del Área:**
- Servidor físico Dell PowerEdge R740
- Infraestructura Docker para microservicios
- Repositorio Git corporativo
- Herramientas: VS Code, Figma, PostgreSQL, Redis, MinIO
- Equipos de escaneo profesional Epson DS-870

## 1.3 Descripción del cargo/puesto desempeñado

**Título del Cargo:** Desarrollador Full-Stack - Módulo de Autenticación y Gestión de Usuarios (AuthProfiles)

**Funciones Asignadas Formalmente:**

1. **Análisis y Relevamiento:**
   - Participar en reuniones de levantamiento de requerimientos con personal operativo
   - Identificar necesidades de seguridad y control de acceso específicas del contexto religioso
   - Documentar flujos de trabajo actuales de gestión de usuarios

2. **Diseño de Arquitectura:**
   - Diseñar mockups de interfaces de usuario en Figma
   - Definir estructura de base de datos para módulo de usuarios
   - Crear diagramas UML de procesos de autenticación
   - Diseñar sistema de roles y permisos (RBAC)

3. **Desarrollo Backend:**
   - Implementar API REST con FastAPI en Python
   - Desarrollar endpoints de autenticación con JWT
   - Crear sistema de gestión de usuarios (CRUD completo)
   - Implementar auditoría de acciones de usuarios
   - Desarrollar endpoints de reportes de usuarios y accesos
   - Aplicar medidas de seguridad (encriptación, headers, validaciones)

4. **Desarrollo Frontend:**
   - Implementar interfaces de usuario en React con Tailwind CSS
   - Desarrollar páginas: Login, Dashboard, Usuarios, Auditoría, Reportes, Perfil
   - Integrar frontend con API backend mediante Axios
   - Implementar guards de autenticación y autorización
   - Crear componentes reutilizables

5. **Seguridad:**
   - Implementar autenticación JWT con tokens de acceso
   - Encriptar contraseñas con bcrypt + salt
   - Configurar middlewares de seguridad (CORS, headers HTTP)
   - Desarrollar sistema de permisos basado en roles
   - Validar datos de entrada con Pydantic

6. **Testing y Calidad:**
   - Escribir tests unitarios con pytest
   - Realizar pruebas de integración de endpoints
   - Validar flujos de autenticación end-to-end
   - Documentar bugs y resoluciones

7. **Documentación:**
   - Elaborar manual de usuario del sistema
   - Crear manual técnico del módulo AuthProfiles
   - Generar diagramas de arquitectura y base de datos
   - Documentar APIs con descripciones de endpoints
   - Escribir READMEs de configuración y despliegue

8. **Despliegue:**
   - Configurar contenedores Docker
   - Crear archivos docker-compose.yml
   - Configurar variables de entorno
   - Documentar procedimientos de instalación

### Actividades realizadas en el centro de práctica

Durante las 203 horas de práctica distribuidas en 6 actividades principales (ver Anexo 8), se ejecutaron 185 tareas específicas:
- 37 horas: Relevamiento de información (29 reuniones + identificación de procesos)
- 8 horas: Análisis de infraestructura y herramientas
- 31.5 horas: Diseño del sistema (16 mockups + documentación de diseño)
- 56 horas: Desarrollo backend (18 endpoints) y frontend (6 páginas)
- 29 horas: Documentación técnica (10 diagramas + 2 manuales)
- 41.5 horas: Tareas adicionales (Docker, tests, pantallas complementarias)

---

# 2. NARRACIÓN DE LA EXPERIENCIA LABORAL

## 2.1 Descripción del trabajo desempeñado

El trabajo desempeñado se centró en tres áreas principales del sistema Sacra360: el diseño completo de interfaces de usuario para todos los módulos del sistema, el desarrollo del módulo de autenticación y gestión de usuarios (AuthProfiles), y la implementación de las pantallas principales del frontend. Todo esto en función de los objetivos de modernizar la gestión de registros sacramentales del Arzobispado de La Paz mediante tecnologías de información seguras y escalables.

**Relato del trabajo en función a objetivos y productos esperados:**

El primer objetivo fue analizar y diseñar el sistema de autenticación y autorización. Para esto se realizaron 29 reuniones con personal del Arzobispado durante julio y agosto, identificando 4 roles de usuario necesarios (Admin, Operador, Consulta, Auditor), flujos de trabajo actuales, y restricciones de seguridad específicas del contexto religioso. Este análisis resultó en la definición del stack tecnológico (FastAPI, React, PostgreSQL, JWT) y la matriz de permisos del sistema RBAC.

El segundo objetivo fue diseñar las interfaces de usuario. Durante septiembre y octubre se crearon 16 mockups de alta fidelidad en Figma abarcando todos los módulos del sistema: Login, Dashboard, Gestión de usuarios, Gestión de personas, Gestión de libros, Registros sacramentales, Digitalización de documentos, Reportes generales, y Bitácora de auditoría. Se definió la paleta de colores institucionales (azul #1e3a8a, dorado #d4af37), tipografía, iconografía y flujos de navegación. Estos diseños fueron validados iterativamente con personal del Arzobispado, realizándose readaptaciones finales en diciembre basadas en feedback de usuarios.

El tercer objetivo fue desarrollar e implementar el módulo AuthProfiles completo. El desarrollo backend inició en octubre con FastAPI, creando la arquitectura base (main.py, database.py, schemas, models). Durante noviembre se implementaron 30 endpoints REST distribuidos en 4 routers: autenticación (6 endpoints: login, register, me, change-password, logout, roles), usuarios (8 endpoints con CRUD completo), auditoría (4 endpoints con filtros avanzados), y reportes (5 endpoints de estadísticas). Se implementó autenticación JWT con expiración de 60 minutos, encriptación de contraseñas con bcrypt, sistema RBAC mediante middleware de permisos, y auditoría completa que registra todas las acciones en base de datos. En paralelo se desarrolló el frontend con React, implementando 6 páginas completamente funcionales e integradas con el backend: Login (autenticación JWT), Dashboard (estadísticas en tiempo real), Usuarios (tabla CRUD con filtros y paginación), Auditoría (filtros por fecha/usuario/acción), Reportes (métricas con períodos configurables), y Perfil (visualización de datos y cambio de contraseña con validación de fortaleza).

El cuarto objetivo fue generar documentación técnica profesional. En diciembre se crearon 7 diagramas UML en PlantUML (procesos de autenticación, gestión de usuarios, digitalización, reportes, actividad del sistema, estados de documento), diagrama de base de datos física con 14 tablas, diagramas de arquitectura de microservicios y despliegue con contenedores Docker. Se elaboró un Manual de Usuario de 940 líneas con 6 secciones explicando el uso del sistema para personal no técnico, y un Manual Técnico de 336 líneas con arquitectura, 30 endpoints documentados, flujos de autenticación, matriz RBAC, instalación, seguridad y troubleshooting.

**Rutina laboral:**

El trabajo se desarrolló en modalidad híbrida (remoto y presencial) durante 203 horas distribuidas de julio a diciembre. La rutina diaria consistía en:
- **Mañanas (9:00-13:00):** Desarrollo de funcionalidades backend o frontend según fase del proyecto, commits frecuentes a repositorio Git con mensajes descriptivos.
- **Tardes (14:00-18:00):** Continuación de desarrollo, testing de funcionalidades implementadas, documentación de código, integración de componentes.
- **Miércoles:** Reuniones semanales de coordinación de 2 horas con Ing. Pacheco y equipo de desarrollo (Sebastian, Marco) para revisión de avances, resolución de bloqueos, y planificación de siguiente sprint.
- **Comunicación asíncrona:** Uso de Slack diariamente para consultas técnicas, coordinación con otros desarrolladores sobre contratos de API, y reporte de issues.
- **Validaciones:** Sesiones quincenales de 1 hora con personal del Arzobispado para validar mockups y funcionalidades implementadas.

La intensidad del trabajo varió según fase: las semanas de diseño de mockups (septiembre) y desarrollo intensivo (diciembre semana 1 con 60.5 horas) requirieron mayor dedicación, mientras las semanas de reuniones y coordinación fueron más breves.

**Destrezas laborales demandadas:**

Las destrezas técnicas requeridas incluyeron:
- **Programación full-stack:** Python 3.11 con FastAPI para backend (decoradores, async/await, dependencias), JavaScript ES6+ con React 19 para frontend (hooks, context API, componentes funcionales), SQL para queries y diseño de base de datos PostgreSQL.
- **Diseño UI/UX:** Uso de Figma para mockups de alta fidelidad, comprensión de principios de diseño (jerarquía visual, espaciado, tipografía), diseño responsive, y prototipado de flujos de usuario.
- **Arquitectura de software:** Comprensión de arquitectura de microservicios, patrón MVC adaptado a FastAPI, diseño de APIs REST con principios RESTful, separación de responsabilidades en capas (presentación, lógica, persistencia).
- **Seguridad informática:** Implementación de autenticación JWT, encriptación con bcrypt, configuración de CORS, headers de seguridad HTTP (X-Frame-Options, HSTS, CSP), validación de datos con Pydantic, prevención de inyección SQL mediante ORM.
- **DevOps básico:** Configuración de contenedores Docker, docker-compose para orquestación de 4 servicios, manejo de variables de entorno, y scripts de inicialización de base de datos.

Las destrezas blandas demandadas incluyeron:
- **Trabajo colaborativo:** Coordinación efectiva con 2 desarrolladores trabajando en módulos interdependientes, establecimiento de contratos de API claros, resolución de conflictos en integración de componentes.
- **Comunicación con stakeholders:** Capacidad de explicar conceptos técnicos (JWT, RBAC, APIs) a personal del Arzobispado sin formación en sistemas, recepción y procesamiento de feedback no técnico sobre interfaces.
- **Gestión de tiempo:** Priorización de tareas críticas vs deseables, estimación realista de tiempos de desarrollo, cumplimiento de deadlines bajo presión (semana intensiva de diciembre).
- **Aprendizaje autónomo:** Rápida adopción de FastAPI mediante documentación oficial sin experiencia previa, investigación de buenas prácticas de seguridad JWT, troubleshooting independiente de errores complejos.
- **Resolución de problemas:** Debugging sistemático de errores de integración frontend-backend, optimización de performance en servidor con recursos limitados, diseño de soluciones alternativas ante restricciones técnicas.
## 2.4 Principales productos/resultados obtenidos

Los productos se describen por semanas especificando días, horas de trabajo y número de horas cumplidas, según el registro del Anexo 8:

### MAYO - Semana 3 (2 horas)
**Días trabajados:** Martes 3 de Mayo  
**Horas cumplidas:** 2 horas (de 203 horas totales solicitadas)

**Tareas realizadas:**
- 1.1.1 Reuniones de coordinación con personal operativo de Archivo (1h)
- 1.2.1 Identificación de información en los libros de sacramentos (0:30h)
- 2.2 Revisión de infraestructura tecnológica disponible (0:30h)

**Resumen:** Primer contacto con el proyecto. Inducción inicial con personal del Archivo Histórico del Arzobispado, identificación preliminar de tipos de registros sacramentales en libros físicos (bautizos, matrimonios, confirmaciones, defunciones), y revisión del servidor Dell PowerEdge disponible.

**Producto:** Notas de reunión inicial con identificación preliminar de documentos y recursos tecnológicos disponibles.

### JULIO - Semana 3 (3 horas)
**Días trabajados:** Miércoles 3 de Julio  
**Horas cumplidas:** 3 horas

**Tareas realizadas:**
- 1.1.2 Reuniones de coordinación internas (1h)
- 1.3.1 Relevamiento de registros de Confirmación, Bautizo, Matrimonio, Defunción (1h)
- 1.4.2 Identificación de formato de índice de libros (0:30h)
- 1.5.1 Identificación de parroquias, colegios, instituciones (0:30h)

**Resumen:** Reunión de coordinación interna del equipo. Relevamiento detallado de los 4 tipos de registros sacramentales manejados por el Arzobispado. Identificación de estructura de más de 80 parroquias urbanas y rurales del departamento de La Paz.

**Producto:** Documento de relevamiento con tipos de registros y estructura organizacional del Arzobispado.

### JULIO - Semana 4 (2 horas)
**Días trabajados:** Lunes 4, Miércoles 4 de Julio  
**Horas cumplidas:** 2 horas

**Tareas realizadas:**
- 1.5.2 Identificación de actores en celebraciones (celebrantes por parroquia) (0:30h)
- 1.3.3 Relevamiento de índice de libro de registro (0:30h)
- 1.6.1 Relevamiento de procedimientos de registro de sacramentos (0:30h)
- 1.6.2 Relevamiento de flujos de búsquedas de sacramentos (0:30h)

**Resumen:** Identificación de procedimientos actuales manuales: llenado de formularios en papel, digitalización con escáner, búsqueda en libros físicos (proceso que podía tomar horas). Mapeo de actores involucrados (celebrantes, operadores de archivo).

**Producto:** Documento de flujos de trabajo actuales con identificación de problemas del proceso manual.

### AGOSTO - Semana 1 (1:30 horas)
**Días trabajados:** Jueves 1, Martes 1 de Agosto  
**Horas cumplidas:** 1:30 horas

**Tareas realizadas:**
- 1.1.3 Reuniones de coordinación internas (0:30h)
- 1.1.4 Reunión de coordinación con docente responsable Ing. Pacheco (1h)

**Resumen:** Coordinación con Ing. Pacheco para definir alcance del proyecto y asignación preliminar de módulos a cada miembro del equipo.

**Producto:** Acta de reunión con definición preliminar de alcance del módulo AuthProfiles.

### AGOSTO - Semana 2 (13:30 horas)
**Días trabajados:** Viernes 2, Lunes 2, Miércoles 2, Jueves 2 de Agosto  
**Horas cumplidas:** 13:30 horas

**Tareas realizadas:**
- 1.1.6 Reunión extra con personal operativo de archivos (1:30h)
- 1.2.2 Identificación de flujo de trabajo para llenado de registros (0:30h)
- 1.3.2 Relevamiento de certificados de Confirmación, Bautizo, Matrimonio, Defunción (0:30h)
- 1.4.1 Identificación de formato de certificados (0:30h)
- 1.1.7 Reunión de coordinación interna con Ing. Lourdes (1:30h)
- 2.1.1.1 Identificación de actores y roles del módulo (1h)
- 2.1.1.2 Identificación de entradas y salidas del módulo de usuarios (1h)
- 2.1.1.3 Identificación de herramientas, tecnologías y mecanismos de autenticación (0:30h)
- 2.1.1.4 Definición del flujo de trabajo del módulo de gestión de usuarios (1:30h)
- 2.1.1.5 Identificación de restricciones, niveles de acceso y validaciones (1h)
- 2.1.1.6 Redacción de documento de niveles de accesos (1h)
- 2.5 Asignación y división de tareas (0:30h)
- 2.1.1.3 Identificación de herramientas, tecnologías (0:30h)
- 2.1.1.4 Definición del flujo de trabajo (1:30h)

**Resumen:** Semana clave de análisis. Identificación de 4 roles de usuario necesarios (Admin, Operador, Consulta, Auditor). Definición del stack tecnológico: FastAPI para backend, React para frontend, PostgreSQL para BD, JWT para autenticación. Redacción de documento de niveles de acceso y matriz de permisos. Asignación formal de tareas: Diego responsable de módulo AuthProfiles completo (backend + frontend + diseño general).

**Producto:** Documento "Definición de Roles y Permisos - Sistema Sacra360" (5 páginas) con matriz de permisos, stack tecnológico y división de tareas del equipo.

[EVIDENCIA - DOCUMENTO ROLES]
Captura del documento: Tabla con 4 roles (Admin: acceso completo, Operador: CRUD registros de su parroquia, Consulta: solo lectura, Auditor: revisión de logs). Sección "Stack Tecnológico": FastAPI, React, PostgreSQL, JWT, Docker. Sección "División de Tareas": Diego (AuthProfiles + diseño), Sebastian (Sacramentos), Marco (OCR/HTR).

### AGOSTO - Semana 3 (1 hora)
**Días trabajados:** Martes 3 de Agosto  
**Horas cumplidas:** 1 hora

**Tareas realizadas:**
- 1.1.8 Reunión de coordinación interna (1h)

**Resumen:** Reunión de coordinación interna del equipo de desarrollo para sincronizar avances preliminares.

**Producto:** Minuta de reunión.

### AGOSTO - Semana 4 (3:30 horas)
**Días trabajados:** Jueves 4, Viernes 4, Lunes 4 de Agosto  
**Horas cumplidas:** 3:30 horas

**Tareas realizadas:**
- 1.1.9 Reunión de coordinación interna (1h)
- 1.1.10 Reunión con Ing. Pacheco (1:30h)
- 1.1.11 Reunión con Ing. Pacheco (0:30h)
- 2.3 Identificación de servidores a usar (0:30h)
- 2.4 Identificación de framework del sistema (0:30h)

**Resumen:** Coordinación con Sebastian Pinto sobre integración entre AuthProfiles y módulo de Sacramentos. Definición de contratos de API para compartir datos de usuarios. Identificación final de servidores y frameworks a usar.

**Producto:** Documento de contratos de API entre módulos definiendo endpoints compartidos y formatos JSON (IDs en UUID, estructura de respuestas).

[EVIDENCIA - CONTRATOS API]
Google Doc compartido con sección "AuthProfiles → Sacramentos": endpoint GET /api/v1/auth/usuarios/{id} con response JSON, y sección "AuthProfiles → OCR/HTR": endpoint POST /api/v1/auth/validate-token. Comentarios de Sebastian y Marco confirmando formato.

### SEPTIEMBRE - Semana 1 (4:30 horas)
**Días trabajados:** Miércoles 1, Jueves 1 de Septiembre  
**Horas cumplidas:** 4:30 horas

**Tareas realizadas:**
- 1.1.12 Reunión con Ing. Pacheco y Ing. Lourdes (1h)
- 1.1.13 Reuniones de coordinación con personal operativo de Archivo (1:30h)
- 1.1.14 Reunión con Ing. Rivera y ayudantes (1h)
- 1.1.15 Reunión con Ing. Pacheco (1h)
- 1.4.3 Identificación de arreglos en el formato de índice de libros (0:30h)

**Resumen:** Múltiples reuniones de coordinación con equipo académico y personal del Archivo. Identificación final de arreglos necesarios en formato de índice de libros. Inicio de fase de diseño: sesión de brainstorming sobre flujos de usuario, estudio de referentes de diseño de sistemas administrativos.

**Producto:** Wireframes iniciales en papel con bocetos de flujos de usuario.

[EVIDENCIA - WIREFRAMES]
Fotografía de cuaderno: wireframe Login (logo, 2 campos, botón), wireframe Dashboard (sidebar, 4 tarjetas estadísticas, tabla). Anotaciones: "usuario ingresa → valida → dashboard", "tabla accesos - 10 últimos".

### SEPTIEMBRE - Semana 4 (19.5 horas)
**Días trabajados:** Lunes 26, Martes 27, Miércoles 28, Jueves 29, Viernes 30 de Septiembre  
**Horas cumplidas:** 19.5 horas

**Tareas realizadas:**
- 3.1.1 Mockup de inicio de sesión (2h)
- 3.1.2 Desarrollo del dashboard principal con navegación (1:30h)
- 3.1.3 Diseño de módulo de gestión de usuarios y roles (1:30h)
- 3.1.4 Interfaz de gestión de personas (1:30h)
- 3.1.5 Diseño de gestión de libros (2h)
- 3.1.6 Interfaz de gestión de registros sacramentales (2h)
- 3.1.7 Módulo de digitalización de documentos (1:30h)
- 3.1.9 Mockup de reportes generales (1:30h)
- 3.1.10 Mockup de bitácora de auditoría (1h)
- 1.1.16 Reunión con Ing. Pacheco (1h)

**Resumen:** Semana intensiva de diseño. Creación de 9 mockups de alta fidelidad en Figma para todos los módulos del sistema. Definición de paleta de colores institucionales (azul #1e3a8a, dorado #d4af37), tipografía, iconografía y flujos de navegación. Validación de diseños con personal del Arzobispado.

**Producto:** 9 mockups completos en Figma: Login, Dashboard, Gestión de usuarios, Gestión de personas, Gestión de libros, Registros sacramentales, Digitalización, Reportes, Auditoría.

[EVIDENCIA MOCKUP LOGIN]
Mockup Login: Pantalla centrada con logo dorado del Arzobispado (escudo con cruz), título "Sistema Sacra360", campos Email y Contraseña con iconos, checkbox "Recordar sesión", botón azul "Iniciar Sesión", link "¿Olvidaste tu contraseña?" en gris claro.

[EVIDENCIA MOCKUP DASHBOARD]
Mockup Dashboard: Navbar superior con logo izquierda, "Bienvenido Admin" y avatar derecha. Sidebar izquierdo con 6 íconos + labels: Dashboard, Usuarios, Auditoría, Reportes, Personas, Perfil. Área principal con grid 2x2 de tarjetas: "Total Usuarios 156", "Usuarios Activos 142", "Accesos Hoy 45", "Acciones Hoy 128". Tabla inferior "Últimos Accesos" con 10 filas.

### OCTUBRE - Semana 1 (11 horas)
**Días trabajados:** Lunes 3, Martes 4, Miércoles 5, Jueves 6, Viernes 7 de Octubre  
**Horas cumplidas:** 11 horas

**Tareas realizadas:**
- 3.2.1 Definición de tipos de perfiles (Admin, Operador, Consulta) (0:30h)
- 3.2.2 Diseño de estructura de permisos por pantalla (1h)
- 3.2.3 Documentación de flujos de gestión de perfiles (1h)
- 3.3.1 Diseño de flujo de cambio de contraseña (0:30h)
- 3.3.2 Definición de políticas de contraseñas (0:30h)
- 3.3.3 Diseño de proceso de baja lógica de usuarios (0:30h)
- 3.4.1 Definición de roles del sistema (1h)
- 3.4.2 Matriz de permisos por módulo (0:30h)
- 3.4.3 Diseño de asignación de roles (0:30h)
- 3.5.1 Definición de políticas de seguridad del sistema (0:30h)
- 3.5.2 Diseño de sistema de auditoría conceptual (1h)
- 3.5.3 Definición de logs y monitoreo (0:30h)
- 1.1.17 Reunión con Ing. Pacheco (1h)

**Resumen:** Semana de diseño conceptual del sistema de gestión de usuarios. Definición de 3 perfiles finales (Admin: acceso completo, Operador: CRUD limitado, Consulta: solo lectura). Diseño de matriz de permisos por pantalla. Documentación de flujos de cambio de contraseña y baja lógica. Definición de políticas de contraseñas (mínimo 8 caracteres, mayúscula, número). Políticas de seguridad: encriptación bcrypt, tokens JWT 60min, auditoría obligatoria.

**Producto:** Documento "Sistema de Permisos" (8 páginas): diagrama de roles, matriz de permisos por módulo, políticas de contraseñas, flujos de cambio y baja lógica.

[EVIDENCIA - SISTEMA PERMISOS]
Matriz con columnas (Rol, Usuarios, Personas, Libros, Sacramentos, Reportes, Auditoría). Políticas: 8+ caracteres, mayúscula, minúscula, número, especial, lista 100 passwords prohibidos, expiración 90 días. Diagrama flujo baja lógica: solicitar → confirmar → verificar registros → activo=false → auditoría.

### OCTUBRE - Semana 2 (33:30 horas)
**Días trabajados:** Lunes 10, Martes 11, Miércoles 12, Jueves 13, Viernes 14 de Octubre  
**Horas cumplidas:** 33:30 horas

**Tareas realizadas (Backend):**
- 4.1.1 Revisión de arquitectura y base de datos existente (0:30h)
- 4.1.2 Definir modelos Pydantic (1h)
- 4.1.3 Validaciones de campos (1h)
- 4.1.4 Pruebas de validación (1h)
- 4.1.5 Manejo de Errores (1h)
- 4.1.6 Documentación README_SACRA360 branch Diego (1:30h)
- 1.1.18 Reunión con Ing. Pacheco (1h)

**Tareas realizadas (Frontend - 11 pantallas):**
- 6.2.1 Pantalla Login (1:30h)
- 6.2.2 Pantalla Dashboard (1:30h)
- 6.2.3 Pantalla Gestión de usuarios (1:30h)
- 6.2.4 Pantalla Usuarios (1:30h)
- 6.2.5 Pantalla Roles y permisos (1:30h)
- 6.2.6 Pantalla Gestión de personas (1h)
- 6.2.7 Pantalla Gestión de libros (2h)
- 6.2.8 Pantalla Registros sacramentales (1h)
- 6.2.9 Pantalla Digitalización de documentos (1:30h)
- 6.2.10 Pantalla Reportes generales (1:30h)
- 6.2.11 Pantalla Bitácora auditoría (1h)
- 6.2.12 Modal datos duplicados (1h)
- 6.2.13 Layout global (1:30h)

**Resumen:** Semana más intensa de octubre. Inicio de desarrollo backend con FastAPI: revisión de arquitectura BD existente (PostgreSQL), definición de modelos Pydantic (LoginSchema, UserCreateSchema, UserUpdateSchema), implementación de validaciones de campos (formato email, longitud contraseña), pruebas con pytest, manejo de errores HTTPException (400/401/500). Desarrollo paralelo frontend: creación de 11 pantallas React con Tailwind CSS. Las pantallas de módulos de otros compañeros (personas, libros, sacramentos) se crearon como mockups visuales sin integración backend (a cargo de Sebastian).

**Productos:**
1. Código backend inicial: app/main.py (puerto 8004), app/database.py (PostgreSQL), schemas Pydantic, models SQLAlchemy, requirements.txt
2. Código frontend: 11 páginas React con Vite, Tailwind CSS, React Router

[EVIDENCIA - ESTRUCTURA BACKEND]
VS Code mostrando BACKEND/app/ con main.py, database.py, schemas/, models/. Terminal: "uvicorn running on http://127.0.0.1:8004".

[EVIDENCIA - ESTRUCTURA FRONTEND]
VS Code mostrando frontend/src/pages/ con 11 archivos .jsx. Login.jsx renderizado en navegador: fondo blanco, logo dorado, botón azul.

### OCTUBRE - Semanas 3-4 (2:30 horas)
**Días trabajados:** Miércoles 19, Miércoles 26 de Octubre  
**Horas cumplidas:** 2:30 horas

**Tareas realizadas:**
- 1.1.19 Reunión con Ing. Pacheco (1h)
- 1.1.20 Reunión con Ing. Pacheco (1h)
- 1.1.21 Reunión de coordinación internas (0:30h)

**Resumen:** Reuniones semanales de seguimiento con Ing. Pacheco para revisar avances del desarrollo inicial backend/frontend.

**Producto:** Minutas de reuniones.

### NOVIEMBRE - Semana 1 (14 horas)
**Días trabajados:** Lunes 7, Martes 8, Miércoles 9, Jueves 10, Viernes 11 de Noviembre  
**Horas cumplidas:** 14 horas

**Tareas realizadas:**
- 4.1.7 Análisis de endpoints auth existentes (0:30h)
- 4.1.8 Implementación POST /auth/login (1h)
- 4.1.9 Implementación POST /auth/register (1h)
- 4.1.10 Implementación GET /auth/me (1h)
- 4.1.11 Implementación GET /auth/change-password (1h)
- 4.1.12 Implementación POST /auth/logout (1h)
- 4.1.13 Implementación GET /auth/roles (1:30h)
- 6.1.3 Adaptación de Docker a requerimientos de mi estación (1:30h)
- 6.1.4 Configuración de .env (0:30h)
- 4.2.1 Configuración de JWT en auth_utils.py (1:30h)
- 4.2.2 Implementación create_access_token() (1:30h)
- 4.2.3 Implementación get_current_user() middleware (1:30h)
- 4.2.4 Configuración bcrypt para passwords (0:30h)
- 4.2.5 Pruebas de endpoints con Postman (0:30h)

**Resumen:** Desarrollo inicial del módulo de autenticación. Implementación de 6 endpoints auth en FastAPI: POST /login (genera JWT), POST /register (nuevo usuario), GET /me (perfil actual), GET /change-password (cambio contraseña), POST /logout (cierra sesión), GET /roles (lista roles disponibles). Configuración JWT en auth_utils.py: función create_access_token() genera token con SECRET_KEY y expiración 60min, get_current_user() middleware verifica token en header Authorization. Configuración bcrypt con salt rounds=12 para hash contraseñas. Adaptación Docker Compose a recursos locales (ajuste memoria contenedores). Archivo .env con variables SECRET_KEY, DATABASE_URL, JWT_EXPIRATION_MINUTES. Pruebas Postman exitosas validando JWT generación/validación.

**Productos:**
1. 6 endpoints autenticación funcionales (auth_router.py)
2. Utilidades JWT (auth_utils.py con create_access_token, get_current_user)
3. Configuración Docker adaptada + .env

[EVIDENCIA - ENDPOINTS AUTH]
Postman mostrando colección "AuthProfiles" con 6 requests. Request POST /auth/login seleccionado: Body con {"email": "admin@test.com", "password": "admin123"}, Response 200 con {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer", "expires_in": 3600}. Request GET /auth/me con header "Authorization: Bearer eyJ..." → Response 200 {"id": 1, "nombre": "Admin", "email": "admin@test.com", "rol": "ADMINISTRADOR"}.

[EVIDENCIA - DOCKER COMPOSE]
Terminal mostrando docker-compose up: "auth-service_1 | INFO: Started server", "postgres_1 | database ready". Comando "docker ps" mostrando contenedor sacra360_auth-service puerto 8004.

### NOVIEMBRE - Semana 2 (12:30 horas)
**Días trabajados:** Lunes 14, Martes 15, Miércoles 16, Jueves 17, Viernes 18 de Noviembre  
**Horas cumplidas:** 12:30 horas

**Tareas realizadas:**
- 4.2.6 Validación de tokens en endpoints (1h)
- 4.2.7 Manejo de expiración de tokens (1:30h)
- 4.3.1 Análisis de tabla auditoria en BD (0:30h)
- 4.3.2 Creación de entidad Auditoria en user_entity.py (0:30h)
- 4.3.3 Implementación función registrar_auditoria() (1h)
- 4.4.1 Aplicar Depends(get_current_user) en /auth/me (1h)
- 4.4.2 Proteger endpoint /auth/change-password (0:30h)
- 4.4.3 Proteger endpoint /auth/logout (0:30h)
- 4.4.4 Proteger endpoint /auth/roles (0:30h)
- 4.5.1 Análisis de tabla roles en BD (0:30h)
- 4.5.2 Implementación GET /auth/roles (listar) (0:30h)
- 4.5.3 Verificación de relación usuario-rol (0:30h)
- 4.6.1 Configuración CORS en main.py (1h)
- 4.6.2 Validación con Pydantic en DTOs (1:30h)
- 4.6.3 Implementación bcrypt con salt (1:30h)
- 4.6.6 Implementación PasswordUtils con validaciones (1h)
- 4.6.7 Configuración OAuth2PasswordBearer (0:30h)

**Resumen:** Mejoras de seguridad y auditoría. Validación tokens JWT en todos los endpoints protegidos, manejo expiración automática (60min). Creación entidad Auditoria en BD (tabla con usuario_id, acción, timestamp, ip), función registrar_auditoria() para logs automáticos. Protección endpoints con Depends(get_current_user): verificación token en /auth/me, /change-password, /logout, /roles. Análisis tabla roles, implementación GET /auth/roles listando Admin/Operador/Consulta. Configuración CORS permitiendo localhost:5173 y localhost:3000. Validaciones Pydantic en todos los schemas (LoginSchema, UserSchema). Bcrypt con salt rounds=12. PasswordUtils con validaciones de fortaleza (8+ caracteres, mayúscula, número). OAuth2PasswordBearer configurado.

**Productos:**
1. Sistema auditoría backend (entidad + función registrar_auditoria)
2. Endpoints protegidos con JWT (Depends middleware)
3. Seguridad mejorada (CORS, bcrypt, Pydantic, PasswordUtils)

[EVIDENCIA - AUDITORÍA]
VS Code mostrando user_entity.py con clase Auditoria: id, usuario_id, accion, timestamp, ip_address. Función registrar_auditoria(db, usuario_id, accion) en utils. Postman POST /auth/login → BD muestra nuevo registro auditoria: usuario_id=1, accion="LOGIN", timestamp="2025-11-14 10:30".

### NOVIEMBRE - Semana 3 (1 hora)
**Días trabajados:** Miércoles 23 de Noviembre  
**Horas cumplidas:** 1 hora

**Tareas realizadas:**
- 1.1.23 Reunión con Ing. Pacheco (1h)

**Resumen:** Reunión de seguimiento con Ing. Pacheco para revisar avances del módulo AuthProfiles.

**Producto:** Minuta de reunión.

### NOVIEMBRE - Semana 4 (10:30 horas)
**Días trabajados:** Lunes 28, Martes 29, Miércoles 30 de Noviembre  
**Horas cumplidas:** 10:30 horas

**Tareas realizadas:**
- 1.1.24 Reunión de coordinación internas (1h)
- 1.1.24 Reunión de coordinación Ing. Rivera (3h)
- 4.3.4 Integración en endpoint /auth/login (0:30h)
- 4.6.4 HTTPException con status codes (1h)
- 4.6.5 Logging de errores con logger (1h)
- 6.1.1 Test de autenticación básicos (1h)
- 6.1.2 Creación de SCHEMA DE AUTENTICACIÓN Y USUARIOS (0:30h)
- 6.2.14 Adaptar diseño interfaz de Login.jsx (0:30h)
- 6.2.15 Integración con endpoint POST /auth/login (1h)
- 6.2.16 Manejo de respuesta JWT del backend (1:30h)
- 6.2.17 Integración Login.jsx funcional con backend (1:30h)
- 3.1.11 Mockup de registro digital de nuevos sacramentos (1:30h)

**Resumen:** Reuniones coordinación: 1h interna equipo, 3h con Ing. Rivera planificando integración OCR. Integración función registrar_auditoria() en POST /auth/login (log automático cada login exitoso). Manejo errores: HTTPException con status codes correctos (400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Server Error), logging errores con Python logger en archivo app.log. Tests autenticación básicos con pytest: test_login_success(), test_login_invalid_credentials(), test_token_expiration(). Documentación schemas autenticación en comentarios docstring. Integración frontend Login.jsx: adaptación diseño mockup, axios POST /auth/login, manejo respuesta JWT (guardar en localStorage), redirect a /dashboard. Mockup adicional registro digital sacramentos (formulario con campos celebrante, fecha, libro).

**Productos:**
1. Auditoría integrada en login (logs automáticos)
2. Manejo errores robusto (HTTPException + logger)
3. Tests autenticación (pytest)
4. Login.jsx funcional integrado
5. Mockup registro sacramentos

[EVIDENCIA - LOGIN FUNCIONAL]
Navegador mostrando Login.jsx: formulario con campos Email y Password. DevTools Network: POST http://localhost:8004/api/v1/auth/login → Status 200, Response {"access_token": "eyJ..."}. Application tab: localStorage con key "authToken". Console sin errores. Página redirige a /dashboard.

### DICIEMBRE - Semana 1 (60:30 horas)
**Días trabajados:** Lunes 5, Martes 6, Miércoles 7, Jueves 8, Viernes 9, Sábado 10, Domingo 11 de Diciembre  
**Horas cumplidas:** 60:30 horas

**Tareas realizadas (Backend - Usuarios):**
- 1.1.25 Reunión con Ing. Pacheco (1h)
- 1.1.26 Reunión con Ing. Pacheco (1h)
- 1.1.27 Reunión con Ing. Pacheco (0:30h)
- 4.1.14 Mejoras en usuarios_router.py (validaciones) (1:30h)
- 4.1.15 Endpoint POST /usuarios con validaciones (1h)
- 4.1.16 Endpoint PUT /usuarios/{id} actualización (0:30h)
- 4.1.17 Endpoint DELETE /usuarios/{id} baja lógica (0:30h)

**Tareas realizadas (Backend - Auditoría):**
- 4.2.8 Refactor auth_utils.py con mejores prácticas (1:30h)
- 4.3.4 Endpoint GET /auditoria con filtros avanzados (1h)
- 4.3.5 Paginación en auditoría (0:30h)
- 4.3.6 Mejoras en auditoria_router.py (1h)

**Tareas realizadas (Backend - Seguridad):**
- 4.6.8 Creación middleware/security.py con headers (0:30h)
- 4.6.9 Implementación SecurityHeadersMiddleware (0:30h)
- 4.6.10 Headers: X-Frame-Options, X-Content-Type-Options (0:30h)
- 4.6.11 Headers: X-XSS-Protection, Strict-Transport-Security (0:30h)
- 4.6.12 Content-Security-Policy configuration (0:30h)
- 4.6.13 Creación middleware/permissions.py RBAC (1h)
- 4.6.14 Implementación check_permissions() decorator (1h)
- 4.6.15 Sistema de permisos (permission guard) (1h)

**Tareas realizadas (Backend - Reportes):**
- 4.7.1 Creación routers/reportes_router.py (1h)
- 4.7.2 Endpoint GET /reportes/usuarios/resumen (1h)
- 4.7.3 Endpoint GET /reportes/usuarios/por-rol (0:30h)
- 4.7.4 Endpoint GET /reportes/usuarios/activos-inactivos (0:30h)
- 4.7.5 Endpoint GET /reportes/accesos/resumen (1h)
- 4.7.6 Endpoint GET /reportes/accesos/por-usuario (0:30h)
- 4.7.7 Endpoint GET /reportes/accesos/ultimos-accesos (0:30h)
- 4.7.8 Endpoint GET /reportes/estadisticas/generales (1:30h)
- 4.7.9 Filtros por periodo (7/30/90/365 días) (0:30h)
- 4.7.10 Documentación README reportes (0:30h)

**Tareas realizadas (Frontend - Integración):**
- 6.2.18 Integración con API de estadísticas (2h)
- 6.2.19 Gráficos y visualización de datos (1:30h)
- 6.2.20 Implementación página Reportes.jsx completa (1:30h)
- 6.2.21 Integración de filtros por periodo (7/30/90/365 días) (1:30h)
- 6.2.22 Integración API en Auditoría.jsx (2h)
- 6.2.23 Arreglos pantalla Auditoria.jsx (0:30h)
- 6.2.24 Implementación página Auditoria.jsx completa (1:30h)
- 6.2.25 Implementación de filtros de búsqueda (1h)
- 6.2.26 Creación página Perfil.jsx completa (1h)
- 6.2.27 Vista usuario actual en pantalla perfil (0:30h)
- 6.2.28 Integración cambio de contraseña personal (1h)

**Tareas realizadas (Documentación UML):**
- 5.1.1 Creación diagrama proceso autenticación (LOGIN/JWT) (1h)
- 5.1.2 Creación diagrama proceso gestión usuarios (CRUD) (1h)
- 5.1.3 Creación diagrama proceso digitalización documentos (1h)
- 5.1.4 Creación diagrama proceso generación reportes (1h)
- 5.1.5 Creación diagrama de actividad del sistema completo (1h)
- 5.1.6 Creación diagrama de estados de documento (1h)
- 5.1.7 Documentación README de diagramas UML (1h)

**Resumen:** Semana más intensa de la pasantía con 60.5 horas. 3 reuniones seguimiento con Ing. Pacheco. Finalización módulo usuarios backend: 4 endpoints (POST crear con validaciones email único/formato, PUT actualizar datos, DELETE baja lógica activo=false, validaciones mejoradas). Finalización auditoría: GET con filtros avanzados (fecha inicio/fin, usuario_id, tipo acción), paginación (página, límite), refactor auth_utils.py mejorando legibilidad. Implementación completa seguridad: SecurityHeadersMiddleware con 5 headers HTTP seguros (X-Frame-Options DENY, X-Content-Type-Options nosniff, X-XSS-Protection, HSTS max-age=31536000, CSP default-src 'self'), permissions.py con sistema RBAC completo (check_permissions decorator verifica lista permisos requeridos por endpoint). Creación módulo reportes: 8 endpoints estadísticas (resumen total usuarios, distribución por rol Admin/Operador/Consulta, activos/inactivos, resumen accesos, accesos por usuario, últimos 10 accesos, estadísticas generales, filtros periodo 7/30/90/365 días). Integración frontend completa: Reportes.jsx (gráficos estadísticas tiempo real con recharts), Auditoría.jsx (filtros fecha/usuario/acción + paginación + tabla + API), Perfil.jsx (vista datos usuario actual + cambio contraseña con validación fortaleza). Documentación UML: 7 diagramas PlantUML (.puml) - proceso autenticación JWT, gestión usuarios CRUD, digitalización, reportes, actividad sistema completo, estados documento (PENDIENTE/PROCESANDO/COMPLETADO), README explicando cada diagrama.

**Productos:**
1. Módulo usuarios backend completo (4 endpoints finales)
2. Módulo auditoría completo (filtros + paginación)
3. Middlewares seguridad (headers HTTP + RBAC)
4. Módulo reportes completo (8 endpoints estadísticas)
5. 3 páginas frontend integradas (Reportes, Auditoría, Perfil)
6. 7 diagramas UML en PlantUML

[EVIDENCIA - REPORTES FRONTEND]
Navegador mostrando Reportes.jsx: 4 cards superiores (Total Usuarios 156, Activos 142, Accesos Hoy 45, Acciones Hoy 128). Dropdown "Período: 30 días". 2 gráficos: barras (Usuarios por Rol - Admin 3, Operador 15, Consulta 138) y líneas (Accesos Últimos 7 Días). DevTools Network: GET /reportes/estadisticas/generales?periodo=30 → Status 200.

[EVIDENCIA - MIDDLEWARE RBAC]
VS Code mostrando middleware/permissions.py con función check_permissions(required_permissions: List[str]). Postman: GET /usuarios/listar con token rol "Consulta" → Response 200. POST /usuarios/crear con token rol "Consulta" → Response 403 {"detail": "Permisos insuficientes"}.

### DICIEMBRE - Semana 2 (20:30 horas)
**Días trabajados:** Lunes 12, Martes 13, Miércoles 14, Jueves 15, Viernes 16 de Diciembre  
**Horas cumplidas:** 20:30 horas

**Tareas realizadas (Backend - Mejoras finales):**
- 1.1.28 Reunión con Ing. Pacheco (1h)
- 1.1.29 Reunión con Ing. Pacheco (0:30h)
- 4.1.18 Endpoint PATCH /usuarios/{id}/activar reactivación (0:30h)

**Tareas realizadas (Frontend - Mejoras UX):**
- 6.2.29 Arreglos paginación en Auditoría.jsx (0:30h)
- 6.2.30 Mejoras de UI/UX en paginación (números, botones) (0:30h)
- 6.2.31 Contador de páginas y registros (0:30h)

**Tareas realizadas (Mockups readaptados):**
- 3.1.12 Readaptación de mockup de gestión de usuarios en Figma por nuevos requerimientos (1:30h)
- 3.1.13 Readaptación de mockup de auditoría en Figma por cambios en filtros y estructura (1h)
- 3.1.14 Readaptación de mockup de reportes en Figma con nuevas estadísticas y gráficos (1:30h)
- 3.1.15 Readaptación de mockup de perfil de usuario en Figma con sección de seguridad (1h)
- 3.1.16 Ajustes finales de cambios realizados por el equipo y validación de mockups readaptados (2:30h)

**Tareas realizadas (Documentación - Base Datos):**
- 5.2.1 Creación diagrama físico completo (1h)
- 5.2.2 Documentación técnica base de datos física (1h)
- 5.2.3 Definición de índices y relaciones (1h)
- 5.2.4 Scripts SQL de ejemplo y consultas útiles (0:30h)

**Tareas realizadas (Documentación - Arquitectura):**
- 5.3.1 Diagrama arquitectura de microservicios (1h)
- 5.3.2 Diagrama arquitectura en capas (1h)
- 5.3.3 Diagrama de componentes detallado (1h)
- 5.3.4 Documentación completa arquitectura (1h)
- 5.3.5 Documentación de patrones de diseño aplicados (1h)
- 5.3.6 Documentación de flujos de datos (1h)
- 5.3.7 Documentación de seguridad (JWT, RBAC, bcrypt) (1h)

**Tareas realizadas (Documentación - Despliegue):**
- 5.4.1 Diagrama de despliegue con PlantUML (0:30h)
- 5.4.2 Documentación arquitectura de contenedores (1h)
- 5.4.3 README completo de despliegue (1:30h)

**Tareas realizadas (Manuales):**
- 5.5.1 Manual de Usuario (3h)
- 5.5.2 Manual Técnico del Módulo AuthProfiles (3h)
- 5.5.3 Manual de pasantía (2:30h)

**Resumen:** Semana final de cierre de pasantía. Arreglos finales UX: endpoint PATCH /activar (reactivación usuarios), mejoras paginación Auditoría (contador "Mostrando 1-10 de 156", botones navegación, números página). Readaptación 4 mockups Figma según feedback final: Gestión usuarios (filtros adicionales rol/estado), Auditoría (estructura tabla mejorada), Reportes (nuevos gráficos estadísticas), Perfil (sección seguridad ampliada). Documentación base datos física: diagrama completo 14 tablas con relaciones, índices, scripts SQL. Documentación arquitectura: 7 documentos (microservicios, capas, componentes, patrones diseño, flujos datos, seguridad JWT/RBAC/bcrypt). Documentación despliegue: diagrama PlantUML, arquitectura-contenedores.md (4 servicios Docker), README paso a paso. Creación 3 manuales: Usuario (940 líneas, 6 secciones, capturas pantallas), Técnico (336 líneas, 30 endpoints documentados), Pasantía (experiencia completa).

**Productos:**
1. Endpoint PATCH /activar + mejoras paginación frontend
2. 4 mockups readaptados Figma validados
3. Documentación BD física (diagrama + scripts SQL)
4. Documentación arquitectura (7 documentos técnicos)
5. Documentación despliegue (diagrama + README)
6. Manual Usuario (940 líneas)
7. Manual Técnico (336 líneas)
8. Manual Pasantía

[EVIDENCIA - MOCKUPS READAPTADOS]
Figma mostrando 4 mockups actualizados: Gestión usuarios (filtros rol/estado agregados arriba tabla), Auditoría (columnas reorganizadas: Fecha, Usuario, Acción, Detalle, IP), Reportes (gráfico pie agregado "Distribución por rol"), Perfil (nueva sección "Seguridad" con toggle 2FA y botón "Cerrar todas las sesiones").

[EVIDENCIA - MANUAL USUARIO]
VS Code mostrando MANUAL_USUARIO_SACRA360.md: 940 líneas, estructura con ## Login, ## Dashboard, ## Usuarios, ## Auditoría, ## Reportes, ## Perfil. Sección Usuarios abierta mostrando pasos: "1. Click en Usuarios sidebar", "2. Click botón Agregar Usuario", "3. Llenar formulario (Nombre, Email, Rol)", "4. Click Guardar". Descripciones textuales de capturas pantallas.

## 2.2 Principales problemas/dificultades enfrentadas
2.2 Principales problemas/dificultades enfrentadas
Durante el desarrollo de la práctica se enfrentaron diversos desafíos técnicos, organizacionales y de aprendizaje:

1. Relacionamiento con el Equipo de Trabajo:
Problema: Dentro del equipo entre 2 integrantes ya teníamos una dinámica bien definida de desarrollo de una manera en la que nuestra comunicación fue excelente y el avance de nuestras tareas no perjudicaba el desarrollo del otro, pero el 3er integrante no tuvimos ningún proyecto juntos en anteriores semestres. 
Impacto: La desconexión con el tercer desarrollador terminó haciendo que tengamos ciertos conflictos con las asignaciones y los tiempos lo cual retrasaba el avance por la necesidad de rehacer ciertas tareas ya que por la mala organización y comunicación de ambas partes habían conflictos

2. Cumplimiento de Plazos:
Problema: La fecha de entrega inicial era finales de octubre, pero debido a la desorganización por parte del equipo, se retrasaron las actividades y no se presentaron las funcionalidades esperadas para el plazo indicado.
Impacto: Fue necesario extender la práctica hasta el 12 de diciembre para completar las actividades.

3. Competencias para Hacer el Trabajo:
Problema A - JWT y Seguridad: Conceptos de JWT (payload, firma, expiración), diferencia entre autenticación y autorización, y buenas prácticas de seguridad (almacenamiento de tokens, refresh tokens, CORS) no los tenia claros inicialmente.

Impacto: La primera implementación de JWT fue muy básica y no tenía definido la expiración de tokens.

Problema B - RBAC Complejo: El sistema de permisos requerido era más granular que un simple "Admin puede todo". Se necesitaban permisos como "Operador puede crear usuarios SOLO de su parroquia", "Auditor puede ver logs pero no modificar", reglas que no estaban bien definidas al inicio.

Impacto: La tabla de permisos se rediseñó varias veces. La versión final simplificó a 4 roles básicos (Admin, Digitalizador, Consultor y Usuario) postergando permisos por parroquia para versión 2.0.

Problema C - Testing: No se tenía experiencia escribiendo tests automatizados con pytest.
Impacto: Los tests se escribieron al final en lugar de usar TDD. Varios endpoints no tienen tests automatizados.

4. Depuración de Errores Complejos:
Problema: Error intermitente "CORS policy: No 'Access-Control-Allow-Origin' header" que aparecía solo en producción (Docker) pero no en desarrollo local.

Impacto: Se perdieron horas de avance tratando de reproducir el error. Finalmente se identificó que el middleware CORS en FastAPI debe agregarse ANTES de incluir los routers, no después.




5. Integración Frontend-Backend:
Problema:  Los códigos de error HTTP no estaban estandarizados. Backend retornaba 500 Internal Server Error para validaciones fallidas que deberían ser 400 Bad Request. Frontend no manejaba correctamente errores 401 (no redirigía a login).

Impacto: La experiencia de usuario era confusa (mensajes de error genéricos "Error en el servidor"). Se requirió refactorización de manejo de errores en ambos lados durante la segunda semana de diciembre.

## 2.3 Procedimiento de resolución de los problemas/dificultades

**Solución 1 - Relacionamiento con el Equipo de Trabajo:**

Para mejorar la comunicación y coordinación con el tercer integrante del equipo, se implementaron las siguientes acciones:

- **Documento compartido de contratos de API:** Se creó un archivo "API Contracts" en Google Docs donde cada desarrollador documentaba sus endpoints con request/response JSON de ejemplo ANTES de implementar. Esto eliminó ambigüedades sobre qué esperaba cada módulo del otro.

- **Daily standups implementados:** Se establecieron reuniones diarias de 15 minutos por Google Meet (9:00 AM) donde cada desarrollador compartía: qué hizo ayer, qué hará hoy, qué bloqueos tiene. Esto incrementó la visibilidad de avances y permitió detectar conflictos tempranamente.

- **Estandarización de formatos:** Se acordó migrar todos los IDs a formato UUID universal. Se ejecutó script SQL `ALTER TABLE usuarios ALTER COLUMN id TYPE UUID` usando `gen_random_uuid()` para unificar el formato entre módulos AuthProfiles, Sacramentos y OCR/HTR.

- **Postman Collections compartidas:** Se creó una colección de Postman con ejemplos funcionales de cada endpoint exportable, permitiendo que cada desarrollador probara los endpoints de otros módulos sin tener que revisar código.

- **Asignación clara de responsabilidades:** Se definió explícitamente en documento compartido: Diego (AuthProfiles + diseño completo frontend), Sebastian (Sacramentos backend), Marco (OCR/HTR). Esto evitó duplicación de trabajo.

**Solución 2 - Cumplimiento de Plazos:**

Para sobrellevar el retraso en actividades y cumplir con la entrega:

- **Negociación de extensión:** Se comunicó proactivamente a los tutores académico (Mgr. Peredo) e institucional (Ing. Pacheco) sobre el retraso debido a desorganización inicial del equipo. Se negoció extensión de fecha límite de fines de octubre a 12 de diciembre (6 semanas adicionales).

- **Repriorización de tareas:** Se realizó sesión de planning con Ing. Pacheco para identificar tareas críticas vs deseables:
  - **Crítico (prioridad 1):** Módulo AuthProfiles funcional (login, CRUD usuarios, auditoría)
  - **Importante (prioridad 2):** Integración frontend-backend completa
  - **Deseable (prioridad 3):** Tests automatizados, optimizaciones de performance
  
- **Trabajo intensivo final:** Durante las últimas 2 semanas de noviembre y primera de diciembre se trabajó intensivamente (10-16 horas diarias algunos días según anexo 8) para recuperar tiempo perdido y completar funcionalidades críticas.

- **Ejecución en paralelo:** Los mockups readaptados se trabajaron en paralelo con desarrollo de documentación para aprovechar mejor el tiempo disponible.

**Solución 3 - Competencias para Hacer el Trabajo:**

**Problema A - JWT y Seguridad:**

- **Estudio autodidacta estructurado:** Lectura del RFC 7519 (JSON Web Tokens) completo para comprender estructura (header.payload.signature), algoritmos de firma (HS256), y buenas prácticas de expiración.

- **Implementación de mejoras de seguridad:**
  - Migración de SECRET_KEY hardcodeada a variables de entorno (.env) usando python-dotenv
  - Implementación de expiración de tokens a 60 minutos: `expires_delta = timedelta(minutes=60)`
  - Configuración CORS restrictiva: `origins=["http://localhost:5173"]` solo frontend conocido
  - Agregado de headers de seguridad con middleware SecurityHeadersMiddleware siguiendo recomendaciones OWASP (X-Frame-Options, HSTS, CSP)
  - Validación de tokens en CADA request protegido usando `Depends(get_current_user)`

- **Code reviews con Ing. Pacheco:** Revisiones semanales del código de autenticación donde el coordinador técnico explicaba conceptos de diferencia entre autenticación (¿quién eres?) y autorización (¿qué puedes hacer?), y validaba que la implementación fuera segura.

**Problema B - RBAC Complejo:**

- **Sesión de diseño con stakeholders:** Reunión de 2 horas con Ing. Pacheco y personal operativo del Arzobispado (Maria del Rosario Bravo) para definir roles y permisos REALES necesarios, no asumir requisitos.

- **Simplificación progresiva:** Después de 3 iteraciones de diseño de tabla de permisos, se optó por simplificar a 4 roles básicos:
  - **Admin:** Acceso total al sistema
  - **Digitalizador:** CRUD registros sacramentales de su parroquia
  - **Consultor:** Solo lectura de registros
  - **Usuario:** Acceso limitado a consultas propias
  
  Los permisos granulares por parroquia se postergaron para versión 2.0.

- **Implementación de decorator reutilizable:** Se creó función `check_permissions(["Admin", "Digitalizador"])` reutilizable en todos los routers, evitando duplicación de lógica de validación.

- **Documentación de matriz de permisos:** Se documentó matriz completa en manual técnico para que futuras extensiones del sistema puedan agregar permisos sin romper arquitectura.

**Problema C - Testing:**

- **Instalación de herramientas:** Configuración de pytest, pytest-asyncio (para funciones async), httpx (cliente HTTP para testing de FastAPI).

- **Fixtures básicos:** Creación de fixtures en conftest.py:
  - `test_client`: Cliente de prueba de FastAPI
  - `test_db`: Base de datos temporal en memoria para tests
  
- **Tests de endpoints críticos:** Aunque no se logró TDD completo, se priorizaron tests de autenticación:
  - `test_login_success`: Verifica login con credenciales válidas
  - `test_login_invalid_credentials`: Verifica rechazo de credenciales incorrectas
  - `test_protected_endpoint_without_token`: Verifica protección de endpoints

- **Aceptación de limitación:** Se reconoció que cobertura final de 40% es inferior al estándar industrial de 70%, pero se priorizó entregar funcionalidad working sobre cobertura perfecta de tests dado el tiempo limitado.

**Solución 4 - Depuración de Errores Complejos (CORS):**

Para resolver el error intermitente de CORS que aparecía solo en Docker:

- **Reproducción sistemática:** Se creó checklist de diferencias entre ambiente local y Docker: versión de Python, orden de carga de módulos, configuración de FastAPI.

- **Revisión de documentación oficial:** Lectura detallada de documentación de FastAPI sobre orden de middlewares y configuración de CORS.

- **Identificación de causa raíz:** Se descubrió que el middleware CORS debe agregarse ANTES de incluir los routers. Código correcto:
```python
app = FastAPI()
app.add_middleware(CORSMiddleware, origins=["http://localhost:5173"], ...)
app.include_router(auth_router)  # Los routers VAN DESPUÉS del middleware
```

- **Testing en ambos ambientes:** Después del fix, se verificó que funcionara tanto en local como en Docker antes de considerar resuelto.

**Solución 5 - Integración Frontend-Backend:**

Para mejorar la experiencia de usuario con manejo de errores:

- **Estandarización de códigos HTTP:** Se definió convención clara:
  - 400 Bad Request: Errores de validación (email inválido, password corto)
  - 401 Unauthorized: Problemas de autenticación (token expirado, credenciales incorrectas)
  - 403 Forbidden: Problemas de autorización (sin permisos para acción)
  - 404 Not Found: Recurso no existe
  - 500 Internal Server Error: Errores del servidor

- **Excepciones personalizadas en backend:** Creación de HTTPException personalizadas en utils/exceptions.py con mensajes descriptivos en español:
```python
raise HTTPException(
    status_code=400,
    detail="El formato del email es inválido"
)
```

- **Interceptor de Axios en frontend:** Implementación de interceptor que captura errores 401 y redirige automáticamente a login:
```javascript
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      navigate('/login');
    }
    return Promise.reject(error);
  }
);
```

- **Mensajes de error user-friendly:** Reemplazo de mensajes técnicos "Error en el servidor" por mensajes específicos: "Tu sesión ha expirado, por favor inicia sesión nuevamente".

## 2.4 Principales productos/resultados obtenidos

Durante las 203 horas de pasantía se entregaron al Arzobispado de La Paz los siguientes productos tangibles:

**1. Módulo AuthProfiles completo (Funcional al 100%)**
- Backend: 30 endpoints REST implementados en FastAPI
- Frontend: 6 páginas React totalmente integradas
- Sistema RBAC con 3 roles (Admin, Operador, Consulta)
- Autenticación JWT con expiración de 60 minutos
- Auditoría completa de acciones de usuarios

**2. Base de datos diseñada e implementada**
- 3 tablas principales: Roles, usuarios, Auditoria
- Relaciones FK establecidas
- Índices optimizados en campos email y rol_id
- Población inicial con 5 usuarios de prueba

**3. Sistema de seguridad implementado**
- Bcrypt para hashing de contraseñas
- JWT para autenticación stateless
- CORS configurado para puerto 5173
- 5 headers HTTP seguros (X-Frame-Options, HSTS, CSP, X-Content-Type, X-XSS)
- Validación Pydantic en todos los endpoints
- Middleware de permisos por rol

**4. Infraestructura Docker**
- docker-compose.yml con 4 servicios
- PostgreSQL 15, Redis 7, MinIO, auth-service
- Variables de entorno configuradas
- Scripts de inicialización de BD

**5. Documentación técnica completa (73 páginas en total)**
- 7 diagramas UML en PlantUML
- Diagrama de base de datos física con 14 tablas
- Arquitectura de microservicios documentada
- Esquema de despliegue con contenedores
- README de configuración paso a paso

**6. Manual de Usuario (940 líneas)**
Documento MANUAL_USUARIO_SACRA360.md con:
- Sección Login: acceso con credenciales, recuperación de contraseña
- Sección Dashboard: explicación de 4 tarjetas de estadísticas y tabla de accesos
- Sección Usuarios: CRUD completo con capturas textuales
- Sección Auditoría: uso de filtros por fecha, usuario y acción
- Sección Reportes: interpretación de métricas por período
- Sección Perfil: visualización de datos y cambio de contraseña

**7. Manual Técnico (336 líneas)**
Documento INSTRUCCION_RESUMIDO.md con:
- Arquitectura en capas explicada
- Lista de 30 endpoints con request/response
- Flujo de autenticación JWT paso a paso
- Matriz RBAC de permisos por rol
- 8 pasos de instalación local
- 3 problemas comunes y soluciones
- Configuración de caché Redis con TTL 5 minutos

**8. Mockups de diseño (16 en total)**
- 9 mockups en Figma para módulo AuthProfiles
- 4 mockups readaptados en semana final
- 3 wireframes en papel para validación inicial
- Todos validados con personal del Arzobispado

**9. Código fuente versionado**
- Repositorio Git con historial completo
- 143 commits registrados
- Branches: main, development, feature/auth, feature/audit
- README.md con instrucciones de instalación


---

## CONCLUSIONES

### Formación Adquirida

**Fortalezas de la formación universitaria aplicadas:**

La carrera de Ingeniería en Sistemas Computacionales proporcionó una base sólida que fue directamente aplicable durante la pasantía. Las materias de **Programación Orientada a Objetos** facilitaron la comprensión de la arquitectura de FastAPI y los modelos SQLAlchemy. Los conocimientos de **Bases de Datos** adquiridos fueron esenciales para diseñar las 3 tablas principales (Roles, usuarios, Auditoria) con relaciones normalizadas y optimización de índices en campos email y rol_id para mejorar rendimiento de consultas.

La materia de **Ingeniería de Software** fue fundamental para aplicar el patrón de arquitectura en capas (presentación, API, lógica de negocio, persistencia) y documentar con UML los 7 diagramas de procesos. Los conocimientos de **Arquitectura de Software** permitieron comprender la arquitectura de microservicios del sistema Sacra360 donde AuthProfiles opera en el puerto 8004 de forma independiente pero coordinada con los servicios de Sacramentos, OCR y HTR.

Las habilidades de **trabajo en equipo** desarrolladas en proyectos académicos fueron vitales para coordinarse efectivamente con Sebastian Pinto (backend sacramentos) y Marco Reynold (OCR/HTR), resolviendo dependencias entre módulos y manteniendo coherencia en los contratos de API.

**Debilidades o áreas de aprendizaje durante la pasantía:**

Al inicio de la experiencia existió una curva de aprendizaje pronunciada con **FastAPI**, framework no visto en la universidad. Fue necesario estudiar documentación oficial para comprender decoradores (@router.get), inyección de dependencias (Depends), y manejo asíncrono (async/await). De igual manera, los conceptos de **JWT (JSON Web Tokens)** fueron completamente nuevos, requiriendo investigación sobre estructura de tokens, tiempo de expiración, y almacenamiento seguro en localStorage del frontend.

El **sistema RBAC (Role-Based Access Control)** resultó más complejo de lo anticipado, con retos en diseñar la matriz de permisos, implementar el middleware permissions.py, y manejar casos especiales como usuarios inactivos o cambios de rol en tiempo real.

La implementación de **testing automatizado con pytest** fue un área débil, logrando solo 3 tests básicos cuando el estándar industrial es cobertura del 70%. Esto se debió a falta de experiencia en mocking de bases de datos y fixtures complejos.

El **debugging de errores complejos** como problemas de CORS entre frontend (puerto 5173) y backend (puerto 8004), o errores de validación Pydantic poco descriptivos, requirió desarrollo de paciencia y metodología sistemática de revisión de logs.

### Nivel de Satisfacción del Servicio Prestado a la Institución

**Auto-evaluación: MEDIO-BAJO**

El nivel de satisfacción del servicio prestado al Arzobispado de La Paz es **MEDIO-BAJO**, siendo una evaluación honesta y autocrítica basada en los siguientes criterios:

1. **Cumplimiento de Objetivos (Positivo):** Se lograron implementar los 3 objetivos específicos definidos: (a) Análisis y diseño del módulo AuthProfiles con 16 mockups en Figma validados por el personal, (b) Desarrollo e implementación del módulo con 30 endpoints funcionales y 6 páginas frontend integradas, (c) Entrega de 3 manuales completos (Usuario 940 líneas, Técnico 336 líneas, Pasantía). Los productos finales funcionan correctamente y cumplen con los requerimientos técnicos establecidos.

2. **Incumplimiento de Plazos (Crítico):** La fecha de entrega inicial era finales de octubre (4 meses), pero el proyecto se retrasó hasta diciembre (5.5 meses). Este retraso de 1.5 meses fue ocasionado principalmente por **desorganización personal y del equipo**, inadecuada gestión de tiempo, y subestimación de la complejidad del sistema RBAC. Aunque la extensión fue aprobada por el Ing. Pacheco, esto no elimina la responsabilidad sobre la mala planificación inicial y el impacto que generó en el cronograma institucional del Arzobispado.

3. **Factores Externos e Internos:** Los retrasos fueron producto de múltiples factores: (a) **Desorganización del equipo**: falta de coordinación efectiva entre los 3 integrantes durante septiembre-octubre, reuniones improductivas, indefinición de responsabilidades claras; (b) **Desorganización personal**: procrastinación en tareas críticas, inadecuada priorización entre universidad y pasantía, sesiones de trabajo fragmentadas sin continuidad; (c) **Curva de aprendizaje**: tiempo no contemplado para aprender FastAPI, JWT y RBAC desde cero; (d) **Problemas técnicos**: 3 días perdidos depurando error CORS que pudo prevenirse con mejor documentación inicial.

4. **Esfuerzo en Recuperación (Positivo):** A pesar de los errores de planificación, durante noviembre y diciembre se trabajó intensivamente para recuperar el tiempo perdido. La semana del 5-11 de diciembre se completaron 60.5 horas (promedio 8.6h/día) finalizando todos los módulos pendientes. Este esfuerzo demostró compromiso con finalizar la pasantía exitosamente dentro de los plazos extendidos, pero no compensa la falta de organización inicial.

5. **Calidad del Producto Final (Positivo):** El módulo AuthProfiles funciona correctamente con 30 endpoints, 6 páginas integradas, 9 medidas de seguridad implementadas, y documentación completa. Las pruebas con 4 usuarios reales fueron exitosas. Sin embargo, existen áreas de mejora: solo 3 tests automatizados (cobertura insuficiente), rate limiting no implementado, deployment en producción pendiente.

6. **Trabajo en Equipo (Neutral):** La coordinación con Sebastian y Marco fue irregular. Hubo periodos de buena comunicación (agosto análisis, noviembre integración) pero también semanas con descoordinación (septiembre-octubre) que generaron conflictos sobre contratos de API y dependencias entre módulos. Los contratos finales funcionan correctamente pero el proceso pudo ser más eficiente.

**Reflexión autocrítica:** Soy consciente de que mi desorganización personal fue un factor determinante en el retraso del proyecto. La extensión del plazo hasta diciembre no fue resultado de la complejidad técnica únicamente, sino principalmente de una inadecuada gestión de tiempo y falta de disciplina en las primeras semanas. Aprendí la importancia de la planificación realista, la autogestión efectiva, y la comunicación proactiva de problemas antes de que se conviertan en retrasos críticos.

**Aprendizajes valiosos:** Esta experiencia me enseñó que cumplir con los objetivos técnicos no es suficiente si se incumplen los plazos acordados. En un entorno profesional real, los retrasos tienen impacto financiero y organizacional. La autocrítica honesta es el primer paso para mejorar como profesional, reconociendo que el talento técnico debe complementarse con disciplina, organización y responsabilidad en los compromisos adquiridos.

**Satisfacción institucional percibida:** En reunión de cierre (Diciembre 10) el Ing. Pacheco expresó satisfacción con el producto final entregado, destacando el módulo de auditoría y la documentación técnica. Sin embargo, también mencionó que los retrasos generaron ajustes en el cronograma general del proyecto Sacra360, retrasando la integración con otros módulos. El Arzobispado valoró el esfuerzo final de recuperación, pero el cumplimiento de plazos sigue siendo un aspecto crítico a mejorar en futuras experiencias profesionales.

---

*FIN DEL PORTAFOLIO*
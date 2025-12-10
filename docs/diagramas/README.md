# 📊 Diagramas UML - Sistema Sacra360

Esta carpeta contiene todos los diagramas de procesos UML del sistema Sacra360, diseñados con PlantUML.

## 📁 Contenido

### Diagramas de Secuencia

#### 1. `01-proceso-autenticacion.puml`
**Proceso de Autenticación y Autorización**
- Flujo completo de login con JWT
- Validación de permisos RBAC
- Acceso a recursos protegidos
- Manejo de tokens expirados
- Registro de auditoría

**Actores:**
- Usuario
- Frontend (React)
- AuthProfiles Service
- PostgreSQL
- Otros Microservicios

**Casos cubiertos:**
- ✅ Login exitoso
- ❌ Credenciales inválidas
- ✅ Acceso con permisos
- ❌ Sin permisos (403)
- ❌ Token expirado (401)
- ✅ Logout

---

#### 2. `02-proceso-gestion-usuarios.puml`
**Gestión Completa de Usuarios**
- Crear usuario con validaciones
- Editar información de usuario
- Cambiar contraseña desde perfil
- Desactivar cuenta (soft delete)
- Reactivar cuenta desactivada

**Validaciones incluidas:**
- Email único
- Contraseña mínimo 8 caracteres
- Hash con bcrypt (12 rounds)
- No auto-eliminación
- Registro en auditoría

---

#### 3. `03-proceso-digitalizacion.puml`
**Digitalización de Documentos Sacramentales**
- Subir documento a MinIO
- Procesamiento OCR con Tesseract
- Procesamiento HTR para manuscritos
- Validación y corrección de campos
- Creación de registro sacramental

**Servicios involucrados:**
- File Storage Service (:8007)
- OCR Service (:8003)
- HTR Service (:8004)
- Documents Service (:8002)

**Flujo completo:**
1. Upload → MinIO storage
2. OCR extraction → campos estructurados
3. Validación manual (si confianza < 70%)
4. Correcciones guardadas
5. Creación de sacramento vinculado

---

#### 4. `04-proceso-generacion-reportes.puml`
**Sistema de Reportes y Analytics**
- Dashboard con múltiples reportes paralelos
- Caché con Redis (TTL: 5 minutos)
- Reporte de usuarios del sistema
- Reporte de accesos y actividad
- Estadísticas generales
- Cambio de período dinámico

**Optimizaciones:**
- Llamadas paralelas
- Caché en Redis
- Queries SQL optimizadas con agregaciones
- Respuesta rápida desde caché

---

### Diagramas de Actividad

#### 5. `05-diagrama-actividad-sistema.puml`
**Flujo General del Sistema**
- Flujo de navegación completo
- Decisiones según permisos
- Todos los módulos disponibles:
  - Digitalización
  - Revisión OCR
  - Registros
  - Usuarios
  - Auditoría
  - Reportes
  - Personas
  - Mi Perfil

---

### Diagramas de Estados

#### 6. `06-diagrama-estados-documento.puml`
**Ciclo de Vida de un Documento**

Estados del documento:
1. **Subido** → Validación de formato
2. **Almacenado** → En cola OCR
3. **Procesando OCR** → Extracción de texto
4. **OCR Completado** → Verificación de confianza
5. **En Revisión** → Si confianza < 70%
6. **Validado** → Listo para registro
7. **Asociado a Sacramento** → Vinculado
8. **Procesado** → Disponible para consultas
9. **Archivado** → Almacenamiento largo plazo

---

## 🛠️ Cómo Visualizar los Diagramas

### Opción 1: VS Code (Recomendado)
```bash
# Instalar extensión PlantUML
code --install-extension jebbs.plantuml

# Abrir cualquier archivo .puml
# Presionar Alt+D para preview
```

### Opción 2: Online
Visitar: http://www.plantuml.com/plantuml/uml/

### Opción 3: Línea de comandos
```bash
# Instalar PlantUML
npm install -g node-plantuml

# Generar imagen PNG
puml generate 01-proceso-autenticacion.puml

# Generar SVG (mejor calidad)
puml generate 01-proceso-autenticacion.puml -t svg
```

### Opción 4: Docker
```bash
# Generar todos los diagramas
docker run --rm -v $(pwd):/data plantuml/plantuml *.puml
```

---

## 📐 Convenciones Usadas

### Colores de Participantes
- **Frontend**: Azul claro
- **Servicios Backend**: Verde
- **Base de Datos**: Gris
- **Storage**: Amarillo

### Tipos de Flechas
- `->` : Llamada síncrona
- `-->` : Respuesta
- `->>` : Llamada asíncrona
- `-->>` : Respuesta asíncrona

### Bloques de Decisión
```
alt Condición exitosa
    ...
else Condición fallida
    ...
end
```

### Loops
```
loop Para cada elemento
    ...
end
```

### Notas
```
note right of Participante
    Información adicional
end note
```

---

## 🎯 Casos de Uso Cubiertos

| Diagrama | Casos de Uso | Complejidad |
|----------|--------------|-------------|
| 01-autenticacion | Login, Autorización, Logout | Media |
| 02-gestion-usuarios | CRUD completo + reactivación | Alta |
| 03-digitalizacion | Upload, OCR, HTR, Validación | Muy Alta |
| 04-reportes | Analytics, Caché, Múltiples reportes | Alta |
| 05-actividad | Navegación completa del sistema | Media |
| 06-estados | Ciclo de vida documento | Media |

---

## 📝 Actualizaciones

**Última actualización:** 9 de diciembre de 2025

**Versión:** 1.0.0

**Próximas adiciones:**
- Diagrama de componentes
- Diagrama de despliegue
- Casos de uso detallados
- Diagrama de clases

---

## 🔗 Referencias

- [PlantUML Documentation](https://plantuml.com/)
- [Sequence Diagram Syntax](https://plantuml.com/sequence-diagram)
- [Activity Diagram Syntax](https://plantuml.com/activity-diagram-beta)
- [State Diagram Syntax](https://plantuml.com/state-diagram)

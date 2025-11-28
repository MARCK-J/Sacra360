/**
 * Sistema de Permisos - Sacra360
 * Define los permisos CRUD para cada módulo según el rol del usuario
 */

// Definición de roles
export const ROLES = {
  ADMINISTRADOR: 'Administrador',
  DIGITALIZADOR: 'Digitalizador',
  VALIDADOR: 'Validador', // Revisor
  USUARIO: 'Usuario' // Consultor
}

// Definición de permisos por módulo
export const PERMISSIONS = {
  // Módulo de Digitalización
  digitalizacion: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: true, read: true, update: true, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: true, update: true, delete: false },
    [ROLES.USUARIO]: { create: false, read: true, update: false, delete: false }
  },
  
  // Módulo de Revisión OCR
  revisionOCR: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.USUARIO]: { create: false, read: true, update: false, delete: false }
  },
  
  // Módulo de Registros (Sacramentos)
  registros: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: true, update: true, delete: false },
    [ROLES.USUARIO]: { create: false, read: true, update: false, delete: false }
  },
  
  // Módulo de Personas
  personas: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: true, update: true, delete: false },
    [ROLES.USUARIO]: { create: false, read: true, update: false, delete: false }
  },
  
  // Módulo de Libros
  libros: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.USUARIO]: { create: false, read: true, update: false, delete: false }
  },
  
  // Módulo de Certificados
  certificados: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: true, read: true, update: false, delete: false },
    [ROLES.USUARIO]: { create: false, read: true, update: false, delete: false }
  },
  
  // Módulo de Usuarios
  usuarios: {
    [ROLES.ADMINISTRADOR]: { create: true, read: true, update: true, delete: true },
    [ROLES.DIGITALIZADOR]: { create: false, read: false, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: false, update: false, delete: false },
    [ROLES.USUARIO]: { create: false, read: false, update: false, delete: false }
  },
  
  // Módulo de Auditoría
  auditoria: {
    [ROLES.ADMINISTRADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.DIGITALIZADOR]: { create: false, read: false, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: false, update: false, delete: false },
    [ROLES.USUARIO]: { create: false, read: false, update: false, delete: false }
  },
  
  // Módulo de Reportes
  reportes: {
    [ROLES.ADMINISTRADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.DIGITALIZADOR]: { create: false, read: false, update: false, delete: false },
    [ROLES.VALIDADOR]: { create: false, read: true, update: false, delete: false },
    [ROLES.USUARIO]: { create: false, read: false, update: false, delete: false }
  }
}

/**
 * Verifica si un usuario tiene un permiso específico en un módulo
 * @param {string} userRole - Rol del usuario
 * @param {string} module - Nombre del módulo
 * @param {string} action - Acción a verificar (create, read, update, delete)
 * @returns {boolean}
 */
export const hasPermission = (userRole, module, action) => {
  if (!userRole || !module || !action) return false
  
  const modulePermissions = PERMISSIONS[module]
  if (!modulePermissions) return false
  
  const rolePermissions = modulePermissions[userRole]
  if (!rolePermissions) return false
  
  return rolePermissions[action] === true
}

/**
 * Obtiene todos los permisos de un usuario para un módulo
 * @param {string} userRole - Rol del usuario
 * @param {string} module - Nombre del módulo
 * @returns {object}
 */
export const getModulePermissions = (userRole, module) => {
  if (!userRole || !module) return { create: false, read: false, update: false, delete: false }
  
  const modulePermissions = PERMISSIONS[module]
  if (!modulePermissions) return { create: false, read: false, update: false, delete: false }
  
  return modulePermissions[userRole] || { create: false, read: false, update: false, delete: false }
}

/**
 * Verifica si un usuario puede acceder a un módulo (al menos lectura)
 * @param {string} userRole - Rol del usuario
 * @param {string} module - Nombre del módulo
 * @returns {boolean}
 */
export const canAccessModule = (userRole, module) => {
  return hasPermission(userRole, module, 'read')
}

/**
 * Lista de módulos visibles según el rol
 */
export const getVisibleModules = (userRole) => {
  const modules = Object.keys(PERMISSIONS)
  return modules.filter(module => canAccessModule(userRole, module))
}

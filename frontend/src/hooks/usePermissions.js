import { useAuth } from '../context/AuthContext'
import { hasPermission, getModulePermissions, canAccessModule } from '../config/permissions'

/**
 * Hook personalizado para verificar permisos
 * @returns {object} Funciones de verificación de permisos
 */
export const usePermissions = () => {
  const { getUserRole } = useAuth()
  const userRole = getUserRole()

  /**
   * Verifica si tiene un permiso específico
   */
  const can = (module, action) => {
    return hasPermission(userRole, module, action)
  }

  /**
   * Verifica si puede crear en un módulo
   */
  const canCreate = (module) => {
    return hasPermission(userRole, module, 'create')
  }

  /**
   * Verifica si puede leer en un módulo
   */
  const canRead = (module) => {
    return hasPermission(userRole, module, 'read')
  }

  /**
   * Verifica si puede actualizar en un módulo
   */
  const canUpdate = (module) => {
    return hasPermission(userRole, module, 'update')
  }

  /**
   * Verifica si puede eliminar en un módulo
   */
  const canDelete = (module) => {
    return hasPermission(userRole, module, 'delete')
  }

  /**
   * Obtiene todos los permisos de un módulo
   */
  const getPermissions = (module) => {
    return getModulePermissions(userRole, module)
  }

  /**
   * Verifica si puede acceder al módulo
   */
  const canAccess = (module) => {
    return canAccessModule(userRole, module)
  }

  /**
   * Verifica si es administrador
   */
  const isAdmin = () => {
    return userRole === 'Administrador'
  }

  return {
    can,
    canCreate,
    canRead,
    canUpdate,
    canDelete,
    getPermissions,
    canAccess,
    isAdmin,
    userRole
  }
}

export default usePermissions

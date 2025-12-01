import { useAuth } from '../context/AuthContext'
import { hasPermission, getModulePermissions, canAccessModule } from '../config/permissions'

/**
 * Hook personalizado para verificar permisos
 * @returns {object} Funciones de verificaci├│n de permisos
 */
export const usePermissions = () => {
  const { getUserRole } = useAuth()
  const userRole = getUserRole()

  /**
   * Verifica si tiene un permiso espec├¡fico
   */
  const can = (module, action) => {
    return hasPermission(userRole, module, action)
  }

  /**
   * Verifica si puede crear en un m├│dulo
   */
  const canCreate = (module) => {
    return hasPermission(userRole, module, 'create')
  }

  /**
   * Verifica si puede leer en un m├│dulo
   */
  const canRead = (module) => {
    return hasPermission(userRole, module, 'read')
  }

  /**
   * Verifica si puede actualizar en un m├│dulo
   */
  const canUpdate = (module) => {
    return hasPermission(userRole, module, 'update')
  }

  /**
   * Verifica si puede eliminar en un m├│dulo
   */
  const canDelete = (module) => {
    return hasPermission(userRole, module, 'delete')
  }

  /**
   * Obtiene todos los permisos de un m├│dulo
   */
  const getPermissions = (module) => {
    return getModulePermissions(userRole, module)
  }

  /**
   * Verifica si puede acceder al m├│dulo
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
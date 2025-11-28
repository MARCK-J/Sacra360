import { useAuth } from '../context/AuthContext'
import { hasPermission } from '../config/permissions'

/**
 * Componente que muestra u oculta contenido según permisos
 * @param {string} module - Nombre del módulo
 * @param {string} action - Acción requerida (create, read, update, delete)
 * @param {React.ReactNode} children - Contenido a mostrar si tiene permiso
 * @param {React.ReactNode} fallback - Contenido alternativo si no tiene permiso
 */
export const PermissionGuard = ({ module, action, children, fallback = null }) => {
  const { getUserRole } = useAuth()
  const userRole = getUserRole()

  const canPerformAction = hasPermission(userRole, module, action)

  return canPerformAction ? children : fallback
}

export default PermissionGuard

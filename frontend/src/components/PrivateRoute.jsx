import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Componente que protege rutas privadas
 * Redirige al login si no está autenticado
 */
export const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando...</p>
        </div>
      </div>
    )
  }

  return isAuthenticated() ? children : <Navigate to="/login" replace />
}

export default PrivateRoute

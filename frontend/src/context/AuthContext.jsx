import { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  // Cargar usuario del localStorage al iniciar
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser && storedUser !== 'undefined') {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      } catch (error) {
        console.error('Error al parsear usuario:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  // Login
  const login = async (email, password) => {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_AUTH_API_URL}/api/v1/auth/login`,
        {
          email,
          password: password
        }
      )

      const { access_token, user_info, permissions } = response.data

      // Agregar permisos al objeto de usuario
      const userData = {
        ...user_info,
        permissions: permissions
      }

      // Guardar en estado
      setToken(access_token)
      setUser(userData)

      // Guardar en localStorage
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))

      // Configurar axios para usar el token
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      return { success: true, user: userData }
    } catch (error) {
      console.error('Error en login:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al iniciar sesiÔö£Ôöén'
      }
    }
  }

  // Logout
  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
    navigate('/login')
  }

  // Obtener rol del usuario
  const getUserRole = () => {
    return user?.nombre_rol || null
  }

  // Verificar si estÔö£├¡ autenticado
  const isAuthenticated = () => {
    return !!token && !!user
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    getUserRole,
    isAuthenticated
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider')
  }
  return context
}

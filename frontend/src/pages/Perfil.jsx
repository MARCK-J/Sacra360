import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import Layout from '../components/Layout'
import axios from 'axios'

const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8004'

export default function Perfil() {
  const { user, token } = useAuth()
  const [modalOpen, setModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    contrasena_actual: '',
    contrasena_nueva: '',
    confirmar_contrasena: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [passwordStrength, setPasswordStrength] = useState({ strength: 0, label: '', color: '' })

  // Función para calcular fortaleza de contraseña
  const calcularFortalezaPassword = (password) => {
    if (!password) {
      return { strength: 0, label: '', color: '' }
    }

    let strength = 0
    
    // Criterios de fortaleza
    if (password.length >= 8) strength += 25
    if (password.length >= 12) strength += 15
    if (/[a-z]/.test(password)) strength += 15
    if (/[A-Z]/.test(password)) strength += 15
    if (/[0-9]/.test(password)) strength += 15
    if (/[^a-zA-Z0-9]/.test(password)) strength += 15

    // Determinar nivel y color
    if (strength < 40) {
      return { strength, label: 'Débil', color: 'bg-red-500' }
    } else if (strength < 70) {
      return { strength, label: 'Media', color: 'bg-yellow-500' }
    } else {
      return { strength, label: 'Fuerte', color: 'bg-green-500' }
    }
  }

  const handleOpenModal = () => {
    setModalOpen(true)
    setFormData({
      contrasena_actual: '',
      contrasena_nueva: '',
      confirmar_contrasena: ''
    })
    setError('')
    setSuccess('')
    setPasswordStrength({ strength: 0, label: '', color: '' })
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setFormData({
      contrasena_actual: '',
      contrasena_nueva: '',
      confirmar_contrasena: ''
    })
    setError('')
    setSuccess('')
    setPasswordStrength({ strength: 0, label: '', color: '' })
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))

    // Calcular fortaleza cuando cambia la nueva contraseña
    if (name === 'contrasena_nueva') {
      setPasswordStrength(calcularFortalezaPassword(value))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validaciones
    if (!formData.contrasena_actual || !formData.contrasena_nueva || !formData.confirmar_contrasena) {
      setError('Todos los campos son obligatorios')
      return
    }

    if (formData.contrasena_nueva.length < 8) {
      setError('La nueva contraseña debe tener al menos 8 caracteres')
      return
    }

    if (formData.contrasena_nueva !== formData.confirmar_contrasena) {
      setError('Las contraseñas no coinciden')
      return
    }

    if (formData.contrasena_actual === formData.contrasena_nueva) {
      setError('La nueva contraseña debe ser diferente a la actual')
      return
    }

    try {
      setLoading(true)
      const headers = { Authorization: `Bearer ${token}` }
      
      await axios.patch(
        `${AUTH_API_URL}/api/v1/usuarios/${user.id_usuario}/password`,
        {
          contrasenia: formData.contrasena_nueva
        },
        { headers }
      )

      setSuccess('Contraseña actualizada exitosamente')
      
      setTimeout(() => {
        handleCloseModal()
      }, 2000)

    } catch (error) {
      console.error('Error al cambiar contraseña:', error)
      setError(error.response?.data?.detail || 'Error al cambiar la contraseña')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout title="Mi Perfil">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Información del Usuario */}
        <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Información Personal</h2>
          
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="flex-shrink-0">
              <div className="w-24 h-24 bg-primary rounded-full flex items-center justify-center text-white text-3xl font-bold">
                {user?.nombre?.charAt(0) || 'U'}
              </div>
            </div>

            {/* Datos del usuario */}
            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Nombre Completo
                </label>
                <p className="text-gray-900 dark:text-white font-semibold">
                  {user?.nombre} {user?.apellido_paterno} {user?.apellido_materno}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Correo Electrónico
                </label>
                <p className="text-gray-900 dark:text-white font-semibold">
                  {user?.email}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Rol
                </label>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary/10 text-primary">
                  {user?.nombre_rol}
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Estado
                </label>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  user?.activo 
                    ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300' 
                    : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300'
                }`}>
                  {user?.activo ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Seguridad */}
        <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Seguridad</h2>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Contraseña</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Cambia tu contraseña regularmente para mantener tu cuenta segura
              </p>
            </div>
            <button
              onClick={handleOpenModal}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              <span className="material-symbols-outlined text-base">lock_reset</span>
              Cambiar Contraseña
            </button>
          </div>
        </div>
      </div>

      {/* Modal para cambiar contraseña */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-background-dark rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">lock_reset</span>
                  Cambiar Contraseña
                </h3>
                <button
                  onClick={handleCloseModal}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400"
                  disabled={loading}
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              {/* Mensajes */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2 text-red-800 dark:text-red-300">
                  <span className="material-symbols-outlined text-base">error</span>
                  <span className="text-sm">{error}</span>
                </div>
              )}

              {success && (
                <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-2 text-green-800 dark:text-green-300">
                  <span className="material-symbols-outlined text-base">check_circle</span>
                  <span className="text-sm">{success}</span>
                </div>
              )}

              {/* Formulario */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Contraseña Actual *
                  </label>
                  <input
                    type="password"
                    name="contrasena_actual"
                    value={formData.contrasena_actual}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 dark:text-white"
                    required
                    disabled={loading}
                    autoComplete="current-password"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nueva Contraseña *
                  </label>
                  <input
                    type="password"
                    name="contrasena_nueva"
                    value={formData.contrasena_nueva}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 dark:text-white"
                    required
                    disabled={loading}
                    autoComplete="new-password"
                    minLength={8}
                  />
                  
                  {/* Indicador de fortaleza de contraseña */}
                  {formData.contrasena_nueva && (
                    <div className="mt-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-600 dark:text-gray-400">
                          Fortaleza de contraseña:
                        </span>
                        <span className={`text-xs font-medium ${
                          passwordStrength.label === 'Débil' ? 'text-red-600 dark:text-red-400' :
                          passwordStrength.label === 'Media' ? 'text-yellow-600 dark:text-yellow-400' :
                          'text-green-600 dark:text-green-400'
                        }`}>
                          {passwordStrength.label}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`}
                          style={{ width: `${passwordStrength.strength}%` }}
                        ></div>
                      </div>
                      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        <p>La contraseña debe contener:</p>
                        <ul className="list-disc list-inside ml-2 mt-1 space-y-0.5">
                          <li className={formData.contrasena_nueva.length >= 8 ? 'text-green-600 dark:text-green-400' : ''}>
                            Mínimo 8 caracteres
                          </li>
                          <li className={/[A-Z]/.test(formData.contrasena_nueva) ? 'text-green-600 dark:text-green-400' : ''}>
                            Al menos una mayúscula
                          </li>
                          <li className={/[a-z]/.test(formData.contrasena_nueva) ? 'text-green-600 dark:text-green-400' : ''}>
                            Al menos una minúscula
                          </li>
                          <li className={/[0-9]/.test(formData.contrasena_nueva) ? 'text-green-600 dark:text-green-400' : ''}>
                            Al menos un número
                          </li>
                          <li className={/[^a-zA-Z0-9]/.test(formData.contrasena_nueva) ? 'text-green-600 dark:text-green-400' : ''}>
                            Caracteres especiales (recomendado)
                          </li>
                        </ul>
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Confirmar Nueva Contraseña *
                  </label>
                  <input
                    type="password"
                    name="confirmar_contrasena"
                    value={formData.confirmar_contrasena}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 dark:text-white"
                    required
                    disabled={loading}
                    autoComplete="new-password"
                  />
                </div>

                {/* Botones */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    disabled={loading}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Guardando...</span>
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined text-base">save</span>
                        <span>Guardar Cambios</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}

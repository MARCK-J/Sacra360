import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import PermissionGuard from '../components/PermissionGuard'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

export default function Usuarios() {
  const { token } = useAuth()
  const [usuarios, setUsuarios] = useState([])
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [modalMode, setModalMode] = useState('create') // 'create' | 'edit'
  const [usuarioSeleccionado, setUsuarioSeleccionado] = useState(null)
  const [formData, setFormData] = useState({
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    email: '',
    contrasenia: '',
    rol_id: 1,
    activo: true
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8004'

  // Cargar usuarios y roles cuando el token esté disponible
  useEffect(() => {
    if (token) {
      cargarDatos()
    }
  }, [token])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      const headers = { Authorization: `Bearer ${token}` }
      const [usuariosRes, rolesRes] = await Promise.all([
        axios.get(`${AUTH_API_URL}/api/v1/usuarios`, { headers }),
        axios.get(`${AUTH_API_URL}/api/v1/usuarios/roles/listar`, { headers })
      ])
      
      setUsuarios(usuariosRes.data)
      setRoles(rolesRes.data)
    } catch (error) {
      console.error('Error cargando datos:', error)
      setError('Error al cargar los datos')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (mode, usuario = null) => {
    setModalMode(mode)
    setUsuarioSeleccionado(usuario)
    
    if (mode === 'edit' && usuario) {
      setFormData({
        nombre: usuario.nombre,
        apellido_paterno: usuario.apellido_paterno,
        apellido_materno: usuario.apellido_materno || '',
        email: usuario.email,
        contrasenia: '',
        rol_id: usuario.rol_id,
        activo: usuario.activo
      })
    } else {
      setFormData({
        nombre: '',
        apellido_paterno: '',
        apellido_materno: '',
        email: '',
        contrasenia: '',
        rol_id: 1,
        activo: true
      })
    }
    
    setError('')
    setSuccess('')
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setUsuarioSeleccionado(null)
    setFormData({
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      email: '',
      contrasenia: '',
      rol_id: 1,
      activo: true
    })
    setError('')
    setSuccess('')
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      if (modalMode === 'create') {
        // Validar que la contraseña esté presente al crear
        if (!formData.contrasenia || formData.contrasenia.length < 8) {
          setError('La contraseña debe tener al menos 8 caracteres')
          return
        }

        const headers = { Authorization: `Bearer ${token}` }
        await axios.post(`${AUTH_API_URL}/api/v1/usuarios`, formData, { headers })
        setSuccess('Usuario creado exitosamente')
      } else {
        // Al editar, no enviar contraseña vacía
        const headers = { Authorization: `Bearer ${token}` }
        const updateData = { ...formData }
        delete updateData.contrasenia
        
        await axios.put(`${AUTH_API_URL}/api/v1/usuarios/${usuarioSeleccionado.id_usuario}`, updateData, { headers })
        setSuccess('Usuario actualizado exitosamente')
      }

      // Recargar usuarios
      await cargarDatos()
      
      // Cerrar modal después de 1.5 segundos
      setTimeout(() => {
        handleCloseModal()
      }, 1500)
      
    } catch (error) {
      console.error('Error al guardar usuario:', error)
      setError(error.response?.data?.detail || 'Error al guardar usuario')
    }
  }

  const handleEliminar = async (usuario) => {
    if (!confirm(`¿Estás seguro de desactivar al usuario ${usuario.nombre} ${usuario.apellido_paterno}?`)) {
      return
    }

    try {
      const headers = { Authorization: `Bearer ${token}` }
      await axios.delete(`${AUTH_API_URL}/api/v1/usuarios/${usuario.id_usuario}`, { headers })
      setSuccess('Usuario desactivado exitosamente')
      await cargarDatos()
      
      setTimeout(() => setSuccess(''), 3000)
    } catch (error) {
      console.error('Error al eliminar usuario:', error)
      setError(error.response?.data?.detail || 'Error al eliminar usuario')
      setTimeout(() => setError(''), 3000)
    }
  }

  const handleReactivar = async (usuario) => {
    if (!confirm(`¿Estás seguro de reactivar al usuario ${usuario.nombre} ${usuario.apellido_paterno}?`)) {
      return
    }

    try {
      const headers = { Authorization: `Bearer ${token}` }
      await axios.patch(`${AUTH_API_URL}/api/v1/usuarios/${usuario.id_usuario}/activar`, {}, { headers })
      setSuccess('Usuario reactivado exitosamente')
      await cargarDatos()
      
      setTimeout(() => setSuccess(''), 3000)
    } catch (error) {
      console.error('Error al reactivar usuario:', error)
      setError(error.response?.data?.detail || 'Error al reactivar usuario')
      setTimeout(() => setError(''), 3000)
    }
  }

  const getRoleBadgeColor = (rolNombre) => {
    const colors = {
      'Administrador': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      'Digitalizador': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      'Validador': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'Usuario': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    }
    return colors[rolNombre] || 'bg-gray-100 text-gray-800'
  }

  return (
    <Layout title="Gestión de Usuarios">
      <div className="space-y-6">
        {/* Mensajes de éxito/error globales */}
        {success && (
          <div className="bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500 p-4 rounded">
            <p className="text-sm text-green-700 dark:text-green-400">{success}</p>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 rounded">
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Botón para crear usuario */}
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Usuarios del Sistema</h2>
          <PermissionGuard module="usuarios" action="create">
            <button
              onClick={() => handleOpenModal('create')}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
            >
              <span className="material-symbols-outlined text-base">add</span>
              Crear Usuario
            </button>
          </PermissionGuard>
        </div>

        {/* Tabla de usuarios */}
        <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-3">Cargando usuarios...</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th scope="col" className="px-6 py-3">ID</th>
                    <th scope="col" className="px-6 py-3">Nombre Completo</th>
                    <th scope="col" className="px-6 py-3">Email</th>
                    <th scope="col" className="px-6 py-3">Rol</th>
                    <th scope="col" className="px-6 py-3">Estado</th>
                    <th scope="col" className="px-6 py-3 text-center">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {usuarios.map((usuario) => (
                    <tr key={usuario.id_usuario} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                      <td className="px-6 py-4">{usuario.id_usuario}</td>
                      <td className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">
                        {usuario.nombre} {usuario.apellido_paterno} {usuario.apellido_materno}
                      </td>
                      <td className="px-6 py-4">{usuario.email}</td>
                      <td className="px-6 py-4">
                        <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${getRoleBadgeColor(usuario.nombre_rol)}`}>
                          {usuario.nombre_rol}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
                          usuario.activo 
                            ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300' 
                            : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300'
                        }`}>
                          {usuario.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex justify-center gap-2">
                          <PermissionGuard module="usuarios" action="update">
                            <button
                              onClick={() => handleOpenModal('edit', usuario)}
                              className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                              title="Editar"
                            >
                              <span className="material-symbols-outlined text-base">edit</span>
                            </button>
                          </PermissionGuard>
                          
                          <PermissionGuard module="usuarios" action="delete">
                            {usuario.activo ? (
                              <button
                                onClick={() => handleEliminar(usuario)}
                                className="text-red-600 hover:text-red-800 dark:text-red-400"
                                title="Desactivar usuario"
                              >
                                <span className="material-symbols-outlined text-base">delete</span>
                              </button>
                            ) : (
                              <button
                                onClick={() => handleReactivar(usuario)}
                                className="text-green-600 hover:text-green-800 dark:text-green-400"
                                title="Reactivar usuario"
                              >
                                <span className="material-symbols-outlined text-base">refresh</span>
                              </button>
                            )}
                          </PermissionGuard>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal para crear/editar usuario */}
        {modalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-background-dark rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                    {modalMode === 'create' ? 'Crear Nuevo Usuario' : 'Editar Usuario'}
                  </h3>
                  <button
                    onClick={handleCloseModal}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400"
                  >
                    <span className="material-symbols-outlined">close</span>
                  </button>
                </div>

                {error && (
                  <div className="mb-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-3 rounded">
                    <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
                  </div>
                )}

                {success && (
                  <div className="mb-4 bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500 p-3 rounded">
                    <p className="text-sm text-green-700 dark:text-green-400">{success}</p>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="nombre" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Nombre *
                      </label>
                      <input
                        id="nombre"
                        name="nombre"
                        type="text"
                        value={formData.nombre}
                        onChange={handleInputChange}
                        required
                        className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
                      />
                    </div>

                    <div>
                      <label htmlFor="apellido_paterno" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Apellido Paterno *
                      </label>
                      <input
                        id="apellido_paterno"
                        name="apellido_paterno"
                        type="text"
                        value={formData.apellido_paterno}
                        onChange={handleInputChange}
                        required
                        className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
                      />
                    </div>

                    <div>
                      <label htmlFor="apellido_materno" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Apellido Materno
                      </label>
                      <input
                        id="apellido_materno"
                        name="apellido_materno"
                        type="text"
                        value={formData.apellido_materno}
                        onChange={handleInputChange}
                        className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
                      />
                    </div>

                    <div>
                      <label htmlFor="email" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Email *
                      </label>
                      <input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                        className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
                      />
                    </div>

                    {modalMode === 'create' && (
                      <div className="md:col-span-2">
                        <label htmlFor="contrasenia" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                          Contraseña * (mínimo 8 caracteres)
                        </label>
                        <input
                          id="contrasenia"
                          name="contrasenia"
                          type="password"
                          value={formData.contrasenia}
                          onChange={handleInputChange}
                          required={modalMode === 'create'}
                          minLength={8}
                          className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
                        />
                      </div>
                    )}

                    <div>
                      <label htmlFor="rol_id" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Rol *
                      </label>
                      <select
                        id="rol_id"
                        name="rol_id"
                        value={formData.rol_id}
                        onChange={handleInputChange}
                        required
                        className="bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
                      >
                        {roles.map(rol => (
                          <option key={rol.id_rol} value={rol.id_rol}>
                            {rol.nombre}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center">
                      <input
                        id="activo"
                        name="activo"
                        type="checkbox"
                        checked={formData.activo}
                        onChange={handleInputChange}
                        className="w-4 h-4 text-primary bg-gray-100 border-gray-300 rounded focus:ring-primary dark:focus:ring-primary dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                      />
                      <label htmlFor="activo" className="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        Usuario Activo
                      </label>
                    </div>
                  </div>

                  <div className="flex justify-end gap-3 mt-6">
                    <button
                      type="button"
                      onClick={handleCloseModal}
                      className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                    >
                      Cancelar
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                    >
                      {modalMode === 'create' ? 'Crear Usuario' : 'Guardar Cambios'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

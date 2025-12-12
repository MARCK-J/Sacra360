import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

export default function Auditoria() {
  const { token } = useAuth()
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [stats, setStats] = useState(null)
  
  // Filtros
  const [filtros, setFiltros] = useState({
    accion: '',
    fecha_inicio: '',
    fecha_fin: '',
    search: ''
  })
  
  // Paginación
  const [page, setPage] = useState(1)
  const [limit] = useState(10)
  const [totalCount, setTotalCount] = useState(0)
  const totalPages = Math.ceil(totalCount / limit)

  const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8004'

  useEffect(() => {
    if (token) {
      cargarDatos()
      cargarEstadisticas()
    }
  }, [token, filtros, page])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      setError('')
      
      const headers = { Authorization: `Bearer ${token}` }
      const params = {
        skip: (page - 1) * limit,
        limit: limit,
        ...filtros
      }
      
      // Limpiar parámetros vacíos
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key]
        }
      })
      
      const response = await axios.get(`${AUTH_API_URL}/api/v1/auditoria`, { 
        headers,
        params 
      })
      
      // Si la respuesta es un array, usarla directamente
      if (Array.isArray(response.data)) {
        setLogs(response.data)
        // Estimar total basado en la cantidad de resultados
        setTotalCount(response.data.length === limit ? (page * limit) + 1 : (page - 1) * limit + response.data.length)
      } 
      // Si la respuesta tiene estructura con total y datos
      else if (response.data.items || response.data.data) {
        const items = response.data.items || response.data.data
        setLogs(items)
        setTotalCount(response.data.total || response.data.count || items.length)
      }
      // Fallback
      else {
        setLogs([])
        setTotalCount(0)
      }
    } catch (error) {
      console.error('Error cargando logs:', error)
      if (error.response?.status === 403) {
        setError('No tienes permisos para ver los logs de auditoría')
      } else {
        setError('Error al cargar los logs')
      }
    } finally {
      setLoading(false)
    }
  }

  const cargarEstadisticas = async () => {
    try {
      const headers = { Authorization: `Bearer ${token}` }
      const params = {}
      
      if (filtros.fecha_inicio) params.fecha_inicio = filtros.fecha_inicio
      if (filtros.fecha_fin) params.fecha_fin = filtros.fecha_fin
      
      const response = await axios.get(`${AUTH_API_URL}/api/v1/auditoria/stats/resumen`, { 
        headers,
        params 
      })
      
      setStats(response.data)
    } catch (error) {
      console.error('Error cargando estadísticas:', error)
    }
  }

  const handleFiltroChange = (e) => {
    const { name, value } = e.target
    setFiltros(prev => ({ ...prev, [name]: value }))
    setPage(1) // Resetear a primera página al cambiar filtros
  }

  const limpiarFiltros = () => {
    setFiltros({
      accion: '',
      exitoso: '',
      fecha_inicio: '',
      fecha_fin: '',
      search: ''
    })
    setPage(1)
  }

  const getAccionBadge = (accion) => {
    const badges = {
      'LOGIN_EXITOSO': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'LOGIN_FALLIDO': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      'LOGOUT': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
      'TOKEN_EXPIRADO': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
    }
    return badges[accion] || 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
  }

  const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <Layout title="Auditoría de Accesos">
      <div className="space-y-6">
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 rounded">
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Estadísticas */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Eventos</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.total_eventos}</p>
            </div>
            <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
              <p className="text-sm text-gray-500 dark:text-gray-400">Logins Exitosos</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">{stats.logins_exitosos}</p>
            </div>
            <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
              <p className="text-sm text-gray-500 dark:text-gray-400">Logins Fallidos</p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">{stats.logins_fallidos}</p>
            </div>
            <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
              <p className="text-sm text-gray-500 dark:text-gray-400">Tasa de Éxito</p>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{stats.tasa_exito}%</p>
            </div>
          </div>
        )}

        {/* Filtros */}
        <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Filtros</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Acción
              </label>
              <select
                name="accion"
                value={filtros.accion}
                onChange={handleFiltroChange}
                className="w-full bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg p-2"
              >
                <option value="">Todas</option>
                <option value="LOGIN">Login</option>
                <option value="LOGOUT">Logout</option>
                <option value="CREAR">Crear</option>
                <option value="ACTUALIZAR">Actualizar</option>
                <option value="ELIMINAR">Eliminar</option>
              </select>
            </div>



            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Fecha Inicio
              </label>
              <input
                type="date"
                name="fecha_inicio"
                value={filtros.fecha_inicio}
                onChange={handleFiltroChange}
                className="w-full bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg p-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Fecha Fin
              </label>
              <input
                type="date"
                name="fecha_fin"
                value={filtros.fecha_fin}
                onChange={handleFiltroChange}
                className="w-full bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg p-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Buscar
              </label>
              <input
                type="text"
                name="search"
                value={filtros.search}
                onChange={handleFiltroChange}
                placeholder="Email, IP, mensaje..."
                className="w-full bg-background-light dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg p-2"
              />
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <button
              onClick={limpiarFiltros}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>

        {/* Tabla de Logs */}
        <div className="bg-white dark:bg-background-dark p-6 rounded-xl shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Logs de Auditoría
            </h2>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Mostrando {((page - 1) * limit) + 1} - {Math.min(page * limit, totalCount)} de {totalCount} registros
            </span>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-3">Cargando logs...</span>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              No se encontraron logs con los filtros aplicados
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                  <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                    <tr>
                      <th scope="col" className="px-4 py-3">ID</th>
                      <th scope="col" className="px-4 py-3">Fecha</th>
                      <th scope="col" className="px-4 py-3">Usuario</th>
                      <th scope="col" className="px-4 py-3">Acción</th>
                      <th scope="col" className="px-4 py-3">Registro Afectado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id_auditoria} className="bg-white dark:bg-background-dark border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="px-4 py-3 text-sm">
                          {log.id_auditoria}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-xs">
                          {formatFecha(log.fecha)}
                        </td>
                        <td className="px-4 py-3">
                          {log.nombre_usuario ? (
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">{log.nombre_usuario}</p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">{log.email_usuario}</p>
                            </div>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500">Usuario desconocido</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${getAccionBadge(log.accion)}`}>
                            {log.accion}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm text-gray-900 dark:text-white">{log.registro_afectado}</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">ID: {log.id_registro}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Paginación */}
              <div className="flex flex-col sm:flex-row justify-between items-center mt-6 gap-4">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="w-full sm:w-auto px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  ← Anterior
                </button>
                
                <div className="flex items-center gap-2">
                  {/* Botones de páginas */}
                  <div className="flex gap-1">
                    {page > 2 && (
                      <>
                        <button
                          onClick={() => setPage(1)}
                          className="px-3 py-1 text-sm rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                        >
                          1
                        </button>
                        {page > 3 && <span className="px-2 text-gray-500">...</span>}
                      </>
                    )}
                    
                    {page > 1 && (
                      <button
                        onClick={() => setPage(page - 1)}
                        className="px-3 py-1 text-sm rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                      >
                        {page - 1}
                      </button>
                    )}
                    
                    <button
                      className="px-3 py-1 text-sm rounded bg-primary text-white font-semibold"
                    >
                      {page}
                    </button>
                    
                    {logs.length === limit && (
                      <>
                        <button
                          onClick={() => setPage(page + 1)}
                          className="px-3 py-1 text-sm rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                        >
                          {page + 1}
                        </button>
                        <span className="px-2 text-gray-500">...</span>
                      </>
                    )}
                  </div>
                  
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Página {page} {totalPages > 0 ? `de ${totalPages}` : ''}
                  </span>
                </div>

                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={logs.length < limit}
                  className="w-full sm:w-auto px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Siguiente →
                </button>
              </div>
              
              {/* Info adicional de paginación */}
              <div className="text-center mt-4">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Mostrando {logs.length} registros por página
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  )
}

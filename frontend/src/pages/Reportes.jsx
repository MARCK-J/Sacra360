import { useState, useEffect } from 'react'
import axios from 'axios'
import Layout from '../components/Layout'

export default function Reportes() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dias, setDias] = useState(30)
  
  // Estados para cada tipo de reporte
  const [reporteUsuarios, setReporteUsuarios] = useState(null)
  const [reporteAccesos, setReporteAccesos] = useState(null)
  const [estadisticas, setEstadisticas] = useState(null)

  // Cargar reportes
  useEffect(() => {
    cargarReportes()
  }, [dias])

  const cargarReportes = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const token = localStorage.getItem('token')
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      }

      const baseUrl = import.meta.env.VITE_AUTH_API_URL

      // Llamadas paralelas a los endpoints
      const [resUsuarios, resAccesos, resEstadisticas] = await Promise.all([
        axios.get(`${baseUrl}/api/v1/reportes/usuarios?dias=${dias}`, config),
        axios.get(`${baseUrl}/api/v1/reportes/accesos?dias=${dias}`, config),
        axios.get(`${baseUrl}/api/v1/reportes/estadisticas`, config)
      ])

      setReporteUsuarios(resUsuarios.data)
      setReporteAccesos(resAccesos.data)
      setEstadisticas(resEstadisticas.data)
    } catch (err) {
      console.error('Error al cargar reportes:', err)
      setError(err.response?.data?.detail || 'Error al cargar reportes')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout title="Reportes y Estadísticas">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando reportes...</p>
          </div>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout title="Reportes y Estadísticas">
        <div className="rounded-xl bg-red-50 dark:bg-red-900/20 p-6 border border-red-200 dark:border-red-800">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-red-600 dark:text-red-400">error</span>
            <div>
              <h3 className="font-semibold text-red-900 dark:text-red-200">Error al cargar reportes</h3>
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          </div>
          <button 
            onClick={cargarReportes}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Reintentar
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Reportes y Estadísticas">
      {/* Filtro de período */}
      <div className="mb-6 flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Período:
        </label>
        <select 
          value={dias}
          onChange={(e) => setDias(Number(e.target.value))}
          className="rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          <option value={7}>Últimos 7 días</option>
          <option value={30}>Últimos 30 días</option>
          <option value={90}>Últimos 90 días</option>
          <option value={365}>Último año</option>
        </select>
        <button
          onClick={cargarReportes}
          className="ml-auto px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-xl">refresh</span>
          Actualizar
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Card: Total Usuarios */}
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Total Usuarios</h3>
            <span className="material-symbols-outlined text-primary">group</span>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {reporteUsuarios?.total_usuarios || 0}
          </p>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Activos</span>
              <span className="font-semibold text-green-600 dark:text-green-400">
                {reporteUsuarios?.usuarios_activos || 0}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Inactivos</span>
              <span className="font-semibold text-red-600 dark:text-red-400">
                {reporteUsuarios?.usuarios_inactivos || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Card: Usuarios por Rol */}
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Usuarios por Rol</h3>
            <span className="material-symbols-outlined text-primary">badge</span>
          </div>
          <div className="space-y-3">
            {reporteUsuarios?.usuarios_por_rol?.map((rol) => (
              <div key={rol.rol_nombre}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-700 dark:text-gray-300">{rol.rol_nombre}</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {rol.cantidad} ({rol.porcentaje}%)
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                  <div 
                    className="h-2 rounded-full bg-primary" 
                    style={{ width: `${rol.porcentaje}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card: Total Accesos */}
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Total Accesos</h3>
            <span className="material-symbols-outlined text-primary">login</span>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {reporteAccesos?.total_accesos || 0}
          </p>
          <div className="mt-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Promedio diario</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {reporteAccesos?.promedio_accesos_diario?.toFixed(1) || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Card: Accesos Diarios */}
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Accesos Diarios</h3>
            <span className="material-symbols-outlined text-primary">show_chart</span>
          </div>
          <div className="mt-4 h-48">
            {reporteAccesos?.accesos_por_dia?.length > 0 ? (
              <div className="grid h-full grid-flow-col items-end gap-2">
                {reporteAccesos.accesos_por_dia.slice(0, 15).map((dia, idx) => {
                  const maxAccesos = Math.max(...reporteAccesos.accesos_por_dia.map(d => d.cantidad))
                  const height = (dia.cantidad / maxAccesos) * 100
                  return (
                    <div 
                      key={idx}
                      className="w-full rounded-t-lg bg-primary/70 hover:bg-primary transition-colors cursor-pointer group relative"
                      style={{ height: `${height}%` }}
                      title={`${dia.fecha}: ${dia.cantidad} accesos`}
                    >
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {dia.fecha}: {dia.cantidad}
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No hay datos disponibles
              </div>
            )}
          </div>
        </div>

        {/* Card: Horas Pico */}
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Horas Pico</h3>
            <span className="material-symbols-outlined text-primary">schedule</span>
          </div>
          <div className="space-y-3">
            {reporteAccesos?.horas_pico?.slice(0, 5).map((hora, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {hora.hora}:00 hrs
                </span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-20 rounded-full bg-gray-200 dark:bg-gray-700">
                    <div 
                      className="h-2 rounded-full bg-accent-gold"
                      style={{ width: `${(hora.cantidad / reporteAccesos.horas_pico[0].cantidad) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white w-8 text-right">
                    {hora.cantidad}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card: Usuarios Más Activos */}
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Usuarios Más Activos</h3>
            <span className="material-symbols-outlined text-primary">trending_up</span>
          </div>
          <div className="space-y-3">
            {reporteAccesos?.usuarios_mas_activos?.map((usuario, idx) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-sm font-bold text-primary">#{idx + 1}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {usuario.nombre_completo}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {usuario.email}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-gray-900 dark:text-white">
                    {usuario.total_accesos}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">accesos</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card: Estadísticas Generales */}
        <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Estadísticas Generales</h3>
            <span className="material-symbols-outlined text-primary">analytics</span>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Promedio accesos/usuario</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {estadisticas?.promedio_accesos_por_usuario?.toFixed(1) || 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Promedio accesos/día</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {estadisticas?.promedio_accesos_por_dia?.toFixed(1) || 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total eventos auditados</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {estadisticas?.total_eventos_auditoria || 0}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

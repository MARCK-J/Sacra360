import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

const API_URL = 'http://localhost:8002/api/v1'

export default function Sacramentos() {
  const [sacramentos, setSacramentos] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filtros, setFiltros] = useState({
    tipo: '',
    persona: '',
    fecha_desde: '',
    fecha_hasta: ''
  })

  useEffect(() => {
    cargarSacramentos()
  }, [])

  const cargarSacramentos = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/sacramentos/list/details?limit=200`)
      if (!res.ok) throw new Error('Error al cargar sacramentos')
      const data = await res.json()
      console.log('Sacramentos cargados:', data)
      setSacramentos(data)
    } catch (err) {
      console.error('Error cargando sacramentos:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filtrarSacramentos = () => {
    return sacramentos.filter(sac => {
      // Filtro por búsqueda de persona
      if (filtros.persona) {
        const nombreCompleto = sac.persona?.nombre_completo?.toLowerCase() || ''
        if (!nombreCompleto.includes(filtros.persona.toLowerCase())) {
          return false
        }
      }
      // Filtro por tipo
      if (filtros.tipo && sac.tipo?.nombre !== filtros.tipo) {
        return false
      }
      return true
    })
  }

  const tiposUnicos = [...new Set(sacramentos.map(s => s.tipo?.nombre).filter(Boolean))]

  return (
    <Layout title="Sacramentos Registrados">
      <div className="bg-white dark:bg-gray-900/50 rounded-lg shadow">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Lista de Sacramentos
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Consulta y gestiona los sacramentos registrados en el sistema
          </p>
        </div>

        {/* Filtros */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Buscar por persona
              </label>
              <input
                type="text"
                placeholder="Nombre de la persona..."
                value={filtros.persona}
                onChange={(e) => setFiltros({...filtros, persona: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tipo de sacramento
              </label>
              <select
                value={filtros.tipo}
                onChange={(e) => setFiltros({...filtros, tipo: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos</option>
                {tiposUnicos.map(tipo => (
                  <option key={tipo} value={tipo}>{tipo}</option>
                ))}
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => setFiltros({ tipo: '', persona: '', fecha_desde: '', fecha_hasta: '' })}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
              >
                Limpiar filtros
              </button>
            </div>
          </div>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando sacramentos...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12 text-red-600">
              <p>❌ Error: {error}</p>
              <button onClick={cargarSacramentos} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded">
                Reintentar
              </button>
            </div>
          ) : filtrarSacramentos().length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400">
                No se encontraron sacramentos registrados
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Persona
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Institución
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Fecha Sacramento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Fecha Registro
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {filtrarSacramentos().map((sacramento) => (
                    <tr key={sacramento.id_sacramento} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {sacramento.id_sacramento}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {sacramento.persona?.nombre_completo || 'N/A'}
                        {sacramento.persona?.fecha_nacimiento && (
                          <div className="text-xs text-gray-500">
                            Nac: {new Date(sacramento.persona.fecha_nacimiento).toLocaleDateString()}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {sacramento.tipo?.nombre || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {sacramento.institucion?.nombre || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {sacramento.fecha_sacramento ? new Date(sacramento.fecha_sacramento).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {sacramento.fecha_registro ? new Date(sacramento.fecha_registro).toLocaleDateString() : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              <div className="mt-4 text-sm text-gray-600 dark:text-gray-400 text-center">
                Mostrando {filtrarSacramentos().length} de {sacramentos.length} registros
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

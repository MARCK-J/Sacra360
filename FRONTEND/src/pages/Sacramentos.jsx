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
  const [selected, setSelected] = useState(null)
  const [isEdit, setIsEdit] = useState(false)
  const [localCompleted, setLocalCompleted] = useState(new Set())

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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Acciones
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        { (localCompleted.has(sacramento.id_sacramento) || sacramento.completado || sacramento.validado)
                          ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                              Completado
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                              Pendiente
                            </span>
                          )}
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        <div className="flex gap-2">
                          <button
                            onClick={() => { setSelected(sacramento); setIsEdit(false) }}
                            className="px-2 py-1 bg-blue-600 text-white rounded text-xs"
                          >Ver</button>

                          <button
                            onClick={() => { setSelected(sacramento); setIsEdit(true) }}
                            className="px-2 py-1 bg-indigo-600 text-white rounded text-xs"
                          >Editar</button>

                          <button
                            onClick={async () => {
                              const id = sacramento.id_sacramento
                              try {
                                // intentar llamar endpoint de confirmación/validación
                                let res = await fetch(`${API_URL}/sacramentos/${id}/confirm`, { method: 'POST' })
                                if (!res.ok) {
                                  res = await fetch(`${API_URL}/sacramentos/${id}/validate`, { method: 'POST' })
                                }
                                if (!res.ok) {
                                  // fallback local
                                  const next = new Set(localCompleted)
                                  next.add(id)
                                  setLocalCompleted(next)
                                  alert('Marca como completado (persistencia no disponible en backend).')
                                } else {
                                  const next = new Set(localCompleted)
                                  next.add(id)
                                  setLocalCompleted(next)
                                  alert('Confirmación realizada correctamente')
                                }
                              } catch (err) {
                                const next = new Set(localCompleted)
                                next.add(id)
                                setLocalCompleted(next)
                                console.error(err)
                                alert('Error al confirmar en backend; marcado localmente como completado.')
                              }
                            }}
                            className="px-2 py-1 bg-green-600 text-white rounded text-xs"
                          >Confirmar</button>

                          <button
                            onClick={async () => {
                              if (!confirm('¿Eliminar (baja lógica) este sacramento?')) return
                              const id = sacramento.id_sacramento
                              try {
                                let res = await fetch(`${API_URL}/sacramentos/${id}`, { method: 'DELETE' })
                                if (!res.ok) {
                                  // intentar endpoint alternativo de baja lógica
                                  res = await fetch(`${API_URL}/sacramentos/${id}/deactivate`, { method: 'POST' })
                                }
                                if (!res.ok) throw new Error('Error en backend')
                                // quitar localmente
                                setSacramentos(prev => prev.filter(s => s.id_sacramento !== id))
                                alert('Sacramento eliminado')
                              } catch (err) {
                                console.error(err)
                                alert('No fue posible eliminar en backend; operación cancelada')
                              }
                            }}
                            className="px-2 py-1 bg-red-600 text-white rounded text-xs"
                          >Borrar</button>
                        </div>
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

        {/* Modal view / edit */}
        {selected && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="bg-white dark:bg-gray-900 rounded-lg w-11/12 md:w-2/3 p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">{isEdit ? 'Editar Sacramento' : 'Detalle de Sacramento'}</h3>
                <button onClick={() => setSelected(null)} className="text-gray-500">Cerrar</button>
              </div>

              {!isEdit ? (
                <div>
                  <p><strong>ID:</strong> {selected.id_sacramento}</p>
                  <p><strong>Persona:</strong> {selected.persona?.nombre_completo || 'N/A'}</p>
                  <p><strong>Tipo:</strong> {selected.tipo?.nombre || 'N/A'}</p>
                  <p><strong>Institución:</strong> {selected.institucion?.nombre || 'N/A'}</p>
                  <p><strong>Fecha sacramento:</strong> {selected.fecha_sacramento || 'N/A'}</p>
                  <p><strong>Fecha registro:</strong> {selected.fecha_registro || 'N/A'}</p>
                </div>
              ) : (
                <EditForm
                  sacramento={selected}
                  onCancel={() => setSelected(null)}
                  onSaved={(updated) => {
                    setSacramentos(prev => prev.map(s => s.id_sacramento === updated.id_sacramento ? updated : s))
                    const next = new Set(localCompleted)
                    next.add(updated.id_sacramento)
                    setLocalCompleted(next)
                    setSelected(null)
                  }}
                />
              )}
            </div>
          </div>
        )}
    </Layout>
  )
}


  function EditForm({ sacramento, onCancel, onSaved }) {
    const [tipo, setTipo] = useState(sacramento.tipo?.nombre || '')
    const [institucion, setInstitucion] = useState(sacramento.institucion?.nombre || '')
    const [fecha, setFecha] = useState(sacramento.fecha_sacramento || '')

    const handleSave = async () => {
      const payload = {
        tipo: tipo,
        institucion: institucion,
        fecha_sacramento: fecha
      }
      try {
        const res = await fetch(`${API_URL}/sacramentos/${sacramento.id_sacramento}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error('error')
        const updated = await res.json()
        onSaved(updated)
        alert('Guardado correctamente')
      } catch (err) {
        console.error(err)
        alert('No se pudo guardar en backend; cambios no persistidos')
      }
    }

    return (
      <div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm">Tipo</label>
            <input value={tipo} onChange={e => setTipo(e.target.value)} className="w-full px-2 py-1 border" />
          </div>
          <div>
            <label className="block text-sm">Institución</label>
            <input value={institucion} onChange={e => setInstitucion(e.target.value)} className="w-full px-2 py-1 border" />
          </div>
          <div>
            <label className="block text-sm">Fecha Sacramento</label>
            <input type="date" value={fecha ? fecha.split('T')[0] : ''} onChange={e => setFecha(e.target.value)} className="w-full px-2 py-1 border" />
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded">Guardar</button>
          <button onClick={onCancel} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        </div>
      </div>
    )
  }

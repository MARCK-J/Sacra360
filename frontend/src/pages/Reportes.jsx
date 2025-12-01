import { useEffect, useState } from 'react'
import Layout from '../components/Layout'

export default function Reportes() {
  const [counts, setCounts] = useState([])
  const [loadingCounts, setLoadingCounts] = useState(true)
  const [errorCounts, setErrorCounts] = useState(null)

  const [tipos, setTipos] = useState([])

  // filtros & lista
  const [filtros, setFiltros] = useState({ fecha_inicio: '', fecha_fin: '', tipo: '', q: '' })
  const [sacramentos, setSacramentos] = useState([])
  const [loadingList, setLoadingList] = useState(false)
  const [errorList, setErrorList] = useState(null)
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(20)

  useEffect(() => {
    loadCounts()
    loadTipos()
    loadSacramentos() // initial load without filters
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function loadCounts() {
    setLoadingCounts(true)
    setErrorCounts(null)
    try {
      const res = await fetch('/api/v1/reportes/count-by-type')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setCounts(data.counts || [])
    } catch (err) {
      setErrorCounts(err.message)
    } finally {
      setLoadingCounts(false)
    }
  }

  async function loadTipos() {
    try {
      const res = await fetch('/api/v1/tipos-sacramentos?skip=0&limit=100')
      if (!res.ok) return
      const data = await res.json()
      // controller returns { tipos_sacramentos: [...], total }
      setTipos(data.tipos_sacramentos || [])
    } catch (err) {
      // ignore non-critical
    }
  }

  function buildQuery() {
    const params = new URLSearchParams()
    if (filtros.tipo) params.append('tipo_sacramento', filtros.tipo)
    if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio)
    if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin)
    if (filtros.q) params.append('sacerdote', filtros.q)
    params.append('page', String(page))
    params.append('limit', String(limit))
    return params.toString()
  }

  async function loadSacramentos(p = page) {
    setLoadingList(true)
    setErrorList(null)
    try {
      const q = buildQuery()
      const res = await fetch('/api/v1/sacramentos/?' + q)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setSacramentos(data || [])
    } catch (err) {
      setErrorList(err.message)
    } finally {
      setLoadingList(false)
    }
  }

  function handleFiltroChange(e) {
    const { name, value } = e.target
    setFiltros((s) => ({ ...s, [name]: value }))
  }

  function applyFilters() {
    setPage(1)
    loadSacramentos(1)
    loadCounts()
  }

  function clearFilters() {
    setFiltros({ fecha_inicio: '', fecha_fin: '', tipo: '', q: '' })
    setPage(1)
    loadSacramentos(1)
    loadCounts()
  }

  function prevPage() {
    if (page <= 1) return
    setPage((p) => {
      const np = p - 1
      loadSacramentos(np)
      return np
    })
  }

  function nextPage() {
    setPage((p) => {
      const np = p + 1
      loadSacramentos(np)
      return np
    })
  }

  return (
    <Layout title="Reportes">
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800/50 p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Filtros</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Fecha inicio</label>
              <input type="date" name="fecha_inicio" value={filtros.fecha_inicio} onChange={handleFiltroChange} className="form-input w-full" />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Fecha fin</label>
              <input type="date" name="fecha_fin" value={filtros.fecha_fin} onChange={handleFiltroChange} className="form-input w-full" />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Tipo</label>
              <select name="tipo" value={filtros.tipo} onChange={handleFiltroChange} className="form-input w-full">
                <option value="">Todos</option>
                {tipos.map((t) => (
                  <option key={t.id_tipo} value={t.nombre}>{t.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Buscar (ministro/persona)</label>
              <input name="q" value={filtros.q} onChange={handleFiltroChange} placeholder="Nombre o ministro" className="form-input w-full" />
            </div>
          </div>
          <div className="flex gap-3 justify-end mt-4">
            <button type="button" onClick={clearFilters} className="px-3 py-2 rounded-lg border">Limpiar</button>
            <button type="button" onClick={applyFilters} className="px-3 py-2 rounded-lg bg-primary text-white">Aplicar</button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sacramentos por Tipo</h3>
            {loadingCounts && <p className="text-sm text-gray-500">Cargando...</p>}
            {errorCounts && <p className="text-sm text-red-600">Error: {errorCounts}</p>}
            {!loadingCounts && !errorCounts && (
              <div className="mt-4">
                {counts.length === 0 && <p className="text-sm text-gray-500">No hay datos disponibles.</p>}
                <ul className="space-y-2">
                  {counts.map((c) => (
                    <li key={c.tipo} className="flex justify-between items-center border-b py-2">
                      <span className="text-sm text-gray-700 dark:text-gray-200">{c.tipo}</span>
                      <span className="text-lg font-semibold text-gray-900 dark:text-white">{c.total}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="rounded-xl bg-white dark:bg-gray-800/50 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Resultados</h3>
            {loadingList && <p className="text-sm text-gray-500">Cargando lista...</p>}
            {errorList && <p className="text-sm text-red-600">Error: {errorList}</p>}
            {!loadingList && !errorList && (
              <div className="mt-4">
                {sacramentos.length === 0 && <p className="text-sm text-gray-500">No hay registros.</p>}
                {sacramentos.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                      <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                        <tr>
                          <th className="px-4 py-2">ID</th>
                          <th className="px-4 py-2">Fecha</th>
                          <th className="px-4 py-2">Tipo</th>
                          <th className="px-4 py-2">Persona ID</th>
                          <th className="px-4 py-2">Institución</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sacramentos.map((s) => (
                          <tr key={s.id_sacramento} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                            <td className="px-4 py-2 font-medium text-gray-900 dark:text-white">{s.id_sacramento}</td>
                            <td className="px-4 py-2">{s.fecha_sacramento?.substring(0,10) || s.fecha_sacramento}</td>
                            <td className="px-4 py-2">{s.tipo_nombre || s.tipo_sacramento}</td>
                            <td className="px-4 py-2">{s.persona_id}</td>
                            <td className="px-4 py-2">{s.institucion_id}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <div className="flex justify-between items-center mt-3">
                      <div className="text-sm text-gray-600">Página {page}</div>
                      <div className="flex gap-2">
                        <button onClick={prevPage} className="px-3 py-1 rounded border">Anterior</button>
                        <button onClick={nextPage} className="px-3 py-1 rounded bg-primary text-white">Siguiente</button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}

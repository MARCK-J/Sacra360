import { useEffect, useState, useRef } from 'react'
import Layout from '../components/Layout'

export default function Reportes() {
  const [counts, setCounts] = useState([])
  const [loadingCounts, setLoadingCounts] = useState(true)
  const [errorCounts, setErrorCounts] = useState(null)

  const [tipos, setTipos] = useState([])
  // preserve original catalog id->name mapping (some entries use ids that contain numeric codes)
  const tipoIdToNameRef = useRef(new Map())
  // preserve raw name returned by backend for each tipo id (may be numeric like '2')
  const tipoIdRawRef = useRef(new Map())

  // Map numeric sacrament codes to canonical names when the catalog uses numbers
  const SACRAMENTO_NAME_BY_CODE = {
    '1': 'bautizo',
    '2': 'confirmacion',
    '3': 'matrimonio',
    '4': 'defuncion'
  }

  // Build a display label for a count 'tipo' value using available maps
  function resolveTipoLabel(rawTipo) {
    if (rawTipo == null) return String(rawTipo)
    const s = String(rawTipo)
    // numeric string -> canonical
    if (/^\d+$/.test(s)) {
      // try SACRAMENTO map first
      if (SACRAMENTO_NAME_BY_CODE[s]) return SACRAMENTO_NAME_BY_CODE[s]
      // try the original catalog id->name mapping
      const n = Number(s)
      if (!Number.isNaN(n) && tipoIdToNameRef.current.has(n)) {
        const v = tipoIdToNameRef.current.get(n)
        // if v is numeric-like, map via SACRAMENTO map
        if (/^\d+$/.test(String(v)) && SACRAMENTO_NAME_BY_CODE[String(v)]) return SACRAMENTO_NAME_BY_CODE[String(v)]
        return v
      }
      return s
    }
    // non-numeric: try matching against canonical tipos
    const key = s.toLowerCase()
    if (tipos && tipos.length > 0) {
      const found = tipos.find((t) => String(t.nombre || '').toLowerCase() === key || String(t.id) === s)
      if (found) return found.nombre
    }
    // try sacraments map by name
    if (SACRAMENTO_NAME_BY_CODE) {
      const entry = Object.entries(SACRAMENTO_NAME_BY_CODE).find(([, name]) => String(name).toLowerCase() === key)
      if (entry) return entry[1]
    }
    return s
  }

  // filtros & lista
  const [filtros, setFiltros] = useState({ fecha_inicio: '', fecha_fin: '', tipo: '', q: '' })
  const [sacramentos, setSacramentos] = useState([])
  const [loadingList, setLoadingList] = useState(false)
  const [errorList, setErrorList] = useState(null)
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(20)

  useEffect(() => {
    async function init() {
      loadCounts()
      await loadTipos()
      await loadSacramentos() // initial load after tipos
    }
    init()
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
      // Normalize tipos to a consistent shape: { id, nombre }
      const raw = data.tipos_sacramentos || []
      const normalized = raw.map((t) => {
        const idVal = Number(t.id_tipo ?? t.id ?? t.id_tipo_sacramento ?? t.id_institucion ?? t.id) || t.id || t.id_tipo || 0
        // capture original/raw name from backend before normalization
        const rawName = String(t.nombre ?? t.nombre_tipo ?? t.tipo ?? '').trim()
        let nombreVal = rawName
        nombreVal = String(nombreVal || '').trim()
        // If the catalog stores numeric codes as names (e.g. "2"), map to canonical name
        if (/^\d+$/.test(nombreVal) && SACRAMENTO_NAME_BY_CODE[nombreVal]) {
          nombreVal = SACRAMENTO_NAME_BY_CODE[nombreVal]
        }
        return { id: idVal, nombre: nombreVal, rawName }
      })
      // store original id->name mapping for lookups (preserve entries like id:9 -> nombre:'confirmacion')
      tipoIdToNameRef.current.clear()
      tipoIdRawRef.current.clear()
      normalized.forEach((t) => {
        if (t && t.id) {
          tipoIdToNameRef.current.set(Number(t.id), t.nombre)
          // rawName may be numeric or textual as returned by backend
          tipoIdRawRef.current.set(Number(t.id), t.rawName || '')
        }
      })

      // Reduce/normalize catalog to the 4 canonical sacrament types.
      const canonical = [
        { id: 1, nombre: null }, // bautizo (keep label from catalog if present)
        { id: 2, nombre: null }, // confirmacion
        { id: 3, nombre: null }, // matrimonio
        { id: 4, nombre: null }  // defuncion
      ]

      // Try to preserve catalog labels for bautizo if present; otherwise use lowercase canonical
      const findByName = (needleRegex) => normalized.find((x) => x && x.nombre && needleRegex.test(String(x.nombre).toLowerCase()))

      // bautizo: prefer any existing 'bautizo' label
      const bautizo = findByName(/bautizo/)
      canonical[0].nombre = bautizo ? bautizo.nombre : 'bautizo'

      // confirmacion: look for explicit name or numeric-coded entry mapped earlier
      const confirmacion = normalized.find((x) => x && (String(x.id) === '2' || String(x.nombre).toLowerCase() === 'confirmacion' || /confirmacion/.test(String(x.nombre).toLowerCase())))
      canonical[1].nombre = confirmacion ? confirmacion.nombre : 'confirmacion'

      // matrimonio: look for any matching label
      const matrimonio = findByName(/matrimonio/)
      canonical[2].nombre = matrimonio ? matrimonio.nombre : 'matrimonio'

      // defuncion: try to find label, fallback to 'defuncion'
      const defuncion = findByName(/defuncion|fallec/)
      canonical[3].nombre = defuncion ? defuncion.nombre : 'defuncion'

      setTipos(canonical)
    } catch (err) {
      // ignore non-critical
    }
  }

  function buildQuery() {
    const params = new URLSearchParams()
    if (filtros.tipo) {
      // The backend expects a tipo_sacramento name (e.g. 'bautizo').
      // The select provides either an id (numeric) or a name. Prefer using the canonical `tipos` array to resolve ids.
      let tipoVal = filtros.tipo
      try {
        if (/^\d+$/.test(String(tipoVal))) {
          const tid = Number(tipoVal)
          const found = tipos && tipos.find((t) => Number(t.id) === tid)
          if (found && found.nombre) {
            // prefer sending the raw backend name if it exists (db may store numeric codes like '2')
            const rawName = tipoIdRawRef.current.get(tid)
            if (rawName && String(rawName).trim() !== '') {
              tipoVal = rawName
            } else {
              tipoVal = found.nombre
            }
          } else if (SACRAMENTO_NAME_BY_CODE[String(tid)]) tipoVal = SACRAMENTO_NAME_BY_CODE[String(tid)]
        } else if (typeof tipoVal === 'string') {
          // normalize to catalog label if possible
          const key = String(tipoVal).trim()
          const byName = tipos && tipos.find((t) => String(t.nombre).toLowerCase() === String(key).toLowerCase())
          if (byName && byName.nombre) tipoVal = byName.nombre
        }
      } catch (e) {}
      params.append('tipo_sacramento', String(tipoVal).trim())
    }
    if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio)
    if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin)
    // filtros.q should search only by persona (not sacerdote).
    // If numeric -> treat as persona id and send as id_persona; otherwise we'll filter client-side by persona name.
    if (filtros.q) {
      const q = String(filtros.q).trim()
      if (/^\d+$/.test(q)) {
        params.append('id_persona', q)
      }
      // else: do not send 'sacerdote' param; client-side filtering will handle text search by persona name
    }
    params.append('page', String(page))
    params.append('limit', String(limit))
    return params.toString()
  }

  async function loadSacramentos(p = page) {
    setLoadingList(true)
    setErrorList(null)
    try {
      const q = buildQuery()
      const res = await fetch('/api/v1/reportes/sacramentos?' + q)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      let data = await res.json()
      // Accept legacy object shape { sacramentos: [...], page, limit }
      if (data && data.sacramentos) data = data.sacramentos
      data = data || []
      

      // Si el backend no devuelve persona_nombre para algunos registros,
      // obtenerlos desde el endpoint de personas y rellenarlos.
      const missingPersonaIds = Array.from(new Set(
        data.filter((r) => (!r.persona_nombre || r.persona_nombre === null) && r.persona_id).map((r) => r.persona_id)
      ))
      if (missingPersonaIds.length > 0) {
        await Promise.all(missingPersonaIds.map(async (pid) => {
          try {
            const pr = await fetch(`/api/v1/personas/${pid}`)
            if (!pr.ok) return
            const pj = await pr.json()
            const full = [pj.nombres, pj.apellido_paterno, pj.apellido_materno].filter(Boolean).join(' ').trim()
            if (full) {
              data = data.map((r) => (r.persona_id === pid && (!r.persona_nombre || r.persona_nombre === null) ? { ...r, persona_nombre: full } : r))
            }
          } catch (e) {
            // ignore individual lookup errors
          }
        }))
      }

      // If filtros.q is present as text (non-numeric), filter client-side by persona name
      if (filtros.q && !/^\d+$/.test(String(filtros.q).trim())) {
        const qLower = String(filtros.q).toLowerCase().trim()
        const nameOf = (r) => {
          if (r.persona_nombre) return String(r.persona_nombre)
          if (r.persona && typeof r.persona === 'object') return [r.persona.nombres, r.persona.apellido_paterno, r.persona.apellido_materno].filter(Boolean).join(' ')
          return r.persona_id ? String(r.persona_id) : ''
        }
        data = data.filter((r) => {
          const name = String(nameOf(r) || '').toLowerCase()
          return name.includes(qLower)
        })
      }

      // Rellenar nombres de institución si el backend no los incluyó
      // Recoger ids de institución usando varias claves posibles
      const extractInstId = (r) => r.institucion_id ?? r.institucion ?? r.id_institucion ?? null
      const missingInstitucionIds = Array.from(new Set(
        data.filter((r) => (!r.institucion_nombre || r.institucion_nombre === null) && extractInstId(r)).map((r) => extractInstId(r))
      ))
      if (missingInstitucionIds.length > 0) {
        try {
          // Intentar la ruta correcta del backend (validacion controller)
          let ir = await fetch('/api/v1/validacion/instituciones')
          if (!ir.ok) {
            // fallback antiguo por compatibilidad
            ir = await fetch('/api/v1/instituciones')
          }
          if (ir.ok) {
            const ij = await ir.json()
            const institMap = new Map()
            ;(ij.instituciones || []).forEach((it) => {
              // guardar como string y número para evitar problemas de tipos
              institMap.set(String(it.id_institucion), it.nombre)
              institMap.set(Number(it.id_institucion), it.nombre)
            })
            data = data.map((r) => {
              const iid = extractInstId(r)
              if (iid && (!r.institucion_nombre || r.institucion_nombre === null)) {
                const name = institMap.get(iid) ?? institMap.get(String(iid))
                if (name) return { ...r, institucion_nombre: name }
              }
              return r
            })
          }
        } catch (e) {
          // ignore
        }
      }

      // Si el backend no proporcionó tipo_nombre para algunos registros,
      // intentar resolverlo con el catálogo tipos que cargamos al inicio.
      if ((data || []).length > 0) {
        // build quick lookup maps if tipos exist
        const tipoById = new Map()
        const tipoByName = new Map()
        if (tipos && tipos.length > 0) {
          tipos.forEach((t) => {
            if (t.id) tipoById.set(Number(t.id), t.nombre)
            if (t.nombre) tipoByName.set(String(t.nombre).toLowerCase(), t.nombre)
          })
        }

        data = data.map((r) => {
          // also treat numeric-looking tipo_nombre ("2") as unresolved and map it
          const tipoNombreIsNumeric = r.tipo_nombre != null && /^\d+$/.test(String(r.tipo_nombre))
          if (!r.tipo_nombre || r.tipo_nombre === null || tipoNombreIsNumeric) {
            const tidRaw = (r.tipo_id ?? r.tipo) || r.tipo_sacramento
            const tidNum = Number(tidRaw)
            let resolved = null
            // First try direct id lookup when catalog present
            if (tipos && tipos.length > 0 && !Number.isNaN(tidNum) && tipoById.has(tidNum)) resolved = tipoById.get(tidNum)
            // Next try known sacrament code map (1,2,3,4) — works even if tipos not yet loaded
            if (!resolved && tidRaw != null) {
              const codeName = SACRAMENTO_NAME_BY_CODE[String(tidRaw)]
              if (codeName) resolved = codeName
            }
            // Also try original catalog id->name mapping (covers cases like id:9 with nombre:'2')
            if (!resolved && !Number.isNaN(tidNum) && tipoIdToNameRef.current.has(tidNum)) {
              resolved = tipoIdToNameRef.current.get(tidNum)
            }
            // Finally try matching by name in the catalog if present
            if (!resolved && tipos && tipos.length > 0 && tidRaw) {
              const key = String(tidRaw).toLowerCase()
              if (tipoByName.has(key)) resolved = tipoByName.get(key)
            }
            if (resolved) return { ...r, tipo_nombre: resolved }
          }
          return r
        })
      }

      setSacramentos(data)
      return data
    } catch (err) {
      setErrorList(err.message)
    } finally {
      setLoadingList(false)
    }
  }

  // Derived statistics helpers
  function getAggregatedCounts() {
    const map = new Map()
    ;(counts || []).forEach((c) => {
      const label = resolveTipoLabel(c.tipo)
      const prev = map.get(label) || 0
      map.set(label, prev + (Number(c.total) || 0))
    })
    return Array.from(map.entries()).map(([tipo, total]) => ({ tipo, total }))
  }

  // Build last N months labels and counts from sacramentos list
  function getMonthlySeries(months = 6) {
    const seriesMap = new Map()
    const now = new Date()
    // init map for last months months
    for (let i = months - 1; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      seriesMap.set(key, 0)
    }
    ;(sacramentos || []).forEach((s) => {
      const f = s.fecha_sacramento || s.fecha || s.fecha_registro
      if (!f) return
      const d = new Date(String(f))
      if (isNaN(d.getTime())) return
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      if (seriesMap.has(key)) seriesMap.set(key, seriesMap.get(key) + 1)
    })
    const labels = Array.from(seriesMap.keys())
    const values = Array.from(seriesMap.values())
    return { labels, values }
  }

  // Simple SVG bar chart for counts by tipo
  function BarChart({ data, width = 360, height = 160 }) {
    if (!data || data.length === 0) return <div className="text-sm text-gray-500">No hay datos para el gráfico.</div>
    const max = Math.max(...data.map((d) => d.total)) || 1
    const barW = Math.max(24, Math.floor((width - 40) / data.length))
    return (
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="mx-auto block">
        <rect x="0" y="0" width={width} height={height} fill="transparent" />
        {data.map((d, i) => {
          const x = 20 + i * barW
          const h = Math.round((d.total / max) * (height - 40))
          const y = height - 20 - h
          return (
            <g key={d.tipo}>
              <rect x={x} y={y} width={barW - 8} height={h} fill="#0b74ff" rx="4" />
              <text x={x + (barW - 8) / 2} y={height - 6} fontSize="11" textAnchor="middle" fill="#0f172a">{d.tipo}</text>
            </g>
          )
        })}
      </svg>
    )
  }

  // Simple sparkline (line) for monthly counts
  function LineSpark({ labels, values, width = 360, height = 80 }) {
    if (!labels || labels.length === 0) return <div className="text-sm text-gray-500">No hay datos.</div>
    const max = Math.max(...values, 1)
    const min = Math.min(...values)
    const points = values.map((v, i) => {
      const x = Math.round((i / (values.length - 1)) * (width - 20)) + 10
      const y = Math.round(((max - v) / (max - min || 1)) * (height - 20)) + 10
      return `${x},${y}`
    }).join(' ')
    return (
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="mx-auto block">
        <polyline points={points} fill="none" stroke="#0b74ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        {values.map((v, i) => {
          const x = Math.round((i / (values.length - 1)) * (width - 20)) + 10
          const y = Math.round(((max - v) / (max - min || 1)) * (height - 20)) + 10
          return <circle key={i} cx={x} cy={y} r={2.5} fill="#0b74ff" />
        })}
        <g>
          {labels.map((lbl, i) => {
            const x = Math.round((i / (labels.length - 1)) * (width - 20)) + 10
            return <text key={i} x={x} y={height - 1} fontSize="10" textAnchor="middle" fill="#64748b">{lbl.split('-').slice(1).join('/')}</text>
          })}
        </g>
      </svg>
    )
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
                  <option key={t.id} value={t.id || t.nombre}>{t.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Buscar (persona)</label>
              <input name="q" value={filtros.q} onChange={handleFiltroChange} placeholder="ID o nombre de la persona" className="form-input w-full" />
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
                <div className="mb-4">
                  {/* Bar chart for counts */}
                  {(() => {
                    const data = getAggregatedCounts()
                    return <BarChart data={data} width={340} height={160} />
                  })()}
                </div>
                <ul className="space-y-2">
                  {getAggregatedCounts().map((c) => (
                    <li key={c.tipo} className="flex justify-between items-center border-b py-2">
                      <div>
                        <span className="text-sm text-gray-700 dark:text-gray-200 mr-2">{c.tipo}</span>
                        <span className="text-xs text-muted-foreground-light text-gray-500">({Math.round((c.total / (getAggregatedCounts().reduce((s, x) => s + x.total, 0) || 1)) * 100)}%)</span>
                      </div>
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
                {/* Monthly sparkline */}
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Sacramentos últimos meses</h4>
                  {(() => {
                    const series = getMonthlySeries(6)
                    return <LineSpark labels={series.labels} values={series.values} width={520} height={96} />
                  })()}
                </div>
                {sacramentos.length === 0 && <p className="text-sm text-gray-500">No hay registros.</p>}
                {sacramentos.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                      <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700/50">
                        <tr>
                          <th className="px-4 py-2">ID</th>
                          <th className="px-4 py-2">Fecha</th>
                          <th className="px-4 py-2">Tipo</th>
                          <th className="px-4 py-2">Persona</th>
                          <th className="px-4 py-2">Institución</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sacramentos.map((s) => (
                          <tr key={s.id_sacramento} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                            <td className="px-4 py-2 font-medium text-gray-900 dark:text-white">{s.id_sacramento}</td>
                            <td className="px-4 py-2">{s.fecha_sacramento?.substring(0,10) || s.fecha_sacramento}</td>
                              <td className="px-4 py-2">
                                {resolveTipoLabel(s.tipo_nombre ?? (s.tipo && typeof s.tipo === 'object' ? (s.tipo.nombre ?? s.tipo.id_tipo) : (s.tipo_sacramento ?? s.tipo)))}
                              </td>
                              <td className="px-4 py-2">
                                {s.persona_nombre ?? (s.persona && typeof s.persona === 'object' ? [s.persona.nombres, s.persona.apellido_paterno, s.persona.apellido_materno].filter(Boolean).join(' ') : s.persona_id)}
                              </td>
                              <td className="px-4 py-2">
                                {s.institucion_nombre ?? (s.institucion && typeof s.institucion === 'object' ? (s.institucion.nombre ?? s.institucion.id_institucion) : (s.institucion ?? s.parroquia ?? s.sacrament_location ?? s.institucion_id))}
                              </td>
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
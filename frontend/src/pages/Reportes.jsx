import { useEffect, useState, useRef } from 'react'
import Layout from '../components/Layout'

export default function Reportes() {
  const [counts, setCounts] = useState([])
  const [loadingCounts, setLoadingCounts] = useState(true)
  const [errorCounts, setErrorCounts] = useState(null)

  const [tipos, setTipos] = useState([])
  // preserve original catalog id->name mapping (some entries use ids that contain numeric codes)
  const tipoIdToNameRef = useRef(new Map())

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
        let nombreVal = t.nombre || t.nombre_tipo || t.tipo || String(t.nombre || '')
        nombreVal = String(nombreVal || '').trim()
        // If the catalog stores numeric codes as names (e.g. "2"), map to canonical name
        if (/^\d+$/.test(nombreVal) && SACRAMENTO_NAME_BY_CODE[nombreVal]) {
          nombreVal = SACRAMENTO_NAME_BY_CODE[nombreVal]
        }
        return { id: idVal, nombre: nombreVal }
      })
      // store original id->name mapping for lookups (preserve entries like id:9 -> nombre:'confirmacion')
      tipoIdToNameRef.current.clear()
      normalized.forEach((t) => {
        if (t && t.id) tipoIdToNameRef.current.set(Number(t.id), t.nombre)
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
      let data = await res.json()
      data = data || []
      

      // Si el backend no devuelve `persona_nombre` para algunos registros,
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
      // intentar resolverlo con el catálogo `tipos` que cargamos al inicio.
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
                  <option key={t.id} value={t.id || t.nombre}>{t.nombre}</option>
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
                  {(() => {
                    // normalize and aggregate counts by canonical label
                    const map = new Map()
                    ;(counts || []).forEach((c) => {
                      const label = resolveTipoLabel(c.tipo)
                      const prev = map.get(label) || 0
                      map.set(label, prev + (Number(c.total) || 0))
                    })
                    const aggregated = Array.from(map.entries()).map(([tipo, total]) => ({ tipo, total }))
                    return aggregated.map((c) => (
                      <li key={c.tipo} className="flex justify-between items-center border-b py-2">
                        <span className="text-sm text-gray-700 dark:text-gray-200">{c.tipo}</span>
                        <span className="text-lg font-semibold text-gray-900 dark:text-white">{c.total}</span>
                      </li>
                    ))
                  })()}
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
                          <th className="px-4 py-2">Persona</th>
                          <th className="px-4 py-2">Institución</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sacramentos.map((s) => (
                          <tr key={s.id_sacramento} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                            <td className="px-4 py-2 font-medium text-gray-900 dark:text-white">{s.id_sacramento}</td>
                            <td className="px-4 py-2">{s.fecha_sacramento?.substring(0,10) || s.fecha_sacramento}</td>
                            <td className="px-4 py-2">{s.tipo_nombre || s.tipo_sacramento}</td>
                            <td className="px-4 py-2">{s.persona_nombre ?? s.persona_id}</td>
                            <td className="px-4 py-2">{s.institucion_nombre ?? s.institucion ?? s.parroquia ?? s.sacrament_location ?? s.institucion_id}</td>
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

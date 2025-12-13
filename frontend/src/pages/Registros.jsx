import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'

// Unified API constants
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8002'
const API_URL = `${API_BASE}/api/v1`

// Shared helpers (from both variants)
function getPersonaLabel(s) {
  if (!s) return '—'
  return s.persona_nombre || s.nombre || (s.persona && s.persona.nombre) || s.titular || s.contrayente || '—'
}

function getSacramentoType(s) {
  const tipoNombre = s && (s.tipo_nombre || s.tipo_sacramento_nombre || s.tipo_sacramento || s.tipo)
  if (!tipoNombre && tipoNombre !== 0) return '—'
  if (typeof tipoNombre === 'string' && isNaN(Number(tipoNombre))) return tipoNombre
  const id = Number(tipoNombre)
  const map = {1: 'bautizo', 2: 'confirmacion', 3: 'matrimonio', 4: 'defuncion', 5: 'primera comunion'}
  return map[id] || String(tipoNombre)
}

function getYear(s) {
  const candidates = [s && s.fecha, s && s.fecha_sacramento, s && s.fecha_defuncion, s && s.fecha_nacimiento]
  for (const c of candidates) {
    if (!c) continue
    try {
      const y = String(c).slice(0, 4)
      if (/^\d{4}$/.test(y)) return y
    } catch (e) {}
  }
  return '—'
}

// Create form component (adapted from first variant)
function CreateForm({ onSaved }) {
  const [tiposSacramentos, setTiposSacramentos] = useState([])
  const [libros, setLibros] = useState([])
  const [instituciones, setInstituciones] = useState([])

  const [tipoSeleccionado, setTipoSeleccionado] = useState('')
  const [libroSeleccionado, setLibroSeleccionado] = useState('')
  const [institucionSeleccionada, setInstitucionSeleccionada] = useState('')

  const [persona, setPersona] = useState({
    nombres: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    fecha_bautismo: '',
    nombre_padre_nombre_madre: '',
    nombre_padrino_nombre_madrina: ''
  })

  const [fechaSacramento, setFechaSacramento] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [validacionDuplicado, setValidacionDuplicado] = useState(null)

  useEffect(() => { cargarCatalogos() }, [])

  const cargarCatalogos = async () => {
    try {
      const [tiposRes, librosRes, institucionesRes] = await Promise.all([
        fetch(`${API_URL}/tipos-sacramentos`),
        fetch(`${API_URL}/libros`),
        fetch(`${API_URL}/instituciones`)
      ])
      if (!tiposRes.ok || !librosRes.ok || !institucionesRes.ok) throw new Error('Error al cargar datos del servidor')
      const tipos = await tiposRes.json()
      const librosData = await librosRes.json()
      const institucionesData = await institucionesRes.json()
      setTiposSacramentos(tipos.tipos_sacramentos || tipos)
      setLibros(librosData)
      setInstituciones(institucionesData)
    } catch (err) {
      console.error('Error cargando catálogos:', err)
      setError('Error al cargar los catálogos: ' + (err.message || err))
    }
  }

  const handlePersonaChange = (e) => {
    const { name, value } = e.target
    setPersona(prev => ({ ...prev, [name]: value }))
  }

  const validarDuplicado = async () => {
    if (!tipoSeleccionado || !persona.nombres || !persona.apellido_paterno || !fechaSacramento || !persona.fecha_nacimiento) {
      setValidacionDuplicado(null)
      return
    }
    try {
      const searchRes = await fetch(
        `${API_URL}/personas/search?nombres=${encodeURIComponent(persona.nombres)}&apellido_paterno=${encodeURIComponent(persona.apellido_paterno)}&fecha_nacimiento=${persona.fecha_nacimiento}`
      )
      const personasEncontradas = await searchRes.json()
      if (personasEncontradas.length > 0) {
        const personaId = personasEncontradas[0].id_persona
        const checkRes = await fetch(`${API_URL}/sacramentos/check-duplicate?persona_id=${personaId}&tipo_id=${tipoSeleccionado}`)
        const resultado = await checkRes.json()
        if (resultado.exists) {
          setValidacionDuplicado({ error: true, mensaje: `⚠️ Esta persona ya tiene el sacramento seleccionado registrado (ID: ${resultado.sacramento?.id_sacramento || resultado.sacramento?.id || '—'})` })
        } else {
          setValidacionDuplicado({ error: false, mensaje: '✓ Persona encontrada. Puede proceder con el registro del sacramento.' })
        }
      } else {
        setValidacionDuplicado({ error: false, mensaje: '✓ Persona nueva. Se creará el registro de la persona y el sacramento.' })
      }
    } catch (err) {
      console.error('Error validando duplicado:', err)
    }
  }

  useEffect(() => {
    const timer = setTimeout(validarDuplicado, 500)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tipoSeleccionado, persona.nombres, persona.apellido_paterno, persona.fecha_nacimiento, fechaSacramento])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (validacionDuplicado?.error) { setError('No se puede registrar un sacramento duplicado'); return }
    setLoading(true); setError(null); setSuccess(null)
    try {
      let personaId
      const searchRes = await fetch(`${API_URL}/personas/search?nombres=${encodeURIComponent(persona.nombres)}&apellido_paterno=${encodeURIComponent(persona.apellido_paterno)}&fecha_nacimiento=${persona.fecha_nacimiento}`)
      const personasEncontradas = await searchRes.json()
      if (personasEncontradas.length > 0) personaId = personasEncontradas[0].id_persona
      else {
        const createPersonaRes = await fetch(`${API_URL}/personas`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(persona) })
        if (!createPersonaRes.ok) throw new Error('Error al crear persona')
        const nuevaPersona = await createPersonaRes.json()
        personaId = nuevaPersona.id_persona
      }

      const sacramentoData = {
        persona_id: personaId,
        tipo_id: parseInt(tipoSeleccionado),
        libro_id: libroSeleccionado ? parseInt(libroSeleccionado) : undefined,
        institucion_id: institucionSeleccionada ? parseInt(institucionSeleccionada) : undefined,
        fecha_sacramento: fechaSacramento,
        usuario_id: 4
      }

      const createSacramentoRes = await fetch(`${API_URL}/sacramentos`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sacramentoData) })
      if (!createSacramentoRes.ok) {
        const tryBody = await createSacramentoRes.text().catch(() => '')
        throw new Error(tryBody || 'Error al crear sacramento')
      }
      const nuevoSacramento = await createSacramentoRes.json()
      setSuccess(`✓ Sacramento registrado exitosamente. ID: ${nuevoSacramento.id_sacramento || nuevoSacramento.id || '—'}`)
      setTimeout(() => resetForm(), 1200)
      if (typeof onSaved === 'function') onSaved()
    } catch (err) {
      setError('Error: ' + (err.message || err))
    } finally { setLoading(false) }
  }

  const resetForm = () => {
    setTipoSeleccionado(''); setLibroSeleccionado(''); setInstitucionSeleccionada('')
    setPersona({ nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '', fecha_bautismo: '', nombre_padre_nombre_madre: '', nombre_padrino_nombre_madrina: '' })
    setFechaSacramento(''); setError(null); setSuccess(null); setValidacionDuplicado(null)
  }

  return (
    <div className="bg-white dark:bg-gray-900/50 rounded-lg shadow">
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Nuevo Registro de Sacramento</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">Siga el orden: Tipo de Sacramento → Libro → Parroquia → Datos de la Persona</p>
      </div>
      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {error && <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg">{error}</div>}
        {success && <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg">{success}</div>}

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">1. Tipo de Sacramento *</label>
          <select value={tipoSeleccionado} onChange={(e) => setTipoSeleccionado(e.target.value)} required className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary">
            <option value="">Seleccione un tipo de sacramento</option>
            {tiposSacramentos.map(tipo => (<option key={tipo.id_tipo || tipo.id} value={tipo.id_tipo || tipo.id}>{tipo.nombre || tipo.tipo_nombre}</option>))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">2. Libro *</label>
          <select value={libroSeleccionado} onChange={(e) => setLibroSeleccionado(e.target.value)} required disabled={!tipoSeleccionado} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed">
            <option value="">Seleccione un libro</option>
            {libros.map(libro => (<option key={libro.id_libro || libro.id} value={libro.id_libro || libro.id}>Libro {libro.id_libro || libro.id} ({libro.fecha_inicio || '—'} - {libro.fecha_fin || '—'})</option>))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">3. Parroquia/Institución *</label>
          <select value={institucionSeleccionada} onChange={(e) => setInstitucionSeleccionada(e.target.value)} required disabled={!libroSeleccionado} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed">
            <option value="">Seleccione una parroquia</option>
            {instituciones.map(inst => (<option key={inst.id_institucion || inst.id} value={inst.id_institucion || inst.id}>{inst.nombre}</option>))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">4. Fecha del Sacramento *</label>
          <input type="date" value={fechaSacramento} onChange={(e) => setFechaSacramento(e.target.value)} required disabled={!institucionSeleccionada} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
        </div>

        <div className="border-t pt-6 dark:border-gray-800">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">5. Datos de la Persona</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Nombres *</label>
              <input type="text" name="nombres" value={persona.nombres} onChange={handlePersonaChange} required disabled={!fechaSacramento} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Apellido Paterno *</label>
              <input type="text" name="apellido_paterno" value={persona.apellido_paterno} onChange={handlePersonaChange} required disabled={!fechaSacramento} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Apellido Materno *</label>
              <input type="text" name="apellido_materno" value={persona.apellido_materno} onChange={handlePersonaChange} required disabled={!fechaSacramento} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Fecha de Nacimiento *</label>
              <input type="date" name="fecha_nacimiento" value={persona.fecha_nacimiento} onChange={handlePersonaChange} required disabled={!fechaSacramento} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Fecha de Bautismo *</label>
              <input type="date" name="fecha_bautismo" value={persona.fecha_bautismo} onChange={handlePersonaChange} required disabled={!fechaSacramento} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Fecha del bautismo previo (requerido para confirmación)</p>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Nombres del Padre y Madre *</label>
              <input type="text" name="nombre_padre_nombre_madre" value={persona.nombre_padre_nombre_madre} onChange={handlePersonaChange} required disabled={!fechaSacramento} placeholder="Ej: Juan Pérez García / María López Rodríguez" className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Nombres del Padrino y Madrina *</label>
              <input type="text" name="nombre_padrino_nombre_madrina" value={persona.nombre_padrino_nombre_madrina} onChange={handlePersonaChange} required disabled={!fechaSacramento} placeholder="Ej: Carlos Gómez / Ana Fernández" className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
          </div>
        </div>

        {validacionDuplicado && (<div className={`px-4 py-3 rounded-lg ${validacionDuplicado.error ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200' : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'}`}>{validacionDuplicado.mensaje}</div>)}

        <div className="flex gap-4 pt-4">
          <button type="submit" disabled={loading || validacionDuplicado?.error} className="flex-1 bg-primary hover:bg-primary/90 text-white font-medium py-3 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed">{loading ? 'Guardando...' : 'Guardar Sacramento'}</button>
          <button type="button" onClick={resetForm} disabled={loading} className="px-6 py-3 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed">Limpiar</button>
        </div>
      </form>
    </div>
  )
}

// Management list component (adapted from second variant)
function ManagementList({ refreshSignal }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [viewItem, setViewItem] = useState(null)
  const [editItem, setEditItem] = useState(null)
  const [editForm, setEditForm] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const [filterYear, setFilterYear] = useState('')
  const [filterParish, setFilterParish] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => { load() }, [refreshSignal])

  const years = Array.from(new Set(items.map((it) => getYear(it)).filter((y) => y && y !== '—'))).sort()
  const parishes = Array.from(new Set(items.map((it) => (it.institucion_nombre || it.institucion || '').trim()).filter((p) => p))).sort()

  const filteredItems = items.filter((it) => {
    if (filterYear && getYear(it) !== filterYear) return false
    if (filterParish && ((it.institucion_nombre || it.institucion || '').trim() !== filterParish)) return false
    if (searchTerm && !getPersonaLabel(it).toLowerCase().includes(searchTerm.toLowerCase())) return false
    return true
  })

  async function load() {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/sacramentos?limit=100`)
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setItems(Array.isArray(data) ? data : data.items || [])
    } catch (err) {
      console.error(err)
      alert('Error cargando registros: ' + (err.message || err))
    } finally { setLoading(false) }
  }

  function estadoBadge(s) {
    const e = (s && (s.estado || s.estado_ui || s.estado_local)) || ''
    const obs = (s && (s.observaciones || s.observacion || s.notes || '')) || ''
    if (String(e).toLowerCase() === 'completado' || /complet/i.test(obs)) {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Completado</span>
    }
    if (String(e).toLowerCase() === 'pendiente' || !e) {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">Pendiente</span>
    }
    return <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">{String(e)}</span>
  }

  async function handleAcceptWithoutChanges(item) {
    try {
      const id = item.id_sacramento || item.id || item.id_sacrament
      const existingObs = item.observaciones || item.observacion || ''
      const newObs = existingObs ? `${existingObs} | estado:completado` : 'estado:completado'
      const res = await fetch(`${API_URL}/sacramentos/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ observaciones: newObs }) })
      if (!res.ok) throw new Error(await res.text())
      alert('Registro aceptado')
      load()
      setEditItem(null)
    } catch (err) { console.error(err); alert('Error al aceptar: ' + (err.message || err)) }
  }

  function openEdit(item) {
    setEditItem(item)
    setEditForm({
      fecha_sacramento: item.fecha_sacramento || '',
      libro_id: item.libro_id || '',
      observaciones: item.observaciones || item.observacion || '',
      ministro: item.ministro || item.sacrament_minister || item.ministro_confirmacion || item.ministro_bautizo || '',
      folio: item.foja || item.folio || '',
      numero_acta: item.numero_acta || item.numero || '' ,
      pagina: item.pagina || ''
    })
  }

  async function handleSaveAndAccept() {
    if (!editItem || !editForm) return
    const allowed = new Set(['persona_id', 'tipo_id', 'usuario_id', 'institucion_id', 'libro_id', 'fecha_sacramento', 'ministro', 'padrinos', 'observaciones', 'folio', 'numero_acta', 'pagina'])
    const payload = {}
    if (editForm.fecha_sacramento) payload.fecha_sacramento = editForm.fecha_sacramento
    if (editForm.libro_id) payload.libro_id = Number(editForm.libro_id)
    if (typeof editForm.observaciones === 'string') payload.observaciones = editForm.observaciones
    if (typeof editForm.ministro === 'string' && editForm.ministro.trim() !== '') payload.ministro = editForm.ministro
    if (editForm.folio) payload.folio = editForm.folio
    if (editForm.numero_acta) payload.numero_acta = editForm.numero_acta
    if (editForm.pagina) payload.pagina = editForm.pagina
    const existingObs = editItem.observaciones || editItem.observacion || ''
    payload.observaciones = existingObs ? `${existingObs} | estado:completado` : (payload.observaciones ? `${payload.observaciones} | estado:completado` : 'estado:completado')
    try {
      const id = editItem.id_sacramento || editItem.id || editItem.id_sacrament
      const res = await fetch(`${API_URL}/sacramentos/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error(await res.text())
      alert('Registro guardado y aceptado')
      setEditItem(null); setEditForm(null); load()
    } catch (err) { console.error(err); alert('Error al guardar: ' + (err.message || err)) }
  }

  async function handleDeleteConfirmed() {
    if (!confirmDelete) return
    try {
      const id = confirmDelete.id_sacramento || confirmDelete.id || confirmDelete.id_sacrament
      let res = null
      try {
        res = await fetch(`${API_URL}/sacramentos/${id}`, { method: 'DELETE' })
        if (!res.ok) { const body = await res.text().catch(() => res.statusText || ''); throw new Error(`HTTP ${res.status} ${body}`) }
      } catch (errPrimary) {
        console.warn('Primary delete failed, trying relative fallback:', errPrimary)
        try {
          res = await fetch(`/api/v1/sacramentos/${id}`, { method: 'DELETE' })
          if (!res.ok) { const body = await res.text().catch(() => res.statusText || ''); throw new Error(`HTTP ${res.status} ${body}`) }
        } catch (errFallback) {
          const primaryMsg = errPrimary && errPrimary.message ? String(errPrimary.message) : String(errPrimary)
          const fallbackMsg = errFallback && errFallback.message ? String(errFallback.message) : String(errFallback)
          throw new Error(`Primary: ${primaryMsg}; Fallback: ${fallbackMsg}`)
        }
      }
      alert('Registro eliminado')
      setConfirmDelete(null)
      load()
    } catch (err) {
      console.error('Error deleting sacramento:', err)
      const msg = String(err && err.message ? err.message : err)
      if (msg.includes('Failed to fetch') || msg.toLowerCase().includes('networkerror') || msg.toLowerCase().includes('primary:')) {
        alert('Error al eliminar: no se pudo conectar con el servidor. Comprueba que el servicio `documents-service` esté en ejecución (por defecto en http://localhost:8002) y que no haya bloqueos de red/CORS.\nDetalles: ' + msg)
      } else { alert('Error al eliminar: ' + msg) }
    }
  }

  return (
    <div className="bg-white dark:bg-gray-900/50 rounded-lg shadow">
      <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-800">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full">
            <div className="relative w-full sm:w-72">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">search</span>
              <input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary" placeholder="Buscar por persona..." type="text" />
            </div>
            <select value={filterYear} onChange={(e) => setFilterYear(e.target.value)} className="form-select border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg">
              <option value="">Año</option>
              {years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
            <select value={filterParish} onChange={(e) => setFilterParish(e.target.value)} className="form-select border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg">
              <option value="">Parroquia</option>
              {parishes.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div>
            <button onClick={() => { setFilterYear(''); setFilterParish(''); setSearchTerm(''); load(); }} className="btn">{loading ? 'Cargando...' : 'Refrescar'}</button>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-800">
            <tr>
              <th className="px-6 py-3">Persona</th>
              <th className="px-6 py-3">Sacramento</th>
              <th className="px-6 py-3">Año</th>
              <th className="px-6 py-3">Estado</th>
              <th className="px-6 py-3 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredItems.map((it) => (
              <tr key={it.id_sacramento || it.id || it.id_sacrament} className="bg-white dark:bg-gray-900/50 border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <th className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">{getPersonaLabel(it)}</th>
                <td className="px-6 py-4">{getSacramentoType(it)}</td>
                <td className="px-6 py-4">{getYear(it)}</td>
                <td className="px-6 py-4">{estadoBadge(it)}</td>
                <td className="px-6 py-4 text-center space-x-2">
                  <button title="Ver" onClick={() => setViewItem(it)} className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">visibility</span></button>
                  <button title="Editar" onClick={() => openEdit(it)} className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">edit</span></button>
                  <button title="Aceptar sin cambios" onClick={() => { if (confirm('Aceptar sin cambios y marcar como completado?')) handleAcceptWithoutChanges(it) }} className="p-1 rounded-full text-gray-500 hover:bg-primary/10 hover:text-primary dark:text-gray-400 dark:hover:bg-primary/20"><span className="material-symbols-outlined text-base">check_circle</span></button>
                  <button title="Eliminar" onClick={() => setConfirmDelete(it)} className="p-1 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-900/20"><span className="material-symbols-outlined text-base">delete</span></button>
                </td>
              </tr>
            ))}
            {filteredItems.length === 0 && !loading && (<tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No hay registros</td></tr>)}
          </tbody>
        </table>
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-gray-800 flex items-center justify-between"><span className="text-sm text-gray-700 dark:text-gray-400">Mostrando {filteredItems.length} registros</span></div>

      {viewItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-900 w-[90%] max-w-3xl rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-medium">Ver Registro</h3>
              <button onClick={() => setViewItem(null)} className="text-gray-500">Cerrar</button>
            </div>
            <div className="max-h-[60vh] overflow-auto text-sm bg-gray-50 dark:bg-gray-800 p-4 rounded">
              <div className="mb-3"><strong>Persona:</strong> {getPersonaLabel(viewItem)}</div>
              <div className="mb-3"><strong>Sacramento:</strong> {getSacramentoType(viewItem)}</div>
              <div className="mb-3"><strong>Fecha del sacramento:</strong> {viewItem.fecha_sacramento || '—'}</div>
              <div className="mb-3"><strong>Ministro:</strong> {viewItem.ministro || viewItem.sacrament_minister || viewItem.ministro_confirmacion || viewItem.ministro_bautizo || '—'}</div>
              <div className="mb-3"><strong>Parroquia / Institución:</strong> {viewItem.institucion_nombre || viewItem.institucion || '—'}</div>
              <div className="mb-3"><strong>Libro:</strong> {viewItem.libro_nombre || viewItem.libro_id || '—'}</div>
              <div className="mb-3"><strong>Foja / Folio:</strong> {viewItem.foja || viewItem.folio || '—'}</div>
              <div className="mb-3"><strong>Número acta:</strong> {viewItem.numero_acta || viewItem.numero || '—'}</div>
              <div className="mb-3"><strong>Página:</strong> {viewItem.pagina || '—'}</div>
              <div className="mb-3"><strong>Observaciones:</strong> {viewItem.observaciones || viewItem.observacion || '—'}</div>
              {viewItem.nombre_esposo && <div className="mb-2"><strong>Esposo:</strong> {viewItem.nombre_esposo}</div>}
              {viewItem.nombre_esposa && <div className="mb-2"><strong>Esposa:</strong> {viewItem.nombre_esposa}</div>}
              {viewItem.persona_padre && <div className="mb-2"><strong>Padre:</strong> {viewItem.persona_padre}</div>}
              {viewItem.persona_madre && <div className="mb-2"><strong>Madre:</strong> {viewItem.persona_madre}</div>}
            </div>
          </div>
        </div>
      )}

      {editItem && editForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-900 w-[95%] max-w-4xl rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-medium">Editar Registro</h3>
              <button onClick={() => { setEditItem(null); setEditForm(null) }} className="text-gray-500">Cerrar</button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <div>
                <label className="block text-sm mb-1">Persona</label>
                <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">{getPersonaLabel(editItem)}</div>
              </div>
              <div>
                <label className="block text-sm mb-1">Sacramento</label>
                <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">{getSacramentoType(editItem)}</div>
              </div>
              <div>
                <label className="block text-sm mb-1">Fecha sacramento</label>
                <input type="date" value={editForm.fecha_sacramento || ''} onChange={(e) => setEditForm({...editForm, fecha_sacramento: e.target.value})} className="form-input w-full" />
              </div>
              <div>
                <label className="block text-sm mb-1">Libro (ID)</label>
                <input type="text" value={editForm.libro_id || ''} onChange={(e) => setEditForm({...editForm, libro_id: e.target.value})} className="form-input w-full" />
              </div>
              <div>
                <label className="block text-sm mb-1">Ministro</label>
                <input type="text" value={editForm.ministro || ''} onChange={(e) => setEditForm({...editForm, ministro: e.target.value})} className="form-input w-full" />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm mb-1">Observaciones</label>
                <textarea rows={4} value={editForm.observaciones || ''} onChange={(e) => setEditForm({...editForm, observaciones: e.target.value})} className="w-full p-2 rounded border bg-gray-50 dark:bg-gray-800" />
              </div>
              <div>
                <label className="block text-sm mb-1">Foja / Folio</label>
                <input type="text" value={editForm.folio || ''} onChange={(e) => setEditForm({...editForm, folio: e.target.value})} className="form-input w-full" />
              </div>
              <div>
                <label className="block text-sm mb-1">Número acta</label>
                <input type="text" value={editForm.numero_acta || ''} onChange={(e) => setEditForm({...editForm, numero_acta: e.target.value})} className="form-input w-full" />
              </div>
              <div>
                <label className="block text-sm mb-1">Página</label>
                <input type="text" value={editForm.pagina || ''} onChange={(e) => setEditForm({...editForm, pagina: e.target.value})} className="form-input w-full" />
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => { setEditItem(null); setEditForm(null) }} className="px-3 py-1 rounded bg-gray-200">Cancelar</button>
              <button onClick={() => handleAcceptWithoutChanges(editItem)} className="px-3 py-1 rounded bg-yellow-500 text-white">Aceptar sin cambios</button>
              <button onClick={handleSaveAndAccept} className="px-3 py-1 rounded bg-green-600 text-white">Guardar y Aceptar</button>
            </div>
          </div>
        </div>
      )}

      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-900 w-full max-w-lg rounded-lg p-4">
            <h3 className="text-lg font-medium mb-2">Confirmar eliminación</h3>
            <p className="mb-4">¿Eliminar el registro de <strong>{getPersonaLabel(confirmDelete)}</strong>? Esta acción no se puede deshacer.</p>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setConfirmDelete(null)} className="px-3 py-1 rounded bg-gray-200">Cancelar</button>
              <button onClick={handleDeleteConfirmed} className="px-3 py-1 rounded bg-red-600 text-white">Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Registros() {
  // Show both flows on the same page (form above, management list below).
  // `refresh` increments when a new sacramento is saved so the list reloads.
  const [refresh, setRefresh] = useState(0)

  return (
    <Layout title="Registros">
      <CreateForm onSaved={() => setRefresh((r) => r + 1)} />
      <div className="mt-6">
        <ManagementList refreshSignal={refresh} />
      </div>
    </Layout>
  )
}



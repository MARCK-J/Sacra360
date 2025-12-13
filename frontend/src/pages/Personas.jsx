import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import DuplicatesMergeModal from '../components/DuplicatesMergeModal'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8002'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002'

export default function Personas() {
  const [mergeOpen, setMergeOpen] = useState(false)
  const [formData, setFormData] = useState({
    nombres: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    lugar_nacimiento: '',
    nombre_padre: '',
    nombre_madre: ''
  })

  const [duplicateAlert, setDuplicateAlert] = useState(null)
  const [isCheckingDuplicate, setIsCheckingDuplicate] = useState(false)

  const [persons, setPersons] = useState([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  const checkForDuplicates = async (nombres, apellido_paterno, apellido_materno, fecha_nacimiento) => {
    if (!nombres || !apellido_paterno || !apellido_materno || !fecha_nacimiento) {
      setDuplicateAlert(null)
      return
    }
    setIsCheckingDuplicate(true)
    try {
      const params = new URLSearchParams({ nombres, apellido_paterno, apellido_materno, fecha_nacimiento })
      const response = await fetch(`${API_URL}/api/v1/personas/check-duplicate?${params}`)
      if (response.ok) {
        const data = await response.json()
        if (data.exists) setDuplicateAlert({ type: 'warning', persona: data.persona })
        else setDuplicateAlert(null)
      }
    } catch (err) {
      console.error('Error verificando duplicados:', err)
    } finally {
      setIsCheckingDuplicate(false)
    }
  }

  useEffect(() => {
    const t = setTimeout(() => {
      checkForDuplicates(formData.nombres, formData.apellido_paterno, formData.apellido_materno, formData.fecha_nacimiento)
    }, 800)
    return () => clearTimeout(t)
  }, [formData.nombres, formData.apellido_paterno, formData.apellido_materno, formData.fecha_nacimiento])

  const handleInputChange = (e) => {
    const { id, value } = e.target
    setFormData(prev => ({ ...prev, [id]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (duplicateAlert) {
      const confirmar = window.confirm(`Ya existe una persona similar:\n\n${duplicateAlert.persona.nombres} ${duplicateAlert.persona.apellido_paterno} ${duplicateAlert.persona.apellido_materno}\nFecha de nacimiento: ${duplicateAlert.persona.fecha_nacimiento}\n\n¿Desea registrar de todas formas?`)
      if (!confirmar) return
    }
    try {
      const res = await fetch(`${API_URL}/api/v1/personas/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) })
      if (res.ok) {
        alert('Persona registrada exitosamente')
        setFormData({ nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '', lugar_nacimiento: '', nombre_padre: '', nombre_madre: '' })
        setDuplicateAlert(null)
        loadPersons()
      } else if (res.status === 409) {
        const error = await res.json().catch(() => ({}))
        alert(`Error: ${error.detail?.message || error.detail || 'Persona duplicada'}`)
      } else alert('Error al registrar persona')
    } catch (err) {
      console.error('Error:', err)
      alert('Error de conexión al servidor')
    }
  }

  async function loadPersons() {
    setLoading(true)
    try {
      let r = await fetch(`${API_BASE}/api/v1/personas?limit=100`)
      if (!r.ok && r.status === 422) r = await fetch(`${API_BASE}/api/v1/personas`)
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const data = await r.json()
      setPersons(Array.isArray(data) ? data : (data.personas || data || []))
      setMsg(null)
    } catch (e) {
      console.error('Error loading persons', e)
      setPersons([])
      setMsg({ type: 'error', text: 'No se pudieron cargar las personas: ' + (e.message || e) })
    } finally { setLoading(false) }
  }

  useEffect(() => { loadPersons() }, [])

  return (
    <Layout title="Gestión de Personas">
      <div className="space-y-8">
        <div className="bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200 dark:border-gray-800"><h3 className="text-lg font-semibold text-gray-900 dark:text-white">Datos Personales</h3></div>
          <form className="p-6" onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="nombres" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombres *</label>
                <input id="nombres" placeholder="Ingrese los nombres" type="text" value={formData.nombres} onChange={handleInputChange} required className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" />
              </div>
              <div>
                <label htmlFor="apellido_paterno" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Apellido Paterno *</label>
                <input id="apellido_paterno" placeholder="Ingrese el apellido paterno" type="text" value={formData.apellido_paterno} onChange={handleInputChange} required className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" />
              </div>
              <div>
                <label htmlFor="apellido_materno" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Apellido Materno *</label>
                <input id="apellido_materno" placeholder="Ingrese el apellido materno" type="text" value={formData.apellido_materno} onChange={handleInputChange} required className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" />
              </div>
              <div>
                <label htmlFor="fecha_nacimiento" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha de Nacimiento *</label>
                <input id="fecha_nacimiento" type="date" value={formData.fecha_nacimiento} onChange={handleInputChange} required className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" />
              </div>
              <div>
                <label htmlFor="lugar_nacimiento" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Lugar de Nacimiento *</label>
                <input id="lugar_nacimiento" placeholder="Ingrese el lugar" type="text" value={formData.lugar_nacimiento} onChange={handleInputChange} required className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" />
              </div>
              <div>
                <label htmlFor="nombre_padre" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Padre *</label>
                <input id="nombre_padre" placeholder="Ingrese el nombre del padre" type="text" value={formData.nombre_padre} onChange={handleInputChange} required className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" />
              </div>
              <div>
                <label htmlFor="nombre_madre" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Madre *</label>
                <input id="nombre_madre" placeholder="Ingrese el nombre de la madre" type="text" value={formData.nombre_madre} onChange={handleInputChange} required className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" />
              </div>
            </div>

            {isCheckingDuplicate && (
              <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400 dark:border-blue-500 p-4 rounded-r-lg"><div className="flex items-center"><span className="material-symbols-outlined text-blue-400 dark:text-blue-500 animate-spin">sync</span><span className="ml-2 text-sm text-blue-700 dark:text-blue-300">Verificando duplicados...</span></div></div>
            )}

            <div className="mt-6 flex justify-end gap-4">
              <button type="button" className="px-6 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600" onClick={() => { setFormData({ nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '', lugar_nacimiento: '', nombre_padre: '', nombre_madre: '' }); setDuplicateAlert(null) }}>Limpiar</button>
              <button type="submit" className="px-6 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90" disabled={isCheckingDuplicate}>Guardar Persona</button>
            </div>
          </form>
        </div>

        <div className="mt-8 bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200 dark:border-gray-800"><h3 className="text-lg font-semibold text-gray-900 dark:text-white">Personas guardadas</h3></div>
          <div className="overflow-x-auto p-4">{loading ? (<div className="text-sm text-gray-500">Cargando...</div>) : (
            <table className="w-full text-sm text-left text-gray-500"><thead className="text-xs text-gray-700 uppercase bg-gray-50"><tr><th className="px-4 py-2">Nombre completo</th><th className="px-4 py-2">Fecha nacimiento</th><th className="px-4 py-2">Lugar</th><th className="px-4 py-2">Padre / Madre</th></tr></thead><tbody>{persons.length === 0 ? (<tr><td colSpan={4} className="px-4 py-6">No hay personas registradas.</td></tr>) : (persons.map((p) => (<tr key={p.id_persona || p.id} className="border-b"><td className="px-4 py-3 font-medium text-gray-900">{[p.nombres, p.apellido_paterno, p.apellido_materno].filter(Boolean).join(' ')}</td><td className="px-4 py-3">{p.fecha_nacimiento ? String(p.fecha_nacimiento).substring(0,10) : '-'}</td><td className="px-4 py-3">{p.lugar_nacimiento || '-'}</td><td className="px-4 py-3">{(p.nombre_padre || '-') + ' / ' + (p.nombre_madre || '-')}</td></tr>)))}</tbody></table>
          )}</div>
        </div>

        {duplicateAlert && (
          <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 dark:border-yellow-500 p-4 rounded-r-lg">
            <div className="flex">
              <div className="flex-shrink-0"><span className="material-symbols-outlined text-yellow-400 dark:text-yellow-500">warning</span></div>
              <div className="ml-3"><h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Posible Duplicado Encontrado</h3>
                <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300"><div className="flex items-center gap-4 mt-4"><div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center"><span className="material-symbols-outlined text-primary">person</span></div><div><p className="font-semibold text-gray-900 dark:text-white">{duplicateAlert.persona.nombres} {duplicateAlert.persona.apellido_paterno} {duplicateAlert.persona.apellido_materno}</p><p className="text-gray-600 dark:text-gray-400">Fecha de Nacimiento: {duplicateAlert.persona.fecha_nacimiento}</p><p className="text-gray-600 dark:text-gray-400">ID: {duplicateAlert.persona.id_persona}</p></div><button className="ml-auto px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90" onClick={() => setMergeOpen(true)}>Ver Detalles</button></div></div></div>
            </div>
          </div>
        )}

        <DuplicatesMergeModal open={mergeOpen} onClose={() => setMergeOpen(false)} />
      </div>
    </Layout>
  )
}
            {isCheckingDuplicate && (
              <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400 dark:border-blue-500 p-4 rounded-r-lg">
                <div className="flex items-center">
                  <span className="material-symbols-outlined text-blue-400 dark:text-blue-500 animate-spin">sync</span>
                  <span className="ml-2 text-sm text-blue-700 dark:text-blue-300">Verificando duplicados...</span>
                </div>
              </div>
            )}

            <div className="mt-6 flex justify-end gap-4">
              <button type="button" className="px-6 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600" onClick={() => { setFormData({ nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '', lugar_nacimiento: '', nombre_padre: '', nombre_madre: '' }); setDuplicateAlert(null) }}>Limpiar</button>
              <button type="submit" className="px-6 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90" disabled={isCheckingDuplicate}>Guardar Persona</button>
            </div>
          </form>
        </div>

        <div className="mt-8 bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200 dark:border-gray-800">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Personas guardadas</h3>
          </div>
          <div className="overflow-x-auto p-4">
            {loading ? (
              <div className="text-sm text-gray-500">Cargando...</div>
            ) : (
              <table className="w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                  <tr>
                    <th className="px-4 py-2">Nombre completo</th>
                    <th className="px-4 py-2">Fecha nacimiento</th>
                    <th className="px-4 py-2">Lugar</th>
                    <th className="px-4 py-2">Padre / Madre</th>
                  </tr>
                </thead>
                <tbody>
                  {persons.length === 0 ? (
                    <tr><td colSpan={4} className="px-4 py-6">No hay personas registradas.</td></tr>
                  ) : (
                    persons.map((p) => (
                      <tr key={p.id_persona || p.id} className="border-b">
                        <td className="px-4 py-3 font-medium text-gray-900">{[p.nombres, p.apellido_paterno, p.apellido_materno].filter(Boolean).join(' ')}</td>
                        <td className="px-4 py-3">{p.fecha_nacimiento ? String(p.fecha_nacimiento).substring(0,10) : '-'}</td>
                        <td className="px-4 py-3">{p.lugar_nacimiento || '-'}</td>
                        <td className="px-4 py-3">{(p.nombre_padre || '-') + ' / ' + (p.nombre_madre || '-')}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {duplicateAlert && (
          <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 dark:border-yellow-500 p-4 rounded-r-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="material-symbols-outlined text-yellow-400 dark:text-yellow-500">warning</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Posible Duplicado Encontrado</h3>
                <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                  <div className="flex items-center gap-4 mt-4">
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="material-symbols-outlined text-primary">person</span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">{duplicateAlert.persona.nombres} {duplicateAlert.persona.apellido_paterno} {duplicateAlert.persona.apellido_materno}</p>
                      <p className="text-gray-600 dark:text-gray-400">Fecha de Nacimiento: {duplicateAlert.persona.fecha_nacimiento}</p>
                      <p className="text-gray-600 dark:text-gray-400">ID: {duplicateAlert.persona.id_persona}</p>
                    </div>
                    <button className="ml-auto px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90" onClick={() => setMergeOpen(true)}>Ver Detalles</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <DuplicatesMergeModal open={mergeOpen} onClose={() => setMergeOpen(false)} />
      </div>
    </Layout>
  )
}
            {isCheckingDuplicate && (
              <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400 dark:border-blue-500 p-4 rounded-r-lg">
                <div className="flex items-center">
                  <span className="material-symbols-outlined text-blue-400 dark:text-blue-500 animate-spin">sync</span>
                  <span className="ml-2 text-sm text-blue-700 dark:text-blue-300">Verificando duplicados...</span>
                </div>
              </div>
            )}

            <div className="mt-6 flex justify-end gap-4">
              <button type="button" className="px-6 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600" onClick={() => { setFormData({ nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '', lugar_nacimiento: '', nombre_padre: '', nombre_madre: '' }); setDuplicateAlert(null) }}>Limpiar</button>
              <button type="submit" className="px-6 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90" disabled={isCheckingDuplicate}>Guardar Persona</button>
            </div>
          </form>
        </div>

        <div className="mt-8 bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200 dark:border-gray-800">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Personas guardadas</h3>
          </div>
          <div className="overflow-x-auto p-4">
            {loading ? (
              <div className="text-sm text-gray-500">Cargando...</div>
            ) : (
              <table className="w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                  <tr>
                    <th className="px-4 py-2">Nombre completo</th>
                    <th className="px-4 py-2">Fecha nacimiento</th>
                    <th className="px-4 py-2">Lugar</th>
                    <th className="px-4 py-2">Padre / Madre</th>
                  </tr>
                </thead>
                <tbody>
                  {persons.length === 0 ? (
                    <tr><td colSpan={4} className="px-4 py-6">No hay personas registradas.</td></tr>
                  ) : (
                    persons.map((p) => (
                      <tr key={p.id_persona || p.id} className="border-b">
                        <td className="px-4 py-3 font-medium text-gray-900">{[p.nombres, p.apellido_paterno, p.apellido_materno].filter(Boolean).join(' ')}</td>
                        <td className="px-4 py-3">{p.fecha_nacimiento ? String(p.fecha_nacimiento).substring(0,10) : '-'}</td>
                        <td className="px-4 py-3">{p.lugar_nacimiento || '-'}</td>
                        <td className="px-4 py-3">{(p.nombre_padre || '-') + ' / ' + (p.nombre_madre || '-')}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {duplicateAlert && (
          <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 dark:border-yellow-500 p-4 rounded-r-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="material-symbols-outlined text-yellow-400 dark:text-yellow-500">warning</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Posible Duplicado Encontrado</h3>
                <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                  <div className="flex items-center gap-4 mt-4">
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="material-symbols-outlined text-primary">person</span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">{duplicateAlert.persona.nombres} {duplicateAlert.persona.apellido_paterno} {duplicateAlert.persona.apellido_materno}</p>
                      <p className="text-gray-600 dark:text-gray-400">Fecha de Nacimiento: {duplicateAlert.persona.fecha_nacimiento}</p>
                      <p className="text-gray-600 dark:text-gray-400">ID: {duplicateAlert.persona.id_persona}</p>
                    </div>
                    <button className="ml-auto px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90" onClick={() => setMergeOpen(true)}>Ver Detalles</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <DuplicatesMergeModal open={mergeOpen} onClose={() => setMergeOpen(false)} />
      </div>
    </Layout>
  )
}
import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8002'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002'

export default function Personas() {
  const [mergeOpen, setMergeOpen] = useState(false)
  const [formData, setFormData] = useState({
    nombres: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    lugar_nacimiento: '',
    nombre_padre: '',
    nombre_madre: ''
  })
  
  const [duplicateAlert, setDuplicateAlert] = useState(null)
  const [isCheckingDuplicate, setIsCheckingDuplicate] = useState(false)

  // Función para verificar duplicados
  const checkForDuplicates = async (nombres, apellido_paterno, apellido_materno, fecha_nacimiento) => {
    // Solo verificar si tenemos todos los datos necesarios
    if (!nombres || !apellido_paterno || !apellido_materno || !fecha_nacimiento) {
      setDuplicateAlert(null)
      return
    }

    setIsCheckingDuplicate(true)

    try {
      const params = new URLSearchParams({
        nombres,
        apellido_paterno,
        apellido_materno,
        fecha_nacimiento
      })

      const response = await fetch(`${API_URL}/api/v1/personas/check-duplicate?${params}`, {
        method: 'GET'
      })

      if (response.ok) {
        const data = await response.json()
        
        if (data.exists) {
          setDuplicateAlert({
            type: 'warning',
            persona: data.persona
          })
        } else {
          setDuplicateAlert(null)
        }
      }
    } catch (error) {
      console.error('Error verificando duplicados:', error)
    } finally {
      setIsCheckingDuplicate(false)
    }
  }

  // Validar con debounce cuando cambian los campos críticos
  useEffect(() => {
    // Crear timeout para validar después de 800ms sin cambios
    const timeout = setTimeout(() => {
      checkForDuplicates(
        formData.nombres, 
        formData.apellido_paterno, 
        formData.apellido_materno, 
        formData.fecha_nacimiento
      )
    }, 800)

    // Cleanup
    return () => {
      clearTimeout(timeout)
    }
  }, [formData.nombres, formData.apellido_paterno, formData.apellido_materno, formData.fecha_nacimiento])

  // Manejar cambios en el formulario
  const handleInputChange = (e) => {
    const { id, value } = e.target
    setFormData(prev => ({
      ...prev,
      [id]: value
    }))
  }

  // Manejar envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault()

    // Si hay duplicado, mostrar confirmación
    if (duplicateAlert) {
      const confirmar = window.confirm(
        `Ya existe una persona similar:\n\n` +
        `${duplicateAlert.persona.nombres} ${duplicateAlert.persona.apellido_paterno} ${duplicateAlert.persona.apellido_materno}\n` +
        `Fecha de nacimiento: ${duplicateAlert.persona.fecha_nacimiento}\n\n` +
        `¿Desea registrar de todas formas?`
      )
      
      if (!confirmar) return
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/personas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        alert('Persona registrada exitosamente')
        // Limpiar formulario
        setFormData({
          nombres: '',
          apellido_paterno: '',
          apellido_materno: '',
          fecha_nacimiento: '',
          lugar_nacimiento: '',
          nombre_padre: '',
          nombre_madre: ''
        })
        setDuplicateAlert(null)
      } else if (response.status === 409) {
        const error = await response.json()
        alert(`Error: ${error.detail?.message || error.detail || 'Persona duplicada'}`)
      } else {
        alert('Error al registrar persona')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error de conexión al servidor')
  const [nombres, setNombres] = useState('')
  const [apellidoPaterno, setApellidoPaterno] = useState('')
  const [apellidoMaterno, setApellidoMaterno] = useState('')
  const [fechaNacimiento, setFechaNacimiento] = useState('')
  const [lugarNacimiento, setLugarNacimiento] = useState('')
  const [padre, setPadre] = useState('')
  const [madre, setMadre] = useState('')

  const [persons, setPersons] = useState([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  useEffect(() => {
    loadPersons()
  }, [])

  async function loadPersons() {
    setLoading(true)
    try {
      // Backend validates limit <= 100; request 100 to avoid 422
      let res = await fetch(`${API_BASE}/api/v1/personas?limit=100`)
      if (!res.ok) {
        // If validation error due to params (422), retry without limit
        if (res.status === 422) {
          try {
            res = await fetch(`${API_BASE}/api/v1/personas`)
          } catch (e2) {
            throw e2
          }
        } else {
          throw new Error(`HTTP ${res.status}`)
        }
      }
      const data = await res.json()
      const list = Array.isArray(data) ? data : (data.personas || data || [])
      setPersons(list)
      setMsg(null)
    } catch (e) {
      console.error('Error loading persons', e)
      setPersons([])
      setMsg({ type: 'error', text: 'No se pudieron cargar las personas: ' + (e.message || e) })
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    setMsg(null)
    if (!nombres.trim()) {
      setMsg({ type: 'error', text: 'El campo Nombres es obligatorio' })
      return
    }
    const payload = {
      nombres: nombres.trim(),
      apellido_paterno: apellidoPaterno.trim() || undefined,
      apellido_materno: apellidoMaterno.trim() || undefined,
      fecha_nacimiento: fechaNacimiento || undefined,
      lugar_nacimiento: lugarNacimiento.trim() || undefined,
      nombre_padre: padre.trim() || undefined,
      nombre_madre: madre.trim() || undefined
    }
    try {
      const res = await fetch(`${API_BASE}/api/v1/personas/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const txt = await res.text().catch(() => '')
        throw new Error(txt || `HTTP ${res.status}`)
      }
      const data = await res.json().catch(() => null)
      setMsg({ type: 'success', text: 'Persona creada correctamente' })
      // reset form
      setNombres('')
      setApellidoPaterno('')
      setApellidoMaterno('')
      setFechaNacimiento('')
      setLugarNacimiento('')
      setPadre('')
      setMadre('')
      // reload list
      loadPersons()
    } catch (err) {
      console.error('Create person error', err)
      setMsg({ type: 'error', text: String(err.message || err) })
    }
  }

  return (
    <Layout title="Gestión de Personas">
      <div className="space-y-8">
        <div className="bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200 dark:border-gray-800">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Datos Personales</h3>
              </div>
              <form className="p-6" onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="nombres">
                      Nombres *
                    </label>
                    <input 
                      className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" 
                      id="nombres" 
                      placeholder="Ingrese los nombres" 
                      type="text"
                      value={formData.nombres}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="apellido_paterno">
                      Apellido Paterno *
                    </label>
                    <input 
                      className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" 
                      id="apellido_paterno" 
                      placeholder="Ingrese el apellido paterno" 
                      type="text"
                      value={formData.apellido_paterno}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="apellido_materno">
                      Apellido Materno *
                    </label>
                    <input 
                      className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" 
                      id="apellido_materno" 
                      placeholder="Ingrese el apellido materno" 
                      type="text"
                      value={formData.apellido_materno}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="fecha_nacimiento">
                      Fecha de Nacimiento *
                    </label>
                    <input 
                      className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" 
                      id="fecha_nacimiento" 
                      type="date"
                      value={formData.fecha_nacimiento}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="lugar_nacimiento">
                      Lugar de Nacimiento *
                    </label>
                    <input 
                      className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" 
                      id="lugar_nacimiento" 
                      placeholder="Ingrese el lugar" 
                      type="text"
                      value={formData.lugar_nacimiento}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="nombre_padre">
                      Padre *
                    </label>
                    <input 
                      className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" 
                      id="nombre_padre" 
                      placeholder="Ingrese el nombre del padre" 
                      type="text"
                      value={formData.nombre_padre}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="nombre_madre">
                      Madre *
                    </label>
                    <input 
                      className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" 
                      id="nombre_madre" 
                      placeholder="Ingrese el nombre de la madre" 
                      type="text"
                      value={formData.nombre_madre}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                {/* Alerta de validación */}
                {isCheckingDuplicate && (
                  <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400 dark:border-blue-500 p-4 rounded-r-lg">
                    <div className="flex items-center">
                      <span className="material-symbols-outlined text-blue-400 dark:text-blue-500 animate-spin">sync</span>
                      <span className="ml-2 text-sm text-blue-700 dark:text-blue-300">Verificando duplicados...</span>
                    </div>
                  </div>
                )}

                {/* Botón de guardar */}
                <div className="mt-6 flex justify-end gap-4">
                  <button
                    type="button"
                    className="px-6 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600"
                    onClick={() => {
                      setFormData({
                        nombres: '',
                        apellido_paterno: '',
                        apellido_materno: '',
                        fecha_nacimiento: '',
                        lugar_nacimiento: '',
                        nombre_padre: '',
                        nombre_madre: ''
                      })
                      setDuplicateAlert(null)
                    }}
                  >
                    Limpiar
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                    disabled={isCheckingDuplicate}
                  >
                    Guardar Persona
                  </button>
                </div>
    <Layout title="Crear Persona">
      <div className="bg-white dark:bg-background-dark/50 rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Crear nueva persona</h3>
        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-1">Nombres</label>
            <input value={nombres} onChange={(e) => setNombres(e.target.value)} className="form-input w-full" />
          </div>
          <div>
            <label className="block text-sm mb-1">Apellido paterno</label>
            <input value={apellidoPaterno} onChange={(e) => setApellidoPaterno(e.target.value)} className="form-input w-full" />
          </div>
          <div>
            <label className="block text-sm mb-1">Apellido materno</label>
            <input value={apellidoMaterno} onChange={(e) => setApellidoMaterno(e.target.value)} className="form-input w-full" />
          </div>
          <div>
            <label className="block text-sm mb-1">Fecha de nacimiento</label>
            <input type="date" value={fechaNacimiento} onChange={(e) => setFechaNacimiento(e.target.value)} className="form-input w-full" />
          </div>
          <div>
            <label className="block text-sm mb-1">Lugar de nacimiento</label>
            <input value={lugarNacimiento} onChange={(e) => setLugarNacimiento(e.target.value)} className="form-input w-full" />
          </div>
          <div>
            <label className="block text-sm mb-1">Padre</label>
            <input value={padre} onChange={(e) => setPadre(e.target.value)} className="form-input w-full" />
          </div>
          <div>
            <label className="block text-sm mb-1">Madre</label>
            <input value={madre} onChange={(e) => setMadre(e.target.value)} className="form-input w-full" />
          </div>
          <div className="md:col-span-2 flex gap-2 justify-end mt-2">
            <button type="submit" className="px-4 py-2 rounded bg-primary text-white">Crear</button>
          </div>
          {msg && (
            <div className={`md:col-span-2 mt-2 text-sm ${msg.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>{msg.text}</div>
          )}
        </form>
      </div>

      <div className="mt-8 bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Personas guardadas</h3>
        </div>
        <div className="overflow-x-auto p-4">
          {loading ? (
            <div className="text-sm text-gray-500">Cargando...</div>
          ) : (
            <table className="w-full text-sm text-left text-gray-500">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-2">Nombre completo</th>
                  <th className="px-4 py-2">Fecha nacimiento</th>
                  <th className="px-4 py-2">Lugar</th>
                  <th className="px-4 py-2">Padre / Madre</th>
                </tr>
              </thead>
              <tbody>
                {persons.length === 0 ? (
                  <tr><td colSpan={4} className="px-4 py-6">No hay personas registradas.</td></tr>
                ) : (
                  persons.map((p) => (
                    <tr key={p.id_persona || p.id} className="border-b">
                      <td className="px-4 py-3 font-medium text-gray-900">{[p.nombres, p.apellido_paterno, p.apellido_materno].filter(Boolean).join(' ')}</td>
                      <td className="px-4 py-3">{p.fecha_nacimiento ? String(p.fecha_nacimiento).substring(0,10) : '-'}</td>
                      <td className="px-4 py-3">{p.lugar_nacimiento || '-'}</td>
                      <td className="px-4 py-3">{(p.nombre_padre || '-') + ' / ' + (p.nombre_madre || '-')}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Alerta de duplicados encontrados */}
      {duplicateAlert && (
        <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 dark:border-yellow-500 p-4 rounded-r-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="material-symbols-outlined text-yellow-400 dark:text-yellow-500">warning</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Posible Duplicado Encontrado</h3>
              <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                <div className="flex items-center gap-4 mt-4">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="material-symbols-outlined text-primary">person</span>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {duplicateAlert.persona.nombres} {duplicateAlert.persona.apellido_paterno} {duplicateAlert.persona.apellido_materno}
                    </p>
                    <p className="text-gray-600 dark:text-gray-400">
                      Fecha de Nacimiento: {duplicateAlert.persona.fecha_nacimiento}
                    </p>
                    <p className="text-gray-600 dark:text-gray-400">
                      ID: {duplicateAlert.persona.id_persona}
                    </p>
                  </div>
                  <button 
                    className="ml-auto px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary" 
                    onClick={() => setMergeOpen(true)}
                  >
                    Ver Detalles
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

        <DuplicatesMergeModal open={mergeOpen} onClose={() => setMergeOpen(false)} />
      </div>
    </Layout>
  )
}

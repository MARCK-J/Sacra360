import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8002'

export default function Personas() {
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
    </Layout>
  )
}

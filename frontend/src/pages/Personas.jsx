import { useState, useEffect, useRef } from 'react'
import Layout from '../components/Layout'
import DuplicatesMergeModal from '../components/DuplicatesMergeModal'

export default function Personas() {
  const [mergeOpen, setMergeOpen] = useState(false)
  // Controlled form state
  const [nombres, setNombres] = useState('')
  const [apellidos, setApellidos] = useState('')
  const [fechaNacimiento, setFechaNacimiento] = useState('')
  const [lugarNacimiento, setLugarNacimiento] = useState('')
  const [padre, setPadre] = useState('')
  const [madre, setMadre] = useState('')

  // Autocomplete / search
  const [searchTerm, setSearchTerm] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const debounceRef = useRef(null)

  // Selected person and their sacramentos
  const [selectedPerson, setSelectedPerson] = useState(null)
  const [sacramentos, setSacramentos] = useState([])

  useEffect(() => {
    // when selectedPerson changes, populate fields and load sacramentos
    if (selectedPerson) {
      setNombres(selectedPerson.nombres || '')
      setApellidos(((selectedPerson.apellido_paterno || '') + ' ' + (selectedPerson.apellido_materno || '')).trim())
      setFechaNacimiento(selectedPerson.fecha_nacimiento ? selectedPerson.fecha_nacimiento.substring(0,10) : '')
      setLugarNacimiento(selectedPerson.lugar_nacimiento || '')
      setPadre(selectedPerson.nombre_padre || selectedPerson.padre || '')
      setMadre(selectedPerson.nombre_madre || selectedPerson.madre || '')
      // fetch sacramentos for this person
      fetch(`/api/v1/personas/${selectedPerson.id_persona || selectedPerson.id}/sacramentos`).then(async res => {
        if (!res.ok) return setSacramentos([])
        const data = await res.json()
        setSacramentos(Array.isArray(data) ? data : (data.sacramentos || []))
      }).catch(() => setSacramentos([]))
    } else {
      setSacramentos([])
    }
  }, [selectedPerson])

  // debounce search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (!searchTerm || searchTerm.length < 2) {
      setSuggestions([])
      return
    }
    setLoadingSuggestions(true)
    debounceRef.current = setTimeout(async () => {
      try {
        // if user typed a space, try to split into nombres and apellidos
        const parts = searchTerm.trim().split(/\s+/)
        let url = '/api/v1/personas/search/by-name?limit=10'
        if (parts.length === 1) {
          url += `&nombres=${encodeURIComponent(parts[0])}`
        } else if (parts.length >= 2) {
          // first token -> nombres, last token -> apellidos (best-effort)
          const nombresPart = parts.slice(0, parts.length - 1).join(' ')
          const apellidosPart = parts[parts.length - 1]
          url += `&nombres=${encodeURIComponent(nombresPart)}&apellidos=${encodeURIComponent(apellidosPart)}`
        }
        const res = await fetch(url)
        if (!res.ok) {
          setSuggestions([])
        } else {
          const data = await res.json()
          setSuggestions(Array.isArray(data) ? data : (data.personas || data || []))
        }
      } catch (e) {
        setSuggestions([])
      } finally {
        setLoadingSuggestions(false)
      }
    }, 300)
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current) }
  }, [searchTerm])

  function handleSelectSuggestion(p) {
    setSelectedPerson(p)
    setSuggestions([])
    setSearchTerm('')
  }

  function handleClearSelection() {
    setSelectedPerson(null)
    setNombres('')
    setApellidos('')
    setFechaNacimiento('')
    setLugarNacimiento('')
    setPadre('')
    setMadre('')
    setSacramentos([])
  }

  return (
    <Layout title="Gestión de Personas">
      <div className="bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Datos Personales</h3>
        </div>
        <form className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="nombres">Nombres</label>
              <input value={nombres} onChange={(e) => { setNombres(e.target.value); setSearchTerm(e.target.value) }} className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="nombres" placeholder="Ingrese los nombres" type="text" />
              {loadingSuggestions && <div className="text-xs text-gray-500 mt-1">Buscando...</div>}
              {suggestions && suggestions.length > 0 && (
                <ul className="mt-1 border rounded bg-white z-10 relative max-h-48 overflow-auto">
                  {suggestions.map((s) => (
                    <li key={s.id_persona || s.id} onClick={() => handleSelectSuggestion(s)} className="px-3 py-2 hover:bg-gray-100 cursor-pointer">
                      <div className="text-sm font-medium">{`${s.nombres} ${s.apellido_paterno || ''} ${s.apellido_materno || ''}`.trim()}</div>
                      <div className="text-xs text-gray-500">{s.fecha_nacimiento ? String(s.fecha_nacimiento).substring(0,10) : ''} {s.lugar_nacimiento ? `• ${s.lugar_nacimiento}` : ''}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="apellidos">Apellidos</label>
              <input value={apellidos} onChange={(e) => setApellidos(e.target.value)} className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="apellidos" placeholder="Ingrese los apellidos" type="text" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="fecha-nacimiento">Fecha de Nacimiento</label>
              <input value={fechaNacimiento} onChange={(e) => setFechaNacimiento(e.target.value)} className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="fecha-nacimiento" type="date" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="lugar-nacimiento">Lugar de Nacimiento</label>
              <input value={lugarNacimiento} onChange={(e) => setLugarNacimiento(e.target.value)} className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="lugar-nacimiento" placeholder="Ingrese el lugar" type="text" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="padre">Padre</label>
              <input value={padre} onChange={(e) => setPadre(e.target.value)} className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="padre" placeholder="Ingrese el nombre del padre" type="text" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="madre">Madre</label>
              <input value={madre} onChange={(e) => setMadre(e.target.value)} className="w-full rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary p-3 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500" id="madre" placeholder="Ingrese el nombre de la madre" type="text" />
            </div>
            <div className="md:col-span-2 flex gap-2">
              <button type="button" onClick={() => setMergeOpen(true)} className="px-4 py-2 rounded bg-primary text-white">Buscar duplicados</button>
              <button type="button" onClick={handleClearSelection} className="px-4 py-2 rounded border">Limpiar</button>
            </div>
          </div>
        </form>
      </div>

      <div className="mt-8 bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Historial de Sacramentos</h3>
        </div>
        <div className="p-6">
          <p className="text-sm text-gray-600">Historial de sacramentos asociados a la persona seleccionada.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700/50 dark:text-gray-400">
              <tr>
                <th className="px-6 py-3" scope="col">Sacramento</th>
                <th className="px-6 py-3" scope="col">Fecha</th>
                <th className="px-6 py-3" scope="col">Lugar</th>
                <th className="px-6 py-3" scope="col">Libro / Foja / Nº</th>
              </tr>
            </thead>
            <tbody>
              {sacramentos.length === 0 ? (
                <tr className="bg-white dark:bg-background-dark/50 border-b dark:border-gray-700">
                  <td className="px-6 py-4" colSpan={4}>No hay sacramentos relacionados.</td>
                </tr>
              ) : (
                sacramentos.map((s) => (
                  <tr key={s.id_sacramento || s.id} className="bg-white dark:bg-background-dark/50 border-b dark:border-gray-700">
                    <th className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" scope="row">{s.tipo_nombre || s.tipo_sacramento || s.tipo}</th>
                    <td className="px-6 py-4">{s.fecha_sacramento?.substring(0,10) || s.fecha || '-'}</td>
                    <td className="px-6 py-4">{s.institucion_nombre || s.institucion || '-'}</td>
                    <td className="px-6 py-4">{`${s.libro_nombre || s.libro || (s.libro_id ? `Libro ${s.libro_id}` : '-') } / ${s.foja || s.folio || '-'} / ${s.numero_acta || s.numero || '-'}`}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <DuplicatesMergeModal open={mergeOpen} onClose={() => setMergeOpen(false)} />
    </Layout>
  )
}

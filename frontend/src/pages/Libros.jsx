import { useEffect, useState } from 'react'
import Layout from '../components/Layout'

export default function Libros() {
  const [libros, setLibros] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedLibro, setSelectedLibro] = useState(null)
  const [estante, setEstante] = useState('')
  const [nivel, setNivel] = useState('')
  const [sigla, setSigla] = useState('')

  useEffect(() => {
    fetchLibros()
  }, [])

  async function fetchLibros() {
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8002/api/v1/libros')
      if (!res.ok) throw new Error('Error cargando libros')
      const data = await res.json()
      setLibros(Array.isArray(data) ? data : (data.libros || []))
    } catch (err) {
      console.error('fetchLibros:', err)
      setLibros([])
    } finally {
      setLoading(false)
    }
  }

  function selectLibro(libro) {
    setSelectedLibro(libro)
    // parse observaciones if it contains a location like A-1-001
    const obs = libro?.observaciones || ''
    if (obs && /[A-Z]-\d-\d{3}/.test(obs)) {
      const parts = obs.split('-')
      setEstante(parts[0] || '')
      setNivel(parts[1] || '')
      setSigla(parts[2] || '')
    } else {
      setEstante('')
      setNivel('')
      setSigla(obs || '')
    }
  }

  async function handleSaveLocation(e) {
    e.preventDefault()
    if (!selectedLibro) return
    const location = estante && nivel ? `${estante}-${nivel}-${sigla || '000'}` : (sigla || '')
    try {
      const body = { observaciones: location }
      const res = await fetch(`http://localhost:8002/api/v1/libros/${selectedLibro.id_libro}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      if (!res.ok) throw new Error('No se pudo actualizar libro')
      const updated = await res.json()
      // refresh list and selected
      await fetchLibros()
      setSelectedLibro(updated)
      alert('Ubicación guardada')
    } catch (err) {
      console.error('handleSaveLocation:', err)
      alert('Error guardando ubicación: ' + err.message)
    }
  }

  async function assignSelectedToShelf(key) {
    if (!selectedLibro) {
      alert('Selecciona primero un libro en la tabla para asignarlo a la estantería, o usa Añadir para crear uno nuevo.')
      return
    }
    try {
      const body = { observaciones: key }
      const res = await fetch(`http://localhost:8002/api/v1/libros/${selectedLibro.id_libro}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      if (!res.ok) throw new Error('No se pudo asignar libro a estantería')
      const updated = await res.json()
      await fetchLibros()
      setSelectedLibro(updated)
      alert(`Libro ${updated.nombre} asignado a ${key}`)
    } catch (err) {
      console.error('assignSelectedToShelf:', err)
      alert('Error asignando libro: ' + err.message)
    }
  }

  async function handleAddLibro() {
    const nombre = window.prompt('Nombre del libro (ej. "10")')
    if (!nombre) return
    const hoy = new Date().toISOString().slice(0,10)
    try {
      const payload = { nombre, fecha_inicio: hoy, fecha_fin: hoy }
      const res = await fetch('http://localhost:8002/api/v1/libros', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const txt = await res.text()
        throw new Error(txt || 'Error creando libro')
      }
      const created = await res.json()
      await fetchLibros()
      setSelectedLibro(created)
      alert('Libro creado: ' + created.nombre)
    } catch (err) {
      console.error('handleAddLibro:', err)
      alert('Error creando libro: ' + err.message)
    }
  }

  return (
    <Layout title="Gestión de Libros">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-card-light dark:bg-card-dark rounded-lg border border-border-light dark:border-border-dark">
            <div className="p-4 border-b border-border-light dark:border-border-dark">
              <h3 className="font-semibold text-lg">Listado de Libros</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-border-light dark:border-border-dark">
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Tipo</th>
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Número</th>
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Rango de Años</th>
                    <th className="p-4 font-medium text-muted-foreground-light dark:text-muted-foreground-dark">Ubicación</th>
                  </tr>
                </thead>
                <tbody>
                  {loading && (
                    <tr>
                      <td colSpan={4} className="p-4 text-center text-sm text-gray-500">Cargando libros...</td>
                    </tr>
                  )}
                  {!loading && libros.length === 0 && (
                    <tr>
                      <td colSpan={4} className="p-4 text-center text-sm text-gray-500">No hay libros registrados.</td>
                    </tr>
                  )}
                  {!loading && libros.map((libro) => {
                    const selected = selectedLibro && selectedLibro.id_libro === libro.id_libro
                    const libroType = libro.nombre?.split(' ')[0] || 'Libro'
                    const range = libro.fecha_inicio && libro.fecha_fin ? `${new Date(libro.fecha_inicio).getFullYear()}-${new Date(libro.fecha_fin).getFullYear()}` : ''
                    const ubic = libro.observaciones || 'Sin asignar'
                    return (
                      <tr key={libro.id_libro} onClick={() => selectLibro(libro)} className={`cursor-pointer border-b border-border-light dark:border-border-dark hover:bg-background-light dark:hover:bg-background-dark ${selected ? 'bg-primary/5' : ''}`}>
                        <td className="p-4">{libroType}</td>
                        <td className="p-4">{libro.id_libro}</td>
                        <td className="p-4">{range}</td>
                        <td className={`p-4 ${ubic === 'Sin asignar' ? 'text-muted-foreground-light dark:text-muted-foreground-dark' : 'text-primary'}`}>{ubic}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div>
          <div className="bg-card-light dark:bg-card-dark rounded-lg border border-border-light dark:border-border-dark p-4">
            <h3 className="font-semibold text-lg mb-4">Asignar Ubicación Física</h3>
            <p className="text-sm text-muted-foreground-light dark:text-muted-foreground-dark mb-4">Seleccionado: {selectedLibro ? `${selectedLibro.nombre} #${selectedLibro.id_libro}` : 'Ninguno'}</p>
            <form className="space-y-4" onSubmit={handleSaveLocation}>
              <div>
                <label htmlFor="estante" className="block text-sm font-medium mb-1">Estante</label>
                <select id="estante" value={estante} onChange={(e) => setEstante(e.target.value)} className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">Seleccionar estante</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                </select>
              </div>
              <div>
                <label htmlFor="nivel" className="block text-sm font-medium mb-1">Nivel</label>
                <select id="nivel" value={nivel} onChange={(e) => setNivel(e.target.value)} className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">Seleccionar nivel</option>
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                </select>
              </div>
              <div>
                <label htmlFor="sigla" className="block text-sm font-medium mb-1">Sigla</label>
                <input id="sigla" value={sigla} onChange={(e) => setSigla(e.target.value)} type="text" placeholder="Ingresar sigla" className="w-full p-2 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <button type="submit" disabled={!selectedLibro} className="w-full bg-primary text-white py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50">Guardar Ubicación</button>
            </form>
          </div>
        </div>
        <div className="lg:col-span-3">
          <div className="bg-card-light dark:bg-card-dark rounded-lg border border-border-light dark:border-border-dark p-4">
            <h3 className="font-semibold text-lg mb-4">Cuadrícula de Estanterías</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
              <div onClick={handleAddLibro} className="group relative rounded-lg border-2 border-dashed border-border-light dark:border-border-dark flex items-center justify-center cursor-pointer hover:border-primary aspect-square">
                <div className="text-center">
                  <span className="material-symbols-outlined text-4xl text-muted-foreground-light dark:text-muted-foreground-dark group-hover:text-primary">add_box</span>
                  <p className="text-xs mt-1 text-muted-foreground-light dark:text-muted-foreground-dark group-hover:text-primary">Añadir</p>
                </div>
              </div>
              {['A-1','A-2','A-3','A-4','B-1','B-2','B-3','B-4','C-1','C-2','C-3'].map((key) => {
                // find libro assigned to this shelf (observaciones like 'A-1-001')
                const assigned = libros.find(l => {
                  if (!l || !l.observaciones) return false
                  const obs = String(l.observaciones)
                  return obs === key || obs.startsWith(key + '-')
                })
                const isSelected = selectedLibro && selectedLibro.observaciones && (selectedLibro.observaciones === key || selectedLibro.observaciones.startsWith(key + '-'))
                return (
                  <div key={key} onClick={() => {
                    if (assigned) {
                      selectLibro(assigned)
                    } else {
                      assignSelectedToShelf(key)
                    }
                  }} className={`rounded-lg flex flex-col items-center justify-center p-2 aspect-square cursor-pointer ${assigned ? 'border-2' : 'border'} ${isSelected ? 'border-primary bg-primary/10' : 'border-border-light dark:border-border-dark bg-background-light dark:bg-background-dark'}`}>
                    <p className="font-bold text-lg">{key}</p>
                    <p className="text-xs mt-1">{assigned ? String(assigned.nombre) : ''}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

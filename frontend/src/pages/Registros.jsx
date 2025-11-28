import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

const API_URL = 'http://localhost:8002/api/v1'

export default function Registros() {
  // Estados para los datos del formulario
  const [tiposSacramentos, setTiposSacramentos] = useState([])
  const [libros, setLibros] = useState([])
  const [instituciones, setInstituciones] = useState([])
  
  // Estados del formulario paso a paso
  const [tipoSeleccionado, setTipoSeleccionado] = useState('')
  const [libroSeleccionado, setLibroSeleccionado] = useState('')
  const [institucionSeleccionada, setInstitucionSeleccionada] = useState('')
  
  // Estados de persona
  const [persona, setPersona] = useState({
    nombres: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    fecha_bautismo: '',
    nombre_padre_nombre_madre: '',
    nombre_padrino_nombre_madrina: ''
  })
  
  // Estados del sacramento
  const [fechaSacramento, setFechaSacramento] = useState('')
  
  // Estados de UI
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [validacionDuplicado, setValidacionDuplicado] = useState(null)
  
  // Cargar catálogos al montar el componente
  useEffect(() => {
    cargarCatalogos()
  }, [])
  
  const cargarCatalogos = async () => {
    try {
      console.log('Cargando catálogos...')
      const [tiposRes, librosRes, institucionesRes] = await Promise.all([
        fetch(`${API_URL}/tipos-sacramentos`),
        fetch(`${API_URL}/libros`),
        fetch(`${API_URL}/instituciones`)
      ])
      
      if (!tiposRes.ok || !librosRes.ok || !institucionesRes.ok) {
        throw new Error('Error al cargar datos del servidor')
      }
      
      const tipos = await tiposRes.json()
      const librosData = await librosRes.json()
      const institucionesData = await institucionesRes.json()
      
      console.log('Catálogos cargados:', { tipos, librosData, institucionesData })
      
      // Extraer el array correcto de tipos_sacramentos
      const tiposArray = tipos.tipos_sacramentos || tipos
      
      setTiposSacramentos(tiposArray)
      setLibros(librosData)
      setInstituciones(institucionesData)
    } catch (err) {
      console.error('Error cargando catálogos:', err)
      setError('Error al cargar los catálogos: ' + err.message)
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
      // Primero buscar si la persona existe
      const searchRes = await fetch(
        `${API_URL}/personas/search?nombres=${encodeURIComponent(persona.nombres)}&apellido_paterno=${encodeURIComponent(persona.apellido_paterno)}&fecha_nacimiento=${persona.fecha_nacimiento}`
      )
      const personasEncontradas = await searchRes.json()
      
      if (personasEncontradas.length > 0) {
        // Si existe, verificar si ya tiene este sacramento
        const personaId = personasEncontradas[0].id_persona
        const checkRes = await fetch(
          `${API_URL}/sacramentos/check-duplicate?persona_id=${personaId}&tipo_id=${tipoSeleccionado}`
        )
        const resultado = await checkRes.json()
        
        if (resultado.exists) {
          setValidacionDuplicado({
            error: true,
            mensaje: `⚠️ Esta persona ya tiene el sacramento seleccionado registrado (ID: ${resultado.sacramento.id_sacramento})`
          })
        } else {
          setValidacionDuplicado({
            error: false,
            mensaje: '✓ Persona encontrada. Puede proceder con el registro del sacramento.'
          })
        }
      } else {
        setValidacionDuplicado({
          error: false,
          mensaje: '✓ Persona nueva. Se creará el registro de la persona y el sacramento.'
        })
      }
    } catch (err) {
      console.error('Error validando duplicado:', err)
    }
  }
  
  useEffect(() => {
    const timer = setTimeout(() => {
      validarDuplicado()
    }, 500)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tipoSeleccionado, persona.nombres, persona.apellido_paterno, persona.fecha_nacimiento, fechaSacramento])
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (validacionDuplicado?.error) {
      setError('No se puede registrar un sacramento duplicado')
      return
    }
    
    setLoading(true)
    setError(null)
    setSuccess(null)
    
    try {
      // 1. Crear o buscar persona
      let personaId
      const searchRes = await fetch(
        `${API_URL}/personas/search?nombres=${encodeURIComponent(persona.nombres)}&apellido_paterno=${encodeURIComponent(persona.apellido_paterno)}&fecha_nacimiento=${persona.fecha_nacimiento}`
      )
      const personasEncontradas = await searchRes.json()
      
      if (personasEncontradas.length > 0) {
        personaId = personasEncontradas[0].id_persona
      } else {
        // Crear nueva persona
        const createPersonaRes = await fetch(`${API_URL}/personas`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(persona)
        })
        
        if (!createPersonaRes.ok) {
          throw new Error('Error al crear persona')
        }
        
        const nuevaPersona = await createPersonaRes.json()
        personaId = nuevaPersona.id_persona
      }
      
      // 2. Crear sacramento
      const sacramentoData = {
        persona_id: personaId,
        tipo_id: parseInt(tipoSeleccionado),
        libro_id: parseInt(libroSeleccionado),
        institucion_id: parseInt(institucionSeleccionada),
        fecha_sacramento: fechaSacramento,
        usuario_id: 4 // Usuario de prueba
      }
      
      const createSacramentoRes = await fetch(`${API_URL}/sacramentos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sacramentoData)
      })
      
      if (!createSacramentoRes.ok) {
        const errorData = await createSacramentoRes.json()
        throw new Error(errorData.detail || 'Error al crear sacramento')
      }
      
      const nuevoSacramento = await createSacramentoRes.json()
      
      setSuccess(`✓ Sacramento registrado exitosamente. ID: ${nuevoSacramento.id_sacramento}`)
      
      // Limpiar formulario
      setTimeout(() => {
        resetForm()
      }, 2000)
      
    } catch (err) {
      setError('Error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }
  
  const resetForm = () => {
    setTipoSeleccionado('')
    setLibroSeleccionado('')
    setInstitucionSeleccionada('')
    setPersona({
      nombres: '',
      apellido_paterno: '',
      apellido_materno: '',
      fecha_nacimiento: '',
      fecha_bautismo: '',
      nombre_padre_nombre_madre: '',
      nombre_padrino_nombre_madrina: ''
    })
    setFechaSacramento('')
    setError(null)
    setSuccess(null)
    setValidacionDuplicado(null)
  }
  
  return (
    <Layout title="Registro de Sacramentos">
      <div className="bg-white dark:bg-gray-900/50 rounded-lg shadow">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Nuevo Registro de Sacramento
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Siga el orden: Tipo de Sacramento → Libro → Parroquia → Datos de la Persona
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Mensajes de error y éxito */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          {success && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg">
              {success}
            </div>
          )}
          
          {/* Paso 1: Tipo de Sacramento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              1. Tipo de Sacramento *
            </label>
            <select
              value={tipoSeleccionado}
              onChange={(e) => setTipoSeleccionado(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary"
            >
              <option value="">Seleccione un tipo de sacramento</option>
              {tiposSacramentos.map(tipo => (
                <option key={tipo.id_tipo} value={tipo.id_tipo}>
                  {tipo.nombre}
                </option>
              ))}
            </select>
          </div>
          
          {/* Paso 2: Libro */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              2. Libro *
            </label>
            <select
              value={libroSeleccionado}
              onChange={(e) => setLibroSeleccionado(e.target.value)}
              required
              disabled={!tipoSeleccionado}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="">Seleccione un libro</option>
              {libros.map(libro => (
                <option key={libro.id_libro} value={libro.id_libro}>
                  Libro {libro.id_libro} ({libro.fecha_inicio} - {libro.fecha_fin})
                </option>
              ))}
            </select>
          </div>
          
          {/* Paso 3: Parroquia/Institución */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              3. Parroquia/Institución *
            </label>
            <select
              value={institucionSeleccionada}
              onChange={(e) => setInstitucionSeleccionada(e.target.value)}
              required
              disabled={!libroSeleccionado}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="">Seleccione una parroquia</option>
              {instituciones.map(inst => (
                <option key={inst.id_institucion} value={inst.id_institucion}>
                  {inst.nombre}
                </option>
              ))}
            </select>
          </div>
          
          {/* Paso 4: Fecha del Sacramento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              4. Fecha del Sacramento *
            </label>
            <input
              type="date"
              value={fechaSacramento}
              onChange={(e) => setFechaSacramento(e.target.value)}
              required
              disabled={!institucionSeleccionada}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
          
          {/* Paso 5: Datos de la Persona */}
          <div className="border-t pt-6 dark:border-gray-800">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              5. Datos de la Persona
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombres *
                </label>
                <input
                  type="text"
                  name="nombres"
                  value={persona.nombres}
                  onChange={handlePersonaChange}
                  required
                  disabled={!fechaSacramento}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Apellido Paterno *
                </label>
                <input
                  type="text"
                  name="apellido_paterno"
                  value={persona.apellido_paterno}
                  onChange={handlePersonaChange}
                  required
                  disabled={!fechaSacramento}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Apellido Materno *
                </label>
                <input
                  type="text"
                  name="apellido_materno"
                  value={persona.apellido_materno}
                  onChange={handlePersonaChange}
                  required
                  disabled={!fechaSacramento}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fecha de Nacimiento *
                </label>
                <input
                  type="date"
                  name="fecha_nacimiento"
                  value={persona.fecha_nacimiento}
                  onChange={handlePersonaChange}
                  required
                  disabled={!fechaSacramento}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fecha de Bautismo *
                </label>
                <input
                  type="date"
                  name="fecha_bautismo"
                  value={persona.fecha_bautismo}
                  onChange={handlePersonaChange}
                  required
                  disabled={!fechaSacramento}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Fecha del bautismo previo (requerido para confirmación)
                </p>
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombres del Padre y Madre *
                </label>
                <input
                  type="text"
                  name="nombre_padre_nombre_madre"
                  value={persona.nombre_padre_nombre_madre}
                  onChange={handlePersonaChange}
                  required
                  disabled={!fechaSacramento}
                  placeholder="Ej: Juan Pérez García / María López Rodríguez"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombres del Padrino y Madrina *
                </label>
                <input
                  type="text"
                  name="nombre_padrino_nombre_madrina"
                  value={persona.nombre_padrino_nombre_madrina}
                  onChange={handlePersonaChange}
                  required
                  disabled={!fechaSacramento}
                  placeholder="Ej: Carlos Gómez / Ana Fernández"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-lg focus:ring-primary focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>
          </div>
          
          {/* Validación de duplicados */}
          {validacionDuplicado && (
            <div className={`px-4 py-3 rounded-lg ${
              validacionDuplicado.error 
                ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200' 
                : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
            }`}>
              {validacionDuplicado.mensaje}
            </div>
          )}
          
          {/* Botones de acción */}
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={loading || validacionDuplicado?.error}
              className="flex-1 bg-primary hover:bg-primary/90 text-white font-medium py-3 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Guardando...' : 'Guardar Sacramento'}
            </button>
            
            <button
              type="button"
              onClick={resetForm}
              disabled={loading}
              className="px-6 py-3 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Limpiar
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}

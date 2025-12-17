import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

const API_URL = 'http://localhost:8002/api/v1'

export default function Sacramento() {
  // Estados para catálogos
  const [tiposSacramentos, setTiposSacramentos] = useState([])
  const [libros, setLibros] = useState([])
  const [instituciones, setInstituciones] = useState([])
  
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [form, setForm] = useState({
    tipo_sacramento: 2, // Confirmación por defecto
    fecha_sacramento: '',
    sacrament_location: '',
    sacrament_minister: '',
    person_name: '',
    person_birthdate: '',
    father_name: '',
    mother_name: '',
    godparent_1_name: '',
    book_number: '',
    folio_number: '',
    record_number: '',
    notes: ''
  })
  
  // Estados de persona (lógica de Registros.jsx)
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
  const [validacionDuplicado, setValidacionDuplicado] = useState(null)
  
  // Estados de autocompletado
  const [sugerencias, setSugerencias] = useState([])
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false)
  const [campoActivo, setCampoActivo] = useState(null)
  
  // Cargar catálogos
  useEffect(() => {
    cargarCatalogos()
  }, [])
  
  const cargarCatalogos = async () => {
    try {
      const [tiposRes, librosRes, institucionesRes] = await Promise.all([
        fetch(`${API_URL}/tipos-sacramentos`),
        fetch(`${API_URL}/libros`),
        fetch(`${API_URL}/instituciones`)
      ])
      
      const tipos = await tiposRes.json()
      const librosData = await librosRes.json()
      const institucionesData = await institucionesRes.json()
      
      const tiposArray = tipos.tipos_sacramentos || tipos
      
      setTiposSacramentos(tiposArray)
      setLibros(librosData)
      setInstituciones(institucionesData)
    } catch (err) {
      console.error('Error cargando catálogos:', err)
    }
  }
  
  const handlePersonaChange = (e) => {
    const { name, value } = e.target
    setPersona(prev => ({ ...prev, [name]: value }))
    
    if (['nombres', 'apellido_paterno', 'apellido_materno'].includes(name)) {
      setCampoActivo(name)
      if (value.length >= 2) {
        buscarSugerencias(name, value)
      } else {
        setSugerencias([])
        setMostrarSugerencias(false)
      }
    }
  }
  
  const buscarSugerencias = async (campo, valor) => {
    if (!valor || valor.length < 2) {
      setSugerencias([])
      return
    }
    
    try {
      const res = await fetch(`${API_URL}/personas?${campo}=${encodeURIComponent(valor)}&limit=10`)
      const personas = await res.json()
      
      if (personas && personas.length > 0) {
        // Guardar personas completas con sus datos para autocompletado
        const personasConDatos = personas.filter(p => 
          p[campo] && p[campo].toLowerCase().includes(valor.toLowerCase())
        )
        
        // Crear sugerencias únicas con datos completos
        const sugerenciasUnicas = []
        const valoresVistos = new Set()
        
        for (const p of personasConDatos) {
          const valorCampo = p[campo]
          if (!valoresVistos.has(valorCampo)) {
            valoresVistos.add(valorCampo)
            sugerenciasUnicas.push({
              valor: valorCampo,
              persona: p  // Guardar persona completa
            })
          }
        }
        
        setSugerencias(sugerenciasUnicas.slice(0, 5))
        setMostrarSugerencias(sugerenciasUnicas.length > 0)
      } else {
        setSugerencias([])
        setMostrarSugerencias(false)
      }
    } catch (err) {
      console.error('Error buscando sugerencias:', err)
      setSugerencias([])
      setMostrarSugerencias(false)
    }
  }
  
  const seleccionarSugerencia = (sugerencia) => {
    if (campoActivo && sugerencia.persona) {
      // Autocompletar todos los campos personales de la persona
      setPersona({
        nombres: sugerencia.persona.nombres || '',
        apellido_paterno: sugerencia.persona.apellido_paterno || '',
        apellido_materno: sugerencia.persona.apellido_materno || '',
        fecha_nacimiento: sugerencia.persona.fecha_nacimiento || '',
        fecha_bautismo: sugerencia.persona.fecha_bautismo || '',
        nombre_padre_nombre_madre: sugerencia.persona.nombre_padre_nombre_madre || '',
        nombre_padrino_nombre_madrina: sugerencia.persona.nombre_padrino_nombre_madrina || '',
        lugar_nacimiento: sugerencia.persona.lugar_nacimiento || ''
      })
      
      // LÓGICA ESPECÍFICA POR TIPO DE SACRAMENTO:
      
      // Para Bautizo (tipo 1): Si la persona ya tiene fecha_bautismo registrada,
      // usar esa fecha como fecha del sacramento para evitar duplicados
      // (Caso: persona con confirmación registrada, ahora se registra su bautizo)
      if (form.tipo_sacramento === 1 && sugerencia.persona.fecha_bautismo) {
        setForm(prev => ({ ...prev, fecha_sacramento: sugerencia.persona.fecha_bautismo }))
      }
      
      // Para Confirmación (tipo 2): NO autocompletar fecha_sacramento
      // porque la fecha de confirmación es nueva y diferente a la de bautizo
      // (Caso: persona con bautizo registrado, ahora se registra su confirmación)
      // La fecha del sacramento debe ser llenada manualmente por el usuario
      
      setSugerencias([])
      setMostrarSugerencias(false)
      setCampoActivo(null)
    }
  }
  
  const validarDuplicado = async () => {
    if (form.tipo_sacramento !== 2) return // Solo para confirmación
    
    if (!persona.nombres || !persona.apellido_paterno || !form.fecha_sacramento || !persona.fecha_nacimiento) {
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
        const checkRes = await fetch(
          `${API_URL}/sacramentos/check-duplicate?persona_id=${personaId}&tipo_id=${form.tipo_sacramento}`
        )
        const resultado = await checkRes.json()
        
        if (resultado.exists) {
          setValidacionDuplicado({
            error: true,
            mensaje: `⚠️ Esta persona ya tiene este sacramento registrado (ID: ${resultado.sacramento.id_sacramento})`
          })
        } else {
          setValidacionDuplicado({
            error: false,
            mensaje: '✓ Persona encontrada. Puede proceder con el registro.'
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
    if (form.tipo_sacramento === 2) {
      const timer = setTimeout(() => {
        validarDuplicado()
      }, 500)
      return () => clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.tipo_sacramento, persona.nombres, persona.apellido_paterno, persona.fecha_nacimiento, form.fecha_sacramento])

  const handleChange = (e) => {
    const { name, value } = e.target
    // tipo_sacramento must be a number so backend treats it as id, not as a name
    if (name === 'tipo_sacramento') {
      setForm((s) => ({ ...s, [name]: Number(value) }))
      return
    }
    
    setForm((s) => ({ ...s, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Bautizo (tipo 1)
    if (form.tipo_sacramento === 1) {
      return await handleSubmitBautizo()
    }
    
    // Confirmación (tipo 2)
    if (form.tipo_sacramento === 2) {
      return await handleSubmitConfirmacion()
    }
    
    // Matrimonio (tipo 3)
    if (form.tipo_sacramento === 3) {
      return await handleSubmitMatrimonio()
    }
    
    // Lógica original para otros sacramentos (Defunción, etc.)
    setLoading(true)
    setMessage(null)
    try {
      const nameTrim = (form.person_name || '').trim()
      if (!form.fecha_sacramento) {
        setMessage({ type: 'error', text: 'La fecha del sacramento es obligatoria.' })
        setLoading(false)
        return
      }
      if (!nameTrim && !form.persona_id) {
        setMessage({ type: 'error', text: 'Debe indicar la persona (nombre) o seleccionar una persona existente.' })
        setLoading(false)
        return
      }
      const payload = {
        tipo_sacramento: Number(form.tipo_sacramento),
        fecha_sacramento: form.fecha_sacramento,
        institucion: form.sacrament_location,
        ministro: form.sacrament_minister,
        person_name: form.person_name,
        person_birthdate: form.person_birthdate,
        father_name: form.father_name,
        mother_name: form.mother_name,
        godparent_1_name: form.godparent_1_name,
        libro: form.book_number,
        folio: form.folio_number,
        numero_acta: form.record_number,
        observaciones: form.notes
      }

      const res = await fetch('/api/v1/sacramentos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      const text = await res.text()
      let data = null
      try {
        data = text ? JSON.parse(text) : null
      } catch (err) {
        data = null
      }
      if (!res.ok) {
        const detail = data?.detail || text || res.statusText
        throw new Error(`${res.status} ${detail}`)
      }
      setMessage({ type: 'success', text: 'Sacramento creado (id: ' + (data?.id_sacramento || data?.id || 'ok') + ')' })
    } catch (err) {
      setMessage({ type: 'error', text: String(err) })
    } finally {
      setLoading(false)
    }
  }
  
  const handleSubmitConfirmacion = async () => {
    if (validacionDuplicado?.error) {
      setMessage({ type: 'error', text: 'No se puede registrar un sacramento duplicado' })
      return
    }
    
    setLoading(true)
    setMessage(null)
    
    try {
      // 1. Buscar persona por nombre completo (sin fecha de nacimiento)
      let personaId
      const searchRes = await fetch(
        `${API_URL}/personas/search?nombres=${encodeURIComponent(persona.nombres)}&apellido_paterno=${encodeURIComponent(persona.apellido_paterno)}&apellido_materno=${encodeURIComponent(persona.apellido_materno)}`
      )
      const personasEncontradas = await searchRes.json()
      
      if (personasEncontradas.length > 0) {
        // Persona ya existe (probablemente tiene bautizo), reutilizar su ID
        personaId = personasEncontradas[0].id_persona
        console.log(`✓ Persona encontrada (ID: ${personaId}), reutilizando registro existente`)
      } else {
        // Persona no existe, crear nuevo registro con datos de confirmación
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
        console.log(`✓ Persona creada (ID: ${personaId})`)
      }
      
      // 2. Crear sacramento
      const sacramentoData = {
        persona_id: personaId,
        tipo_id: parseInt(form.tipo_sacramento),
        libro_id: parseInt(libroSeleccionado),
        institucion_id: parseInt(institucionSeleccionada),
        fecha_sacramento: form.fecha_sacramento,
        usuario_id: 4
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
      
      setMessage({ type: 'success', text: `✓ Sacramento registrado exitosamente. ID: ${nuevoSacramento.id_sacramento}` })
      
      setTimeout(() => {
        resetFormConfirmacion()
      }, 2000)
      
    } catch (err) {
      setMessage({ type: 'error', text: 'Error: ' + err.message })
    } finally {
      setLoading(false)
    }
  }
  
  const resetFormConfirmacion = () => {
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
    setForm(prev => ({ ...prev, fecha_sacramento: '' }))
    setValidacionDuplicado(null)
    setMessage(null)
  }
  
  const handleSubmitBautizo = async () => {
    setLoading(true)
    setMessage(null)
    
    try {
      const bautizoData = {
        libro_id: parseInt(libroSeleccionado),
        institucion_id: parseInt(institucionSeleccionada),
        fecha_sacramento: form.fecha_sacramento,
        nombres: persona.nombres,
        apellido_paterno: persona.apellido_paterno,
        apellido_materno: persona.apellido_materno,
        fecha_nacimiento: persona.fecha_nacimiento,
        fecha_bautismo: form.fecha_sacramento, // La fecha de bautismo es la misma que la del sacramento
        nombre_padre_nombre_madre: persona.nombre_padre_nombre_madre,
        nombre_padrino_nombre_madrina: persona.nombre_padrino_nombre_madrina,
        usuario_id: 4
      }
      
      const res = await fetch(`${API_URL}/bautizos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bautizoData)
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Error al registrar bautizo')
      }
      
      const resultado = await res.json()
      setMessage({ type: 'success', text: `✓ Bautizo registrado. Persona ID: ${resultado.persona_id}, Sacramento ID: ${resultado.sacramento_id}` })
      
      setTimeout(() => {
        resetFormConfirmacion()
      }, 2000)
      
    } catch (err) {
      setMessage({ type: 'error', text: 'Error: ' + err.message })
    } finally {
      setLoading(false)
    }
  }
  
  const handleSubmitMatrimonio = async () => {
    setLoading(true)
    setMessage(null)
    
    try {
      // 1. Buscar o crear Esposo
      let esposoId
      const searchEsposoRes = await fetch(
        `${API_URL}/personas/search?nombres=${encodeURIComponent(persona.nombres_esposo || '')}&apellido_paterno=${encodeURIComponent(persona.apellido_paterno_esposo || '')}&apellido_materno=${encodeURIComponent(persona.apellido_materno_esposo || '')}`
      )
      const espososEncontrados = await searchEsposoRes.json()
      
      if (espososEncontrados.length > 0) {
        esposoId = espososEncontrados[0].id_persona
        console.log(`✓ Esposo encontrado (ID: ${esposoId}), reutilizando registro`)
      } else {
        // Crear esposo
        const createEsposoRes = await fetch(`${API_URL}/personas`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nombres: persona.nombres_esposo,
            apellido_paterno: persona.apellido_paterno_esposo,
            apellido_materno: persona.apellido_materno_esposo,
            fecha_nacimiento: persona.fecha_nacimiento_esposo,
            fecha_bautismo: persona.fecha_bautismo_esposo,
            nombre_padre_nombre_madre: persona.padres_esposo || '',
            nombre_padrino_nombre_madrina: ''
          })
        })
        
        if (!createEsposoRes.ok) {
          throw new Error('Error al crear esposo')
        }
        
        const nuevoEsposo = await createEsposoRes.json()
        esposoId = nuevoEsposo.id_persona
        console.log(`✓ Esposo creado (ID: ${esposoId})`)
      }
      
      // 2. Buscar o crear Esposa
      let esposaId
      const searchEsposaRes = await fetch(
        `${API_URL}/personas/search?nombres=${encodeURIComponent(persona.nombres_esposa || '')}&apellido_paterno=${encodeURIComponent(persona.apellido_paterno_esposa || '')}&apellido_materno=${encodeURIComponent(persona.apellido_materno_esposa || '')}`
      )
      const esposasencontradas = await searchEsposaRes.json()
      
      if (esposasencontradas.length > 0) {
        esposaId = esposasencontradas[0].id_persona
        console.log(`✓ Esposa encontrada (ID: ${esposaId}), reutilizando registro`)
      } else {
        // Crear esposa
        const createEsposaRes = await fetch(`${API_URL}/personas`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nombres: persona.nombres_esposa,
            apellido_paterno: persona.apellido_paterno_esposa,
            apellido_materno: persona.apellido_materno_esposa,
            fecha_nacimiento: persona.fecha_nacimiento_esposa,
            fecha_bautismo: persona.fecha_bautismo_esposa,
            nombre_padre_nombre_madre: persona.padres_esposa || '',
            nombre_padrino_nombre_madrina: ''
          })
        })
        
        if (!createEsposaRes.ok) {
          throw new Error('Error al crear esposa')
        }
        
        const nuevaEsposa = await createEsposaRes.json()
        esposaId = nuevaEsposa.id_persona
        console.log(`✓ Esposa creada (ID: ${esposaId})`)
      }
      
      // 3. Crear sacramento de matrimonio
      const sacramentoData = {
        persona_id: esposoId, // El esposo es la persona principal
        tipo_id: 3, // Matrimonio
        libro_id: parseInt(libroSeleccionado),
        institucion_id: parseInt(institucionSeleccionada),
        fecha_sacramento: form.fecha_sacramento,
        usuario_id: 4
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
      const sacramentoId = nuevoSacramento.id_sacramento
      
      // 4. Crear registro en tabla matrimonios
      const matrimonioData = {
        sacramento_id: sacramentoId,
        esposo_id: esposoId,
        esposa_id: esposaId,
        nombre_padre_esposo: persona.padres_esposo?.split('/')[0]?.trim() || '',
        nombre_madre_esposo: persona.padres_esposo?.split('/')[1]?.trim() || '',
        nombre_padre_esposa: persona.padres_esposa?.split('/')[0]?.trim() || '',
        nombre_madre_esposa: persona.padres_esposa?.split('/')[1]?.trim() || '',
        testigos: persona.testigos || ''
      }
      
      const createMatrimonioRes = await fetch(`${API_URL}/matrimonios/registro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(matrimonioData)
      })
      
      if (!createMatrimonioRes.ok) {
        const errorData = await createMatrimonioRes.json()
        throw new Error(errorData.detail || 'Error al crear matrimonio')
      }
      
      setMessage({ type: 'success', text: `✓ Matrimonio registrado. Esposo ID: ${esposoId}, Esposa ID: ${esposaId}, Sacramento ID: ${sacramentoId}` })
      
      setTimeout(() => {
        resetFormConfirmacion()
      }, 2000)
      
    } catch (err) {
      setMessage({ type: 'error', text: 'Error: ' + err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout title="Registrar Nuevo Sacramento">
      <main className="p-8">
        <div className="max-w-6xl mx-auto flex flex-col gap-6">
          <div className="flex flex-wrap justify-between gap-3 items-center">
            <p className="text-gray-900 dark:text-white text-3xl font-bold leading-tight tracking-[-0.03em] min-w-72">Registrar Nuevo Sacramento</p>
          </div>

          <div className="flex">
            <div className="flex h-12 flex-1 items-center justify-center rounded-xl bg-gray-200 dark:bg-gray-800 p-1.5">
              {[{id:1,label:'Bautizo'},{id:2,label:'Confirmación'},{id:3,label:'Matrimonio'},{id:4,label:'Defunción'}].map((it)=>{
                const active = form.tipo_sacramento === it.id
                const base = 'flex cursor-pointer h-full grow items-center justify-center overflow-hidden rounded-lg px-4 text-sm font-medium leading-normal transition-all duration-200 select-none'
                const activeCls = active ? 'bg-white dark:bg-gray-900/80 text-primary shadow-md scale-105' : 'text-gray-500 dark:text-gray-400 hover:bg-white/50 dark:hover:bg-gray-700/50'
                return (
                  <button type="button" key={it.id} onClick={() => setForm(s=>({...s,tipo_sacramento: it.id}))} className={base + ' ' + activeCls}>
                    <span className="truncate">{it.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-xl p-8 flex flex-col gap-8">
            {message && (
              <div className={`px-4 py-3 rounded-lg ${message.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-200' : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200'}`}>
                {message.text}
              </div>
            )}
            
            {/* Para Bautizo, Confirmación y Matrimonio, mostrar selección de Libro e Institución */}
            {[1, 2, 3].includes(form.tipo_sacramento) && (
              <>
                <div className="flex flex-col gap-4">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-800 pb-3">Libro e Institución</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Libro *</label>
                      <select
                        value={libroSeleccionado}
                        onChange={(e) => setLibroSeleccionado(e.target.value)}
                        required
                        className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      >
                        <option value="">Seleccione un libro</option>
                        {libros.map(libro => (
                          <option key={libro.id_libro} value={libro.id_libro}>
                            {libro.nombre} ({libro.fecha_inicio} - {libro.fecha_fin})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="flex flex-col gap-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Parroquia/Institución *</label>
                      <select
                        value={institucionSeleccionada}
                        onChange={(e) => setInstitucionSeleccionada(e.target.value)}
                        required
                        disabled={!libroSeleccionado}
                        className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      >
                        <option value="">Seleccione una parroquia</option>
                        {instituciones.map(inst => (
                          <option key={inst.id_institucion} value={inst.id_institucion}>
                            {inst.nombre}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </>
            )}
            
            <div className="flex flex-col gap-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-800 pb-3">Datos del Sacramento</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="sacrament-date">Fecha del Sacramento *</label>
                  <input 
                    name="fecha_sacramento" 
                    value={form.fecha_sacramento} 
                    onChange={handleChange} 
                    className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" 
                    id="sacrament-date" 
                    type="date"
                    required
                    disabled={form.tipo_sacramento === 2 && !institucionSeleccionada}
                  />
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-800 pb-3">
                {form.tipo_sacramento === 1 ? 'Datos del Bautizado' : form.tipo_sacramento === 2 ? 'Datos del Confirmando' : form.tipo_sacramento === 3 ? 'Datos de los Contrayentes' : 'Datos del Fallecido'}
              </h3>
              
              {/* Formulario específico para Confirmación */}
              {form.tipo_sacramento === 2 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="relative">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres *</label>
                    <input
                      type="text"
                      name="nombres"
                      value={persona.nombres}
                      onChange={handlePersonaChange}
                      onBlur={() => setTimeout(() => setMostrarSugerencias(false), 200)}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      placeholder="Ej: Juan Carlos"
                      autoComplete="off"
                    />
                    {mostrarSugerencias && campoActivo === 'nombres' && sugerencias.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {sugerencias.map((sugerencia, index) => (
                          <div
                            key={index}
                            onClick={() => seleccionarSugerencia(sugerencia)}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                          >
                            {sugerencia.valor}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="relative">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Paterno *</label>
                    <input
                      type="text"
                      name="apellido_paterno"
                      value={persona.apellido_paterno}
                      onChange={handlePersonaChange}
                      onBlur={() => setTimeout(() => setMostrarSugerencias(false), 200)}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      placeholder="Ej: García"
                      autoComplete="off"
                    />
                    {mostrarSugerencias && campoActivo === 'apellido_paterno' && sugerencias.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {sugerencias.map((sugerencia, index) => (
                          <div
                            key={index}
                            onClick={() => seleccionarSugerencia(sugerencia)}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                          >
                            {sugerencia.valor}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="relative">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Materno *</label>
                    <input
                      type="text"
                      name="apellido_materno"
                      value={persona.apellido_materno}
                      onChange={handlePersonaChange}
                      onBlur={() => setTimeout(() => setMostrarSugerencias(false), 200)}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      placeholder="Ej: Pérez"
                      autoComplete="off"
                    />
                    {mostrarSugerencias && campoActivo === 'apellido_materno' && sugerencias.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {sugerencias.map((sugerencia, index) => (
                          <div
                            key={index}
                            onClick={() => seleccionarSugerencia(sugerencia)}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                          >
                            {sugerencia.valor}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Fecha de Nacimiento *</label>
                    <input
                      type="date"
                      name="fecha_nacimiento"
                      value={persona.fecha_nacimiento}
                      onChange={handlePersonaChange}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Fecha de Bautismo *</label>
                    <input
                      type="date"
                      name="fecha_bautismo"
                      value={persona.fecha_bautismo}
                      onChange={handlePersonaChange}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres del Padre y Madre *</label>
                    <input
                      type="text"
                      name="nombre_padre_nombre_madre"
                      value={persona.nombre_padre_nombre_madre}
                      onChange={handlePersonaChange}
                      required
                      placeholder="Ej: Juan Pérez García / María López Rodríguez"
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres del Padrino y Madrina *</label>
                    <input
                      type="text"
                      name="nombre_padrino_nombre_madrina"
                      value={persona.nombre_padrino_nombre_madrina}
                      onChange={handlePersonaChange}
                      required
                      placeholder="Ej: Carlos Gómez / Ana Fernández"
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>
                </div>
              ) : form.tipo_sacramento === 1 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="relative">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres *</label>
                    <input
                      type="text"
                      name="nombres"
                      value={persona.nombres}
                      onChange={handlePersonaChange}
                      onBlur={() => setTimeout(() => setMostrarSugerencias(false), 200)}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      placeholder="Ej: Juan Carlos"
                      autoComplete="off"
                    />
                    {mostrarSugerencias && campoActivo === 'nombres' && sugerencias.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {sugerencias.map((sugerencia, index) => (
                          <div
                            key={index}
                            onClick={() => seleccionarSugerencia(sugerencia)}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                          >
                            {sugerencia.valor}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="relative">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Paterno *</label>
                    <input
                      type="text"
                      name="apellido_paterno"
                      value={persona.apellido_paterno}
                      onChange={handlePersonaChange}
                      onBlur={() => setTimeout(() => setMostrarSugerencias(false), 200)}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      placeholder="Ej: Pérez"
                      autoComplete="off"
                    />
                    {mostrarSugerencias && campoActivo === 'apellido_paterno' && sugerencias.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {sugerencias.map((sugerencia, index) => (
                          <div
                            key={index}
                            onClick={() => seleccionarSugerencia(sugerencia)}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                          >
                            {sugerencia.valor}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="relative">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Materno *</label>
                    <input
                      type="text"
                      name="apellido_materno"
                      value={persona.apellido_materno}
                      onChange={handlePersonaChange}
                      onBlur={() => setTimeout(() => setMostrarSugerencias(false), 200)}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                      placeholder="Ej: González"
                      autoComplete="off"
                    />
                    {mostrarSugerencias && campoActivo === 'apellido_materno' && sugerencias.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {sugerencias.map((sugerencia, index) => (
                          <div
                            key={index}
                            onClick={() => seleccionarSugerencia(sugerencia)}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                          >
                            {sugerencia.valor}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Fecha de Nacimiento *</label>
                    <input
                      type="date"
                      name="fecha_nacimiento"
                      value={persona.fecha_nacimiento}
                      onChange={handlePersonaChange}
                      required
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres de los Padres *</label>
                    <input
                      type="text"
                      name="nombre_padre_nombre_madre"
                      value={persona.nombre_padre_nombre_madre}
                      onChange={handlePersonaChange}
                      required
                      placeholder="Ej: Juan Pérez / María González"
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres del Padrino y Madrina *</label>
                    <input
                      type="text"
                      name="nombre_padrino_nombre_madrina"
                      value={persona.nombre_padrino_nombre_madrina}
                      onChange={handlePersonaChange}
                      required
                      placeholder="Ej: Carlos Gómez / Ana Fernández"
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>
                </div>
              ) : form.tipo_sacramento === 3 ? (
                <div className="space-y-6">
                  {/* Datos del Esposo */}
                  <div className="border border-gray-300 dark:border-gray-700 rounded-lg p-4">
                    <h4 className="text-md font-semibold text-gray-800 dark:text-gray-200 mb-4">Datos del Esposo</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres *</label>
                        <input
                          type="text"
                          name="nombres_esposo"
                          value={persona.nombres_esposo || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                          placeholder="Ej: Juan Carlos"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Paterno *</label>
                        <input
                          type="text"
                          name="apellido_paterno_esposo"
                          value={persona.apellido_paterno_esposo || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                          placeholder="Ej: Pérez"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Materno *</label>
                        <input
                          type="text"
                          name="apellido_materno_esposo"
                          value={persona.apellido_materno_esposo || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                          placeholder="Ej: González"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Fecha de Nacimiento *</label>
                        <input
                          type="date"
                          name="fecha_nacimiento_esposo"
                          value={persona.fecha_nacimiento_esposo || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Fecha de Bautismo *</label>
                        <input
                          type="date"
                          name="fecha_bautismo_esposo"
                          value={persona.fecha_bautismo_esposo || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres de los Padres del Esposo *</label>
                        <input
                          type="text"
                          name="padres_esposo"
                          value={persona.padres_esposo || ''}
                          onChange={handlePersonaChange}
                          required
                          placeholder="Ej: Juan Pérez / María González"
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Datos de la Esposa */}
                  <div className="border border-gray-300 dark:border-gray-700 rounded-lg p-4">
                    <h4 className="text-md font-semibold text-gray-800 dark:text-gray-200 mb-4">Datos de la Esposa</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres *</label>
                        <input
                          type="text"
                          name="nombres_esposa"
                          value={persona.nombres_esposa || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                          placeholder="Ej: Ana María"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Paterno *</label>
                        <input
                          type="text"
                          name="apellido_paterno_esposa"
                          value={persona.apellido_paterno_esposa || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                          placeholder="Ej: Flores"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Apellido Materno *</label>
                        <input
                          type="text"
                          name="apellido_materno_esposa"
                          value={persona.apellido_materno_esposa || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                          placeholder="Ej: Quispe"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Fecha de Nacimiento *</label>
                        <input
                          type="date"
                          name="fecha_nacimiento_esposa"
                          value={persona.fecha_nacimiento_esposa || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Fecha de Bautismo *</label>
                        <input
                          type="date"
                          name="fecha_bautismo_esposa"
                          value={persona.fecha_bautismo_esposa || ''}
                          onChange={handlePersonaChange}
                          required
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombres de los Padres de la Esposa *</label>
                        <input
                          type="text"
                          name="padres_esposa"
                          value={persona.padres_esposa || ''}
                          onChange={handlePersonaChange}
                          required
                          placeholder="Ej: Pedro Flores / Carmen Quispe"
                          className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Testigos */}
                  <div className="md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Testigos *</label>
                    <input
                      type="text"
                      name="testigos"
                      value={persona.testigos || ''}
                      onChange={handlePersonaChange}
                      required
                      placeholder="Ej: Roberto Sánchez / Laura Martínez"
                      className="mt-2 form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50"
                    />
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="person-name">Nombres y Apellidos</label>
                    <input name="person_name" value={form.person_name} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="person-name" placeholder="Ingrese el nombre completo" type="text" />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="person-birthdate">Fecha de Nacimiento</label>
                    <input name="person_birthdate" value={form.person_birthdate} onChange={handleChange} className="form-input rounded-lg border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-primary/50 focus:border-primary/50" id="person-birthdate" type="date" />
                  </div>
                </div>
              )}
            </div>
            
            {/* Validación de duplicados para Confirmación */}
            {form.tipo_sacramento === 2 && validacionDuplicado && (
              <div className={`px-4 py-3 rounded-lg ${
                validacionDuplicado.error 
                  ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200' 
                  : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
              }`}>
                {validacionDuplicado.mensaje}
              </div>
            )}

            <div className="flex justify-end gap-4 pt-4 border-t border-gray-200 dark:border-gray-800">
              <button type="button" className="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-11 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 gap-2 text-sm font-bold min-w-0 px-6 hover:bg-gray-300 dark:hover:bg-gray-600">
                Cancelar
              </button>
              <button 
                type="submit" 
                disabled={loading || (form.tipo_sacramento === 2 && validacionDuplicado?.error)} 
                className="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-11 bg-primary text-white gap-2 text-sm font-bold min-w-0 px-6 hover:bg-primary/90"
              >
                {loading ? 'Guardando...' : 'Guardar Registro'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </Layout>
  )
}


import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import DuplicatesMergeModal from '../components/DuplicatesMergeModal'

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
        </form>
      </div>
      <div className="mt-8 bg-white dark:bg-background-dark/50 rounded-xl shadow-sm">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sacramentos Vinculados</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                  <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700/50 dark:text-gray-400">
                    <tr>
                      <th className="px-6 py-3" scope="col">Sacramento</th>
                      <th className="px-6 py-3" scope="col">Fecha</th>
                      <th className="px-6 py-3" scope="col">Lugar</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="bg-white dark:bg-background-dark/50 border-b dark:border-gray-700">
                      <th className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" scope="row">Bautizo</th>
                      <td className="px-6 py-4">2000-05-15</td>
                      <td className="px-6 py-4">Parroquia San Juan</td>
                    </tr>
                    <tr className="bg-white dark:bg-background-dark/50 border-b dark:border-gray-700">
                      <th className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" scope="row">Confirmación</th>
                      <td className="px-6 py-4">2015-08-20</td>
                      <td className="px-6 py-4">Catedral Metropolitana</td>
                    </tr>
                    <tr className="bg-white dark:bg-background-dark/50">
                      <th className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" scope="row">Matrimonio</th>
                      <td className="px-6 py-4">2025-03-10</td>
                      <td className="px-6 py-4">Iglesia del Carmen</td>
                    </tr>
                  </tbody>
          </table>
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

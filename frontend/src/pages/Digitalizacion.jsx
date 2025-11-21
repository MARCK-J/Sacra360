import { useState, useEffect } from 'react'
import Layout from '../components/Layout'

export default function Digitalizacion() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [processingQueue, setProcessingQueue] = useState([])
  const [formData, setFormData] = useState({
    sacramento: 0,
    libro: 0,
    parroquia: '',
    provincia: '',
    ano: '',
    binarizacion: false,
    deskew: false,
    denoise: false
  })

  // Estados para datos del servidor
  const [libros, setLibros] = useState([])
  const [loadingLibros, setLoadingLibros] = useState(true)

  useEffect(() => {
    // Cargar libros desde la API
    fetchLibros()
  }, [])

  const fetchLibros = async () => {
    try {
      setLoadingLibros(true)
      // TODO: Reemplazar con endpoint real
      const response = await fetch('http://localhost:8002/api/v1/libros')
      if (response.ok) {
        const data = await response.json()
        setLibros(data)
      }
    } catch (error) {
      console.error('Error cargando libros:', error)
      // Datos de ejemplo mientras no esté el backend completo
      setLibros([
        { id: 1, nombre: 'Libro de Confirmaciones 2023' },
        { id: 2, nombre: 'Libro de Bautizos 2023' },
        { id: 3, nombre: 'Libro de Matrimonios 2023' }
      ])
    } finally {
      setLoadingLibros(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : 
               (name === 'sacramento' || name === 'libro') ? parseInt(value) || 0 : value
    }))
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }

  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files)
    handleFiles(selectedFiles)
  }

  const handleFiles = (newFiles) => {
    // Validar archivos
    const validFiles = newFiles.filter(file => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
      const maxSize = 50 * 1024 * 1024 // 50MB
      
      if (!validTypes.includes(file.type)) {
        alert(`Archivo ${file.name} no es un tipo válido. Solo JPG, PNG y PDF.`)
        return false
      }
      
      if (file.size > maxSize) {
        alert(`Archivo ${file.name} es demasiado grande. Máximo 50MB.`)
        return false
      }
      
      return true
    })

    setFiles(prev => [...prev, ...validFiles])
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    if (files.length === 0) {
      alert('Selecciona al menos un archivo')
      return
    }

    if (!formData.libro || formData.libro === 0) {
      alert('Selecciona un libro')
      return
    }

    if (!formData.sacramento || formData.sacramento === 0) {
      alert('Selecciona un tipo de sacramento')
      return
    }

    setUploading(true)

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        
        // Agregar a cola de procesamiento
        const queueItem = {
          id: Date.now() + i,
          filename: file.name,
          status: 'uploading',
          progress: 0
        }
        
        setProcessingQueue(prev => [...prev, queueItem])

        // Crear FormData
        const uploadData = new FormData()
        uploadData.append('archivo', file)
        uploadData.append('libro_id', formData.libro)
        uploadData.append('tipo_sacramento', formData.sacramento)
        uploadData.append('institucion_id', '1')
        uploadData.append('procesar_automaticamente', 'true')

        try {
          // Subir archivo
          const response = await fetch('http://localhost:8002/api/v1/digitalizacion/upload', {
            method: 'POST',
            body: uploadData
          })

          if (response.ok) {
            const result = await response.json()
            
            // Actualizar estado en cola
            setProcessingQueue(prev => prev.map(item => 
              item.id === queueItem.id 
                ? { 
                    ...item, 
                    status: result.ocr_procesado ? 'completed' : 'processing',
                    progress: result.ocr_procesado ? 100 : 50,
                    documentId: result.documento_id,
                    ocrResult: result.ocr_resultado
                  }
                : item
            ))

            console.log('Archivo subido exitosamente:', result)
          } else {
            const errorText = await response.text()
            console.error('Error uploading file:', file.name, 'Status:', response.status, 'Error:', errorText)
            throw new Error(`Error ${response.status}: ${errorText}`)
          }
        } catch (error) {
          console.error('Error subiendo archivo:', error)
          
          // Actualizar estado en cola con error
          setProcessingQueue(prev => prev.map(item => 
            item.id === queueItem.id 
              ? { ...item, status: 'error', progress: 0, error: error.message }
              : item
          ))
        }
      }

      // Limpiar archivos después de subir
      setFiles([])
      
    } catch (error) {
      console.error('Error general:', error)
      alert('Error procesando archivos: ' + error.message)
    } finally {
      setUploading(false)
    }
  }

  const getSacramentoId = (sacramento) => {
    // Ya no necesitamos mapeo ya que usamos IDs directos
    return sacramento
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'uploading': return 'bg-blue-100 text-blue-800 dark:bg-primary/20 dark:text-blue-300'
      case 'processing': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'uploading': return 'Subiendo'
      case 'processing': return 'Procesando OCR'
      case 'completed': return 'Completado'
      case 'error': return 'Error'
      default: return 'Desconocido'
    }
  }
  return (
    <Layout title="Digitalización de Documentos">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Metadatos</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="sacramento" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sacramento *</label>
                <select 
                  id="sacramento" 
                  name="sacramento"
                  value={formData.sacramento}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value={0}>Seleccione el sacramento</option>
                  <option value={1}>Bautizo</option>
                  <option value={2}>Confirmación</option>
                  <option value={4}>Matrimonio</option>
                  <option value={5}>Defunción</option>
                </select>
              </div>
              <div>
                <label htmlFor="libro" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Libro *</label>
                <select 
                  id="libro" 
                  name="libro"
                  value={formData.libro}
                  onChange={handleInputChange}
                  required
                  disabled={loadingLibros}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
                >
                  <option value={0}>
                    {loadingLibros ? 'Cargando libros...' : 'Seleccione el libro'}
                  </option>
                  {libros.map(libro => (
                    <option key={libro.id} value={libro.id}>
                      {libro.nombre}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="parroquia" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Parroquia</label>
                <select 
                  id="parroquia" 
                  name="parroquia"
                  value={formData.parroquia}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">Seleccione la parroquia</option>
                  <option value="1">San Miguel Arcángel</option>
                  <option value="2">Sagrado Corazón</option>
                </select>
              </div>
              <div>
                <label htmlFor="provincia" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Provincia</label>
                <select 
                  id="provincia" 
                  name="provincia"
                  value={formData.provincia}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">Seleccione la provincia</option>
                  <option value="santa-fe">Santa Fe</option>
                  <option value="cordoba">Córdoba</option>
                </select>
              </div>
              <div>
                <label htmlFor="ano" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Año</label>
                <select 
                  id="ano" 
                  name="ano"
                  value={formData.ano}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">Seleccione el año</option>
                  {Array.from({length: 10}, (_, i) => new Date().getFullYear() - i).map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Preprocesamiento</h3>
            <div className="space-y-3">
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  name="binarizacion"
                  checked={formData.binarizacion}
                  onChange={handleInputChange}
                  className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary" 
                />
                <span className="ml-3 text-gray-700 dark:text-gray-300">Binarización</span>
              </label>
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  name="deskew"
                  checked={formData.deskew}
                  onChange={handleInputChange}
                  className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary" 
                />
                <span className="ml-3 text-gray-700 dark:text-gray-300">Deskew</span>
              </label>
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  name="denoise"
                  checked={formData.denoise}
                  onChange={handleInputChange}
                  className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary" 
                />
                <span className="ml-3 text-gray-700 dark:text-gray-300">Denoise</span>
              </label>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Carga de Documentos</h3>
            
            {/* Zona de arrastrar y soltar */}
            <div 
              className="flex items-center justify-center w-full"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <label 
                htmlFor="dropzone-file" 
                className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <span className="material-symbols-outlined text-4xl mb-4 text-gray-500 dark:text-gray-400">cloud_upload</span>
                  <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-semibold">Arrastra y suelta</span> o haz clic para subir
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">PDF, JPG, PNG (MAX. 50MB)</p>
                </div>
                <input 
                  id="dropzone-file" 
                  type="file" 
                  multiple 
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileInput}
                  className="hidden" 
                />
              </label>
            </div>

            {/* Lista de archivos seleccionados */}
            {files.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Archivos seleccionados ({files.length})
                </h4>
                <div className="space-y-2">
                  {files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {file.name}
                        </span>
                        <span className="text-xs text-gray-500">
                          ({(file.size / 1024 / 1024).toFixed(1)} MB)
                        </span>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <span className="material-symbols-outlined text-sm">close</span>
                      </button>
                    </div>
                  ))}
                </div>
                
                <button
                  onClick={uploadFiles}
                  disabled={uploading}
                  className="mt-4 w-full px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Subiendo...' : 'Procesar Documentos'}
                </button>
              </div>
            )}
          </div>

          {/* Cola de procesamiento */}
          <div className="bg-white dark:bg-background-dark rounded-lg shadow overflow-hidden">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white p-6">Cola de Procesamiento</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                  <tr>
                    <th scope="col" className="px-6 py-3">Documento</th>
                    <th scope="col" className="px-6 py-3">Estado</th>
                    <th scope="col" className="px-6 py-3">Progreso</th>
                    <th scope="col" className="px-6 py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {processingQueue.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                        No hay documentos en proceso
                      </td>
                    </tr>
                  ) : (
                    processingQueue.map((item) => (
                      <tr key={item.id} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                        <th scope="row" className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                          {item.filename}
                        </th>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                            {getStatusText(item.status)}
                          </span>
                          {item.error && (
                            <div className="text-xs text-red-500 mt-1">{item.error}</div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                              <div 
                                className={`h-2.5 rounded-full transition-all duration-300 ${
                                  item.status === 'completed' ? 'bg-green-500' : 
                                  item.status === 'error' ? 'bg-red-500' : 'bg-primary'
                                }`}
                                style={{ width: `${item.progress}%` }}
                              ></div>
                            </div>
                            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                              {item.progress}%
                            </span>
                          </div>
                          {item.ocrResult && (
                            <div className="text-xs text-green-600 mt-1">
                              OCR: {item.ocrResult.total_tuplas || 0} tuplas extraídas
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {item.status === 'completed' && item.documentId && (
                            <button className="text-blue-600 hover:text-blue-800 text-xs">
                              Ver resultados
                            </button>
                          )}
                          {item.status === 'error' && (
                            <button className="text-red-600 hover:text-red-800 text-xs">
                              Reintentar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

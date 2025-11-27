import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'

export default function Digitalizacion() {
  const navigate = useNavigate()
  // files: array of { file: File, preview: string | null }
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [dragActive, setDragActive] = useState(false)
  const [formData, setFormData] = useState({
    sacramento: 0,
    libro: 0
  })

  const [libros, setLibros] = useState([])
  const [loadingLibros, setLoadingLibros] = useState(true)
  const createdPreviewsRef = useRef(new Set())

  useEffect(() => {
    fetchLibros()
  }, [])

  const fetchLibros = async () => {
    try {
      setLoadingLibros(true)
      const response = await fetch('http://localhost:8002/api/v1/libros')
      if (response.ok) {
        const data = await response.json()
        setLibros(data)
      }
    } catch (error) {
      console.error('Error cargando libros:', error)
      setLibros([
        { id: 1, nombre: 'Bautismos 2024 Updated' },
        { id: 2, nombre: 'Bautismos 2024' },
        { id: 4, nombre: 'Matrimonios 2024' }
      ])
    } finally {
      setLoadingLibros(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'sacramento' || name === 'libro' ? parseInt(value) || 0 : value
    }))
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files)
    handleFiles(selectedFiles)
  }

  const handleFiles = (newFiles) => {
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    const maxSize = 50 * 1024 * 1024

    const validFiles = Array.from(newFiles).map(file => ({ file, preview: null })).filter(item => {
      const file = item.file
      if (!validTypes.includes(file.type)) {
        alert(`Archivo ${file.name} no es válido. Solo PDF, JPG, PNG.`)
        return false
      }

      if (file.size > maxSize) {
        alert(`Archivo ${file.name} es muy grande. Máximo 50MB.`)
        return false
      }

      // create preview for images
      if (file.type.startsWith('image/')) {
        try {
          const url = URL.createObjectURL(file)
          item.preview = url
          createdPreviewsRef.current.add(url)
        } catch (e) {
          item.preview = null
        }
      }

      return true
    })

    setFiles(prev => [...prev, ...validFiles])
  }

  const removeFile = (index) => {
    setFiles(prev => {
      const toRemove = prev[index]
      if (toRemove && toRemove.preview) {
        try { URL.revokeObjectURL(toRemove.preview) } catch (e) {}
        createdPreviewsRef.current.delete(toRemove.preview)
      }
      return prev.filter((_, i) => i !== index)
    })
  }

  const uploadFiles = async () => {
    if (files.length === 0 || formData.sacramento === 0 || formData.libro === 0) {
      alert('Por favor, selecciona archivos, sacramento y libro')
      return
    }

    setUploading(true)
    const newUploadedFiles = []

    try {
      for (const fileObj of files) {
        const file = fileObj.file
        const uploadData = new FormData()
        uploadData.append('archivo', file)
        uploadData.append('tipo_sacramento', formData.sacramento)
        uploadData.append('libro_id', formData.libro)
        uploadData.append('institucion_id', '1')
        uploadData.append('procesar_automaticamente', 'true')

        try {
          const response = await fetch('http://localhost:8002/api/v1/digitalizacion/upload', {
            method: 'POST',
            body: uploadData
          })

          if (response.ok) {
            const result = await response.json()
            newUploadedFiles.push({
              ...result,
              fileName: file.name,
              preview: result.imagen_url || fileObj.preview || null,
              status: 'uploaded',
              timestamp: new Date().toLocaleString()
            })
          } else {
            const errorText = await response.text()
            newUploadedFiles.push({
              fileName: file.name,
              status: 'error',
              timestamp: new Date().toLocaleString(),
              error: `Error ${response.status}: ${errorText}`
            })
          }
        } catch (error) {
          newUploadedFiles.push({
            fileName: file.name,
            status: 'error',
            timestamp: new Date().toLocaleString(),
            error: error.message
          })
        }
      }

      setUploadedFiles(prev => [...prev, ...newUploadedFiles])
      // revoke and clear previews from selected files
      setFiles(prev => {
        prev.forEach(p => { if (p.preview) { try { URL.revokeObjectURL(p.preview) } catch(e){} } })
        createdPreviewsRef.current.clear()
        return []
      })
      setFormData({ sacramento: 0, libro: 0 })

      // Redirección automática si todo fue exitoso
      if (newUploadedFiles.length > 0 && newUploadedFiles.every(f => f.status === 'uploaded')) {
        setTimeout(() => {
          navigate('/revision-ocr')
        }, 1500)
      }

    } catch (error) {
      alert('Error procesando archivos: ' + error.message)
    } finally {
      setUploading(false)
    }
  }

  // cleanup previews on unmount
  useEffect(() => {
    return () => {
      createdPreviewsRef.current.forEach(url => {
        try { URL.revokeObjectURL(url) } catch (e) {}
      })
      createdPreviewsRef.current.clear()
    }
  }, [])

  return (
    <Layout title="Digitalización de Documentos">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Formulario de Metadatos */}
        <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Información del Documento</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sacramento *
              </label>
              <select
                name="sacramento"
                value={formData.sacramento}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value={0}>Seleccionar sacramento</option>
                <option value={1}>Bautismo</option>
                <option value={2}>Confirmación</option>
                <option value={4}>Matrimonio</option>
                <option value={5}>Defunción</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Libro *
              </label>
              <select
                name="libro"
                value={formData.libro}
                onChange={handleInputChange}
                disabled={loadingLibros}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
              >
                <option value={0}>
                  {loadingLibros ? 'Cargando...' : 'Seleccionar libro'}
                </option>
                {libros.map((libro) => (
                  <option key={libro.id_libro} value={libro.id_libro}>
                    {libro.nombre}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Zona de Carga */}
        <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Subir Documentos</h3>

          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive ? 'border-primary bg-primary/5' : 'border-gray-300 dark:border-gray-700'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="text-gray-600 dark:text-gray-400">
              <p className="text-lg font-medium mb-2">
                Arrastra archivos aquí o
              </p>
              <input
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileInput}
                className="hidden"
                id="file-upload"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload"
                className="inline-block px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 cursor-pointer"
              >
                Seleccionar archivos
              </label>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Soporta PDF, JPG, PNG (máx. 50MB cada uno)
              </p>
            </div>
          </div>

          {/* Lista de archivos seleccionados */}
          {files.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Archivos seleccionados ({files.length})
              </h4>
              <div className="space-y-2">
                {files.map((item, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded-md">
                    <div className="flex items-center gap-3">
                      {item.preview ? (
                        <img src={item.preview} alt={item.file.name} className="w-16 h-12 object-cover rounded-md border" />
                      ) : (
                        <div className="w-16 h-12 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-md text-sm text-gray-600">PDF</div>
                      )}
                      <div>
                        <span className="font-medium text-gray-900 dark:text-white">{item.file.name}</span>
                        <span className="text-gray-500 ml-2 text-sm">
                          ({(item.file.size / 1024 / 1024).toFixed(2)} MB)
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700"
                      disabled={uploading}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>

              <button
                onClick={uploadFiles}
                disabled={uploading}
                className={`w-full mt-4 py-3 px-4 rounded-md text-white font-medium ${
                  uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'
                }`}
              >
                {uploading ? 'Subiendo archivos...' : `Subir ${files.length} archivo(s)`}
              </button>
            </div>
          )}
        </div>

        {/* Lista de archivos procesados */}
        {uploadedFiles.length > 0 && (
          <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">Documentos Procesados</h3>
              <button
                onClick={() => navigate('/revision-ocr')}
                className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 flex items-center gap-2"
              >
                <span>Ir a Revisión OCR</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
            <div className="space-y-3">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="border rounded-lg p-4 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">{file.fileName}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{file.timestamp}</p>
                      {file.documento_id && (
                        <p className="text-xs text-gray-500">ID: {file.documento_id}</p>
                      )}
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        file.status === 'uploaded'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                      }`}
                    >
                      {file.status === 'uploaded' ? 'Subido' : 'Error'}
                    </span>
                  </div>
                  {file.error && (
                    <p className="text-xs text-red-600 mt-2">{file.error}</p>
                  )}
                  {file.mensaje && (
                    <p className="text-sm text-blue-600 dark:text-blue-400 mt-2">{file.mensaje}</p>
                  )}
                  {(file.preview || file.imagen_url || file.url) && (
                    <div className="mt-3">
                      <img
                        src={file.preview || file.imagen_url || file.url}
                        alt={file.fileName}
                        className="max-w-xs max-h-48 object-contain rounded-md border"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

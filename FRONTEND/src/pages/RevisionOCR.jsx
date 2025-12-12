import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import ValidacionOCRModal from '../components/ValidacionOCRModal'

export default function RevisionOCR() {
  const navigate = useNavigate()
  const [documentos, setDocumentos] = useState([])
  const [loading, setLoading] = useState(true)
  const [validacionModal, setValidacionModal] = useState({
    isOpen: false,
    documentoId: null,
    nombreArchivo: '',
    tipoSacramento: ''
  })

  useEffect(() => {
    cargarDocumentos()
  }, [])

  const cargarDocumentos = async () => {
    try {
      setLoading(true)
      // Cargar documentos desde el backend
      const response = await fetch('http://localhost:8002/api/v1/digitalizacion/documentos-pendientes')
      if (response.ok) {
        const data = await response.json()
        setDocumentos(data)
      } else {
        // Fallback a datos de ejemplo si falla la API
        console.warn('No se pudieron cargar documentos desde la API')
        setDocumentos([])
      }
    } catch (error) {
      console.error('Error cargando documentos:', error)
      // Datos de ejemplo en caso de error
      setDocumentos([])
    } finally {
      setLoading(false)
    }
  }

  const abrirModalValidacion = (doc) => {
    const tiposSacramento = {
      1: 'Bautismo',
      2: 'Confirmación',
      4: 'Matrimonio',
      5: 'Defunción'
    }

    setValidacionModal({
      isOpen: true,
      documentoId: doc.id,
      nombreArchivo: doc.nombre_archivo || `documento_${doc.id}.png`,
      tipoSacramento: tiposSacramento[doc.tipo_sacramento] || 'Desconocido'
    })
  }

  const cerrarModal = () => {
    setValidacionModal({
      isOpen: false,
      documentoId: null,
      nombreArchivo: '',
      tipoSacramento: ''
    })
  }

  const manejarValidacionCompleta = (documentoId) => {
    console.log('Validación completada para documento:', documentoId)
    cerrarModal()
    // Actualizar lista de documentos
    setDocumentos(prev => prev.filter(doc => doc.id !== documentoId))
    // Redirigir a registros
    setTimeout(() => {
      navigate('/registros')
    }, 500)
  }

  return (
    <Layout title="Revisión OCR">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white dark:bg-background-dark p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Documentos Pendientes de Validación
            </h2>
            <button
              onClick={() => navigate('/digitalizacion')}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90"
            >
              ← Volver a Digitalización
            </button>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-3">Cargando documentos...</span>
            </div>
          ) : documentos.length === 0 ? (
            <div className="text-center py-12">
              <span className="material-symbols-outlined text-6xl text-gray-400 mb-4">
                check_circle
              </span>
              <p className="text-gray-600 dark:text-gray-400">
                No hay documentos pendientes de validación
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-300">
                  <tr>
                    <th scope="col" className="px-6 py-3">ID</th>
                    <th scope="col" className="px-6 py-3">Nombre Archivo</th>
                    <th scope="col" className="px-6 py-3">Modelo</th>
                    <th scope="col" className="px-6 py-3">Sacramento</th>
                    <th scope="col" className="px-6 py-3">Fecha</th>
                    <th scope="col" className="px-6 py-3">Tuplas</th>
                    <th scope="col" className="px-6 py-3">Estado</th>
                    <th scope="col" className="px-6 py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {documentos.map((doc) => (
                    <tr key={doc.id} className="bg-white dark:bg-background-dark border-b dark:border-gray-700">
                      <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                        {doc.id}
                      </td>
                      <td className="px-6 py-4">{doc.nombre_archivo}</td>
                      <td className="px-6 py-4">
                        {/* Badge diferenciado para OCR vs HTR */}
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          doc.modelo_procesamiento === 'htr' 
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300' 
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                        }`}>
                          {doc.modelo_procesamiento === 'htr' ? '✍️ HTR' : '📝 OCR'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 rounded-full text-xs bg-primary/10 text-primary">
                          {doc.tipo_sacramento === 1 && 'Bautismo'}
                          {doc.tipo_sacramento === 2 && 'Confirmación'}
                          {doc.tipo_sacramento === 4 && 'Matrimonio'}
                          {doc.tipo_sacramento === 5 && 'Defunción'}
                        </span>
                      </td>
                      <td className="px-6 py-4">{doc.fecha_subida ? new Date(doc.fecha_subida).toLocaleDateString() : 'N/A'}</td>
                      <td className="px-6 py-4">{doc.total_tuplas}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
                          Pendiente
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => abrirModalValidacion(doc)}
                          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                        >
                          Validar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Validación */}
      <ValidacionOCRModal
        isOpen={validacionModal.isOpen}
        onClose={cerrarModal}
        documentoId={validacionModal.documentoId}
        nombreArchivo={validacionModal.nombreArchivo}
        tipoSacramento={validacionModal.tipoSacramento}
        onValidacionCompleta={manejarValidacionCompleta}
      />
    </Layout>
  )
}

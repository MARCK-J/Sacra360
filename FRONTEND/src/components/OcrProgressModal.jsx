import { useEffect, useState } from 'react'
import { useOcrProgress } from '../context/OcrProgressContext'

/**
 * Modal de progreso de procesamiento OCR
 * Muestra una barra de progreso animada con el estado actual del procesamiento
 * Ahora usa el Context centralizado para evitar polling duplicado
 */
export default function OcrProgressModal({ documentoId, onComplete, onError }) {
  const { documentosEnProceso } = useOcrProgress()
  const [error, setError] = useState(null)
  
  // Obtener progreso del documento desde el Context
  const progreso = documentosEnProceso[documentoId] || {
    estado: 'iniciando',
    progreso: 0,
    mensaje: 'Iniciando procesamiento...',
    etapa: 'init'
  }

  useEffect(() => {
    // Monitorear cambios de estado para notificar completado/error
    if (progreso.estado === 'completado' && onComplete) {
      console.log('✅ OCR completado para documento', documentoId)
      setTimeout(() => onComplete(documentoId), 1000)
    } else if (progreso.estado === 'error') {
      console.log('❌ OCR con error:', progreso.mensaje)
      setError(progreso.mensaje || 'Error en procesamiento')
      if (onError) onError(progreso.mensaje)
    }
  }, [progreso.estado, documentoId, onComplete, onError, progreso.mensaje])

  // Determinar color según estado
  const getColorClass = () => {
    switch (progreso.estado) {
      case 'completado':
        return 'bg-green-500'
      case 'error':
        return 'bg-red-500'
      case 'procesando_ocr':
        return 'bg-blue-500'
      default:
        return 'bg-indigo-500'
    }
  }

  // Determinar icono según estado
  const getIcon = () => {
    switch (progreso.estado) {
      case 'completado':
        return '✅'
      case 'error':
        return '❌'
      case 'procesando_ocr':
        return '🔍'
      case 'descargando':
        return '⬇️'
      case 'guardando':
        return '💾'
      default:
        return '⏳'
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="text-6xl mb-4 animate-pulse">
            {getIcon()}
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Procesando Documento
          </h2>
          <p className="text-sm text-gray-600">
            Documento ID: {documentoId}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              {progreso.mensaje}
            </span>
            <span className="text-sm font-bold text-gray-900">
              {progreso.progreso}%
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className={`h-full ${getColorClass()} transition-all duration-500 ease-out rounded-full`}
              style={{ width: `${progreso.progreso}%` }}
            >
              {/* Animación de brillo */}
              {progreso.estado !== 'completado' && progreso.estado !== 'error' && (
                <div className="h-full w-full bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer"></div>
              )}
            </div>
          </div>
        </div>

        {/* Status Details */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <div className="text-xs text-gray-600 space-y-1">
            <div className="flex justify-between">
              <span>Estado:</span>
              <span className="font-semibold capitalize">{progreso.estado.replace('_', ' ')}</span>
            </div>
            <div className="flex justify-between">
              <span>Etapa:</span>
              <span className="font-semibold">{progreso.etapa}</span>
            </div>
          </div>
        </div>

        {/* Info adicional para etapa de OCR */}
        {progreso.estado === 'procesando_ocr' && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
            <p className="text-sm text-blue-800">
              <strong>⏱️ Proceso en curso</strong>
              <br />
              El análisis OCR puede tardar varios minutos dependiendo del tamaño y complejidad del documento.
            </p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
            <p className="text-sm text-red-800">
              <strong>❌ Error:</strong><br />
              {error}
            </p>
          </div>
        )}

        {/* Success Message */}
        {progreso.estado === 'completado' && (
          <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-4">
            <p className="text-sm text-green-800">
              <strong>✅ Completado</strong>
              <br />
              El documento ha sido procesado exitosamente.
            </p>
          </div>
        )}

        {/* Nota informativa */}
        {progreso.progreso < 100 && !error && (
          <p className="text-xs text-center text-gray-500 mt-4">
            Por favor, no cierre esta ventana mientras se procesa el documento.
          </p>
        )}
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes ocr-shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: ocr-shimmer 2s infinite;
        }
      `}} />
    </div>
  )
}

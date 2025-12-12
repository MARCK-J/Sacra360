import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useOcrProgress } from '../context/OcrProgressContext'

/**
 * Modal de progreso de procesamiento OCR/HTR
 * Muestra una barra de progreso animada con el estado actual del procesamiento
 * Ahora usa el Context centralizado para evitar polling duplicado
 * Soporta tanto OCR (texto mecanografiado) como HTR (texto manuscrito)
 */
export default function OcrProgressModal({ documentoId, onComplete, onError }) {
  const { documentosEnProceso, detenerSeguimiento } = useOcrProgress()
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  
  // Obtener progreso del documento desde el Context
  const progreso = documentosEnProceso[documentoId] || {
    estado: 'iniciando',
    progreso: 0,
    mensaje: 'Iniciando procesamiento...',
    etapa: 'init',
    modelo: 'OCR'  // Por defecto OCR
  }

  // Determinar el nombre del modelo desde el mensaje o estado
  const modeloNombre = progreso.mensaje?.includes('HTR') || progreso.etapa?.includes('htr') 
    ? 'HTR' 
    : 'OCR'

  useEffect(() => {
    // Monitorear cambios de estado para notificar completado/error
    if (progreso.estado === 'completado' && onComplete) {
      console.log(`✅ ${modeloNombre} completado para documento`, documentoId)
      
      // Detener seguimiento ANTES de redirigir
      setTimeout(() => {
        detenerSeguimiento(documentoId)
        console.log(`🛑 Seguimiento detenido para documento completado: ${documentoId}`)
      }, 1000) // Dar 1 segundo para que el usuario vea el estado completado
      
      // Redirigir automáticamente a pantalla de revisión
      navigate('/revision-ocr')
    } else if (progreso.estado === 'error') {
      console.log(`❌ ${modeloNombre} con error:`, progreso.mensaje)
      setError(progreso.mensaje || 'Error en procesamiento')
      
      // Detener seguimiento en caso de error
      setTimeout(() => {
        detenerSeguimiento(documentoId)
      }, 2000)
      
      if (onError) onError(progreso.mensaje)
    }
  }, [progreso.estado, documentoId, onComplete, onError, progreso.mensaje, modeloNombre, navigate, detenerSeguimiento])

  // Cleanup cuando el componente se desmonta
  useEffect(() => {
    return () => {
      // Si el modal se cierra por cualquier razón, detener el seguimiento
      // SOLO si el documento NO está en proceso activo
      if (progreso.estado === 'completado' || progreso.estado === 'error') {
        detenerSeguimiento(documentoId)
      }
    }
  }, [documentoId, progreso.estado, detenerSeguimiento])

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
      case 'procesando_htr':
        return modeloNombre === 'HTR' ? '✍️' : '🔍'
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
          <h2 className="text-2x - {modeloNombre}l font-bold text-gray-800 mb-2">
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

        {(progreso.estado === 'procesando_ocr' || progreso.estado === 'procesando_htr') && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
            <p className="text-sm text-blue-800">
              <strong>⏱️ Proceso en curso</strong>
              <br />
              El análisis {modeloNombre} puede tardar varios minutos dependiendo del tamaño y complejidad del documento.
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

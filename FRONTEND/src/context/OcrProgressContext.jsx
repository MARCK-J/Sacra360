import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react'

/**
 * Context para manejar el progreso de OCR de forma centralizada
 * Evita el problema de polling infinito al mantener un único intervalo global
 */
const OcrProgressContext = createContext()

export function OcrProgressProvider({ children }) {
  const [documentosEnProceso, setDocumentosEnProceso] = useState({})
  const intervalRef = useRef(null)
  const isPollingRef = useRef(false)

  /**
   * Inicia el seguimiento de un documento
   */
  const iniciarSeguimiento = useCallback((documentoId) => {
    console.log('🔄 Iniciando seguimiento OCR para documento:', documentoId)
    
    setDocumentosEnProceso(prev => ({
      ...prev,
      [documentoId]: {
        estado: 'iniciando',
        progreso: 0,
        mensaje: 'Iniciando procesamiento...',
        timestamp: Date.now()
      }
    }))
  }, [])

  /**
   * Detiene el seguimiento de un documento
   */
  const detenerSeguimiento = useCallback((documentoId) => {
    console.log('🛑 Deteniendo seguimiento OCR para documento:', documentoId)
    
    setDocumentosEnProceso(prev => {
      const nuevo = { ...prev }
      delete nuevo[documentoId]
      return nuevo
    })
  }, [])

  /**
   * Consulta el progreso de todos los documentos en proceso
   */
  const consultarProgresos = useCallback(async () => {
    const documentosIds = Object.keys(documentosEnProceso)
    
    if (documentosIds.length === 0) {
      return
    }

    // Consultar cada documento (en paralelo para eficiencia)
    // Ahora consulta Documents-service que redirige a OCR o HTR según el modelo
    const promesas = documentosIds.map(async (docId) => {
      try {
        const response = await fetch(`http://localhost:8002/api/v1/digitalizacion/progreso/${docId}`)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const data = await response.json()
        return { docId, data }
      } catch (error) {
        console.error(`⚠️ Error consultando progreso de documento ${docId}:`, error)
        return { docId, data: null }
      }
    })

    const resultados = await Promise.all(promesas)

    // Actualizar estados y MANTENER documentos completados para permitir redirección
    setDocumentosEnProceso(prev => {
      const nuevo = { ...prev }
      
      resultados.forEach(({ docId, data }) => {
        if (data && nuevo[docId]) {
          console.log(`📊 Progreso documento ${docId}:`, {
            estado: data.estado,
            progreso: data.progreso,
            mensaje: data.mensaje
          })
          
          // Actualizar estado siempre (incluso si está completado/error)
          // El modal se encarga de redirigir y luego detener el seguimiento
          nuevo[docId] = {
            ...data,
            timestamp: Date.now()
          }
        }
      })

      return nuevo
    })
  }, [documentosEnProceso])

  /**
   * Efecto para manejar el polling global
   * Se ejecuta SOLO cuando hay documentos en proceso
   */
  useEffect(() => {
    const documentosIds = Object.keys(documentosEnProceso)
    
    // Si no hay documentos, limpiar intervalo
    if (documentosIds.length === 0) {
      if (intervalRef.current) {
        console.log('🛑 Deteniendo polling global - no hay documentos')
        clearInterval(intervalRef.current)
        intervalRef.current = null
        isPollingRef.current = false
      }
      return
    }

    // Si hay documentos y NO hay polling activo, iniciarlo
    if (!isPollingRef.current) {
      console.log('🔄 Iniciando polling global cada 15 segundos')
      isPollingRef.current = true
      
      // Primera consulta inmediata
      consultarProgresos()
      
      // Luego cada 15 segundos para capturar cambios
      intervalRef.current = setInterval(consultarProgresos, 1000)
    }
    // NO hacer cleanup aquí - solo detener cuando documentosIds.length === 0
  }, [documentosEnProceso, consultarProgresos])

  const value = {
    documentosEnProceso,
    iniciarSeguimiento,
    detenerSeguimiento
  }

  return (
    <OcrProgressContext.Provider value={value}>
      {children}
    </OcrProgressContext.Provider>
  )
}

/**
 * Hook para usar el contexto de progreso OCR
 */
export function useOcrProgress() {
  const context = useContext(OcrProgressContext)
  
  if (!context) {
    throw new Error('useOcrProgress debe usarse dentro de OcrProgressProvider')
  }
  
  return context
}

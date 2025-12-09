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
    const promesas = documentosIds.map(async (docId) => {
      try {
        const response = await fetch(`http://localhost:8003/api/v1/ocr/progreso/${docId}`)
        
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

    // Actualizar estados y REMOVER documentos completados/con error
    setDocumentosEnProceso(prev => {
      const nuevo = { ...prev }
      const documentosARemover = []
      
      resultados.forEach(({ docId, data }) => {
        if (data && nuevo[docId]) {
          console.log(`📊 Progreso documento ${docId}:`, {
            estado: data.estado,
            progreso: data.progreso,
            mensaje: data.mensaje
          })
          
          // Si completó o hubo error, marcar para ELIMINAR del tracking
          if (data.estado === 'completado' || data.estado === 'error') {
            console.log(`✅ Documento ${docId} terminó con estado: ${data.estado} - REMOVIENDO del tracking`)
            documentosARemover.push(docId)
          } else {
            // Solo actualizar si NO está completado
            nuevo[docId] = {
              ...data,
              timestamp: Date.now()
            }
          }
        }
      })
      
      // ELIMINAR documentos completados/error del tracking
      documentosARemover.forEach(docId => {
        delete nuevo[docId]
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

    // Si ya hay polling activo, solo actualizar (no crear nuevo interval)
    if (isPollingRef.current) {
      console.log(`📊 Polling activo - ahora rastreando ${documentosIds.length} documento(s)`)
      return
    }

    // Iniciar polling
    console.log(`🔄 Iniciando polling global para ${documentosIds.length} documento(s)`)
    isPollingRef.current = true

    // Consultar inmediatamente
    consultarProgresos()

    // Consultar cada 3 segundos
    intervalRef.current = setInterval(consultarProgresos, 3000)

    // Cleanup
    return () => {
      if (intervalRef.current) {
        console.log('🧹 Limpiando interval de polling')
        clearInterval(intervalRef.current)
        intervalRef.current = null
        isPollingRef.current = false
      }
    }
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

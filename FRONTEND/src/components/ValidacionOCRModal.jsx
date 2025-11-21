import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, RotateCcw, Save, ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * Modal de Validación de OCR
 * Permite validar tupla por tupla los resultados del procesamiento OCR
 */
const ValidacionOCRModal = ({ 
  isOpen, 
  onClose, 
  documentoId, 
  nombreArchivo, 
  tipoSacramento,
  onValidacionCompleta 
}) => {
  // Estados del componente
  const [tuplas, setTuplas] = useState([]);
  const [tuplaActual, setTuplaActual] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [estadisticas, setEstadisticas] = useState({
    total: 0,
    validadas: 0,
    pendientes: 0
  });
  const [correcciones, setCorrecciones] = useState({});
  const [observaciones, setObservaciones] = useState('');
  const [modoEdicion, setModoEdicion] = useState(false);

  // Efecto para cargar tuplas cuando se abre el modal
  useEffect(() => {
    if (isOpen && documentoId) {
      cargarTuplasPendientes();
    }
  }, [isOpen, documentoId]);

  /**
   * Carga las tuplas pendientes de validación
   */
  const cargarTuplasPendientes = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8002/api/v1/validacion/tuplas-pendientes/${documentoId}`
      );

      if (!response.ok) {
        if (response.status === 404) {
          setError('No se encontraron tuplas pendientes para este documento');
          return;
        }
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.length === 0) {
        setError('No hay tuplas pendientes de validación');
        return;
      }

      setTuplas(data);
      setTuplaActual(0);
      
      // Actualizar estadísticas
      const total = data[0]?.total_tuplas_documento || data.length;
      setEstadisticas({
        total,
        validadas: 0,
        pendientes: data.length
      });

      console.log('Tuplas cargadas:', data);

    } catch (err) {
      console.error('Error al cargar tuplas:', err);
      setError('Error al cargar las tuplas de validación: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Maneja los cambios en los campos de corrección
   */
  const manejarCorreccion = (idOcr, valorOriginal, nuevoValor, comentario = '') => {
    setCorrecciones(prev => ({
      ...prev,
      [idOcr]: {
        id_ocr: idOcr,
        valor_original: valorOriginal,
        valor_corregido: nuevoValor,
        comentario
      }
    }));
  };

  /**
   * Valida la tupla actual
   */
  const validarTupla = async (accion) => {
    if (!tuplas[tuplaActual]) return;

    setLoading(true);
    const tupla = tuplas[tuplaActual];

    const datosValidacion = {
      documento_id: documentoId,
      tupla_numero: tupla.tupla_numero,
      usuario_validador_id: 1, // TODO: Obtener del contexto de usuario
      correcciones: Object.values(correcciones),
      observaciones,
      accion // 'aprobar', 'corregir', 'rechazar'
    };

    try {
      const response = await fetch('http://localhost:8002/api/v1/validacion/validar-tupla', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(datosValidacion)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al validar tupla');
      }

      const resultado = await response.json();
      console.log('Tupla validada:', resultado);

      // Actualizar estadísticas
      setEstadisticas(prev => ({
        total: resultado.total_tuplas,
        validadas: resultado.tuplas_validadas,
        pendientes: resultado.tuplas_pendientes
      }));

      // Si hay siguiente tupla, avanzar
      if (resultado.siguiente_tupla !== null) {
        const siguienteIndex = tuplas.findIndex(t => t.tupla_numero === resultado.siguiente_tupla);
        if (siguienteIndex !== -1) {
          setTuplaActual(siguienteIndex);
          setCorrecciones({});
          setObservaciones('');
          setModoEdicion(false);
        }
      } else if (resultado.completado) {
        // Validación completada
        await onValidacionCompleta?.(documentoId);
        onClose();
      }

    } catch (err) {
      console.error('Error al validar tupla:', err);
      setError('Error al validar: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Navega entre tuplas
   */
  const navegarTupla = (direccion) => {
    const nuevoIndex = tuplaActual + direccion;
    if (nuevoIndex >= 0 && nuevoIndex < tuplas.length) {
      setTuplaActual(nuevoIndex);
      setCorrecciones({});
      setObservaciones('');
      setModoEdicion(false);
    }
  };

  /**
   * Renderiza un campo OCR
   */
  const renderizarCampoOCR = (campo) => {
    const tieneCorreccion = correcciones[campo.id_ocr];
    const valorMostrado = tieneCorreccion ? correcciones[campo.id_ocr].valor_corregido : campo.valor_extraido;

    // Determinar color según confianza
    const getConfianzaColor = (confianza) => {
      if (confianza >= 0.9) return 'text-green-600';
      if (confianza >= 0.7) return 'text-yellow-600';
      return 'text-red-600';
    };

    return (
      <div key={campo.id_ocr} className="bg-gray-50 p-4 rounded-lg border">
        <div className="flex justify-between items-start mb-2">
          <label className="font-medium text-gray-700 capitalize">
            {campo.campo.replace('_', ' ')}
          </label>
          <span className={`text-xs px-2 py-1 rounded ${getConfianzaColor(campo.confianza)}`}>
            {Math.round(campo.confianza * 100)}%
          </span>
        </div>

        {modoEdicion ? (
          <div className="space-y-2">
            <input
              type="text"
              value={valorMostrado}
              onChange={(e) => manejarCorreccion(
                campo.id_ocr,
                campo.valor_extraido,
                e.target.value
              )}
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            {tieneCorreccion && (
              <input
                type="text"
                placeholder="Comentario sobre la corrección"
                value={correcciones[campo.id_ocr]?.comentario || ''}
                onChange={(e) => manejarCorreccion(
                  campo.id_ocr,
                  campo.valor_extraido,
                  correcciones[campo.id_ocr].valor_corregido,
                  e.target.value
                )}
                className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
            )}
          </div>
        ) : (
          <div className={`p-2 bg-white rounded border ${tieneCorreccion ? 'border-yellow-400 bg-yellow-50' : ''}`}>
            {tieneCorreccion && (
              <div className="text-xs text-gray-500 line-through mb-1">
                Original: {campo.valor_extraido}
              </div>
            )}
            <div className="font-medium">{valorMostrado}</div>
            {tieneCorreccion && correcciones[campo.id_ocr].comentario && (
              <div className="text-xs text-yellow-700 mt-1">
                📝 {correcciones[campo.id_ocr].comentario}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (!isOpen) return null;

  const tupla = tuplas[tuplaActual];
  const progreso = estadisticas.total > 0 ? (estadisticas.validadas / estadisticas.total) * 100 : 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl max-h-[90vh] w-full overflow-hidden">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold mb-2">Validación OCR</h2>
              <p className="text-blue-100">
                📄 {nombreArchivo} - {tipoSacramento}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Barra de Progreso */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-blue-100 mb-2">
              <span>Progreso: {estadisticas.validadas}/{estadisticas.total}</span>
              <span>{Math.round(progreso)}%</span>
            </div>
            <div className="w-full bg-blue-800 rounded-full h-2">
              <div 
                className="bg-green-400 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progreso}%` }}
              />
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3">Cargando...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                {error}
              </div>
            </div>
          )}

          {tupla && !loading && !error && (
            <div className="space-y-6">
              {/* Navegación de Tuplas */}
              <div className="flex justify-between items-center bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => navegarTupla(-1)}
                    disabled={tuplaActual === 0}
                    className="flex items-center px-3 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed rounded transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4 mr-1" />
                    Anterior
                  </button>
                  
                  <span className="font-medium">
                    Tupla {tupla.tupla_numero} de {estadisticas.total}
                  </span>
                  
                  <button
                    onClick={() => navegarTupla(1)}
                    disabled={tuplaActual === tuplas.length - 1}
                    className="flex items-center px-3 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed rounded transition-colors"
                  >
                    Siguiente
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </button>
                </div>

                <button
                  onClick={() => setModoEdicion(!modoEdicion)}
                  className={`px-4 py-2 rounded transition-colors ${
                    modoEdicion 
                      ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  {modoEdicion ? 'Ver Modo' : 'Editar'}
                </button>
              </div>

              {/* Campos OCR */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {tupla.campos_ocr.map(renderizarCampoOCR)}
              </div>

              {/* Observaciones */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Observaciones de la tupla
                </label>
                <textarea
                  value={observaciones}
                  onChange={(e) => setObservaciones(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows="3"
                  placeholder="Añadir observaciones sobre esta tupla..."
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        {tupla && !loading && !error && (
          <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {Object.keys(correcciones).length > 0 && (
                <span className="text-yellow-600">
                  ⚠️ {Object.keys(correcciones).length} corrección(es) pendiente(s)
                </span>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => validarTupla('rechazar')}
                className="px-4 py-2 bg-red-100 text-red-700 hover:bg-red-200 rounded transition-colors"
                disabled={loading}
              >
                Rechazar
              </button>
              
              <button
                onClick={() => validarTupla(Object.keys(correcciones).length > 0 ? 'corregir' : 'aprobar')}
                className="px-6 py-2 bg-green-600 text-white hover:bg-green-700 rounded transition-colors flex items-center"
                disabled={loading}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                {Object.keys(correcciones).length > 0 ? 'Corregir y Validar' : 'Aprobar'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ValidacionOCRModal;
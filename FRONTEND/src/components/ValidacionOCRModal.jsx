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
  const [notificacion, setNotificacion] = useState(null);
  const [instituciones, setInstituciones] = useState([]);
  const [institucionSeleccionada, setInstitucionSeleccionada] = useState(null);

  // Efecto para cargar tuplas cuando se abre el modal
  useEffect(() => {
    if (isOpen && documentoId) {
      cargarTuplasPendientes();
      cargarInstituciones();
    }
  }, [isOpen, documentoId]);

  /**
   * Carga las instituciones/parroquias disponibles
   */
  const cargarInstituciones = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/validacion/instituciones');
      
      if (!response.ok) {
        throw new Error('Error al cargar instituciones');
      }

      const data = await response.json();
      setInstituciones(data.instituciones || []);
      
      // Seleccionar la primera institución por defecto si existe
      if (data.instituciones && data.instituciones.length > 0) {
        setInstitucionSeleccionada(data.instituciones[0].id_institucion);
      }
      
      console.log('Instituciones cargadas:', data.instituciones);
    } catch (err) {
      console.error('Error al cargar instituciones:', err);
    }
  };

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

      // Generar IDs únicos para cada campo en el frontend
      const tuplasConCamposUnicos = data.map((tupla, tuplaIndex) => ({
        ...tupla,
        campos_ocr: tupla.campos_ocr.map((campo, campoIndex) => ({
          ...campo,
          id_campo_local: `${tupla.id_ocr}-${campo.campo}-${campoIndex}`, // ID único local
          tupla_id_ocr: tupla.id_ocr // Referencia al ID de la tupla original
        }))
      }));

      setTuplas(tuplasConCamposUnicos);
      setTuplaActual(0);
      
      // Actualizar estadísticas
      const total = data[0]?.total_tuplas_documento || data.length;
      setEstadisticas({
        total,
        validadas: 0,
        pendientes: data.length
      });

      console.log('Tuplas cargadas con IDs únicos:', tuplasConCamposUnicos);

    } catch (err) {
      console.error('Error al cargar tuplas:', err);
      setError('Error al cargar las tuplas de validación: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Valida el tipo de dato según el campo
   */
  const validarTipoDato = (nombreCampo, valor) => {
    // Campos numéricos (fechas)
    const camposNumericos = ['dia_nacimiento', 'mes_nacimiento', 'ano_nacimiento', 
                             'dia_bautismo', 'mes_bautismo', 'ano_bautismo'];
    
    // Campos alfabéticos (nombres)
    const camposAlfabeticos = ['nombre_confirmando', 'padres', 'padrinos'];

    if (camposNumericos.includes(nombreCampo)) {
      // Solo permitir números
      return valor.replace(/[^0-9]/g, '');
    }
    
    if (camposAlfabeticos.includes(nombreCampo)) {
      // Solo permitir letras, espacios, acentos y caracteres especiales de nombres
      return valor.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.]/g, '');
    }

    return valor;
  };

  /**
   * Maneja los cambios en los campos de corrección
   */
  const manejarCorreccion = (campo, valorOriginal, nuevoValor, comentario = '') => {
    // Validar tipo de dato
    const valorValidado = validarTipoDato(campo.campo, nuevoValor);

    const idLocal = campo.id_campo_local;
    console.log(`Actualizando campo ${campo.campo} (id_local: ${idLocal}):`, {
      valorOriginal,
      nuevoValor,
      valorValidado
    });

    setCorrecciones(prev => {
      const nuevasCorrecciones = {
        ...prev,
        [idLocal]: {
          id_campo_local: idLocal,
          tupla_id_ocr: campo.tupla_id_ocr,
          campo: campo.campo,
          valor_original: valorOriginal,
          valor_corregido: valorValidado,
          comentario: comentario || prev[idLocal]?.comentario || ''
        }
      };
      console.log('Estado de correcciones actualizado:', nuevasCorrecciones);
      return nuevasCorrecciones;
    });
  };

  /**
   * Valida la tupla actual y registra en BD
   */
  const validarTupla = async (accion) => {
    if (!tuplas[tuplaActual]) return;

    // Validar que se haya seleccionado una institución
    if (!institucionSeleccionada) {
      setError('Debe seleccionar una Institución/Parroquia antes de validar');
      return;
    }

    setLoading(true);
    setError(null);
    const tupla = tuplas[tuplaActual];

    // Construir datos_validados con valores corregidos o originales
    const datosValidados = {};
    tupla.campos_ocr.forEach(campo => {
      const idLocal = campo.id_campo_local;
      const valorFinal = correcciones[idLocal]?.valor_corregido || campo.valor_extraido || '';
      datosValidados[campo.campo] = valorFinal;
    });

    const datosValidacion = {
      documento_id: documentoId,
      tupla_numero: tupla.tupla_numero,
      tupla_id_ocr: tupla.id_ocr,
      usuario_validador_id: 1, // TODO: Obtener del contexto de usuario
      institucion_id: institucionSeleccionada,
      datos_validados: datosValidados,
      observaciones,
      accion // 'aprobar', 'corregir', 'rechazar'
    };

    console.log('📤 Enviando validación:', datosValidacion);

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
      console.log('✅ Tupla validada:', resultado);

      // Mostrar notificación de éxito
      setNotificacion({
        tipo: 'success',
        mensaje: `✅ Tupla ${tupla.tupla_numero} registrada - Persona: ${resultado.persona_id}, Sacramento: ${resultado.sacramento_id}`
      });

      // Ocultar notificación después de 3 segundos
      setTimeout(() => setNotificacion(null), 3000);

      // Actualizar estadísticas
      setEstadisticas({
        total: resultado.total_tuplas || estadisticas.total,
        validadas: resultado.tuplas_validadas || (estadisticas.validadas + 1),
        pendientes: resultado.tuplas_pendientes || (estadisticas.pendientes - 1)
      });

      // Si hay siguiente tupla, avanzar automáticamente
      if (resultado.siguiente_tupla !== null && !resultado.completado) {
        const siguienteIndex = tuplas.findIndex(t => t.tupla_numero === resultado.siguiente_tupla);
        if (siguienteIndex !== -1) {
          setTuplaActual(siguienteIndex);
          setCorrecciones({});
          setObservaciones('');
          setModoEdicion(false);
          console.log(`➡️ Avanzando a tupla ${resultado.siguiente_tupla}`);
        }
      } else if (resultado.completado) {
        // Validación completada - todas las tuplas procesadas
        console.log('🎉 Documento completamente validado');
        alert(`¡Documento validado completamente!\n${resultado.tuplas_validadas} tuplas procesadas.`);
        
        if (onValidacionCompleta) {
          await onValidacionCompleta(documentoId);
        }
        onClose();
      }

    } catch (err) {
      console.error('❌ Error al validar tupla:', err);
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
   * Orden de campos según la tabla de las hojas
   */
  const ORDEN_CAMPOS = [
    'nombre_confirmando',
    'dia_nacimiento',
    'mes_nacimiento',
    'ano_nacimiento',
    'dia_bautismo',
    'mes_bautismo',
    'ano_bautismo',
    'padres',
    'padrinos'
  ];

  /**
   * Ordena los campos según el orden definido
   */
  const ordenarCampos = (campos) => {
    return [...campos].sort((a, b) => {
      const indexA = ORDEN_CAMPOS.indexOf(a.campo);
      const indexB = ORDEN_CAMPOS.indexOf(b.campo);
      return indexA - indexB;
    });
  };

  /**
   * Obtiene la etiqueta amigable del campo
   */
  const obtenerEtiquetaCampo = (nombreCampo) => {
    const etiquetas = {
      'nombre_confirmando': 'CONFIRMANDO (Nombre - Ap. Paterno - Ap. Materno)',
      'dia_nacimiento': 'Día de Nacimiento',
      'mes_nacimiento': 'Mes de Nacimiento',
      'ano_nacimiento': 'Año de Nacimiento',
      'dia_bautismo': 'Día de Bautismo',
      'mes_bautismo': 'Mes de Bautismo',
      'ano_bautismo': 'Año de Bautismo',
      'padres': 'PADRES (Nombres - Ap. Paterno - Ap. Materno)',
      'padrinos': 'PADRINOS (Nombres - Ap. Paterno - Ap. Materno)'
    };
    return etiquetas[nombreCampo] || nombreCampo.replace(/_/g, ' ');
  };

  /**
   * Obtiene el placeholder según el tipo de campo
   */
  const obtenerPlaceholder = (nombreCampo) => {
    const placeholders = {
      'nombre_confirmando': 'Ej: Juan - Pérez - García',
      'dia_nacimiento': 'Día (1-31)',
      'mes_nacimiento': 'Mes (1-12)',
      'ano_nacimiento': 'Año (ej: 1990)',
      'dia_bautismo': 'Día (1-31)',
      'mes_bautismo': 'Mes (1-12)',
      'ano_bautismo': 'Año (ej: 1990)',
      'padres': 'Nombres - Ap. Paterno - Ap. Materno',
      'padrinos': 'Nombres - Ap. Paterno - Ap. Materno'
    };
    return placeholders[nombreCampo] || 'Ingrese el valor';
  };

  /**
   * Renderiza un campo OCR
   */
  const renderizarCampoOCR = (campo) => {
    const idLocal = campo.id_campo_local;

    // Determinar color según confianza
    const getConfianzaColor = (confianza) => {
      if (confianza >= 0.9) return 'text-green-600';
      if (confianza >= 0.7) return 'text-yellow-600';
      return 'text-red-600';
    };

    // Obtener valor actual del campo (corregido o extraído)
    const obtenerValorCampo = () => {
      return correcciones[idLocal]?.valor_corregido || campo.valor_extraido || '';
    };

    const tieneCorreccion = correcciones[idLocal];

    return (
      <div key={idLocal} className="bg-gray-50 p-4 rounded-lg border">
        <div className="flex justify-between items-start mb-2">
          <label className="font-medium text-gray-700">
            {obtenerEtiquetaCampo(campo.campo)}
          </label>
          <span className={`text-xs px-2 py-1 rounded ${getConfianzaColor(campo.confianza)}`}>
            {Math.round(campo.confianza * 100)}%
          </span>
        </div>

        {modoEdicion ? (
          <div className="space-y-2">
            <input
              type="text"
              value={obtenerValorCampo()}
              onChange={(e) => manejarCorreccion(
                campo,
                campo.valor_extraido,
                e.target.value,
                correcciones[idLocal]?.comentario || ''
              )}
              placeholder={obtenerPlaceholder(campo.campo)}
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            {tieneCorreccion && (
              <input
                type="text"
                placeholder="Comentario sobre la corrección"
                value={correcciones[idLocal]?.comentario || ''}
                onChange={(e) => manejarCorreccion(
                  campo,
                  campo.valor_extraido,
                  correcciones[idLocal].valor_corregido,
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
            <div className="font-medium">{obtenerValorCampo()}</div>
            {tieneCorreccion && correcciones[idLocal].comentario && (
              <div className="text-xs text-yellow-700 mt-1">
                📝 {correcciones[idLocal].comentario}
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
        
        {/* Notificación de éxito */}
        {notificacion && (
          <div className={`absolute top-4 right-4 z-10 px-4 py-3 rounded-lg shadow-lg ${
            notificacion.tipo === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          } animate-fade-in-down`}>
            {notificacion.mensaje}
          </div>
        )}

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

          {/* Selector de Institución/Parroquia */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-blue-100 mb-2">
              🏛️ Institución/Parroquia *
            </label>
            <select
              value={institucionSeleccionada || ''}
              onChange={(e) => setInstitucionSeleccionada(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-white text-gray-800 rounded-lg border border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading || instituciones.length === 0}
            >
              <option value="">Seleccione una institución...</option>
              {instituciones.map((inst) => (
                <option key={inst.id_institucion} value={inst.id_institucion}>
                  {inst.nombre} {inst.direccion ? `- ${inst.direccion}` : ''}
                </option>
              ))}
            </select>
            {!institucionSeleccionada && (
              <p className="text-xs text-yellow-200 mt-1">
                ⚠️ Debe seleccionar una institución para poder validar
              </p>
            )}
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
                {ordenarCampos(tupla.campos_ocr).map((campo) => renderizarCampoOCR(campo))}
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
        {tupla && !error && (
          <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {Object.keys(correcciones).length > 0 ? (
                <span className="text-yellow-600 font-medium">
                  ⚠️ {Object.keys(correcciones).length} corrección(es) aplicada(s)
                </span>
              ) : (
                <span className="text-gray-500">
                  ℹ️ Sin correcciones - Datos originales del OCR
                </span>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => validarTupla('rechazar')}
                className="px-4 py-2 bg-red-100 text-red-700 hover:bg-red-200 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                {loading ? 'Procesando...' : 'Rechazar'}
              </button>
              
              <button
                onClick={() => validarTupla(Object.keys(correcciones).length > 0 ? 'corregir' : 'aprobar')}
                className="px-6 py-2 bg-green-600 text-white hover:bg-green-700 rounded transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Registrando...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    {Object.keys(correcciones).length > 0 ? 'Validar y Registrar' : 'Aprobar y Registrar'}
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ValidacionOCRModal;
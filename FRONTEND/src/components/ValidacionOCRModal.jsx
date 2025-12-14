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
  
  // Estados para validación de persona existente
  const [personaExistente, setPersonaExistente] = useState(null);
  const [mostrarModalConfirmacion, setMostrarModalConfirmacion] = useState(false);
  const [datosParaRegistrar, setDatosParaRegistrar] = useState(null);

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
   * Acepta tanto col_X como nombres de campo
   */
  const validarTipoDato = (nombreCampo, valor) => {
    // Mapear col_X a nombre de campo si es necesario
    const nombreCampoReal = COL_TO_FIELD_MAP[nombreCampo] || nombreCampo;
    
    // Campos numéricos (fechas)
    const camposNumericos = ['dia_nacimiento', 'mes_nacimiento', 'ano_nacimiento', 
                             'dia_bautismo', 'mes_bautismo', 'ano_bautismo'];
    
    // Campos alfabéticos (nombres)
    const camposAlfabeticos = ['nombre_confirmando', 'padres', 'padrinos'];

    if (camposNumericos.includes(nombreCampoReal)) {
      // Solo permitir números
      return valor.replace(/[^0-9]/g, '');
    }
    
    if (camposAlfabeticos.includes(nombreCampoReal)) {
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

    setLoading(true);
    setError(null);
    const tupla = tuplas[tuplaActual];

    // Si la acción es rechazar, no necesitamos validar institución ni datos
    if (accion === 'rechazar') {
      await registrarTupla({
        documento_id: documentoId,
        tupla_numero: tupla.tupla_numero,
        tupla_id_ocr: tupla.id_ocr,
        usuario_validador_id: 4,
        institucion_id: null,
        datos_validados: {},
        observaciones: observaciones || 'Tupla rechazada',
        accion: 'rechazar'
      });
      return;
    }

    // Para aprobar o corregir, validar que se haya seleccionado una institución
    if (!institucionSeleccionada) {
      setError('Debe seleccionar una Institución/Parroquia antes de validar');
      setLoading(false);
      return;
    }

    // Construir datos_validados con valores corregidos o originales
    const datosValidados = {};
    tupla.campos_ocr.forEach(campo => {
      const idLocal = campo.id_campo_local;
      const valorFinal = correcciones[idLocal]?.valor_corregido || campo.valor_extraido || '';
      datosValidados[campo.campo] = valorFinal;
    });

    // Construir fechas completas desde día/mes/año
    const fechaNacimiento = `${datosValidados.ano_nacimiento}-${String(datosValidados.mes_nacimiento).padStart(2, '0')}-${String(datosValidados.dia_nacimiento).padStart(2, '0')}`;
    const fechaBautismo = `${datosValidados.ano_bautismo}-${String(datosValidados.mes_bautismo).padStart(2, '0')}-${String(datosValidados.dia_bautismo).padStart(2, '0')}`;

    // Parsear nombre_confirmando.
    // Soporta dos formatos:
    // 1) Con guiones: "Nombres - Apellido Paterno - Apellido Materno"
    // 2) Sin guiones (OCR típico): "Nombres1 Nombres2 ApellidoPaterno ApellidoMaterno"
    const rawNombre = datosValidados.nombre_confirmando || '';
    let nombres = '';
    let apellidoPaterno = '';
    let apellidoMaterno = '';

    if (rawNombre.includes('-')) {
      const nombrePartes = rawNombre.split('-').map(p => p.trim());
      nombres = nombrePartes[0] || '';
      apellidoPaterno = nombrePartes[1] || '';
      apellidoMaterno = nombrePartes[2] || '';
    } else {
      const tokens = rawNombre.split(/\s+/).filter(Boolean);
      if (tokens.length >= 4) {
        // Primeros 2 tokens => nombres, 3ro => apellido paterno, 4to => apellido materno
        nombres = tokens.slice(0, 2).join(' ');
        apellidoPaterno = tokens[2] || '';
        apellidoMaterno = tokens[3] || '';
      } else if (tokens.length === 3) {
        // 2 tokens nombres, 3ro apellido paterno
        nombres = tokens.slice(0, 2).join(' ');
        apellidoPaterno = tokens[2] || '';
        apellidoMaterno = '';
      } else if (tokens.length === 2) {
        // 1 token nombre, 2do apellido paterno
        nombres = tokens[0] || '';
        apellidoPaterno = tokens[1] || '';
        apellidoMaterno = '';
      } else {
        // fallback
        nombres = rawNombre;
        apellidoPaterno = '';
        apellidoMaterno = '';
      }
    }

    // Buscar si ya existe persona con mismo nombre, fecha_nacimiento y fecha_bautismo
    try {
      const searchRes = await fetch(
        `http://localhost:8002/api/v1/personas/search?nombres=${encodeURIComponent(nombres)}&apellido_paterno=${encodeURIComponent(apellidoPaterno)}&apellido_materno=${encodeURIComponent(apellidoMaterno)}`
      );
      
      if (searchRes.ok) {
        const personasEncontradas = await searchRes.json();
        
        // Filtrar por fecha_nacimiento y fecha_bautismo exactas
        const personaCoincidente = personasEncontradas.find(p => 
          p.fecha_nacimiento === fechaNacimiento && 
          p.fecha_bautismo === fechaBautismo
        );
        
        if (personaCoincidente) {
          // Persona existente encontrada - mostrar modal de confirmación
          setPersonaExistente(personaCoincidente);
          setDatosParaRegistrar({
            documento_id: documentoId,
            tupla_numero: tupla.tupla_numero,
            tupla_id_ocr: tupla.id_ocr,
            usuario_validador_id: 4,
            institucion_id: institucionSeleccionada,
            datos_validados: datosValidados,
            observaciones,
            accion,
            persona_id_existente: personaCoincidente.id_persona
          });
          setMostrarModalConfirmacion(true);
          setLoading(false);
          return; // Esperar confirmación del usuario
        }
      }
    } catch (err) {
      console.warn('⚠️ Error al buscar persona existente:', err);
      // Continuar con registro normal si falla búsqueda
    }

    // No se encontró persona existente, proceder con registro normal
    await registrarTupla({
      documento_id: documentoId,
      tupla_numero: tupla.tupla_numero,
      tupla_id_ocr: tupla.id_ocr,
      usuario_validador_id: 4,
      institucion_id: institucionSeleccionada,
      datos_validados: datosValidados,
      observaciones,
      accion
    });
  };

  /**
   * Registra la tupla en el backend
   */
  const registrarTupla = async (datosValidacion) => {
    setLoading(true);
    const tupla = tuplas[tuplaActual];

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
      console.log('✅ Tupla procesada:', resultado);

      // Mostrar notificación de éxito según el tipo de acción
      const mensaje = resultado.estado === 'rechazado'
        ? `⏭️ Tupla ${tupla.tupla_numero} rechazada`
        : `✅ Tupla ${tupla.tupla_numero} registrada - Persona: ${resultado.persona_id}, Sacramento: ${resultado.sacramento_id}`;
      
      setNotificacion({
        tipo: 'success',
        mensaje
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
   * Confirma el registro con persona existente
   */
  const confirmarRegistroConPersonaExistente = async () => {
    setMostrarModalConfirmacion(false);
    await registrarTupla(datosParaRegistrar);
    setPersonaExistente(null);
    setDatosParaRegistrar(null);
  };

  /**
   * Cancela el registro y vuelve a editar
   */
  const cancelarRegistroPersonaExistente = () => {
    setMostrarModalConfirmacion(false);
    setPersonaExistente(null);
    setDatosParaRegistrar(null);
    setLoading(false);
    setModoEdicion(true); // Permitir editar datos
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
   * Mapeo de col_X a nombres de campos
   * col_4 NO se incluye (parroquia/institución - no se valida)
   */
  const COL_TO_FIELD_MAP = {
    'col_0': 'nombre_confirmando',
    'col_1': 'dia_nacimiento',
    'col_2': 'mes_nacimiento',
    'col_3': 'ano_nacimiento',
    // col_4 NO se mapea (parroquia - no se valida)
    'col_5': 'dia_bautismo',
    'col_6': 'mes_bautismo',
    'col_7': 'ano_bautismo',
    'col_8': 'padres',
    'col_9': 'padrinos'
  };

  /**
   * Orden de campos según la tabla de las hojas (sin col_4)
   */
  const ORDEN_CAMPOS = [
    'col_0',  // nombre_confirmando
    'col_1',  // dia_nacimiento
    'col_2',  // mes_nacimiento
    'col_3',  // ano_nacimiento',
    // col_4 omitido (parroquia)
    'col_5',  // dia_bautismo
    'col_6',  // mes_bautismo
    'col_7',  // ano_bautismo
    'col_8',  // padres
    'col_9'   // padrinos
  ];

  /**
   * Ordena los campos según el orden definido y FILTRA col_4
   */
  const ordenarCampos = (campos) => {
    // FILTRAR col_4 (parroquia) antes de ordenar
    const camposFiltrados = campos.filter(campo => campo.campo !== 'col_4');
    
    return [...camposFiltrados].sort((a, b) => {
      const indexA = ORDEN_CAMPOS.indexOf(a.campo);
      const indexB = ORDEN_CAMPOS.indexOf(b.campo);
      return indexA - indexB;
    });
  };

  /**
   * Obtiene la etiqueta amigable del campo
   * Acepta tanto col_X como nombres de campo
   */
  const obtenerEtiquetaCampo = (nombreCampo) => {
    // Mapear col_X a nombre de campo si es necesario
    const nombreCampoReal = COL_TO_FIELD_MAP[nombreCampo] || nombreCampo;
    
    const etiquetas = {
      'nombre_confirmando': 'Nombre del Confirmado',
      'dia_nacimiento': 'Día de Nacimiento',
      'mes_nacimiento': 'Mes de Nacimiento',
      'ano_nacimiento': 'Año de Nacimiento',
      'dia_bautismo': 'Día de Bautismo',
      'mes_bautismo': 'Mes de Bautismo',
      'ano_bautismo': 'Año de Bautismo',
      'padres': 'Padres (Nombres - Ap. Paterno - Ap. Materno)',
      'padrinos': 'Padrinos (Nombres - Ap. Paterno - Ap. Materno)'
    };
    return etiquetas[nombreCampoReal] || nombreCampoReal.replace(/_/g, ' ');
  };

  /**
   * Obtiene el placeholder según el tipo de campo
   * Acepta tanto col_X como nombres de campo
   */
  const obtenerPlaceholder = (nombreCampo) => {
    // Mapear col_X a nombre de campo si es necesario
    const nombreCampoReal = COL_TO_FIELD_MAP[nombreCampo] || nombreCampo;
    
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
    return placeholders[nombreCampoReal] || 'Ingrese el valor';
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

              {/* Selector de Institución/Parroquia */}
              <div className="bg-gradient-to-r from-green-50 to-green-100 border-2 border-green-300 p-4 rounded-lg">
                <label className="block text-sm font-medium text-green-800 mb-2">
                  ✅ Seleccione la Institución/Parroquia correcta *
                </label>
                <select
                  value={institucionSeleccionada || ''}
                  onChange={(e) => setInstitucionSeleccionada(parseInt(e.target.value))}
                  className="w-full px-3 py-2 bg-white text-gray-800 rounded-lg border-2 border-green-400 focus:ring-2 focus:ring-green-500 focus:border-green-500"
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
                  <p className="text-xs text-red-600 mt-2 font-medium">
                    ⚠️ Debe seleccionar una institución para poder validar
                  </p>
                )}
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

      {/* Modal de confirmación de persona existente */}
      {mostrarModalConfirmacion && personaExistente && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="flex items-start mb-4">
              <AlertTriangle className="w-6 h-6 text-yellow-500 mr-3 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  ⚠️ Persona Encontrada con Bautizo Registrado
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Se encontró una persona con el mismo nombre, fecha de nacimiento y fecha de bautismo:
                </p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Nombre:</span>
                  <span className="ml-2 text-gray-900">
                    {personaExistente.nombres} {personaExistente.apellido_paterno} {personaExistente.apellido_materno}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Fecha de Nacimiento:</span>
                  <span className="ml-2 text-gray-900">{personaExistente.fecha_nacimiento}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Fecha de Bautismo:</span>
                  <span className="ml-2 text-gray-900">{personaExistente.fecha_bautismo}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">ID Persona:</span>
                  <span className="ml-2 text-gray-900">{personaExistente.id_persona}</span>
                </div>
              </div>
            </div>

            <p className="text-sm text-gray-700 mb-6">
              ¿Desea registrar la <span className="font-bold">Confirmación</span> para esta persona existente? 
              No se creará una nueva persona, solo se agregará el sacramento de confirmación.
            </p>

            <div className="flex space-x-3">
              <button
                onClick={cancelarRegistroPersonaExistente}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded transition-colors"
              >
                Cancelar y Editar
              </button>
              <button
                onClick={confirmarRegistroConPersonaExistente}
                className="flex-1 px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded transition-colors flex items-center justify-center"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Confirmar y Registrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidacionOCRModal;
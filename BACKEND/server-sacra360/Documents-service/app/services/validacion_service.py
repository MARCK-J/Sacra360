"""
Servicio de validación de tuplas OCR
Maneja la lógica de negocio para el proceso de validación tupla por tupla
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import logging

from app.models.documento_model import DocumentoDigitalizado
from app.models.ocr_model import OCRResultado
from app.models.validacion_model import ValidacionTupla
# from app.models.sacramento_model import Sacramento  # Comentado temporalmente
from app.models.correccion_model import CorreccionDocumento
from app.dto.validacion_dto import (
    TuplaValidacionResponse,
    CampoOCRResponse,
    ValidacionRequest,
    ValidacionStatusResponse,
    ValidacionCompleteRequest,
    EstadoValidacionResponse
)

logger = logging.getLogger(__name__)

class ValidacionService:
    """Servicio para manejar la validación de tuplas OCR"""
    
    async def obtener_tuplas_pendientes(self, documento_id: int, db: Session) -> List[TuplaValidacionResponse]:
        """
        Obtiene todas las tuplas pendientes de validación para un documento
        
        Args:
            documento_id: ID del documento digitalizado
            db: Sesión de base de datos
            
        Returns:
            Lista de tuplas con sus datos OCR
        """
        try:
            # Verificar que el documento existe usando query directa
            documento_exists = db.execute(
                text("SELECT COUNT(*) FROM documento_digitalizado WHERE id_documento = :doc_id"),
                {"doc_id": documento_id}
            ).scalar()
            
            if documento_exists == 0:
                raise ValueError(f"Documento con ID {documento_id} no encontrado")
            
            # Obtener números de tuplas pendientes usando query directa
            tuplas_pendientes = db.execute(
                text("""
                    SELECT DISTINCT tupla_numero 
                    FROM validacion_tuplas 
                    WHERE documento_id = :doc_id AND estado = 'pendiente'
                    ORDER BY tupla_numero
                """),
                {"doc_id": documento_id}
            ).fetchall()
            
            if not tuplas_pendientes:
                logger.info(f"No hay tuplas pendientes para documento {documento_id}")
                return []
            
            # Obtener total de tuplas del documento usando query directa
            total_tuplas = db.execute(
                text("""
                    SELECT COALESCE(MAX(tupla_numero), 0) 
                    FROM ocr_resultado 
                    WHERE documento_id = :doc_id
                """),
                {"doc_id": documento_id}
            ).scalar() or 0
            
            tuplas_response = []
            
            for tupla_row in tuplas_pendientes:
                tupla_numero = tupla_row[0]
                
                # Obtener campos OCR para esta tupla usando query directa
                # Soporta tanto el formato antiguo (campo, valor_extraido) como el nuevo (datos_ocr JSONB)
                campos_ocr_raw = db.execute(
                    text("""
                        SELECT id_ocr, datos_ocr, confianza, validado, sacramento_id
                        FROM ocr_resultado 
                        WHERE documento_id = :doc_id AND tupla_numero = :tupla_num
                        LIMIT 1
                    """),
                    {"doc_id": documento_id, "tupla_num": tupla_numero}
                ).fetchone()
                
                if campos_ocr_raw:
                    campos_response = []
                    id_ocr = campos_ocr_raw[0]
                    datos_ocr = campos_ocr_raw[1]  # JSONB data
                    confianza = float(campos_ocr_raw[2])
                    validado = campos_ocr_raw[3]
                    sacramento_id = campos_ocr_raw[4]
                    
                    # Convertir JSON de col_0-col_9 a campos individuales
                    # Mapeo de columnas a nombres de campos (índices 0-9)
                    campo_nombres = [
                        'nombre_confirmando',  # col_0
                        'dia_nacimiento',      # col_1
                        'mes_nacimiento',      # col_2
                        'ano_nacimiento',      # col_3
                        None,                  # col_4 - parroquia/institución (NO se muestra en validación)
                        'dia_bautismo',        # col_5
                        'mes_bautismo',        # col_6
                        'ano_bautismo',        # col_7
                        'padres',              # col_8
                        'padrinos'             # col_9
                    ]
                    
                    # Crear un CampoOCRResponse por cada columna (excepto col_4)
                    for i, campo_nombre in enumerate(campo_nombres):
                        # Saltar col_4 (parroquia) - no se valida, solo se guarda en datos_ocr
                        if campo_nombre is None:
                            continue
                            
                        col_key = f'col_{i}'
                        valor = datos_ocr.get(col_key, '') if datos_ocr else ''
                        
                        campos_response.append(CampoOCRResponse(
                            id_ocr=id_ocr,
                            campo=campo_nombre,
                            valor_extraido=valor,
                            confianza=confianza,
                            validado=validado,
                            sacramento_id=sacramento_id
                        ))
                    
                    tuplas_response.append(
                        TuplaValidacionResponse(
                            documento_id=documento_id,
                            tupla_numero=tupla_numero,
                            campos_ocr=campos_response,
                            estado_validacion='pendiente',
                            total_tuplas_documento=total_tuplas
                        )
                    )
            
            logger.info(f"Obtenidas {len(tuplas_response)} tuplas pendientes para documento {documento_id}")
            return tuplas_response
            
        except Exception as e:
            logger.error(f"Error al obtener tuplas pendientes: {str(e)}")
            raise
    
    async def obtener_tupla_especifica(
        self, 
        documento_id: int, 
        tupla_numero: int, 
        db: Session
    ) -> TuplaValidacionResponse:
        """
        Obtiene una tupla específica con sus datos OCR
        
        Args:
            documento_id: ID del documento digitalizado
            tupla_numero: Número de la tupla
            db: Sesión de base de datos
            
        Returns:
            Datos de la tupla específica
        """
        try:
            # Verificar que existe la validación de la tupla
            validacion = db.query(ValidacionTupla).filter(
                and_(
                    ValidacionTupla.documento_id == documento_id,
                    ValidacionTupla.tupla_numero == tupla_numero
                )
            ).first()
            
            if not validacion:
                raise ValueError(f"Tupla {tupla_numero} del documento {documento_id} no encontrada")
            
            # Obtener campos OCR para esta tupla (formato OCR V2 con datos_ocr JSONB)
            campo_ocr = db.query(OCRResultado).filter(
                and_(
                    OCRResultado.documento_id == documento_id,
                    OCRResultado.tupla_numero == tupla_numero
                )
            ).first()
            
            if not campo_ocr:
                raise ValueError(f"No se encontraron datos OCR para la tupla {tupla_numero}")
            
            # Obtener total de tuplas
            total_tuplas = db.query(func.max(OCRResultado.tupla_numero)).filter(
                OCRResultado.documento_id == documento_id
            ).scalar() or 0
            
            # Convertir formato JSONB a campos individuales
            campo_nombres = [
                'nombre_confirmado', 'dia_nacimiento', 'mes_nacimiento', 'ano_nacimiento',
                'parroquia', 'dia_confirmacion', 'mes_confirmacion', 'ano_confirmacion',
                'padres', 'padrinos'
            ]
            
            campos_response = []
            for i, campo_nombre in enumerate(campo_nombres, 1):
                col_key = f'col{i}'
                valor = campo_ocr.datos_ocr.get(col_key, '') if campo_ocr.datos_ocr else ''
                
                campos_response.append(CampoOCRResponse(
                    id_ocr=campo_ocr.id_ocr,
                    campo=campo_nombre,
                    valor_extraido=valor,
                    confianza=float(campo_ocr.confianza),
                    validado=campo_ocr.validado,
                    sacramento_id=campo_ocr.sacramento_id
                ))
            
            return TuplaValidacionResponse(
                documento_id=documento_id,
                tupla_numero=tupla_numero,
                campos_ocr=campos_response,
                estado_validacion=validacion.estado,
                fecha_extraccion=None,  # No disponible en el nuevo formato
                total_tuplas_documento=total_tuplas
            )
            
        except Exception as e:
            logger.error(f"Error al obtener tupla específica: {str(e)}")
            raise
    
    async def validar_tupla(self, validacion_data: ValidacionRequest, db: Session) -> ValidacionStatusResponse:
        """
        Valida una tupla aplicando correcciones si es necesario
        
        Args:
            validacion_data: Datos de la validación
            db: Sesión de base de datos
            
        Returns:
            Estado de la validación
        """
        try:
            # Obtener la validación de la tupla
            validacion = db.query(ValidacionTupla).filter(
                and_(
                    ValidacionTupla.documento_id == validacion_data.documento_id,
                    ValidacionTupla.tupla_numero == validacion_data.tupla_numero
                )
            ).first()
            
            if not validacion:
                raise ValueError("Tupla de validación no encontrada")
            
            # Obtener el resultado OCR de esta tupla
            ocr_resultado = db.query(OCRResultado).filter(
                and_(
                    OCRResultado.documento_id == validacion_data.documento_id,
                    OCRResultado.tupla_numero == validacion_data.tupla_numero
                )
            ).first()
            
            if not ocr_resultado:
                raise ValueError("Resultado OCR no encontrado para esta tupla")
            
            # Aplicar correcciones desde datos_validados (contiene valores finales)
            if validacion_data.datos_validados:
                # Mapeo de nombres de campos a columnas JSONB
                campo_map = {
                    'nombre_confirmado': 'col1',
                    'dia_nacimiento': 'col2',
                    'mes_nacimiento': 'col3',
                    'ano_nacimiento': 'col4',
                    'parroquia': 'col5',
                    'dia_confirmacion': 'col6',
                    'mes_confirmacion': 'col7',
                    'ano_confirmacion': 'col8',
                    'padres': 'col9',
                    'padrinos': 'col10'
                }
                
                # Actualizar datos_ocr JSONB con valores validados
                datos_actualizados = dict(ocr_resultado.datos_ocr or {})
                
                for campo_nombre, valor_nuevo in validacion_data.datos_validados.items():
                    col_key = campo_map.get(campo_nombre)
                    if col_key:
                        valor_original = datos_actualizados.get(col_key, '')
                        
                        # Si el valor cambió, registrar corrección
                        if valor_original != valor_nuevo:
                            nueva_correccion = CorreccionDocumento(
                                ocr_resultado_id=ocr_resultado.id_ocr,
                                valor_original=f"{campo_nombre}: {valor_original}",
                                valor_corregido=f"{campo_nombre}: {valor_nuevo}",
                                razon_correccion="Corrección manual durante validación",
                                usuario_corrector_id=validacion_data.usuario_validador_id,
                                fecha_correccion=datetime.utcnow()
                            )
                            db.add(nueva_correccion)
                            logger.info(f"Corrección aplicada: {campo_nombre} = {valor_nuevo}")
                        
                        # Actualizar el valor en el JSONB
                        datos_actualizados[col_key] = valor_nuevo
                
                # Guardar datos actualizados
                ocr_resultado.datos_ocr = datos_actualizados
                ocr_resultado.validado = True
            
            # Actualizar estado de validación según la acción
            if validacion_data.accion == "aprobar":
                validacion.estado = "validado"
                # Marcar todos los campos OCR como validados
                db.query(OCRResultado).filter(
                    and_(
                        OCRResultado.documento_id == validacion_data.documento_id,
                        OCRResultado.tupla_numero == validacion_data.tupla_numero
                    )
                ).update({"validado": True, "estado_validacion": "validado"})
                
            elif validacion_data.accion == "corregir":
                validacion.estado = "validado"
                # Los campos ya se actualizaron en el loop de correcciones
                db.query(OCRResultado).filter(
                    and_(
                        OCRResultado.documento_id == validacion_data.documento_id,
                        OCRResultado.tupla_numero == validacion_data.tupla_numero
                    )
                ).update({"validado": True, "estado_validacion": "corregido"})
                
            elif validacion_data.accion == "rechazar":
                validacion.estado = "rechazado"
                db.query(OCRResultado).filter(
                    and_(
                        OCRResultado.documento_id == validacion_data.documento_id,
                        OCRResultado.tupla_numero == validacion_data.tupla_numero
                    )
                ).update({"estado_validacion": "rechazado"})
            
            # Actualizar datos de validación
            validacion.usuario_validador_id = validacion_data.usuario_validador_id
            validacion.fecha_validacion = datetime.utcnow()
            validacion.observaciones = validacion_data.observaciones
            
            db.commit()
            
            # Obtener estadísticas actuales
            total_tuplas = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                ValidacionTupla.documento_id == validacion_data.documento_id
            ).scalar()
            
            tuplas_validadas = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                and_(
                    ValidacionTupla.documento_id == validacion_data.documento_id,
                    ValidacionTupla.estado.in_(["validado"])
                )
            ).scalar()
            
            tuplas_pendientes = total_tuplas - tuplas_validadas
            
            # Obtener siguiente tupla pendiente
            siguiente_tupla = db.query(ValidacionTupla.tupla_numero).filter(
                and_(
                    ValidacionTupla.documento_id == validacion_data.documento_id,
                    ValidacionTupla.estado == 'pendiente',
                    ValidacionTupla.tupla_numero > validacion_data.tupla_numero
                )
            ).order_by(ValidacionTupla.tupla_numero).first()
            
            siguiente_tupla_num = siguiente_tupla[0] if siguiente_tupla else None
            completado = tuplas_pendientes == 0
            
            mensaje = self._generar_mensaje_validacion(
                validacion_data.accion,
                completado,
                siguiente_tupla_num
            )
            
            logger.info(f"Tupla {validacion_data.tupla_numero} validada exitosamente")
            
            return ValidacionStatusResponse(
                documento_id=validacion_data.documento_id,
                tupla_actual=validacion_data.tupla_numero,
                tupla_validada=True,
                siguiente_tupla=siguiente_tupla_num,
                tuplas_pendientes=tuplas_pendientes,
                tuplas_validadas=tuplas_validadas,
                total_tuplas=total_tuplas,
                completado=completado,
                mensaje=mensaje
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al validar tupla: {str(e)}")
            raise
    
    async def completar_validacion_documento(
        self, 
        documento_id: int, 
        completion_data: ValidacionCompleteRequest, 
        db: Session
    ) -> ValidacionStatusResponse:
        """
        Completa la validación de un documento y registra los sacramentos
        
        Args:
            documento_id: ID del documento
            completion_data: Datos de completación
            db: Sesión de base de datos
            
        Returns:
            Estado final de validación
        """
        try:
            # Verificar que todas las tuplas estén validadas
            tuplas_pendientes = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                and_(
                    ValidacionTupla.documento_id == documento_id,
                    ValidacionTupla.estado == 'pendiente'
                )
            ).scalar()
            
            if tuplas_pendientes > 0:
                raise ValueError(f"Aún hay {tuplas_pendientes} tuplas pendientes de validación")
            
            # Si se debe registrar sacramentos
            if completion_data.registrar_sacramentos:
                await self._registrar_sacramentos_validados(documento_id, db)
            
            # Marcar documento como completado
            documento = db.query(DocumentoDigitalizado).filter(
                DocumentoDigitalizado.id_documento == documento_id
            ).first()
            
            if documento:
                documento.estado_procesamiento = "validado_completado"
                documento.fecha_validacion = datetime.utcnow()
            
            db.commit()
            
            total_tuplas = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                ValidacionTupla.documento_id == documento_id
            ).scalar()
            
            logger.info(f"Validación del documento {documento_id} completada exitosamente")
            
            return ValidacionStatusResponse(
                documento_id=documento_id,
                tupla_actual=0,
                tupla_validada=True,
                siguiente_tupla=None,
                tuplas_pendientes=0,
                tuplas_validadas=total_tuplas,
                total_tuplas=total_tuplas,
                completado=True,
                mensaje="Validación del documento completada exitosamente"
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al completar validación: {str(e)}")
            raise
    
    async def obtener_estado_validacion(self, documento_id: int, db: Session) -> Dict[str, Any]:
        """
        Obtiene el estado actual de validación de un documento
        
        Args:
            documento_id: ID del documento
            db: Sesión de base de datos
            
        Returns:
            Estado de validación con estadísticas
        """
        try:
            documento = db.query(DocumentoDigitalizado).filter(
                DocumentoDigitalizado.id_documento == documento_id
            ).first()
            
            if not documento:
                raise ValueError(f"Documento {documento_id} no encontrado")
            
            # Estadísticas de validación
            total_tuplas = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                ValidacionTupla.documento_id == documento_id
            ).scalar()
            
            tuplas_validadas = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                and_(
                    ValidacionTupla.documento_id == documento_id,
                    ValidacionTupla.estado == 'validado'
                )
            ).scalar()
            
            tuplas_pendientes = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                and_(
                    ValidacionTupla.documento_id == documento_id,
                    ValidacionTupla.estado == 'pendiente'
                )
            ).scalar()
            
            tuplas_rechazadas = db.query(func.count(ValidacionTupla.id_validacion)).filter(
                and_(
                    ValidacionTupla.documento_id == documento_id,
                    ValidacionTupla.estado == 'rechazado'
                )
            ).scalar()
            
            progreso = (tuplas_validadas / total_tuplas * 100) if total_tuplas > 0 else 0
            
            return {
                "documento_id": documento_id,
                "nombre_archivo": documento.nombre_archivo,
                "tipo_sacramento": documento.tipo_sacramento,
                "total_tuplas": total_tuplas,
                "tuplas_validadas": tuplas_validadas,
                "tuplas_pendientes": tuplas_pendientes,
                "tuplas_rechazadas": tuplas_rechazadas,
                "progreso_porcentaje": round(progreso, 2),
                "estado_general": self._calcular_estado_general(tuplas_pendientes, tuplas_validadas, total_tuplas),
                "fecha_digitalizacion": documento.fecha_subida.isoformat() if documento.fecha_subida else None
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estado de validación: {str(e)}")
            raise
    
    async def cancelar_validacion(self, documento_id: int, db: Session):
        """
        Cancela el proceso de validación
        
        Args:
            documento_id: ID del documento
            db: Sesión de base de datos
        """
        try:
            # Resetear validaciones a pendiente
            db.query(ValidacionTupla).filter(
                ValidacionTupla.documento_id == documento_id
            ).update({
                "estado": "pendiente",
                "usuario_validador_id": None,
                "fecha_validacion": None,
                "observaciones": None
            })
            
            # Resetear estado de OCR
            db.query(OCRResultado).filter(
                OCRResultado.documento_id == documento_id
            ).update({
                "validado": False,
                "estado_validacion": "pendiente"
            })
            
            db.commit()
            logger.info(f"Validación del documento {documento_id} cancelada")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al cancelar validación: {str(e)}")
            raise
    
    def _generar_mensaje_validacion(self, accion: str, completado: bool, siguiente_tupla: Optional[int]) -> str:
        """Genera mensaje apropiado basado en el estado de validación"""
        if completado:
            return "Todas las tuplas han sido validadas. El documento está listo para finalización."
        
        base_messages = {
            "aprobar": "Tupla aprobada exitosamente",
            "corregir": "Tupla corregida y validada",
            "rechazar": "Tupla rechazada"
        }
        
        base_msg = base_messages.get(accion, "Tupla procesada")
        
        if siguiente_tupla:
            return f"{base_msg}. Siguiente tupla #{siguiente_tupla} disponible."
        else:
            return f"{base_msg}. No hay más tuplas pendientes."
    
    def _calcular_estado_general(self, pendientes: int, validadas: int, total: int) -> str:
        """Calcula el estado general del documento"""
        if pendientes == 0 and validadas == total:
            return "completado"
        elif validadas > 0:
            return "en_progreso"
        else:
            return "pendiente"
    
    async def obtener_tuplas_pendientes_json(self, documento_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Obtiene todas las tuplas pendientes en formato JSON (nueva estructura)
        
        Args:
            documento_id: ID del documento digitalizado
            db: Sesión de base de datos
            
        Returns:
            Lista de tuplas con datos_ocr parseados
        """
        try:
            query = text("""
                SELECT 
                    o.id_ocr,
                    o.tupla_numero,
                    o.datos_ocr,
                    o.confianza,
                    o.estado_validacion,
                    d.nombre_archivo,
                    d.libros_id
                FROM ocr_resultado o
                JOIN documento_digitalizado d ON o.documento_id = d.id_documento
                WHERE o.documento_id = :doc_id
                AND o.estado_validacion = 'pendiente'
                ORDER BY o.tupla_numero
            """)
            
            result = db.execute(query, {"doc_id": documento_id})
            tuplas_raw = result.fetchall()
            
            if not tuplas_raw:
                return []
            
            tuplas = []
            for row in tuplas_raw:
                import json
                datos_json = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                
                tuplas.append({
                    "id_ocr": row[0],
                    "tupla_numero": row[1],
                    "datos_ocr": datos_json,
                    "confianza": float(row[3]),
                    "estado_validacion": row[4],
                    "nombre_archivo": row[5],
                    "libro_id": row[6]
                })
            
            return tuplas
            
        except Exception as e:
            logger.error(f"Error obteniendo tuplas JSON: {str(e)}")
            raise

    async def validar_tupla_json(
        self, 
        documento_id: int,
        tupla_numero: int,
        campos_corregidos: Dict[str, Any],
        usuario_id: int,
        institucion_id: int,
        db: Session,
        persona_id_existente: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Valida una tupla con estructura JSON y registra en personas y sacramentos
        
        Args:
            documento_id: ID del documento
            tupla_numero: Número de tupla
            campos_corregidos: Diccionario con campos validados/corregidos (puede tener col_X o nombres de campo)
            usuario_id: ID del usuario que valida
            institucion_id: ID de la institución/parroquia seleccionada
            db: Sesión de base de datos
            
        Returns:
            Diccionario con IDs creados y estado
        """
        try:
            # 0. Mapear col_X a nombres de campos si es necesario
            COL_TO_FIELD_MAP = {
                'col_0': 'nombre_confirmando',
                'col_1': 'dia_nacimiento',
                'col_2': 'mes_nacimiento',
                'col_3': 'ano_nacimiento',
                # col_4 no se mapea (parroquia - no se usa)
                'col_5': 'dia_bautismo',
                'col_6': 'mes_bautismo',
                'col_7': 'ano_bautismo',
                'col_8': 'padres',
                'col_9': 'padrinos'
            }
            
            # Convertir col_X a nombres de campos si es necesario
            campos_normalizados = {}
            for key, value in campos_corregidos.items():
                # Si la key es col_X, mapear al nombre del campo
                campo_normalizado = COL_TO_FIELD_MAP.get(key, key)
                campos_normalizados[campo_normalizado] = value
            
            logger.info(f"Campos normalizados: {campos_normalizados}")
            
            # 1. Obtener tupla y datos del documento
            tupla_query = text("""
                SELECT o.id_ocr, o.datos_ocr, d.libros_id, d.tipo_sacramento
                FROM ocr_resultado o
                JOIN documento_digitalizado d ON o.documento_id = d.id_documento
                WHERE o.documento_id = :doc_id 
                AND o.tupla_numero = :tupla_num
                AND o.estado_validacion = 'pendiente'
            """)
            
            tupla = db.execute(tupla_query, {
                "doc_id": documento_id,
                "tupla_num": tupla_numero
            }).fetchone()
            
            if not tupla:
                raise ValueError("Tupla no encontrada o ya validada")
            
            id_ocr, datos_ocr, libro_id, tipo_sacramento = tupla
            
            # 2. Parsear nombre completo desde campos normalizados
            nombre_completo = campos_normalizados.get("nombre_confirmando", "").strip()
            partes = nombre_completo.split()
            
            if len(partes) >= 3:
                apellido_paterno = partes[0]
                apellido_materno = partes[1]
                nombres = " ".join(partes[2:])
            elif len(partes) == 2:
                apellido_paterno = partes[0]
                apellido_materno = ""
                nombres = partes[1]
            else:
                nombres = nombre_completo
                apellido_paterno = ""
                apellido_materno = ""
            
            # 3. Construir fecha de nacimiento
            try:
                dia_nac = int(campos_normalizados.get("dia_nacimiento", 1))
                mes_nac = int(campos_normalizados.get("mes_nacimiento", 1))
                ano_nac = int(campos_normalizados.get("ano_nacimiento", 2000))
                fecha_nacimiento = f"{ano_nac:04d}-{mes_nac:02d}-{dia_nac:02d}"
            except:
                fecha_nacimiento = "2000-01-01"
            
            # 4. Construir fecha del sacramento
            try:
                dia_baut = int(campos_normalizados.get("dia_bautismo", 1))
                mes_baut = int(campos_normalizados.get("mes_bautismo", 1))
                ano_baut = int(campos_normalizados.get("ano_bautismo", 2000))
                fecha_sacramento = f"{ano_baut:04d}-{mes_baut:02d}-{dia_baut:02d}"
            except:
                fecha_sacramento = "2000-01-01"
            
            # 5. Procesar nombres de padres y padrinos
            padres_texto = campos_normalizados.get("padres", "No especificado")
            padrinos_texto = campos_normalizados.get("padrinos", "No especificado")
            
            # Combinar padre y madre en un solo campo
            nombre_padre_nombre_madre = padres_texto[:200] if padres_texto else "No especificado"
            
            # Combinar padrino y madrina en un solo campo
            nombre_padrino_nombre_madrina = padrinos_texto[:200] if padrinos_texto else "No especificado"
            
            # Usar fecha del sacramento como fecha_bautismo estimada
            fecha_bautismo = fecha_sacramento
            
            # 6. Insertar o usar persona existente
            if persona_id_existente:
                # Persona ya existe, usar el ID proporcionado
                persona_id = persona_id_existente
                logger.info(f"Usando persona existente con ID: {persona_id}")
            else:
                # VALIDACIÓN: Verificar si ya existe una persona con estos datos
                # Criterio: nombres + apellidos + fecha_nacimiento + fecha_bautismo
                check_duplicado = text("""
                    SELECT id_persona 
                    FROM personas 
                    WHERE nombres = :nombres 
                    AND apellido_paterno = :ap_paterno 
                    AND apellido_materno = :ap_materno 
                    AND fecha_nacimiento = :fecha_nac
                    AND fecha_bautismo = :fecha_bautismo
                    LIMIT 1
                """)
                
                persona_existente = db.execute(check_duplicado, {
                    "nombres": nombres,
                    "ap_paterno": apellido_paterno,
                    "ap_materno": apellido_materno,
                    "fecha_nac": fecha_nacimiento,
                    "fecha_bautismo": fecha_bautismo
                }).fetchone()
                
                if persona_existente:
                    # Ya existe una persona con los mismos datos
                    persona_id = persona_existente[0]
                    logger.warning(f"Persona duplicada encontrada. Usando ID existente: {persona_id}")
                    raise ValueError(
                        f"Ya existe una persona registrada con el mismo nombre ({nombre_completo}), "
                        f"fecha de nacimiento ({fecha_nacimiento}) y fecha de bautizo ({fecha_bautismo}). "
                        f"Persona ID: {persona_id}"
                    )
                else:
                    # Crear nueva persona
                    try:
                        insert_persona = text("""
                            INSERT INTO personas (
                                nombres, apellido_paterno, apellido_materno,
                                fecha_nacimiento, fecha_bautismo,
                                nombre_padre_nombre_madre, nombre_padrino_nombre_madrina
                            ) VALUES (
                                :nombres, :ap_paterno, :ap_materno,
                                :fecha_nac, :fecha_bautismo,
                                :padre_madre, :padrino_madrina
                            )
                            RETURNING id_persona
                        """)
                        
                        result_persona = db.execute(insert_persona, {
                            "nombres": nombres,
                            "ap_paterno": apellido_paterno,
                            "ap_materno": apellido_materno,
                            "fecha_nac": fecha_nacimiento,
                            "fecha_bautismo": fecha_bautismo,
                            "padre_madre": nombre_padre_nombre_madre,
                            "padrino_madrina": nombre_padrino_nombre_madrina
                        })
                        
                        persona_id = result_persona.fetchone()[0]
                        logger.info(f"Persona creada con ID: {persona_id}")
                    except IntegrityError as e:
                        # Capturar violación de constraint único de PostgreSQL
                        if 'personas_datos_basicos_unique' in str(e):
                            logger.warning(f"Intento de insertar persona duplicada: {nombre_completo}")
                            raise ValueError(
                                f"Esta persona ya está registrada en el sistema. "
                                f"Nombre: {nombre_completo}, "
                                f"Fecha de nacimiento: {fecha_nacimiento}, "
                                f"Fecha de bautizo: {fecha_bautismo}. "
                                f"Por favor, verifique los datos o use el registro existente."
                            )
                        else:
                            # Otro tipo de error de integridad
                            raise
            
            # 7. Insertar en tabla sacramentos
            insert_sacramento = text("""
                INSERT INTO sacramentos (
                    persona_id, tipo_id, usuario_id, institucion_id, libro_id,
                    fecha_sacramento, fecha_registro, fecha_actualizacion
                ) VALUES (
                    :persona_id, :tipo_id, :usuario_id, :institucion_id, :libro_id,
                    :fecha_sacramento, NOW(), NOW()
                )
                RETURNING id_sacramento
            """)
            
            result_sacramento = db.execute(insert_sacramento, {
                "persona_id": persona_id,
                "tipo_id": tipo_sacramento or 1,
                "usuario_id": usuario_id,
                "institucion_id": institucion_id,
                "libro_id": libro_id,
                "fecha_sacramento": fecha_sacramento
            })
            
            sacramento_id = result_sacramento.fetchone()[0]
            logger.info(f"Sacramento creado con ID: {sacramento_id}")
            
            # 8. Marcar tupla como validada
            update_ocr = text("""
                UPDATE ocr_resultado
                SET estado_validacion = 'validado',
                    validado = true,
                    sacramento_id = :sacramento_id,
                    fecha_validacion = NOW()
                WHERE id_ocr = :id_ocr
            """)
            
            db.execute(update_ocr, {
                "sacramento_id": sacramento_id,
                "id_ocr": id_ocr
            })
            
            db.commit()
            logger.info(f"Tupla {tupla_numero} validada exitosamente")
            
            # 9. Verificar si hay más tuplas pendientes
            query_siguiente = text("""
                SELECT tupla_numero
                FROM ocr_resultado
                WHERE documento_id = :doc_id
                AND estado_validacion = 'pendiente'
                ORDER BY tupla_numero
                LIMIT 1
            """)
            
            siguiente = db.execute(query_siguiente, {"doc_id": documento_id}).fetchone()
            siguiente_tupla = siguiente[0] if siguiente else None
            
            return {
                "success": True,
                "persona_id": persona_id,
                "sacramento_id": sacramento_id,
                "siguiente_tupla": siguiente_tupla,
                "message": f"Tupla {tupla_numero} validada. Persona {persona_id}, Sacramento {sacramento_id}"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error validando tupla JSON: {str(e)}")
            raise

    async def _registrar_sacramentos_validados(self, documento_id: int, db: Session):
        """
        Registra sacramentos basado en los datos OCR validados
        
        Args:
            documento_id: ID del documento
            db: Sesión de base de datos
        """
        # Esta función se implementará según la lógica específica
        # de cada tipo de sacramento (bautismo, matrimonio, etc.)
        logger.info(f"Iniciando registro de sacramentos para documento {documento_id}")
        
        # TODO: Implementar lógica específica de registro de sacramentos
        # basada en el tipo de documento y los campos OCR validados
        
        pass
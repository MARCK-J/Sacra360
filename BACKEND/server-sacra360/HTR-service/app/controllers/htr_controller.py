"""
HTR Controller - Sacra360
Controlador para el procesamiento HTR (Handwritten Text Recognition)
Similar a ocr_controller.py pero usando el modelo HTR_Sacra360
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from typing import Dict, Any
from datetime import datetime

from services.htr_processor import HTRProcessor
from database import get_db

logger = logging.getLogger(__name__)

# Tracker de progreso en memoria (compartido entre requests)
progress_tracker = {}


class HTRController:
    """Controlador para operaciones HTR"""
    
    def __init__(self, db: Session, htr_processor: HTRProcessor):
        self.db = db
        self.htr_processor = htr_processor
    
    async def procesar_desde_bd(self, documento_id: int) -> Dict[str, Any]:
        """
        Procesa un documento desde la BD usando HTR
        
        Args:
            documento_id: ID del documento en documento_digitalizado
            
        Returns:
            Dict con estado del procesamiento
        """
        try:
            logger.info("=" * 70)
            logger.info(f"📄 Procesando documento con HTR: ID={documento_id}")
            logger.info("=" * 70)
            
            # Inicializar progreso
            progress_tracker[documento_id] = {
                'estado': 'iniciando',
                'progreso': 5,
                'mensaje': 'Iniciando procesamiento HTR...',
                'etapa': 'init'
            }
            
            # 1. Obtener documento de BD
            query = text("""
                SELECT id_documento, imagen_url, nombre_archivo, libros_id, tipo_sacramento
                FROM documento_digitalizado
                WHERE id_documento = :doc_id
            """)
            
            resultado = self.db.execute(query, {"doc_id": documento_id}).fetchone()
            
            if not resultado:
                raise ValueError(f"Documento {documento_id} no encontrado")
            
            doc_id, imagen_url, nombre_archivo, libro_id, tipo_sacramento = resultado
            logger.info(f"📄 Documento encontrado: {nombre_archivo}")
            
            # Actualizar progreso
            progress_tracker[documento_id] = {
                'estado': 'descargando',
                'progreso': 10,
                'mensaje': 'Descargando archivo...',
                'etapa': 'download'
            }
            
            # 2. Descargar archivo desde MinIO
            from services.minio_service import MinIOService
            minio_service = MinIOService()
            
            # Extraer path de MinIO desde URL
            # URL puede ser: http://minio:9000/sacra360-documents/documents/file.pdf
            # Necesitamos solo la parte: documents/file.pdf
            if '/sacra360-documents/' in imagen_url:
                minio_path = imagen_url.split('/sacra360-documents/')[-1]
            elif '/sacra360-htr/' in imagen_url:
                minio_path = imagen_url.split('/sacra360-htr/')[-1]
            else:
                # Fallback: usar la parte después del bucket
                parts = imagen_url.split('/')
                if len(parts) > 4:
                    minio_path = '/'.join(parts[4:])
                else:
                    minio_path = parts[-1]
            
            logger.info(f"☁️  Descargando desde MinIO: {imagen_url}")
            logger.info(f"📁 Path en bucket: {minio_path}")
            
            contenido = minio_service.download_file(minio_path)
            logger.info(f"✅ Archivo descargado: {len(contenido)} bytes")
            
            # Actualizar progreso
            progress_tracker[documento_id] = {
                'estado': 'procesando_htr',
                'progreso': 15,
                'mensaje': 'Procesando con HTR...',
                'etapa': 'htr'
            }
            
            # 3. Determinar si es PDF
            es_pdf = nombre_archivo.lower().endswith('.pdf')
            
            # 4. Procesar con HTR con callback de progreso
            logger.info("🔍 Iniciando procesamiento HTR...")
            
            def actualizar_progreso_htr(celda_actual, total_celdas):
                """Callback para actualizar progreso durante HTR"""
                # Progreso entre 20% y 80% basado en celdas procesadas
                progreso_htr = 20 + int((celda_actual / total_celdas) * 60)
                mensaje = f'Procesadas {celda_actual}/{total_celdas} celdas (HTR)'
                
                # Actualizar en memoria
                progress_tracker[documento_id] = {
                    'estado': 'procesando_htr',
                    'progreso': progreso_htr,
                    'mensaje': mensaje,
                    'etapa': 'htr'
                }
                
                # Actualizar en BD para persistencia
                try:
                    update_query = text("""
                        UPDATE documento_digitalizado
                        SET progreso_ocr = :progreso,
                            mensaje_progreso = :mensaje
                        WHERE id_documento = :doc_id
                    """)
                    self.db.execute(update_query, {
                        'doc_id': documento_id,
                        'progreso': progreso_htr,
                        'mensaje': mensaje
                    })
                    self.db.commit()
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo guardar progreso en BD: {e}")
            
            resultado_htr_data = self.htr_processor.process_pdf(
                pdf_bytes=contenido,
                progress_callback=actualizar_progreso_htr
            )
            
            # Adaptar respuesta al formato esperado
            resultado_htr = {
                'estado': 'success',
                'mensaje': f'HTR completado: {len(resultado_htr_data)} tuplas extraídas',
                'total_tuplas': len(resultado_htr_data),
                'datos': resultado_htr_data
            }
            
            if resultado_htr['estado'] != 'success':
                progress_tracker[documento_id] = {
                    'estado': 'error',
                    'progreso': 100,
                    'mensaje': f"Error en HTR: {resultado_htr.get('mensaje', 'Error desconocido')}",
                    'etapa': 'error'
                }
                logger.error(f"❌ Error en HTR: {resultado_htr.get('mensaje')}")
                return {
                    'estado': 'error',
                    'mensaje': resultado_htr.get('mensaje', 'Error en procesamiento HTR'),
                    'total_tuplas': 0
                }
            
            logger.info(f"✅ HTR completado: {resultado_htr['total_tuplas']} tuplas extraídas")
            
            # Actualizar progreso
            progress_tracker[documento_id] = {
                'estado': 'guardando',
                'progreso': 85,
                'mensaje': 'Guardando resultados en BD...',
                'etapa': 'save'
            }
            
            # 5. Guardar resultados en ocr_resultado (reutilizamos la tabla)
            total_tuplas = 0
            for tupla_data in resultado_htr['datos']:
                import json
                insert_query = text("""
                    INSERT INTO ocr_resultado (
                        documento_id, tupla_numero, datos_ocr, confianza,
                        fuente_modelo, validado, estado_validacion
                    ) VALUES (
                        :doc_id, :tupla_num, CAST(:datos_json AS jsonb), :conf,
                        :modelo, false, 'pendiente'
                    )
                """)
                
                self.db.execute(insert_query, {
                    'doc_id': documento_id,
                    'tupla_num': tupla_data['tupla_numero'],
                    'datos_json': json.dumps(tupla_data['datos_ocr']),
                    'conf': 0.85,  # Confianza estimada del HTR
                    'modelo': 'HTR_Sacra360'
                })
                total_tuplas += 1
            
            # 6. Actualizar estado del documento
            update_doc = text("""
                UPDATE documento_digitalizado
                SET estado_procesamiento = 'ocr_completado',
                    fecha_procesamiento = NOW(),
                    modelo_fuente = 'HTR_Sacra360',
                    modelo_procesamiento = 'htr',
                    progreso_ocr = 100,
                    mensaje_progreso = 'HTR completado'
                WHERE id_documento = :doc_id
            """)
            
            self.db.execute(update_doc, {"doc_id": documento_id})
            self.db.commit()
            
            # Actualizar progreso final
            progress_tracker[documento_id] = {
                'estado': 'completado',
                'progreso': 100,
                'mensaje': f'HTR completado: {total_tuplas} tuplas extraídas',
                'etapa': 'completed'
            }
            
            logger.info(f"✅ Resultados guardados: {total_tuplas} tuplas")
            logger.info("=" * 70)
            
            return {
                'estado': 'success',
                'mensaje': f'HTR completado exitosamente',
                'total_tuplas': total_tuplas,
                'documento_id': documento_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando documento {documento_id}: {e}", exc_info=True)
            
            progress_tracker[documento_id] = {
                'estado': 'error',
                'progreso': 100,
                'mensaje': f'Error: {str(e)}',
                'etapa': 'error'
            }
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar documento: {str(e)}"
            )
    
    def obtener_progreso(self, documento_id: int) -> Dict[str, Any]:
        """
        Obtiene el progreso actual del procesamiento HTR
        
        Args:
            documento_id: ID del documento
            
        Returns:
            Dict con información de progreso
        """
        # Primero verificar en BD (fuente de verdad)
        query = text("""
            SELECT estado_procesamiento, progreso_ocr, mensaje_progreso
            FROM documento_digitalizado
            WHERE id_documento = :doc_id
        """)
        result = self.db.execute(query, {"doc_id": documento_id}).fetchone()
        
        if not result:
            return {
                'estado': 'no_encontrado',
                'progreso': 0,
                'mensaje': 'Documento no encontrado',
                'etapa': 'none'
            }
        
        estado_bd, progreso_bd, mensaje_bd = result[0], result[1] or 0, result[2] or ''
        
        logger.info(f"📊 Consultando progreso HTR doc {documento_id}: estado_bd={estado_bd}, progreso={progreso_bd}")
        
        # Si está en procesamiento y tiene progreso, devolverlo
        if estado_bd == 'procesando' and progreso_bd > 0:
            respuesta = {
                'estado': 'procesando_htr',
                'progreso': progreso_bd,
                'mensaje': mensaje_bd or f'Procesando HTR: {progreso_bd}%',
                'etapa': 'htr'
            }
            logger.info(f"✅ Devolviendo progreso desde BD: {respuesta}")
            return respuesta
        
        # Si hay info en memoria, usarla
        if documento_id in progress_tracker:
            logger.info(f"✅ Devolviendo progreso desde memoria")
            return progress_tracker[documento_id]
        
        # Mapear estado de BD a respuesta
        if estado_bd == 'ocr_completado':
            return {
                'estado': 'completado',
                'progreso': 100,
                'mensaje': 'Procesamiento HTR completado',
                'etapa': 'completed'
            }
        else:
            return {
                'estado': 'pendiente',
                'progreso': 0,
                'mensaje': 'Esperando procesamiento HTR',
                'etapa': 'pending'
            }

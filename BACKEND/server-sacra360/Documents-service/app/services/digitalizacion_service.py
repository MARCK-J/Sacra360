"""
Servicio de digitalización - Orquestador principal
Maneja el flujo completo: MinIO → BD → OCR → Resultados
"""

import os
import uuid
import time
import requests
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from minio import Minio
from minio.error import S3Error
from io import BytesIO

from app.dto.digitalizacion_dto import (
    UploadDocumentResponse, ProcessingStatusResponse, 
    DocumentListResponse, DocumentoInfo, EstadoProcesamiento,
    OcrResultadoResponse
)

logger = logging.getLogger(__name__)

class DigitalizacionService:
    """Servicio principal para gestión de digitalización"""
    
    def __init__(self):
        # Configuración MinIO
        self.minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        self.minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')
        self.minio_bucket = os.getenv('MINIO_BUCKET', 'sacra360-documents')
        self.minio_secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        
        # URL del OCR Service
        self.ocr_service_url = os.getenv('OCR_SERVICE_URL', 'http://localhost:8003')
        
        # Inicializar cliente MinIO
        self._init_minio_client()
    
    def _init_minio_client(self):
        """Inicializar cliente MinIO"""
        try:
            self.minio_client = Minio(
                endpoint=self.minio_endpoint,
                access_key=self.minio_access_key,
                secret_key=self.minio_secret_key,
                secure=self.minio_secure
            )
            
            # Verificar que el bucket existe
            if not self.minio_client.bucket_exists(self.minio_bucket):
                self.minio_client.make_bucket(self.minio_bucket)
                logger.info(f"Bucket '{self.minio_bucket}' creado")
            else:
                logger.info(f"Bucket '{self.minio_bucket}' ya existe")
                
        except Exception as e:
            logger.error(f"Error inicializando MinIO: {e}")
            raise
    
    async def procesar_documento(
        self, 
        archivo_bytes: bytes,
        archivo_nombre: str,
        content_type: str,
        libro_id: int,
        tipo_sacramento: int,
        institucion_id: int,
        procesar_ocr: bool = True,
        db: Session = None
    ) -> UploadDocumentResponse:
        """
        Procesa un documento completo: MinIO → BD → OCR
        """
        inicio_tiempo = time.time()
        
        try:
            # 1. Subir archivo a MinIO
            logger.info("Subiendo archivo a MinIO...")
            minio_info = await self._subir_a_minio(
                archivo_bytes=archivo_bytes,
                archivo_nombre=archivo_nombre,
                content_type=content_type
            )
            
            # 2. Guardar metadata en BD
            logger.info("Guardando metadata en BD...")
            documento_id = await self._guardar_documento_bd(
                archivo_url=minio_info['url'],
                libro_id=libro_id,
                tipo_sacramento=tipo_sacramento,
                nombre_archivo=archivo_nombre,
                db=db
            )
            
            # 3. Procesar con OCR si se solicita
            ocr_resultado = None
            if procesar_ocr:
                logger.info("Procesando con OCR...")
                ocr_resultado = await self._procesar_ocr(
                    archivo_bytes=archivo_bytes,
                    archivo_nombre=archivo_nombre,
                    content_type=content_type,
                    documento_id=documento_id,
                    libro_id=libro_id,
                    tipo_sacramento=tipo_sacramento
                )
            
            tiempo_total = time.time() - inicio_tiempo
            
            # Preparar respuesta
            response = UploadDocumentResponse(
                success=True,
                documento_id=documento_id,
                mensaje="Documento procesado exitosamente",
                archivo_url=minio_info['url'],
                estado=EstadoProcesamiento.COMPLETADO if procesar_ocr else EstadoProcesamiento.SUBIDO,
                tiempo_upload=tiempo_total,
                ocr_procesado=procesar_ocr and ocr_resultado is not None
            )
            
            if ocr_resultado:
                response.ocr_resultado = ocr_resultado
                response.total_tuplas = ocr_resultado.get('total_tuplas', 0)
                response.calidad_general = ocr_resultado.get('calidad_general', 0)
                response.tiempo_ocr = ocr_resultado.get('tiempo_procesamiento', 0)
                
                # Crear registros de validación para las tuplas OCR
                await self._crear_registros_validacion(
                    documento_id=documento_id,
                    total_tuplas=ocr_resultado.get('total_tuplas', 0),
                    db=db
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando documento: {e}")
            raise
    
    async def _subir_a_minio(
        self, 
        archivo_bytes: bytes, 
        archivo_nombre: str, 
        content_type: str
    ) -> Dict[str, Any]:
        """Sube archivo a MinIO y retorna información"""
        try:
            # Generar nombre único
            extension = os.path.splitext(archivo_nombre)[1]
            unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{extension}"
            object_name = f"documents/{unique_name}"
            
            # Subir archivo
            file_stream = BytesIO(archivo_bytes)
            self.minio_client.put_object(
                bucket_name=self.minio_bucket,
                object_name=object_name,
                data=file_stream,
                length=len(archivo_bytes),
                content_type=content_type
            )
            
            # URL del archivo
            archivo_url = f"http://{self.minio_endpoint}/{self.minio_bucket}/{object_name}"
            
            return {
                'object_name': object_name,
                'url': archivo_url,
                'size': len(archivo_bytes),
                'content_type': content_type
            }
            
        except S3Error as e:
            logger.error(f"Error MinIO: {e}")
            raise Exception(f"Error subiendo archivo a MinIO: {str(e)}")
    
    async def _guardar_documento_bd(
        self, 
        archivo_url: str, 
        libro_id: int, 
        tipo_sacramento: int, 
        db: Session,
        nombre_archivo: Optional[str] = None
    ) -> int:
        """Guarda documento en base de datos y retorna ID"""
        try:
            # Crear registro en documento_digitalizado
            from app.models.documento_model import DocumentoDigitalizadoModel
            
            documento = DocumentoDigitalizadoModel(
                libros_id=libro_id,
                tipo_sacramento=tipo_sacramento,
                imagen_url=archivo_url,
                nombre_archivo=nombre_archivo,
                ocr_texto="",  # Se llenará después del OCR
                modelo_fuente="",  # Se llenará después del OCR
                confianza=0.0,  # Se llenará después del OCR
                fecha_procesamiento=datetime.now(),
                estado_procesamiento='pendiente'
            )
            
            db.add(documento)
            db.commit()
            db.refresh(documento)
            
            return documento.id_documento
            
        except Exception as e:
            logger.error(f"Error guardando en BD: {e}")
            db.rollback()
            raise Exception(f"Error guardando documento en BD: {str(e)}")
    
    async def _procesar_ocr(
        self,
        archivo_bytes: bytes,
        archivo_nombre: str,
        content_type: str,
        documento_id: int,
        libro_id: int,
        tipo_sacramento: int
    ) -> Optional[Dict[str, Any]]:
        """Llama al OCR service para procesar el documento usando endpoint interno"""
        try:
            # Llamar al OCR service endpoint que procesa desde BD
            ocr_url = f"{self.ocr_service_url}/api/v1/ocr/procesar-desde-bd/{documento_id}"
            
            logger.info(f"Llamando OCR service: {ocr_url}")
            
            response = requests.post(
                url=ocr_url,
                timeout=60  # Timeout de 60 segundos
            )
            
            if response.status_code == 200:
                ocr_resultado = response.json()
                logger.info(f"OCR procesado exitosamente. Tuplas: {ocr_resultado.get('total_tuplas', 0)}")
                return ocr_resultado
            else:
                logger.error(f"Error OCR: HTTP {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Timeout llamando al OCR service")
            return None
        except Exception as e:
            logger.error(f"Error procesando OCR: {e}")
            return None
    
    async def _crear_registros_validacion(
        self,
        documento_id: int,
        total_tuplas: int,
        db: Session
    ) -> None:
        """Crea registros de validación para cada tupla del documento"""
        try:
            from app.models.validacion_model import ValidacionTupla
            
            logger.info(f"Creando {total_tuplas} registros de validación para documento {documento_id}")
            
            # Crear un registro de validación para cada tupla
            for tupla_numero in range(1, total_tuplas + 1):
                validacion = ValidacionTupla(
                    documento_id=documento_id,
                    tupla_numero=tupla_numero,
                    estado='pendiente'
                )
                db.add(validacion)
            
            db.commit()
            logger.info(f"Registros de validación creados exitosamente")
            
        except Exception as e:
            logger.error(f"Error creando registros de validación: {e}")
            db.rollback()
            # No lanzamos excepción para no interrumpir el flujo principal
            # pero registramos el error
    
    async def obtener_estado_procesamiento(
        self, 
        documento_id: int, 
        db: Session
    ) -> ProcessingStatusResponse:
        """Obtiene el estado de procesamiento de un documento"""
        try:
            # Buscar documento en BD
            from app.models.documento_model import DocumentoDigitalizadoModel
            
            documento = db.query(DocumentoDigitalizadoModel).filter(
                DocumentoDigitalizadoModel.id_documento == documento_id
            ).first()
            
            if not documento:
                raise Exception(f"Documento {documento_id} no encontrado")
            
            # Determinar estado basado en los datos
            if documento.ocr_texto and documento.ocr_texto != "":
                estado = EstadoProcesamiento.COMPLETADO
                progreso = 100
            else:
                estado = EstadoProcesamiento.SUBIDO
                progreso = 50
            
            return ProcessingStatusResponse(
                documento_id=documento_id,
                estado=estado,
                progreso=progreso,
                mensaje="Documento procesado" if estado == EstadoProcesamiento.COMPLETADO else "Documento subido",
                archivo_url=documento.imagen_url,
                fecha_subida=documento.fecha_procesamiento,
                ocr_completado=bool(documento.ocr_texto),
                calidad_general=float(documento.confianza) if documento.confianza else None
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            raise
    
    async def listar_documentos(
        self,
        libro_id: Optional[int] = None,
        tipo_sacramento: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
        db: Session = None
    ) -> DocumentListResponse:
        """Lista documentos con filtros"""
        try:
            from app.models.documento_model import DocumentoDigitalizadoModel
            
            query = db.query(DocumentoDigitalizadoModel)
            
            if libro_id:
                query = query.filter(DocumentoDigitalizadoModel.libros_id == libro_id)
            if tipo_sacramento:
                query = query.filter(DocumentoDigitalizadoModel.tipo_sacramento == tipo_sacramento)
            
            total = query.count()
            documentos = query.offset(skip).limit(limit).all()
            
            docs_info = []
            for doc in documentos:
                docs_info.append(DocumentoInfo(
                    documento_id=doc.id_documento,
                    libro_id=doc.libros_id,
                    tipo_sacramento=doc.tipo_sacramento or 0,
                    archivo_url=doc.imagen_url,
                    estado=EstadoProcesamiento.COMPLETADO if doc.ocr_texto else EstadoProcesamiento.SUBIDO,
                    fecha_subida=doc.fecha_procesamiento,
                    nombre_archivo=os.path.basename(doc.imagen_url),
                    tamaño_archivo=0,  # TODO: obtener desde MinIO
                    ocr_procesado=bool(doc.ocr_texto),
                    calidad_general=float(doc.confianza) if doc.confianza else None
                ))
            
            return DocumentListResponse(
                documentos=docs_info,
                total=total,
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error listando documentos: {e}")
            raise
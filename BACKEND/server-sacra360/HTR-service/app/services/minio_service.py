"""
MinIO Service for HTR - File storage operations
Usa bucket separado 'sacra360-htr' para archivos procesados con HTR
"""

from minio import Minio
from minio.error import S3Error
import os
import uuid
import logging
from io import BytesIO
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MinIOService:
    """
    Servicio para interactuar con MinIO
    HTR Service usa bucket separado: 'sacra360-htr'
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Configuración desde variables de entorno
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', 'admin')
        self.secret_key = os.getenv('MINIO_SECRET_KEY', 'password123')
        # HTR usa bucket diferente al de OCR
        self.bucket_name = os.getenv('MINIO_HTR_BUCKET', 'sacra360-htr')
        self.secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        
        # Inicializar cliente MinIO
        self.client = None
        MinIOService._initialized = True
    
    def _ensure_connection(self):
        """Inicializar conexión MinIO solo cuando se necesite"""
        if self.client is None:
            self.client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Crear el bucket HTR si no existe"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"✅ Bucket HTR '{self.bucket_name}' creado exitosamente")
            else:
                logger.info(f"✅ Bucket HTR '{self.bucket_name}' ya existe")
        except S3Error as e:
            logger.error(f"❌ Error verificando/creando bucket HTR: {e}")
            raise
    
    def upload_file(self, file_data: bytes, file_name: str, content_type: str = None) -> Dict[str, Any]:
        """ (bucket HTR)
        
        Args:
            object_path: Ruta del objeto en MinIO (ej: "htr-documents/file.pdf")
            
        Returns:
            Bytes del archivo
        """
        self._ensure_connection()
        try:
            logger.info(f"📥 Descargando objeto desde HTR bucket: {object_path}")
            response = self.client.get_object(self.bucket_name, object_path)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"✅ Archivo descargado exitosamente: {object_path}")
            return data
        except S3Error as e:
            logger.error(f"❌ Error descargando archivo desde HTR bucket: {e}")
            raise
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Generar URL presignada temporal para un objeto
        
        Args:
            object_name: Nombre del objeto en MinIO
            expires: Tiempo de expiración en segundos (default: 1 hora)
            
        Returns:
            URL presignada
        """
        self._ensure_connection()
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"❌ Error generando URL presignada: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """
        Eliminar un archivo del bucket HTR
        
        Args:
            object_name: Nombre del objeto a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        self._ensure_connection()
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"✅ Archivo eliminado: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"❌ Error eliminando archivo: {e}")
            return False
    
    def list_files(self, prefix: str = "htr-documents/") -> list:
        """
        Listar archivos en el bucket HTR
        
        Args:
            prefix: Prefijo para filtrar objetos
            
        Returns:
            Lista de objetos
        """
        self._ensure_connection()
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"❌ Error listando archivos: {e}")
            return []
    
    def upload_file(self, object_name: str, file_data: bytes, content_type: str = None) -> str:
        """
        Sube un archivo a MinIO
        
        Args:
            object_name: Nombre del objeto en MinIO
            file_data: Datos del archivo en bytes
            content_type: Tipo MIME del archivo
            
        Returns:
            URL del archivo subido
        """
        self._ensure_connection()
        try:
            # Detectar content_type si no se proporciona
            if not content_type:
                content_type = self._get_content_type(object_name.split('.')[-1])
            
            # Subir archivo
            file_stream = BytesIO(file_data)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_stream,
                length=len(file_data),
                content_type=content_type
            )
            
            # Generar URL del objeto
            object_url = f"http://{self.endpoint}/{self.bucket_name}/{object_name}"
            
            logger.info(f"✅ Archivo subido a HTR bucket: {object_name}")
            
            return {
                "success": True,
                "object_name": object_name,
                "url": object_url,
                "bucket": self.bucket_name,
                "size": len(file_data)
            }
        except S3Error as e:
            logger.error(f"❌ Error subiendo archivo a HTR bucket: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_content_type(self, extension: str) -> str:
        """Determinar content type basado en extensión"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.pdf': 'application/pdf',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }
        return content_types.get(extension.lower(), 'application/octet-stream')
    
    def download_file(self, object_path: str) -> bytes:
        """
        Descarga un archivo desde MinIO
        
        Args:
            object_path: Ruta del objeto en MinIO (ej: "documents/file.pdf")
            
        Returns:
            Bytes del archivo
        """
        self._ensure_connection()
        try:
            logger.info(f"Descargando objeto: {object_path}")
            response = self.client.get_object(self.bucket_name, object_path)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Archivo descargado exitosamente: {object_path}")
            return data
        except S3Error as e:
            logger.error(f"Error descargando archivo: {e}")
            raise

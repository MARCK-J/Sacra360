"""
Servicio de gestión de archivos con MinIO
Maneja subida, descarga y gestión de URLs para documentos
"""
import os
import uuid
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MinioService:
    """Servicio para gestionar archivos en MinIO Object Storage"""
    
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
        self.bucket_name = os.getenv('MINIO_BUCKET', 'sacra360-documents')
        self.secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        
        # Inicializar cliente MinIO
        self.client = None
        MinioService._initialized = True
    
    def _ensure_connection(self):
        """Inicializar conexión MinIO solo cuando se necesite"""
        if self.client is None:
            self.client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Crear el bucket si no existe"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' creado exitosamente")
            else:
                logger.info(f"Bucket '{self.bucket_name}' ya existe")
        except S3Error as e:
            logger.error(f"Error verificando/creando bucket: {e}")
            raise
    
    def upload_file(self, file_data: bytes, file_name: str, content_type: str = None) -> Dict[str, Any]:
        """
        Subir archivo a MinIO
        
        Args:
            file_data: Contenido del archivo en bytes
            file_name: Nombre original del archivo
            content_type: Tipo MIME del archivo
            
        Returns:
            Dict con información del archivo subido
        """
        self._ensure_connection()
        try:
            # Generar nombre único para el archivo
            file_extension = os.path.splitext(file_name)[1]
            unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
            object_name = f"documents/{unique_name}"
            
            # Detectar content_type si no se proporciona
            if not content_type:
                content_type = self._get_content_type(file_extension)
            
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
            
            result = {
                'object_name': object_name,
                'original_name': file_name,
                'url': object_url,
                'size': len(file_data),
                'content_type': content_type,
                'upload_time': datetime.now().isoformat()
            }
            
            logger.info(f"Archivo subido exitosamente: {object_name}")
            return result
            
        except S3Error as e:
            logger.error(f"Error subiendo archivo: {e}")
            raise Exception(f"Error al subir archivo: {str(e)}")
    
    def download_file(self, object_name: str) -> Optional[bytes]:
        """
        Descargar archivo desde MinIO
        
        Args:
            object_name: Nombre del objeto en MinIO
            
        Returns:
            Contenido del archivo en bytes o None si hay error
        """
        self._ensure_connection()
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            
            logger.info(f"Archivo descargado exitosamente: {object_name}")
            return data
            
        except S3Error as e:
            logger.error(f"Error descargando archivo {object_name}: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """
        Eliminar archivo de MinIO
        
        Args:
            object_name: Nombre del objeto en MinIO
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        self._ensure_connection()
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Archivo eliminado exitosamente: {object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Error eliminando archivo {object_name}: {e}")
            return False
    
    def get_presigned_url(self, object_name: str, expires_hours: int = 24) -> Optional[str]:
        """
        Generar URL firmada temporalmente para acceso directo al archivo
        
        Args:
            object_name: Nombre del objeto en MinIO
            expires_hours: Horas de validez de la URL (default 24)
            
        Returns:
            URL firmada o None si hay error
        """
        self._ensure_connection()
        try:
            expires = timedelta(hours=expires_hours)
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            
            logger.info(f"URL presignada generada para: {object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"Error generando URL presignada para {object_name}: {e}")
            return None
    
    def list_files(self, prefix: str = "documents/") -> list:
        """
        Listar archivos en el bucket
        
        Args:
            prefix: Prefijo para filtrar objetos
            
        Returns:
            Lista de objetos en el bucket
        """
        try:
            objects = []
            for obj in self.client.list_objects(self.bucket_name, prefix=prefix):
                objects.append({
                    'object_name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified.isoformat() if obj.last_modified else None,
                    'etag': obj.etag
                })
            
            logger.info(f"Listados {len(objects)} archivos con prefijo: {prefix}")
            return objects
            
        except S3Error as e:
            logger.error(f"Error listando archivos: {e}")
            return []
    
    def _get_content_type(self, file_extension: str) -> str:
        """Determinar content type basado en extensión"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.pdf': 'application/pdf',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')
    
    def get_file_info(self, object_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un archivo en MinIO
        
        Args:
            object_name: Nombre del objeto en MinIO
            
        Returns:
            Dict con información del archivo o None si hay error
        """
        self._ensure_connection()
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            
            return {
                'object_name': object_name,
                'size': stat.size,
                'last_modified': stat.last_modified.isoformat() if stat.last_modified else None,
                'etag': stat.etag,
                'content_type': stat.content_type,
                'metadata': stat.metadata
            }
            
        except S3Error as e:
            logger.error(f"Error obteniendo información del archivo {object_name}: {e}")
            return None

# Instancia global del servicio
minio_service = MinioService()
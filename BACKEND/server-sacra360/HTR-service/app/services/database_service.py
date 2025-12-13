"""
Servicio de base de datos para HTR Service - Sacra360
Usa las mismas tablas que OCR Service con diferenciación por modelo
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from datetime import datetime

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sacra360")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_database() -> Generator[Session, None, None]:
    """Generador de sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseService:
    """Servicio para operaciones de base de datos relacionadas con HTR"""
    
    def __init__(self, db: Session):
        self.db = db
        # Importar aquí para evitar imports circulares
        from ..entities.htr_entity import OcrResultado, DocumentoDigitalizado
        self.OcrResultado = OcrResultado
        self.DocumentoDigitalizado = DocumentoDigitalizado
    
    def guardar_documento(self, imagen_url: str, ocr_texto: str, libros_id: int, 
                         tipo_sacramento: int, modelo_fuente: str, confianza: float,
                         modelo_procesamiento: str = 'htr') -> 'DocumentoDigitalizado':
        """
        Guarda un documento digitalizado en la base de datos
        
        Args:
            imagen_url: URL del documento en MinIO
            ocr_texto: Texto extraído completo
            libros_id: ID del libro al que pertenece
            tipo_sacramento: Tipo de sacramento (1=bautizo, 2=confirmacion, etc.)
            modelo_fuente: Identificador del modelo (ej: "HTR_Sacra360")
            confianza: Nivel de confianza del procesamiento
            modelo_procesamiento: 'htr' o 'ocr'
        """
        documento = self.DocumentoDigitalizado(
            libros_id=libros_id,
            tipo_sacramento=tipo_sacramento,
            imagen_url=imagen_url,
            ocr_texto=ocr_texto,
            modelo_fuente=modelo_fuente,
            confianza=confianza,
            modelo_procesamiento=modelo_procesamiento,
            fecha_procesamiento=datetime.utcnow()
        )
        
        self.db.add(documento)
        self.db.commit()
        self.db.refresh(documento)
        return documento
    
    def actualizar_documento_htr(self, documento_id: int, ocr_texto: str, 
                                modelo_fuente: str, confianza: float):
        """Actualiza un documento existente con resultados HTR"""
        documento = self.db.query(self.DocumentoDigitalizado).filter(
            self.DocumentoDigitalizado.id_documento == documento_id
        ).first()
        
        if documento:
            documento.ocr_texto = ocr_texto
            documento.modelo_fuente = modelo_fuente
            documento.confianza = confianza
            documento.modelo_procesamiento = 'htr'
            documento.fecha_procesamiento = datetime.utcnow()
            self.db.commit()
            self.db.refresh(documento)
            return documento
        else:
            raise Exception(f"Documento {documento_id} no encontrado")
    
    def actualizar_progreso(self, documento_id: int, progreso: int, mensaje: str = None):
        """Actualiza el progreso de procesamiento de un documento"""
        documento = self.db.query(self.DocumentoDigitalizado).filter(
            self.DocumentoDigitalizado.id_documento == documento_id
        ).first()
        
        if documento:
            documento.progreso_ocr = progreso
            if mensaje:
                documento.mensaje_progreso = mensaje
            self.db.commit()
            return documento
        else:
            raise Exception(f"Documento {documento_id} no encontrado")
    
    def guardar_resultado_htr(self, documento_id: int, tupla_numero: int, datos_htr: dict,
                            confianza: float, fuente_modelo: str = "HTR_Sacra360", 
                            validado: bool = False) -> 'OcrResultado':
        """
        Guarda una tupla completa de HTR como un registro JSON
        
        Args:
            documento_id: ID del documento procesado
            tupla_numero: Número de tupla/registro en el documento
            datos_htr: Diccionario con los campos extraídos
            confianza: Nivel de confianza del procesamiento
            fuente_modelo: Identificador del modelo HTR (default: "HTR_Sacra360")
            validado: Si el resultado ha sido validado
        """
        htr_resultado = self.OcrResultado(
            documento_id=documento_id,
            tupla_numero=tupla_numero,
            datos_ocr=datos_htr,  # Nota: campo se llama datos_ocr pero almacena datos HTR
            confianza=confianza,
            fuente_modelo=fuente_modelo,
            validado=validado,
            estado_validacion='pendiente'
        )
        
        self.db.add(htr_resultado)
        self.db.commit()
        self.db.refresh(htr_resultado)
        return htr_resultado
    
    def obtener_documento(self, documento_id: int) -> 'DocumentoDigitalizado':
        """Obtiene un documento por ID"""
        return self.db.query(self.DocumentoDigitalizado).filter(
            self.DocumentoDigitalizado.id_documento == documento_id
        ).first()
    
    def obtener_resultados_htr(self, documento_id: int):
        """Obtiene todos los resultados HTR de un documento"""
        return self.db.query(self.OcrResultado).filter(
            self.OcrResultado.documento_id == documento_id,
            self.OcrResultado.fuente_modelo.like('%HTR%')
        ).all()
    
    def obtener_documentos_por_libro(self, libro_id: int):
        """Obtiene todos los documentos procesados con HTR de un libro"""
        return self.db.query(self.DocumentoDigitalizado).filter(
            self.DocumentoDigitalizado.libros_id == libro_id,
            self.DocumentoDigitalizado.modelo_procesamiento == 'htr'
        ).all()
    
    def validar_resultado(self, id_ocr: int, sacramento_id: int = None):
        """Marca un resultado HTR como validado"""
        resultado = self.db.query(self.OcrResultado).filter(
            self.OcrResultado.id_ocr == id_ocr
        ).first()
        
        if resultado:
            resultado.validado = True
            resultado.estado_validacion = 'validado'
            resultado.fecha_validacion = datetime.utcnow()
            if sacramento_id:
                resultado.sacramento_id = sacramento_id
            self.db.commit()
            self.db.refresh(resultado)
            return resultado
        else:
            raise Exception(f"Resultado HTR {id_ocr} no encontrado")

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
    """Servicio para operaciones de base de datos relacionadas con OCR"""
    
    def __init__(self, db: Session):
        self.db = db
        # Importar aquí para evitar imports circulares
        from ..entities.ocr_entity import OcrResultado, DocumentoDigitalizado
        self.OcrResultado = OcrResultado
        self.DocumentoDigitalizado = DocumentoDigitalizado
    
    def guardar_documento(self, imagen_url: str, ocr_texto: str, libros_id: int, 
                         tipo_sacramento: int, modelo_fuente: str, confianza: float) -> 'DocumentoDigitalizado':
        """Guarda un documento digitalizado en la base de datos"""
        documento = self.DocumentoDigitalizado(
            libros_id=libros_id,
            tipo_sacramento=tipo_sacramento,
            imagen_url=imagen_url,
            ocr_texto=ocr_texto,
            modelo_fuente=modelo_fuente,
            confianza=confianza,
            fecha_procesamiento=datetime.utcnow()
        )
        
        self.db.add(documento)
        self.db.commit()
        self.db.refresh(documento)
        return documento
    
    def actualizar_documento_ocr(self, documento_id: int, ocr_texto: str, 
                                modelo_fuente: str, confianza: float):
        """Actualiza un documento existente con resultados OCR"""
        documento = self.db.query(self.DocumentoDigitalizado).filter(
            self.DocumentoDigitalizado.id_documento == documento_id
        ).first()
        
        if documento:
            documento.ocr_texto = ocr_texto
            documento.modelo_fuente = modelo_fuente
            documento.confianza = confianza
            documento.fecha_procesamiento = datetime.utcnow()
            self.db.commit()
            self.db.refresh(documento)
            return documento
        else:
            raise Exception(f"Documento {documento_id} no encontrado")
    
    def guardar_resultado_ocr(self, documento_id: int, campo: str, valor_extraido: str,
                            confianza: float, fuente_modelo: str, validado: bool = False) -> 'OcrResultado':
        """Alias para mantener compatibilidad"""
        return self.guardar_campo_ocr(
            documento_id=documento_id,
            campo=campo,
            valor_extraido=valor_extraido,
            confianza=confianza,
            fuente_modelo=fuente_modelo,
            validado=validado
        )
    
    def guardar_campo_ocr(self, documento_id: int, campo: str, valor_extraido: str,
                         confianza: float, fuente_modelo: str, validado: bool = False) -> 'OcrResultado':
        """Guarda un campo OCR individual en la base de datos"""
        ocr_resultado = self.OcrResultado(
            documento_id=documento_id,
            campo=campo,
            valor_extraido=valor_extraido,
            confianza=confianza,
            fuente_modelo=fuente_modelo,
            validado=validado
        )
        
        self.db.add(ocr_resultado)
        self.db.commit()
        self.db.refresh(ocr_resultado)
        return ocr_resultado
    
    def obtener_documento(self, documento_id: int) -> 'DocumentoDigitalizado':
        """Obtiene un documento por ID"""
        return self.db.query(self.DocumentoDigitalizado).filter(
            self.DocumentoDigitalizado.id_documento == documento_id
        ).first()
    
    def obtener_resultados_ocr(self, documento_id: int) -> list:
        """Obtiene todos los resultados OCR de un documento"""
        return self.db.query(self.OcrResultado).filter(
            self.OcrResultado.documento_id == documento_id
        ).all()
    
    def validar_campo_ocr(self, ocr_id: int) -> bool:
        """Marca un campo OCR como validado"""
        ocr_resultado = self.db.query(self.OcrResultado).filter(
            self.OcrResultado.id_ocr == ocr_id
        ).first()
        
        if ocr_resultado:
            ocr_resultado.validado = True
            self.db.commit()
            return True
        return False
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
    
    def guardar_resultado_ocr(self, documento_id: int, tupla_numero: int, datos_ocr: dict,
                            confianza: float, fuente_modelo: str, validado: bool = False) -> 'OcrResultado':
        """Guarda una tupla completa de OCR como un registro JSON"""
        ocr_resultado = self.OcrResultado(
            documento_id=documento_id,
            tupla_numero=tupla_numero,
            datos_ocr=datos_ocr,
            confianza=confianza,
            fuente_modelo=fuente_modelo,
            validado=validado
        )
        
        self.db.add(ocr_resultado)
        self.db.commit()
        self.db.refresh(ocr_resultado)
        return ocr_resultado
    
    def guardar_campo_ocr(self, documento_id: int, tupla_numero: int, datos_ocr: dict,
                         confianza: float, fuente_modelo: str, validado: bool = False) -> 'OcrResultado':
        """Alias para mantener compatibilidad - guarda tupla completa"""
        return self.guardar_resultado_ocr(
            documento_id=documento_id,
            tupla_numero=tupla_numero,
            datos_ocr=datos_ocr,
            confianza=confianza,
            fuente_modelo=fuente_modelo,
            validado=validado
        )
    
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
    
    def guardar_documento_completo(self, archivo_nombre: str, archivo_url: str, 
                            tuplas: list, total_tuplas: int) -> int:
        """
        Guarda un resultado completo de OCR V2
        
        Args:
            archivo_nombre: Nombre del archivo procesado
            archivo_url: URL del archivo en MinIO
            tuplas: Lista de tuplas extraídas (cada tupla es una lista de 10 valores)
            total_tuplas: Número total de tuplas
            
        Returns:
            ID del documento guardado
        """
        # Primero crear el documento digitalizado
        documento = self.DocumentoDigitalizado(
            libros_id=-1,  # Valor temporal - se asignará después
            tipo_sacramento=1,  # Confirmación por defecto
            imagen_url=archivo_url,
            ocr_texto="",  # No se usa en V2
            modelo_fuente="EasyOCR V2",
            confianza=0.95,  # Confianza por defecto para V2
            fecha_procesamiento=datetime.utcnow()
        )
        
        self.db.add(documento)
        self.db.commit()
        self.db.refresh(documento)
        
        documento_id = documento.id_documento
        
        # Guardar cada tupla como un registro OCR
        for idx, tupla in enumerate(tuplas, 1):
            # Convertir tupla a dict con nombres de columnas
            datos_ocr = {
                'col1': tupla[0] if len(tupla) > 0 else '',
                'col2': tupla[1] if len(tupla) > 1 else '',
                'col3': tupla[2] if len(tupla) > 2 else '',
                'col4': tupla[3] if len(tupla) > 3 else '',
                'col5': tupla[4] if len(tupla) > 4 else '',
                'col6': tupla[5] if len(tupla) > 5 else '',
                'col7': tupla[6] if len(tupla) > 6 else '',
                'col8': tupla[7] if len(tupla) > 7 else '',
                'col9': tupla[8] if len(tupla) > 8 else '',
                'col10': tupla[9] if len(tupla) > 9 else ''
            }
            
            ocr_resultado = self.OcrResultado(
                documento_id=documento_id,
                tupla_numero=idx,
                datos_ocr=datos_ocr,
                confianza=0.95,
                fuente_modelo="EasyOCR V2",
                validado=False
            )
            
            self.db.add(ocr_resultado)
        
        self.db.commit()
        
        return documento_id
    
    def obtener_resultado_por_id(self, documento_id: int) -> dict:
        """
        Obtiene el resultado completo de un documento procesado
        
        Args:
            documento_id: ID del documento
            
        Returns:
            Dict con información del documento y tuplas
        """
        # Obtener documento
        documento = self.db.query(self.DocumentoDigitalizado).filter(
            self.DocumentoDigitalizado.id_documento == documento_id
        ).first()
        
        if not documento:
            return None
        
        # Obtener resultados OCR
        resultados_ocr = self.db.query(self.OcrResultado).filter(
            self.OcrResultado.documento_id == documento_id
        ).order_by(self.OcrResultado.tupla_numero).all()
        
        # Convertir a tuplas
        tuplas = []
        for resultado in resultados_ocr:
            datos = resultado.datos_ocr
            tupla = [
                datos.get('col1', ''),
                datos.get('col2', ''),
                datos.get('col3', ''),
                datos.get('col4', ''),
                datos.get('col5', ''),
                datos.get('col6', ''),
                datos.get('col7', ''),
                datos.get('col8', ''),
                datos.get('col9', ''),
                datos.get('col10', '')
            ]
            tuplas.append(tupla)
        
        return {
            'documento_id': documento.id_documento,
            'archivo_nombre': archivo_nombre,
            'archivo_url': documento.imagen_url,
            'total_tuplas': len(tuplas),
            'tuplas': tuplas,
            'fecha_procesamiento': documento.fecha_procesamiento.isoformat() if documento.fecha_procesamiento else None,
            'modelo_fuente': documento.modelo_fuente,
            'confianza': documento.confianza
        }
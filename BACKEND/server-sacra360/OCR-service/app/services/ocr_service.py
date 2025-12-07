"""
Servicio OCR Principal - Sacra360
Wrapper simplificado que utiliza OCRv2 con EasyOCR
"""

import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..dto.ocr_dto import (
    OcrProcessResponse, OcrTuplaResponse, OcrCampoResponse
)
from .database_service import DatabaseService
from .ocr_v2_processor import OcrV2Processor

logger = logging.getLogger(__name__)

class OcrService:
    """Servicio principal para procesamiento OCR - usa OCRv2 con EasyOCR"""
    
    def __init__(self):
        self.ocr_v2_processor = OcrV2Processor()
        self.modelo_fuente = "Sacra360_OCRv2_EasyOCR_v2.0"
        logger.info(f"OcrService inicializado con modelo: {self.modelo_fuente}")
    
    def procesar_imagen(self, imagen_bytes: bytes, libros_id: int, 
                       tipo_sacramento: int = 2, guardar_en_bd: bool = True,
                       db_service: Optional[DatabaseService] = None,
                       minio_info: Optional[Dict] = None,
                       es_pdf: bool = False) -> OcrProcessResponse:
        """Procesa imagen o PDF con OCRv2"""
        inicio_tiempo = time.time()
        
        try:
            logger.info(f"🚀 Iniciando OCRv2. PDF: {es_pdf}, Libro: {libros_id}")
            
            # Ejecutar OCRv2
            resultado_v2 = self.ocr_v2_processor.procesar_documento_completo(
                imagen_bytes, 
                es_pdf=es_pdf
            )
            
            if not resultado_v2["success"]:
                raise ValueError(f"Error OCRv2: {resultado_v2.get('error', 'Desconocido')}")
            
            tuplas_procesadas = resultado_v2["tuplas"]
            logger.info(f"✅ OCRv2: {len(tuplas_procesadas)} tuplas extraídas")
            
            # Calcular calidad
            calidad_general, tuplas_alta_calidad = self._calcular_calidad(tuplas_procesadas)
            
            # Guardar en BD si se requiere
            documento_id = None
            if guardar_en_bd and db_service:
                imagen_url = minio_info.get('url', '') if minio_info else ''
                documento_id = self._guardar_en_bd(
                    tuplas_procesadas, libros_id, tipo_sacramento, 
                    calidad_general, db_service, imagen_url
                )
            
            # Formato de respuesta
            tuplas_response = self._convertir_a_response(tuplas_procesadas)
            tiempo_total = time.time() - inicio_tiempo
            
            return OcrProcessResponse(
                success=True,
                documento_id=documento_id,
                total_tuplas=len(tuplas_procesadas),
                tuplas=tuplas_response,
                calidad_general=calidad_general,
                tuplas_alta_calidad=tuplas_alta_calidad,
                modelo_utilizado=self.modelo_fuente,
                tiempo_procesamiento=tiempo_total,
                fecha_procesamiento=datetime.utcnow(),
                message=f"✅ {len(tuplas_procesadas)} tuplas procesadas"
            )
            
        except Exception as e:
            logger.error(f"❌ Error OCRv2: {str(e)}", exc_info=True)
            return OcrProcessResponse(
                success=False,
                documento_id=None,
                total_tuplas=0,
                tuplas=[],
                calidad_general=0.0,
                tuplas_alta_calidad=0,
                modelo_utilizado=self.modelo_fuente,
                tiempo_procesamiento=time.time() - inicio_tiempo,
                fecha_procesamiento=datetime.utcnow(),
                message="Error OCR",
                error=str(e)
            )
    
    def _calcular_calidad(self, tuplas: List[Dict]) -> tuple:
        """Calcula métricas de calidad"""
        if not tuplas:
            return 0.0, 0
        
        total_celdas = 0
        celdas_llenas = 0
        tuplas_buenas = 0
        
        for tupla in tuplas:
            celdas = tupla.get('celdas', [])
            llenas = sum(1 for c in celdas if c and str(c).strip())
            total_celdas += len(celdas)
            celdas_llenas += llenas
            
            if len(celdas) > 0 and (llenas / len(celdas)) >= 0.7:
                tuplas_buenas += 1
        
        calidad = celdas_llenas / total_celdas if total_celdas > 0 else 0.0
        return calidad, tuplas_buenas
    
    def _guardar_en_bd(self, tuplas: List[Dict], libros_id: int, 
                       tipo_sacramento: int, calidad: float,
                       db_service: DatabaseService, imagen_url: str) -> int:
        """Guarda resultados en base de datos"""
        
        # Texto OCR consolidado
        ocr_texto = json.dumps({
            "total_tuplas": len(tuplas),
            "calidad_general": calidad,
            "tuplas": tuplas
        }, ensure_ascii=False, indent=2)
        
        # Guardar documento
        documento = db_service.guardar_documento(
            imagen_url=imagen_url or "no_url",
            ocr_texto=ocr_texto,
            libros_id=libros_id,
            tipo_sacramento=tipo_sacramento,
            modelo_fuente=self.modelo_fuente,
            confianza=calidad
        )
        
        # Guardar tuplas individuales
        for tupla in tuplas:
            tupla_num = tupla.get('tupla_numero', 0)
            campos = tupla.get('campos', {})
            celdas = tupla.get('celdas', [])
            
            # Calcular confianza de tupla
            llenas = sum(1 for c in celdas if c and str(c).strip())
            confianza_tupla = llenas / len(celdas) if celdas else 0.0
            
            # Guardar
            db_service.guardar_resultado_ocr(
                documento_id=documento.id_documento,
                tupla_numero=tupla_num,
                datos_ocr=campos,
                confianza=confianza_tupla,
                fuente_modelo=self.modelo_fuente,
                validado=False
            )
        
        return documento.id_documento
    
    def _convertir_a_response(self, tuplas: List[Dict]) -> List[OcrTuplaResponse]:
        """Convierte tuplas a formato de respuesta"""
        response_tuplas = []
        
        for tupla in tuplas:
            campos = tupla.get('campos', {})
            celdas = tupla.get('celdas', [])
            
            # Calcular confianza
            llenas = sum(1 for c in celdas if c and str(c).strip())
            conf = llenas / len(celdas) if celdas else 0.0
            
            # Crear campos de respuesta
            tupla_response = OcrTuplaResponse(
                tupla_numero=tupla.get('tupla_numero', 0),
                confirmando=OcrCampoResponse(
                    id_ocr=None,
                    campo="nombre_confirmando",
                    valor_extraido=campos.get('nombre_confirmando', ''),
                    confianza=conf,
                    fuente_modelo=self.modelo_fuente,
                    validado=False
                ),
                fecha_nacimiento=OcrCampoResponse(
                    id_ocr=None,
                    campo="fecha_nacimiento",
                    valor_extraido=f"{campos.get('dia_nacimiento','')}/{campos.get('mes_nacimiento','')}/{campos.get('ano_nacimiento','')}",
                    confianza=conf,
                    fuente_modelo=self.modelo_fuente,
                    validado=False
                ),
                parroquia_bautismo=OcrCampoResponse(
                    id_ocr=None,
                    campo="parroquia_bautismo",
                    valor_extraido=campos.get('parroquia_bautismo', ''),
                    confianza=conf,
                    fuente_modelo=self.modelo_fuente,
                    validado=False
                ),
                fecha_bautismo=OcrCampoResponse(
                    id_ocr=None,
                    campo="fecha_bautismo",
                    valor_extraido=f"{campos.get('dia_bautismo','')}/{campos.get('mes_bautismo','')}/{campos.get('ano_bautismo','')}",
                    confianza=conf,
                    fuente_modelo=self.modelo_fuente,
                    validado=False
                ),
                padres=OcrCampoResponse(
                    id_ocr=None,
                    campo="padres",
                    valor_extraido=campos.get('padres', ''),
                    confianza=conf,
                    fuente_modelo=self.modelo_fuente,
                    validado=False
                ),
                padrinos=OcrCampoResponse(
                    id_ocr=None,
                    campo="padrinos",
                    valor_extraido=campos.get('padrinos', ''),
                    confianza=conf,
                    fuente_modelo=self.modelo_fuente,
                    validado=False
                ),
                calidad_general=conf,
                coordenadas=None
            )
            
            response_tuplas.append(tupla_response)
        
        return response_tuplas

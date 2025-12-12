"""
HTR Processor - Código EXACTO del notebook HTR_Sacra360_Colab_Final.ipynb
Este código ha sido probado y funciona correctamente en el entorno local.

Versiones de librerías utilizadas (CRÍTICO):
- opencv-python-headless==4.12.0.88
- numpy==2.2.0
- pandas==2.2.3
- easyocr==1.7.2
- pdf2image==1.17.0
- Pillow==10.0.1
- torch==2.2.0+cpu
- torchvision==0.17.0+cpu
- Poppler: 22.02.0 (Ubuntu 22.04)
"""

import cv2
import numpy as np
import pandas as pd
import easyocr
import json
import re
import difflib
from pdf2image import convert_from_bytes
from typing import Dict, Any, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class BolivianContext:
    """Diccionario ampliado con nombres y lugares comunes de Bolivia"""
    
    def __init__(self):
        self.APELLIDOS = [
            "QUISPE", "MAMANI", "FLORES", "CONDORI", "CHOQUE", "VARGAS", "GUTIERREZ",
            "ROJAS", "LOPEZ", "CRUZ", "ALIAGA", "COLQUE", "OROZCO", "CHURQUI",
            "LANDAETA", "CHAVEZ", "COLLAO", "LUNA", "BUSTILLOS", "CHACON", "CUTILI",
            "LINARES", "PATI", "ARGANDOÑA", "DELGADILLO", "ESPEJO", "SIRPA", "PRIMY",
            "MENDIETA", "AGUILERA", "PALMA", "LLAMPA", "CALLISAYA", "GONZALES",
            "TANGARA", "RODRIGUEZ", "MORALES", "RIVERO", "SIÑANI", "URIARTE", "SUXO",
            "CARREÑO", "LIMA", "ESPADA", "LARREA", "ORMACHEA", "ALVAREZ", "PEREZ",
            "MARIACA", "ESTRADA", "GUACHALLA", "VERA", "MARQUEZ", "ANCASI", "PARI",
            "ALABY", "ALAVI", "NAVIA", "CORNEJO", "LUNARIO", "ANTEZANA", "RIVERA",
            "MEJIA", "VALVERDE", "YAVE", "VILELA", "DORADO", "SIDNEY", "MIRANDA",
            "PEÑALOZA", "PALACIOS", "LIZARAZU", "REVOLLO", "BOGADO", "MONASTERIOS",
            "ZAPANA", "ORIHUELA", "GOSALVEZ", "QUISBERT", "OCXA", "SILVA", "RAMOS",
            "ARUQUIPA", "MAURICIO", "RICALDI", "SALINAS", "VILLALTA", "VELARDE", "GAMARRA",
            "FERNANDEZ", "GARCIA", "MARTINEZ", "SANCHEZ", "RAMIREZ", "TORRES", "DIAZ",
            "HERRERA", "MEDINA", "CASTRO", "ROMERO", "SOTO", "CONTRERAS", "JIMENEZ"
        ]

        self.NOMBRES = [
            "JUAN", "MARIA", "JOSE", "LUIS", "ANA", "CARLOS", "ROSA", "MIGUEL",
            "JORGE", "ELIZABETH", "GERALDINE", "ANGELA", "MICAELA", "LIZETH",
            "ILSEN", "SUMEY", "LIVIA", "VIOLETA", "ILSE", "PATRICIA", "LUZ",
            "MARINA", "NAYELI", "BRIGITTE", "HELEN", "NINEL", "TATIANA", "MARIO",
            "JHENY", "RUBEN", "MARCELO", "CAROLA", "FRANKLIN", "JANNETTE",
            "ROSARIO", "HUGO", "AQUINO", "LAURA", "ORLANDO", "ENRIQUE", "FABIOLA",
            "STEPHANIA", "PETER", "EDGAR", "ROY", "ANGEL", "XIMENA", "GERMAN",
            "MARGARITA", "FRANCO", "EDWIN", "HUMBERTO", "HILARIA", "ADRIAN",
            "VICTOR", "SILVIA", "AMOROSA", "GUILLERMO", "NICOLE", "MACIEL",
            "OSMAR", "ZOBEIDA", "IVON", "ALAN", "IVAN", "NESTOR", "JAVIER",
            "FREDDY", "JHOSELIN", "BELEN", "RONALD", "XAVIER", "GILKA", "CARLO",
            "FELIPE", "ANDREE", "HIRIBERTO", "ELVIRA", "MOISES", "ALEXIS", "MITZI",
            "CAMILA", "GIOVANNA", "SANDRO", "SAUL", "CLIVER", "DELMA", "ALEJANDRA",
            "ALEX", "NINETT", "VIVIANA", "VANIA", "PABLO", "ANTONIO", "IVER",
            "RONAL", "TERESA", "MAGDA", "JOAQUIN", "MARLENY", "ROSEMERY", "NORKA",
            "SAMANTHA", "MICHELLE", "EDDY", "MICHAEL", "CECILIA", "GABRIELA",
            "GUSTAVO", "RODOLFO", "PEDRO", "SANTIAGO", "DIEGO", "FERNANDO", "RICARDO",
            "DANIEL", "ANDRES", "MANUEL", "FRANCISCO", "RAUL", "SERGIO", "ROBERTO"
        ]

        self.LUGARES = [
            "LA PAZ", "EL ALTO", "SAN PEDRO", "NUEVA PAZ", "SAN ANTONIO",
            "PADUA", "FATIMA", "SAN SEBASTIAN", "LA MERCED", "SANTO DOMINGO",
            "SANTA CRUZ", "COCHABAMBA", "ORURO", "POTOSI", "TARIJA",
            "SUCRE", "BENI", "PANDO", "CHUQUISACA"
        ]

    def correct_text(self, raw_text, category="GENERAL"):
        if not raw_text or len(raw_text) < 2:
            return raw_text

        raw_upper = raw_text.upper().strip()
        words = raw_upper.split()
        corrected_words = []

        # Seleccionar diccionario según categoría
        if category == "LUGAR":
            dictionary = self.LUGARES
            threshold = 0.7
        else:
            dictionary = self.NOMBRES + self.APELLIDOS
            threshold = 0.75

        # Corrección por similitud
        for word in words:
            if len(word) <= 2:
                corrected_words.append(word)
                continue

            matches = difflib.get_close_matches(word, dictionary, n=1, cutoff=threshold)
            if matches:
                corrected_words.append(matches[0])
            else:
                corrected_words.append(word)

        return " ".join(corrected_words)


class GridDetector:
    """Detecta estructura de tabla con 10 columnas fijas - VERSIÓN DEL NOTEBOOK"""
    
    def __init__(self):
        self.debug_mode = False
        self.TARGET_COLS = 10

    def get_structure(self, img):
        logger.info("   📐 Detectando estructura (10 Columnas Fijas)...")

        H, W = img.shape[:2]
        logger.info(f"   📏 Dimensiones: {W}x{H}")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY_INV, 11, 2)

        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (W // 30, 1))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, H // 40))

        h_lines = cv2.dilate(cv2.erode(thresh, h_kernel), h_kernel)
        v_lines = cv2.dilate(cv2.erode(thresh, v_kernel), v_kernel)

        # FILAS (YS)
        raw_ys = self.find_peaks(h_lines, 1)
        ys = self.merge_lines(raw_ys, thr=20)

        # COLUMNAS (XS)
        raw_xs = np.sum(v_lines, axis=0)
        peak_indices = np.where(raw_xs > np.max(raw_xs) * 0.1)[0]
        candidate_lines = self.merge_lines(list(peak_indices), thr=20)
        
        logger.info(f"   🔍 Líneas candidatas antes de forzar: {len(candidate_lines)}")
        
        # Forzar 11 líneas (10 columnas)
        if len(candidate_lines) > 11:
            line_strengths = []
            for x in candidate_lines:
                start = max(0, x - 5)
                end = min(len(raw_xs), x + 5)
                strength = np.sum(raw_xs[start:end])
                line_strengths.append((x, strength))
            
            line_strengths.sort(key=lambda item: item[1], reverse=True)
            top_lines = line_strengths[:11]
            top_lines.sort(key=lambda item: item[0])
            xs = [x for x, s in top_lines]
            logger.info(f"   ✂️ Reducidas de {len(candidate_lines)} a 11 líneas (10 columnas)")
        else:
            xs = candidate_lines

        # Asegurar bordes
        if not ys or ys[0] > 50: ys.insert(0, 0)
        if ys[-1] < H - 50: ys.append(H)
        
        if not xs or xs[0] > 50: xs.insert(0, 0)
        if xs[-1] < W - 50: xs.append(W)

        logger.info(f"   📍 Columnas detectadas: {len(xs)-1} (objetivo: 10)")
        logger.info(f"   📍 Filas detectadas: {len(ys)-1}")

        # Guardar imagen de debug
        self._save_debug_image(img, xs, ys)

        return ys, xs

    def find_peaks(self, mask, axis):
        proj = np.sum(mask, axis=axis)
        return sorted(list(np.where(proj > np.max(proj) * 0.2)[0]))

    def merge_lines(self, lines, thr=20):
        if len(lines) == 0: return []
        merged = [lines[0]]
        for x in lines[1:]:
            if x - merged[-1] > thr:
                merged.append(x)
        return merged

    def _save_debug_image(self, img, xs, ys):
        """Guarda imagen con grid dibujado para debugging"""
        try:
            import tempfile
            import os
            
            debug_img = img.copy()
            
            # Dibujar líneas horizontales (filas) en verde
            for y in ys:
                cv2.line(debug_img, (0, y), (img.shape[1], y), (0, 255, 0), 2)
            
            # Dibujar líneas verticales (columnas) en rojo
            for x in xs:
                cv2.line(debug_img, (x, 0), (x, img.shape[0]), (0, 0, 255), 2)
            
            # Guardar en /tmp del contenedor
            debug_path = "/tmp/htr_grid_debug.jpg"
            cv2.imwrite(debug_path, debug_img)
            logger.info(f"   🖼️ Grid debug guardado en: {debug_path}")
            logger.info(f"   💡 Copia con: docker cp sacra360_htr_service:/tmp/htr_grid_debug.jpg .")
            
        except Exception as e:
            logger.warning(f"   ⚠️ No se pudo guardar imagen de debug: {e}")


class ManuscriptOCR:
    """Motor OCR optimizado para texto manuscrito"""
    
    def __init__(self):
        logger.info("   🔧 Inicializando EasyOCR...")
        # Inicializar solo los idiomas necesarios
        self.reader = easyocr.Reader(['es'], gpu=False) # GPU False para Docker general, True si tienes soporte CUDA
        self.corrector = BolivianContext()
        self.scale_factor = 2.5 

    def preprocess_cell(self, cell_img):
        if cell_img.shape[0] < 8 or cell_img.shape[1] < 8: return None
        gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = cv2.resize(gray, None, fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_CUBIC)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        binary = cv2.dilate(binary, kernel, iterations=1)
        binary = cv2.copyMakeBorder(binary, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=255)
        return binary

    def read_cell(self, cell_img, col_type="text"):
        processed = self.preprocess_cell(cell_img)
        if processed is None: return ""

        allowlist = '0123456789/' if col_type == "date" else None

        try:
            results = self.reader.readtext(processed, detail=0, paragraph=False, allowlist=allowlist)
            raw_text = " ".join(results).strip()

            if not raw_text:
                results = self.reader.readtext(cell_img, detail=0, paragraph=False)
                raw_text = " ".join(results).strip()

            if col_type == "date":
                return self._format_date(raw_text)
            else:
                return self.corrector.correct_text(raw_text, "GENERAL")

        except Exception as e:
            logger.error(f"Error OCR en celda: {str(e)}")
            return ""

    def _format_date(self, text):
        text = text.upper().replace('O', '0').replace('D', '0').replace('B', '8').replace('S', '5')
        nums = re.sub(r'[^\d]', '', text)
        if len(nums) == 6: return f"{nums[:2]}/{nums[2:4]}/{nums[4:]}"
        elif len(nums) == 8: return f"{nums[:2]}/{nums[2:4]}/{nums[4:8]}"
        return nums if nums else text


class HybridHTRProcessor:
    """Procesador híbrido - Código EXACTO del notebook"""
    
    def __init__(self):
        self.grid_detector = GridDetector()
        self.ocr_engine = ManuscriptOCR()
        self.min_chars_per_row = 3
        self.FIXED_PATTERN = ['text', 'date', 'date', 'date', 'text', 'date', 'date', 'date', 'text', 'text']

    def process_pdf(self, pdf_bytes: bytes, progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Dict[str, Any]]:
        """Procesa un archivo PDF"""
        try:
            logger.info("📄 Convirtiendo PDF a imagen...")
            images = convert_from_bytes(pdf_bytes, dpi=200)
            
            if not images:
                raise ValueError("No se pudieron extraer imágenes del PDF")
                
            pil_image = images[0]
            img = np.array(pil_image)
            
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # FORZAR DIMENSIONES EXACTAS DEL NOTEBOOK: (alto=3965, ancho=8038)
            # Esto garantiza procesamiento idéntico entre Docker y notebook local
            target_height, target_width = 3965, 8038
            current_h, current_w = img.shape[:2]
            
            if current_h != target_height or current_w != target_width:
                logger.info(f"🔄 Resizing: {current_w}x{current_h} → {target_width}x{target_height}")
                img = cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_AREA)
            else:
                logger.info(f"✅ Dimensiones correctas: {current_w}x{current_h}")

            return self.process_image(img, progress_callback)
            
        except Exception as e:
            logger.error(f"Error procesando PDF: {str(e)}")
            raise

    def process_image(self, img: np.ndarray, progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Dict[str, Any]]:
        logger.info("\n" + "="*70)
        logger.info("   🚀 PROCESAMIENTO HTR - VERSIÓN NOTEBOOK")
        logger.info("="*70)

        # Detección de Estructura
        logger.info("\n[PASO 1] Detección de estructura")
        ys, xs = self.grid_detector.get_structure(img)

        logger.info("\n[PASO 2] Lectura OCR y Filtrado")
        data = []
        real_row_idx = 1
        
        start_idx = 0
        if len(ys) > 1 and (ys[1] - ys[0] < 100):
            start_idx = 1
        
        # Lógica de alternancia
        expect_noise_next = False
        prev_row_height = 0
        total_rows = len(ys) - 1 - start_idx

        for i in range(start_idx, len(ys) - 1):
            y1, y2 = ys[i], ys[i + 1]
            row_height = y2 - y1

            # Filtro básico
            if row_height < 20:
                continue

            # Lógica de alternancia
            if expect_noise_next:
                if prev_row_height > 0 and row_height < (prev_row_height * 0.75):
                    logger.info(f"   ⏭️ Fila {i+1} SALTADA (Ruido/Separación detectada: {row_height}px)")
                    expect_noise_next = False
                    continue
                else:
                    logger.info(f"   ⚠️ Fila {i+1} (Esperaba ruido, pero es alta {row_height}px. Procesando...)")

            logger.info(f"   📝 Proc. Fila {real_row_idx} (h={row_height}px)...")

            temp_row = []
            row_text_content = ""

            max_cols = min(len(xs) - 1, len(self.FIXED_PATTERN))

            for j in range(max_cols):
                x1, x2 = xs[j], xs[j + 1]
                cell = img[y1+2:y2-2, x1+2:x2-2]
                
                c_type = self.FIXED_PATTERN[j]
                text = self.ocr_engine.read_cell(cell, col_type=c_type)
                
                if c_type == "text":
                    row_text_content += text

                temp_row.append({
                    "col": j + 1,
                    "tipo": "L" if c_type == "text" else "N",
                    "valor": text
                })
                
                if progress_callback:
                    current_cell = (i - start_idx) * max_cols + (j + 1)
                    total_cells = total_rows * max_cols
                    pct = 10 + int((current_cell / total_cells) * 80)
                    progress_callback(pct, total_cells)

            # Validar contenido
            clean_content = re.sub(r'[\d\s]', '', row_text_content)
            if len(row_text_content.strip()) < 3 and len(clean_content) < 2:
                logger.info("❌ VACÍA (ignorada)")
                expect_noise_next = False
                continue

            logger.info("✅ VÁLIDA")
            
            datos_json = {}
            for item in temp_row:
                col_num = item['col'] - 1  # Convertir a 0-indexed
                
                # OMITIR col_4 (parroquia) - no se valida en frontend
                if col_num == 4:
                    continue
                    
                # Usar col_0, col_1, col_2... igual que OCR-service
                col_key = f"col_{col_num}"
                datos_json[col_key] = item['valor']

            data.append({
                "tupla_numero": real_row_idx,
                "datos_ocr": datos_json
            })
            
            real_row_idx += 1
            expect_noise_next = True
            prev_row_height = row_height

        logger.info(f"\n{'='*70}")
        logger.info(f"   ✅ COMPLETADO: {len(data)} filas válidas extraídas")
        
        return data


# Alias para compatibilidad con código existente
HTRProcessor = HybridHTRProcessor
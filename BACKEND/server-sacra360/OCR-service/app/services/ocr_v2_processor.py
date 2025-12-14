"""
OCRv2 Processor - Implementación del modelo Sacra360_OCRv2
Basado en el notebook: Sacra360_OCRv2.ipynb

Este procesador implementa el flujo completo:
1. Conversión de PDF a imagen
2. Detección de tabla con OpenCV
3. Extracción de celdas
4. Preprocesamiento de imágenes
5. OCR con EasyOCR
6. Validación de patrón y corrección
"""

import cv2
import numpy as np
import pandas as pd
import os
import shutil
import logging
from typing import List, Tuple, Dict, Any
import easyocr
from pathlib import Path

logger = logging.getLogger(__name__)


class OcrV2Processor:
    """Procesador OCRv2 para extracción de tablas de documentos sacramentales"""
    
    def __init__(self):
        """Inicializa el procesador OCRv2"""
        self.temp_dir = "temp"
        self.temp_preprocessed_dir = "temp_preprocessed"
        self.num_cols = 10  # Número de columnas esperadas en la tabla
        self.pattern = ['L','N','N','N','L','N','N','N','L','L']  # Patrón esperado
        self._reader = None
        
        logger.info("✅ OCRv2Processor inicializado")
    
    @property
    def reader(self):
        """Lazy loading de EasyOCR reader"""
        if self._reader is None:
            logger.info("🔧 Inicializando EasyOCR...")
            import platform
            
            # En Windows solo funciona con CPU
            if platform.system() == 'Windows':
                logger.info("💻 Windows detectado - usando CPU")
                self._reader = easyocr.Reader(
                    ['en'], 
                    gpu=False,
                    verbose=False,
                    download_enabled=True
                )
            else:
                # En Linux intentar GPU
                try:
                    self._reader = easyocr.Reader(
                        ['en'], 
                        gpu=True,
                        verbose=False,
                        download_enabled=True
                    )
                    logger.info("✅ EasyOCR con GPU")
                except:
                    logger.warning("⚠️  GPU no disponible, usando CPU")
                    self._reader = easyocr.Reader(
                        ['en'], 
                        gpu=False,
                        verbose=False,
                        download_enabled=True
                    )
            
            logger.info("✅ EasyOCR inicializado")
        
        return self._reader
    
    def crear_carpetas_temporales(self):
        """Crea las carpetas temporales necesarias"""
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.temp_preprocessed_dir, exist_ok=True)
    
    def limpiar_carpetas_temporales(self):
        """Elimina las carpetas temporales"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if os.path.exists(self.temp_preprocessed_dir):
            shutil.rmtree(self.temp_preprocessed_dir)
    
    def convertir_pdf_a_imagen(self, pdf_bytes: bytes, dpi: int = 150) -> np.ndarray:
        """
        Convierte PDF a imagen (primera página)
        Usa PyMuPDF (fitz) que no requiere poppler
        """
        logger.info(f"📄 Convirtiendo PDF a imagen (DPI={dpi})...")
        
        try:
            import fitz  # PyMuPDF
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = pdf_document[0]  # Primera página
            
            # Calcular zoom para DPI deseado
            zoom = dpi / 72  # 72 DPI es el default de PDF
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convertir a numpy array
            img_rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            
            # Convertir RGB a BGR para OpenCV
            if pix.n == 4:  # RGBA
                img = cv2.cvtColor(img_rgb, cv2.COLOR_RGBA2BGR)
            else:  # RGB
                img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            
            pdf_document.close()
            logger.info(f"✅ PDF convertido. Dimensiones: {img.shape}")
            return img
            
        except Exception as e:
            logger.error(f"❌ Error al convertir PDF: {e}")
            raise
    
    def detectar_y_extraer_tabla(self, img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta la tabla y extrae las celdas
        Implementación del notebook: células 4 y 5
        """
        logger.info("🔍 Detectando tabla...")
        
        # Convertir a escala de grises y aplicar threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)[1]
        
        # Detectar líneas horizontales y verticales
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 1))
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 100))
        
        horiz = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_h)
        vert = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_v)
        
        # Combinar líneas para crear máscara de tabla
        table_mask = horiz + vert
        
        # Dilatar para conectar componentes
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        table_mask = cv2.dilate(table_mask, kernel_dilate, iterations=1)
        
        # Encontrar contorno de la tabla
        ys, xs = np.where(table_mask > 0)
        if len(xs) == 0 or len(ys) == 0:
            logger.error("❌ No se detectó ninguna tabla")
            return []
        
        x_min, x_max = xs.min(), xs.max()
        y_min, y_max = ys.min(), ys.max()
        cv2.rectangle(table_mask, (x_min, y_min), (x_max, y_max), color=255, thickness=5)
        
        # Encontrar contornos de celdas
        contours, _ = cv2.findContours(table_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        logger.info(f"✅ Detectados {len(contours)} contornos")
        
        # Filtrar y merge celdas
        min_h, min_w = 80, 20
        max_h, max_w = 1500, 1500
        padding = 5
        ignore_left = 50
        
        # Filtrar celdas por tamaño
        filtered_cells = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if x >= ignore_left and w >= min_w and h >= min_h and w <= max_w and h <= max_h:
                filtered_cells.append((x, y, w, h))
        
        # Merge celdas superpuestas
        merged_cells = []
        for x, y, w, h in filtered_cells:
            merged = False
            for i, (mx, my, mw, mh) in enumerate(merged_cells):
                if (abs(x - mx) < 10 and abs(y - my) < 10) or \
                   (abs(x+w - (mx+mw)) < 10 and abs(y+h - (my+mh)) < 10):
                    nx = min(x, mx)
                    ny = min(y, my)
                    nw = max(x+w, mx+mw) - nx
                    nh = max(y+h, my+mh) - ny
                    merged_cells[i] = (nx, ny, nw, nh)
                    merged = True
                    break
            if not merged:
                merged_cells.append((x, y, w, h))
        
        logger.info(f"✅ {len(merged_cells)} celdas después de merge")
        
        # Ordenar por fila (y) y luego por columna (x)
        merged_cells = sorted(merged_cells, key=lambda c: c[1])
        
        return merged_cells, img
    
    def extraer_y_guardar_celdas(self, img: np.ndarray, cells: List[Tuple[int, int, int, int]]):
        """
        Extrae las celdas de la imagen y las guarda
        Implementación del notebook: célula 5
        """
        logger.info(f"✂️  Extrayendo {len(cells)} celdas...")
        
        self.crear_carpetas_temporales()
        
        padding = 5
        idx = 1
        cells_copy = cells.copy()
        
        while cells_copy:
            bx, by, bw, bh = cells_copy[0]
            line_y = by + bh/2
            
            current_row = []
            remaining = []
            
            # Agrupar celdas de la misma fila
            for cell in cells_copy:
                x, y, w, h = cell
                top = y
                bottom = y + h
                
                if top <= line_y <= bottom:
                    current_row.append(cell)
                else:
                    remaining.append(cell)
            
            # Ordenar fila por x
            current_row = sorted(current_row, key=lambda c: c[0])
            
            # Guardar celdas de la fila
            for x, y, w, h in current_row:
                x1p = max(x - padding, 0)
                y1p = max(y - padding, 0)
                x2p = min(x + w + padding, img.shape[1])
                y2p = min(y + h + padding, img.shape[0])
                roi = img[y1p:y2p, x1p:x2p]
                filename = os.path.join(self.temp_dir, f"cell_{idx:03d}.png")
                cv2.imwrite(filename, roi)
                idx += 1
            
            cells_copy = remaining
        
        logger.info(f"✅ {idx-1} celdas guardadas en {self.temp_dir}")
    
    def preprocesar_imagenes(self):
        """
        Preprocesa las imágenes de las celdas
        Implementación del notebook: célula 6
        """
        logger.info("🔄 Preprocesando imágenes...")
        
        scale_factor = 3
        padding = 5
        
        image_files = sorted([f for f in os.listdir(self.temp_dir) if f.endswith(".png")])
        
        for idx, filename in enumerate(image_files, 1):
            filepath = os.path.join(self.temp_dir, filename)
            img = cv2.imread(filepath)
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Escalar
            gray = cv2.resize(
                gray, 
                (gray.shape[1]*scale_factor, gray.shape[0]*scale_factor), 
                interpolation=cv2.INTER_CUBIC
            )
            
            # Agregar padding
            gray = cv2.copyMakeBorder(
                gray, padding, padding, padding, padding, 
                cv2.BORDER_CONSTANT, value=255
            )
            
            # Threshold binario
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Dilatar
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
            thresh = cv2.dilate(thresh, kernel, iterations=1)
            
            # Guardar imagen preprocesada
            save_path = os.path.join(self.temp_preprocessed_dir, filename)
            cv2.imwrite(save_path, thresh)
            
            # Eliminar original
            os.remove(filepath)
        
        logger.info(f"✅ {len(image_files)} imágenes preprocesadas")
    
    def aplicar_ocr_easyocr(self, progress_callback=None, total_celdas=0) -> pd.DataFrame:
        """
        Aplica EasyOCR a las imágenes preprocesadas
        Implementación del notebook: célula 7
        
        Args:
            progress_callback: Función opcional para reportar progreso (celda_actual, total)
            total_celdas: Total de celdas para calcular progreso
        """
        logger.info("📝 Aplicando EasyOCR...")
        
        image_files = sorted([f for f in os.listdir(self.temp_preprocessed_dir) if f.endswith(".png")])
        
        rows = []
        current_row = []
        
        # IMPORTANTE: Forzar workers=0 para evitar BlockingIOError en señales UNIX/Docker
        num_workers = 0
        
        for idx, filename in enumerate(image_files, 1):
            filepath = os.path.join(self.temp_preprocessed_dir, filename)
            img = cv2.imread(filepath)
            
            # Aplicar OCR
            result = self.reader.readtext(
                img, 
                detail=0, 
                paragraph=False,
                workers=num_workers
            )
            text = " ".join(result).strip() if result else ""
            
            current_row.append(text)
            
            # Eliminar archivo procesado
            os.remove(filepath)
            
            # Completar fila
            if len(current_row) == self.num_cols:
                rows.append(current_row)
                current_row = []
            
            # Reportar progreso cada 10 celdas para dar feedback visual
            if progress_callback and (idx + 1) % 10 == 0:
                progress_callback(idx + 1, len(image_files))
                logger.info(f"📊 Procesadas {idx + 1}/{len(image_files)} celdas")
            elif idx % 10 == 0:
                logger.info(f"   Procesadas {idx}/{len(image_files)} celdas")
        
        # Agregar última fila si existe
        if current_row:
            rows.append(current_row)
        
        df = pd.DataFrame(rows)
        logger.info(f"✅ OCR completado: {len(df)} filas extraídas")
        
        return df
    
    def validar_y_corregir_patron(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida el patrón y corrige errores
        Implementación del notebook: célula 8
        """
        logger.info("✓  Validando patrón...")
        
        # Aplanar DataFrame
        arr_flat = df.to_numpy().flatten()
        arr_flat = [str(v).strip() for v in arr_flat]
        
        new_rows = []
        
        while len(arr_flat) >= self.num_cols:
            block = arr_flat[:self.num_cols]
            block_pattern = []
            
            # Determinar patrón del bloque
            for v in block:
                if v == 'nD':
                    block_pattern.append('E')
                else:
                    first_char = v[0] if v else ''
                    if first_char.isalpha():
                        block_pattern.append('L')
                    elif first_char.isdigit():
                        block_pattern.append('N')
                    else:
                        block_pattern.append('E')
            
            # Verificar si coincide con el patrón esperado
            match = all(bp == p or bp == 'E' for bp, p in zip(block_pattern, self.pattern))
            
            if match:
                new_rows.append(block)
                arr_flat = arr_flat[self.num_cols:]
            else:
                # Insertar 'nD' para intentar realinear
                arr_flat.insert(0, 'nD')
        
        df_fixed = pd.DataFrame(new_rows, columns=[f"Col{i+1}" for i in range(self.num_cols)])
        logger.info(f"✅ Patrón validado: {len(df_fixed)} tuplas válidas")
        
        return df_fixed
    
    def procesar_documento_completo(self, archivo_bytes: bytes, es_pdf: bool = True, progress_callback=None) -> Dict[str, Any]:
        """
        Procesa un documento completo con OCRv2
        
        Args:
            archivo_bytes: Bytes del archivo (PDF o imagen)
            es_pdf: Si el archivo es PDF
            progress_callback: Función opcional para reportar progreso (celda_actual, total)
            
        Returns:
            Dict con tuplas extraídas y metadatos
        """
        try:
            logger.info("=" * 70)
            logger.info("🚀 Iniciando procesamiento OCRv2")
            logger.info("=" * 70)
            
            # 1. Convertir PDF a imagen
            if es_pdf:
                img = self.convertir_pdf_a_imagen(archivo_bytes)
            else:
                # Decodificar imagen directamente
                nparr = np.frombuffer(archivo_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 2. Detectar tabla y extraer celdas
            cells, img = self.detectar_y_extraer_tabla(img)
            
            if not cells:
                return {
                    'estado': 'error',
                    'mensaje': 'No se detectó ninguna tabla',
                    'total_tuplas': 0,
                    'tuplas': []
                }
            
            # 3. Extraer y guardar celdas
            self.extraer_y_guardar_celdas(img, cells)
            
            # 4. Preprocesar imágenes
            self.preprocesar_imagenes()
            
            # 5. Aplicar OCR
            df_raw = self.aplicar_ocr_easyocr(progress_callback=progress_callback, total_celdas=len(cells))
            
            # 6. Validar y corregir patrón
            df_final = self.validar_y_corregir_patron(df_raw)
            
            # 7. Convertir a formato de salida
            tuplas = []
            for _, row in df_final.iterrows():
                tupla = [str(val) for val in row.values]
                tuplas.append(tupla)
            
            logger.info("=" * 70)
            logger.info(f"✅ Procesamiento completado: {len(tuplas)} tuplas extraídas")
            logger.info("=" * 70)
            
            return {
                'estado': 'success',
                'total_tuplas': len(tuplas),
                'tuplas': tuplas,
                'num_columnas': self.num_cols,
                'patron': self.pattern
            }
            
        except Exception as e:
            logger.error(f"❌ Error en pipeline OCR V2: {e}")
            import traceback
            traceback.print_exc()
            return {
                'estado': 'error',
                'mensaje': str(e),
                'total_tuplas': 0,
                'tuplas': []
            }
        
        finally:
            # Limpiar carpetas temporales
            self.limpiar_carpetas_temporales()

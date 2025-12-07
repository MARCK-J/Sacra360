"""
Procesador de Tablas - Sacra360 OCR Service
Implementación del flujo completo del notebook Sacra360_OCRv2.ipynb
Optimizado para GPU AMD con EasyOCR
"""

import cv2
import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import os
import shutil
import time
from pathlib import Path
from typing import List, Tuple, Optional
from loguru import logger

# Import EasyOCR (puede requerir torch, pero torch puede tener problemas de DLL en Windows)
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception as e:
    logger.warning(f"EasyOCR no disponible: {e}")
    EASYOCR_AVAILABLE = False

try:
    from .gpu_utils import detect_gpu_type, get_optimal_device
except Exception as e:
    logger.warning(f"gpu_utils no disponible: {e}")
    def detect_gpu_type():
        return {'gpu_type': 'CPU', 'backend': 'CPU', 'can_use_gpu': False, 'vram_gb': 0}
    def get_optimal_device():
        return 'cpu'


class TableProcessor:
    """
    Procesador completo de tablas desde PDF a DataFrame estructurado.
    Implementa el flujo: PDF → Grid Detection → Cell Extraction → 
    Preprocessing → EasyOCR → Pattern Matching → DataFrame
    """
    
    def __init__(
        self, 
        use_gpu: bool = True,
        languages: List[str] = ['en'],
        dpi: int = 150,
        num_cols: int = 10
    ):
        """
        Inicializa el procesador de tablas con EasyOCR.
        
        Args:
            use_gpu: Si True, intenta usar GPU (AMD/NVIDIA)
            languages: Idiomas para EasyOCR (ej: ['en', 'es'])
            dpi: DPI para conversión de PDF a imagen
            num_cols: Número esperado de columnas en la tabla
        """
        self.dpi = dpi
        self.num_cols = num_cols
        self.languages = languages
        
        # Detectar GPU
        gpu_info = detect_gpu_type()
        self.gpu_info = gpu_info
        self.use_gpu = use_gpu and gpu_info['can_use_gpu']
        
        logger.info(f"Inicializando TableProcessor con GPU={self.use_gpu}")
        logger.info(f"GPU Type: {gpu_info['gpu_type']}, Backend: {gpu_info['backend']}")
        
        # Verificar disponibilidad de EasyOCR
        if not EASYOCR_AVAILABLE:
            raise RuntimeError(
                "EasyOCR no está disponible. "
                "Posible problema con PyTorch DLLs en Windows. "
                "Instalar Visual C++ Redistributable: "
                "https://aka.ms/vs/17/release/vc_redist.x64.exe"
            )
        
        # Inicializar EasyOCR
        # EasyOCR soporta GPU NVIDIA con CUDA, no AMD/OpenCL
        try:
            start_time = time.time()
            
            # Verificar si hay GPU NVIDIA con CUDA disponible
            cuda_available = False
            try:
                import torch
                cuda_available = torch.cuda.is_available()
                if cuda_available:
                    cuda_device = torch.cuda.get_device_name(0)
                    logger.info(f"🎮 GPU NVIDIA detectada: {cuda_device}")
            except Exception:
                pass
            
            # Decidir si usar GPU basado en disponibilidad de CUDA
            if self.use_gpu and not cuda_available:
                if gpu_info['gpu_type'] in ['AMD', 'AMD/Other']:
                    logger.warning("⚠️  GPU AMD detectada pero EasyOCR requiere NVIDIA/CUDA")
                    logger.info("   Usando CPU optimizado (quantize=True)")
                else:
                    logger.warning("⚠️  GPU solicitada pero CUDA no disponible")
                    logger.info("   Usando CPU optimizado")
                self.use_gpu = False
            elif self.use_gpu and cuda_available:
                logger.info("✓ GPU NVIDIA/CUDA disponible, habilitando aceleración GPU")
            
            # Inicializar EasyOCR con GPU si está disponible
            self.reader = easyocr.Reader(
                languages, 
                gpu=self.use_gpu,
                verbose=False,
                quantize=not self.use_gpu,  # Cuantizar solo en CPU para mejor rendimiento
                download_enabled=True
            )
            init_time = time.time() - start_time
            
            # Log de confirmación
            if self.use_gpu:
                logger.info(f"✓ EasyOCR inicializado en {init_time:.2f}s")
                logger.info(f"  🚀 Modo: GPU NVIDIA/CUDA")
                logger.info(f"  ⚡ Aceleración GPU activa")
            else:
                logger.info(f"✓ EasyOCR inicializado en {init_time:.2f}s")
                logger.info(f"  💻 Modo: CPU optimizado (quantized)")
                logger.info(f"  ℹ️  Para GPU se requiere NVIDIA con CUDA")
                
        except Exception as e:
            logger.warning(f"Error inicializando EasyOCR con configuración solicitada: {e}")
            logger.info("Fallback: Reintentando con CPU...")
            try:
                self.reader = easyocr.Reader(languages, gpu=False, verbose=False, quantize=True)
                self.use_gpu = False
                logger.info("✓ EasyOCR inicializado en modo CPU fallback")
            except Exception as e2:
                logger.error(f"Error crítico inicializando EasyOCR: {e2}")
                raise
    
    def process_pdf(
        self, 
        pdf_path: str, 
        output_dir: Optional[str] = None,
        pattern: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Procesa un PDF completo y retorna un DataFrame estructurado.
        
        Args:
            pdf_path: Ruta al archivo PDF
            output_dir: Directorio de salida para archivos temporales
            pattern: Patrón de validación ['L','N','N',...] donde L=Letter, N=Number
            
        Returns:
            DataFrame con los datos extraídos y estructurados
        """
        start_time = time.time()
        logger.info(f"═══════════════════════════════════════════════")
        logger.info(f"PROCESANDO PDF: {Path(pdf_path).name}")
        logger.info(f"═══════════════════════════════════════════════")
        
        # Crear directorios temporales
        if output_dir is None:
            output_dir = Path(pdf_path).parent / "temp_processing"
        else:
            output_dir = Path(output_dir)
        
        temp_dir = output_dir / "temp"
        temp_preprocessed_dir = output_dir / "temp_preprocessed"
        
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_preprocessed_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Convertir PDF a imágenes
            logger.info(f"[1/6] Convirtiendo PDF a imágenes (DPI={self.dpi})...")
            step_start = time.time()
            pages = convert_from_path(pdf_path, dpi=self.dpi)
            logger.info(f"  ✓ {len(pages)} página(s) convertida(s) en {time.time()-step_start:.2f}s")
            
            # Por ahora procesamos solo la primera página (como en el notebook)
            img = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)
            
            # 2. Detectar grid de tabla
            logger.info(f"[2/6] Detectando grid de tabla...")
            step_start = time.time()
            table_mask, merged_cells = self._detect_table_grid(img)
            logger.info(f"  ✓ {len(merged_cells)} celdas detectadas en {time.time()-step_start:.2f}s")
            
            # 3. Extraer celdas
            logger.info(f"[3/6] Extrayendo celdas individuales...")
            step_start = time.time()
            num_cells = self._extract_cells(img, merged_cells, temp_dir)
            logger.info(f"  ✓ {num_cells} celdas extraídas en {time.time()-step_start:.2f}s")
            
            # 4. Preprocesar celdas
            logger.info(f"[4/6] Preprocesando imágenes (escala, binarización)...")
            step_start = time.time()
            num_preprocessed = self._preprocess_cells(temp_dir, temp_preprocessed_dir)
            logger.info(f"  ✓ {num_preprocessed} imágenes procesadas en {time.time()-step_start:.2f}s")
            
            # 5. OCR con EasyOCR
            logger.info(f"[5/6] Ejecutando OCR con EasyOCR (GPU={self.use_gpu})...")
            step_start = time.time()
            raw_data = self._run_ocr(temp_preprocessed_dir)
            ocr_time = time.time() - step_start
            logger.info(f"  ✓ {len(raw_data)} celdas procesadas en {ocr_time:.2f}s")
            logger.info(f"  ⚡ Promedio: {ocr_time/len(raw_data)*1000:.1f}ms por celda")
            
            # 6. Estructurar con pattern matching
            logger.info(f"[6/6] Estructurando datos con pattern matching...")
            step_start = time.time()
            if pattern is None:
                pattern = ['L','N','N','N','L','N','N','N','L','L']  # Default del notebook
            
            df = self._structure_data(raw_data, pattern)
            logger.info(f"  ✓ DataFrame creado: {len(df)} filas × {len(df.columns)} columnas en {time.time()-step_start:.2f}s")
            
            total_time = time.time() - start_time
            logger.info(f"═══════════════════════════════════════════════")
            logger.info(f"✅ PROCESAMIENTO COMPLETADO EN {total_time:.2f}s ({total_time/60:.2f} min)")
            logger.info(f"═══════════════════════════════════════════════")
            
            return df
            
        finally:
            # Limpiar directorios temporales
            self._cleanup(output_dir)
    
    def _detect_table_grid(self, img: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int, int, int]]]:
        """
        Detecta el grid de la tabla usando morfología.
        Retorna: (table_mask, merged_cells)
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)[1]
        
        # Detectar líneas horizontales y verticales
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 1))
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 100))
        
        horiz = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_h)
        vert = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_v)
        
        # Combinar líneas
        table_mask = horiz + vert
        
        # Dilatar para unir componentes
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        table_mask = cv2.dilate(table_mask, kernel_dilate, iterations=1)
        
        # Detectar contornos
        contours, _ = cv2.findContours(table_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar y fusionar celdas
        min_h, min_w = 80, 20
        max_h, max_w = 1500, 1500
        ignore_left = 50
        
        # Filtrar por tamaño
        filtered_cells = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if x >= ignore_left and w >= min_w and h >= min_h and w <= max_w and h <= max_h:
                filtered_cells.append((x, y, w, h))
        
        # Fusionar celdas superpuestas
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
        
        # Ordenar por posición vertical
        merged_cells = sorted(merged_cells, key=lambda c: c[1])
        
        return table_mask, merged_cells
    
    def _extract_cells(
        self, 
        img: np.ndarray, 
        merged_cells: List[Tuple[int, int, int, int]], 
        output_dir: Path
    ) -> int:
        """
        Extrae celdas individuales organizadas por filas.
        Retorna: número de celdas extraídas
        """
        padding = 5
        idx = 1
        
        while merged_cells:
            bx, by, bw, bh = merged_cells[0]
            line_y = by + bh/2
            
            current_row = []
            remaining = []
            
            # Agrupar celdas en la misma fila
            for cell in merged_cells:
                x, y, w, h = cell
                top, bottom = y, y + h
                
                if top <= line_y <= bottom:
                    current_row.append(cell)
                else:
                    remaining.append(cell)
            
            # Ordenar fila por posición horizontal
            current_row = sorted(current_row, key=lambda c: c[0])
            
            # Guardar celdas de la fila
            for x, y, w, h in current_row:
                x1p = max(x - padding, 0)
                y1p = max(y - padding, 0)
                x2p = min(x + w + padding, img.shape[1])
                y2p = min(y + h + padding, img.shape[0])
                
                roi = img[y1p:y2p, x1p:x2p]
                filename = output_dir / f"cell_{idx:03d}.png"
                cv2.imwrite(str(filename), roi)
                idx += 1
            
            merged_cells = remaining
        
        return idx - 1
    
    def _preprocess_cells(self, input_dir: Path, output_dir: Path) -> int:
        """
        Preprocesa las celdas: escala, padding, binarización OPTIMIZADO.
        Retorna: número de imágenes procesadas
        """
        # Reducir escala para acelerar OCR (2x en lugar de 3x)
        scale_factor = 2
        padding = 5
        
        image_files = sorted([f for f in input_dir.glob("*.png")])
        
        for idx, filepath in enumerate(image_files, 1):
            img = cv2.imread(str(filepath))
            
            # Escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Escalar 2x (más rápido que 3x)
            gray = cv2.resize(
                gray, 
                (gray.shape[1]*scale_factor, gray.shape[0]*scale_factor), 
                interpolation=cv2.INTER_LINEAR  # INTER_LINEAR es más rápido que INTER_CUBIC
            )
            
            # Agregar padding
            gray = cv2.copyMakeBorder(
                gray, padding, padding, padding, padding, 
                cv2.BORDER_CONSTANT, value=255
            )
            
            # Binarización con Otsu
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Dilatar ligeramente (reducir iteraciones)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            thresh = cv2.dilate(thresh, kernel, iterations=1)
            
            # Guardar
            save_path = output_dir / filepath.name
            cv2.imwrite(str(save_path), thresh)
            
            # Eliminar original
            filepath.unlink()
        
        return len(image_files)
    
    def _run_ocr(self, input_dir: Path) -> List[List[str]]:
        """
        Ejecuta OCR en todas las celdas preprocesadas.
        Retorna: lista de filas, cada fila es una lista de textos
        """
        image_files = sorted([f for f in input_dir.glob("*.png")])
        
        rows = []
        current_row = []
        
        for idx, filepath in enumerate(image_files, 1):
            img = cv2.imread(str(filepath))
            
            # OCR con EasyOCR optimizado
            result = self.reader.readtext(
                img, 
                detail=0, 
                paragraph=False,
                decoder='greedy',  # Más rápido que beamsearch
                beamWidth=1,
                batch_size=1,
                contrast_ths=0.1,
                adjust_contrast=0.5,
                text_threshold=0.7,
                low_text=0.4,
                link_threshold=0.4,
                canvas_size=1280,
                mag_ratio=1.0
            )
            text = " ".join(result).strip() if result else ""
            
            current_row.append(text)
            
            # Eliminar imagen procesada
            filepath.unlink()
            
            # Cuando completamos una fila
            if len(current_row) == self.num_cols:
                rows.append(current_row)
                current_row = []
        
        # Agregar última fila si existe
        if current_row:
            rows.append(current_row)
        
        return rows
    
    def _structure_data(
        self, 
        rows: List[List[str]], 
        pattern: List[str]
    ) -> pd.DataFrame:
        """
        Estructura los datos usando pattern matching.
        Pattern: 'L' = Letter, 'N' = Number, 'E' = Empty/Error
        """
        # Aplanar todas las filas
        arr_flat = []
        for row in rows:
            arr_flat.extend([str(v).strip() for v in row])
        
        new_rows = []
        
        while len(arr_flat) >= self.num_cols:
            block = arr_flat[:self.num_cols]
            
            # Detectar patrón del bloque
            block_pattern = []
            for v in block:
                if v == 'nD' or v == '' or v.lower() == 'nan':
                    block_pattern.append('E')
                else:
                    first_char = v[0] if v else ''
                    if first_char.isalpha():
                        block_pattern.append('L')
                    elif first_char.isdigit():
                        block_pattern.append('N')
                    else:
                        block_pattern.append('E')
            
            # Verificar match con patrón esperado
            match = all(
                bp == p or bp == 'E' 
                for bp, p in zip(block_pattern, pattern)
            )
            
            if match:
                new_rows.append(block)
                arr_flat = arr_flat[self.num_cols:]
            else:
                # Insertar marcador y re-intentar
                arr_flat.insert(0, 'nD')
        
        # Crear DataFrame
        columns = [f"Col{i+1}" for i in range(self.num_cols)]
        df = pd.DataFrame(new_rows, columns=columns)
        
        return df
    
    def _cleanup(self, output_dir: Path):
        """Limpia directorios temporales"""
        try:
            if output_dir.exists():
                shutil.rmtree(output_dir)
                logger.info(f"✓ Directorios temporales eliminados")
        except Exception as e:
            logger.warning(f"Error limpiando directorios: {e}")
    
    def get_info(self) -> dict:
        """Retorna información del procesador"""
        # Verificar CUDA para info adicional
        cuda_available = False
        cuda_device_name = "N/A"
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                cuda_device_name = torch.cuda.get_device_name(0)
        except Exception:
            pass
        
        return {
            "use_gpu": self.use_gpu,
            "gpu_type": self.gpu_info.get('gpu_type', 'Unknown'),
            "backend": self.gpu_info.get('backend', 'Unknown'),
            "vram_gb": self.gpu_info.get('vram_gb', 'N/A'),
            "cuda_available": cuda_available,
            "cuda_device": cuda_device_name if cuda_available else "N/A",
            "mode": "GPU NVIDIA/CUDA" if self.use_gpu else "CPU Optimizado",
            "languages": self.languages,
            "dpi": self.dpi,
            "num_cols": self.num_cols
        }

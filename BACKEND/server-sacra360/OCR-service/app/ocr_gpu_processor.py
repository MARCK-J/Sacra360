"""
OCR GPU Processor for Sacra360
Módulo optimizado para procesamiento OCR de tablas usando EasyOCR con GPU.
Compatible con AMD GPU (ROCm/OpenCL) y NVIDIA GPU (CUDA).
Basado en Sacra360_OCRv2.ipynb adaptado para entorno de producción.

Autor: Sacra360 Team
Versión: 3.0 (AMD/NVIDIA GPU-enabled)
"""

import os
import shutil
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import logging

import cv2
import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import easyocr

from .gpu_utils import detect_gpu_type, get_optimal_device

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableOCRProcessor:
    """
    Procesador OCR optimizado para extraer tablas de documentos PDF
    usando EasyOCR con aceleración GPU (AMD o NVIDIA).
    """

    def __init__(
        self,
        use_gpu: bool = True,
        languages: List[str] = ['en', 'es'],
        dpi: int = 150,
        temp_dir: str = "temp",
        preprocessed_dir: str = "temp_preprocessed"
    ):
        """
        Inicializa el procesador OCR.

        Args:
            use_gpu: Activar aceleración GPU (AMD ROCm/OpenCL o NVIDIA CUDA)
            languages: Lista de idiomas para EasyOCR
            dpi: Resolución para conversión de PDF
            temp_dir: Directorio temporal para celdas extraídas
            preprocessed_dir: Directorio para celdas preprocesadas
        """
        self.languages = languages
        self.dpi = dpi
        self.temp_dir = temp_dir
        self.preprocessed_dir = preprocessed_dir
        
        # Detectar tipo de GPU
        self.gpu_info = detect_gpu_type()
        
        # Determinar si usar GPU basado en disponibilidad
        self.use_gpu = use_gpu and self.gpu_info["can_use_gpu"]
        
        if use_gpu and not self.use_gpu:
            logger.warning(f"GPU solicitada pero no disponible. Usando CPU.")
            logger.info(f"GPU detectada: {self.gpu_info['gpu_type']}, Backend: {self.gpu_info['backend']}")

        # Inicializar EasyOCR reader
        logger.info(f"Inicializando EasyOCR (GPU: {self.use_gpu}, Tipo: {self.gpu_info['gpu_type']})...")
        try:
            self.reader = easyocr.Reader(languages, gpu=self.use_gpu)
            logger.info("✓ EasyOCR reader inicializado correctamente")
            if self.use_gpu:
                logger.info(f"✓ Usando {self.gpu_info['gpu_type']} GPU: {self.gpu_info['device_name']}")
        except Exception as e:
            logger.error(f"Error al inicializar EasyOCR con GPU: {e}")
            # Fallback a CPU
            if self.use_gpu:
                logger.warning("Reintentando con CPU...")
                self.use_gpu = False
                self.reader = easyocr.Reader(languages, gpu=False)
                logger.info("✓ EasyOCR inicializado en modo CPU")
            else:
                raise

        # Crear directorios temporales
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.preprocessed_dir, exist_ok=True)

    def process_pdf_table(
        self,
        pdf_path: str,
        page_number: int = 0,
        num_cols: int = 10,
        pattern: Optional[List[str]] = None,
        cleanup: bool = True
    ) -> pd.DataFrame:
        """
        Procesa un PDF y extrae una tabla estructurada.

        Args:
            pdf_path: Ruta al archivo PDF
            page_number: Número de página a procesar (0-indexed)
            num_cols: Número esperado de columnas en la tabla
            pattern: Patrón esperado de tipos de datos ['L'=letra, 'N'=número, 'E'=vacío]
            cleanup: Limpiar directorios temporales al finalizar

        Returns:
            DataFrame de pandas con la tabla extraída
        """
        if pattern is None:
            pattern = ['L', 'N', 'N', 'N', 'L', 'N', 'N', 'N', 'L', 'L']

        try:
            # 1. Convertir PDF a imagen
            logger.info(f"Convirtiendo PDF: {pdf_path}")
            pages = convert_from_path(pdf_path, dpi=self.dpi)
            img = cv2.cvtColor(np.array(pages[page_number]), cv2.COLOR_RGB2BGR)

            # 2. Detectar y extraer celdas de la tabla
            logger.info("Detectando estructura de tabla...")
            self._extract_table_cells(img)

            # 3. Preprocesar celdas
            logger.info("Preprocesando celdas...")
            self._preprocess_cells()

            # 4. Ejecutar OCR con GPU
            logger.info("Ejecutando OCR con GPU...")
            rows = self._ocr_cells(num_cols)

            # 5. Corregir alineación de columnas
            logger.info("Corrigiendo alineación...")
            df_fixed = self._fix_column_alignment(rows, num_cols, pattern)

            logger.info(f"✓ Tabla extraída: {len(df_fixed)} filas x {num_cols} columnas")

            return df_fixed

        except Exception as e:
            logger.error(f"Error procesando PDF: {e}")
            raise

        finally:
            if cleanup:
                self._cleanup_temp_dirs()

    def _extract_table_cells(self, img: np.ndarray) -> None:
        """Detecta y extrae celdas individuales de la tabla."""
        # Convertir a escala de grises y binarizar
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)[1]

        # Detectar líneas horizontales y verticales
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 1))
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 100))

        horiz = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_h)
        vert = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_v)

        # Crear máscara de tabla
        table_mask = horiz + vert
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        table_mask = cv2.dilate(table_mask, kernel_dilate, iterations=1)

        # Encontrar contornos
        contours, _ = cv2.findContours(table_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrar y fusionar celdas
        min_h, min_w = 80, 20
        max_h, max_w = 1500, 1500
        padding = 5
        ignore_left = 50

        filtered_cells = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if x >= ignore_left and min_w <= w <= max_w and min_h <= h <= max_h:
                filtered_cells.append((x, y, w, h))

        # Fusionar celdas superpuestas
        merged_cells = self._merge_overlapping_cells(filtered_cells)

        # Ordenar por posición vertical y horizontal
        merged_cells = sorted(merged_cells, key=lambda c: c[1])

        # Guardar celdas como imágenes
        idx = 1
        while merged_cells:
            bx, by, bw, bh = merged_cells[0]
            line_y = by + bh / 2

            current_row = []
            remaining = []

            for cell in merged_cells:
                x, y, w, h = cell
                if y <= line_y <= y + h:
                    current_row.append(cell)
                else:
                    remaining.append(cell)

            current_row = sorted(current_row, key=lambda c: c[0])

            for x, y, w, h in current_row:
                x1 = max(x - padding, 0)
                y1 = max(y - padding, 0)
                x2 = min(x + w + padding, img.shape[1])
                y2 = min(y + h + padding, img.shape[0])
                roi = img[y1:y2, x1:x2]

                filename = os.path.join(self.temp_dir, f"cell_{idx:03d}.png")
                cv2.imwrite(filename, roi)
                idx += 1

            merged_cells = remaining

    def _merge_overlapping_cells(
        self,
        cells: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int, int, int]]:
        """Fusiona celdas que se superponen."""
        merged = []
        for x, y, w, h in cells:
            merged_flag = False
            for i, (mx, my, mw, mh) in enumerate(merged):
                # Verificar superposición
                if (abs(x - mx) < 10 and abs(y - my) < 10) or \
                   (abs(x + w - (mx + mw)) < 10 and abs(y + h - (my + mh)) < 10):
                    nx = min(x, mx)
                    ny = min(y, my)
                    nw = max(x + w, mx + mw) - nx
                    nh = max(y + h, my + mh) - ny
                    merged[i] = (nx, ny, nw, nh)
                    merged_flag = True
                    break
            if not merged_flag:
                merged.append((x, y, w, h))
        return merged

    def _preprocess_cells(self, scale_factor: int = 3, padding: int = 5) -> None:
        """Preprocesa celdas para mejorar calidad de OCR."""
        image_files = sorted([f for f in os.listdir(self.temp_dir) if f.endswith(".png")])

        for idx, filename in enumerate(image_files, 1):
            filepath = os.path.join(self.temp_dir, filename)
            img = cv2.imread(filepath)

            # Escala de grises y aumento de resolución
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(
                gray,
                (gray.shape[1] * scale_factor, gray.shape[0] * scale_factor),
                interpolation=cv2.INTER_CUBIC
            )

            # Agregar padding
            gray = cv2.copyMakeBorder(
                gray, padding, padding, padding, padding,
                cv2.BORDER_CONSTANT, value=255
            )

            # Binarización con OTSU
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Dilatación ligera
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            thresh = cv2.dilate(thresh, kernel, iterations=1)

            # Guardar imagen preprocesada
            save_path = os.path.join(self.preprocessed_dir, filename)
            cv2.imwrite(save_path, thresh)
            os.remove(filepath)

            if idx % 10 == 0:
                logger.info(f"Preprocesadas {idx}/{len(image_files)} celdas")

    def _ocr_cells(self, num_cols: int) -> List[List[str]]:
        """Ejecuta OCR en todas las celdas usando EasyOCR con GPU."""
        image_files = sorted([
            f for f in os.listdir(self.preprocessed_dir)
            if f.endswith(".png")
        ])

        rows = []
        current_row = []

        for idx, filename in enumerate(image_files, 1):
            filepath = os.path.join(self.preprocessed_dir, filename)
            img = cv2.imread(filepath)

            # Ejecutar OCR con EasyOCR (usa GPU automáticamente)
            result = self.reader.readtext(img, detail=0, paragraph=False)
            text = " ".join(result).strip() if result else ""

            current_row.append(text)

            # Eliminar imagen procesada
            os.remove(filepath)

            # Completar fila cuando alcanza el número de columnas
            if len(current_row) == num_cols:
                rows.append(current_row)
                current_row = []

            if idx % 10 == 0:
                logger.info(f"OCR ejecutado en {idx}/{len(image_files)} celdas")

        # Agregar última fila si existe
        if current_row:
            rows.append(current_row)

        return rows

    def _fix_column_alignment(
        self,
        rows: List[List[str]],
        num_cols: int,
        pattern: List[str]
    ) -> pd.DataFrame:
        """Corrige desalineación de columnas usando patrón esperado."""
        df = pd.DataFrame(rows)
        arr_flat = df.to_numpy().flatten()
        arr_flat = [str(v).strip() for v in arr_flat]

        new_rows = []

        while len(arr_flat) >= num_cols:
            block = arr_flat[:num_cols]
            block_pattern = []

            for v in block:
                if v == 'nD' or not v:
                    block_pattern.append('E')
                else:
                    first_char = v[0] if v else ''
                    if first_char.isalpha():
                        block_pattern.append('L')
                    elif first_char.isdigit():
                        block_pattern.append('N')
                    else:
                        block_pattern.append('E')

            # Verificar coincidencia con patrón
            match = all(bp == p or bp == 'E' for bp, p in zip(block_pattern, pattern))

            if match:
                new_rows.append(block)
                arr_flat = arr_flat[num_cols:]
            else:
                # Insertar valor nulo y reintentar
                arr_flat.insert(0, 'nD')

        # Crear DataFrame final
        df_fixed = pd.DataFrame(
            new_rows,
            columns=[f"Col{i+1}" for i in range(num_cols)]
        )

        return df_fixed

    def _cleanup_temp_dirs(self) -> None:
        """Limpia directorios temporales."""
        for dir_path in [self.temp_dir, self.preprocessed_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                logger.info(f"Directorio temporal eliminado: {dir_path}")

    def get_gpu_info(self) -> Dict[str, any]:
        """Obtiene información sobre disponibilidad de GPU (AMD o NVIDIA)."""
        return self.gpu_info.copy()


# Función auxiliar para uso rápido
def process_table_pdf(
    pdf_path: str,
    page_number: int = 0,
    use_gpu: bool = True,
    output_csv: Optional[str] = None
) -> pd.DataFrame:
    """
    Función auxiliar para procesar rápidamente un PDF con tabla.

    Args:
        pdf_path: Ruta al PDF
        page_number: Página a procesar
        use_gpu: Usar aceleración GPU
        output_csv: Ruta opcional para guardar CSV

    Returns:
        DataFrame con la tabla extraída
    """
    processor = TableOCRProcessor(use_gpu=use_gpu)
    df = processor.process_pdf_table(pdf_path, page_number=page_number)

    if output_csv:
        df.to_csv(output_csv, index=False)
        logger.info(f"Tabla guardada en: {output_csv}")

    return df

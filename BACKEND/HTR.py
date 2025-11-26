# --- PASO 1: INSTALACIÓN DE DEPENDENCIAS (Si no las has instalado aún) ---
# Descomenta las siguientes lineas si es la primera vez que ejecutas en esta sesión
!python -m pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
!pip install opencv-python-headless pandas openpyxl
!pip install easyocr opencv-python-headless pandas openpyxl

import cv2
import numpy as np
import pandas as pd
import easyocr
from google.colab import files
import os
import warnings
import matplotlib.pyplot as plt
import re

# Filtrar advertencias
warnings.filterwarnings("ignore")

class SacramentalDigitizer:
    def __init__(self):
        print("🔵 Cargando modelo de IA EasyOCR (Modo Manuscrito Mejorado)...")
        # Inicializamos el lector
        self.reader = easyocr.Reader(['es'], gpu=True, verbose=False)

    def plot_step(self, img, title, cmap='gray'):
        plt.figure(figsize=(12, 8))
        plt.imshow(img, cmap=cmap)
        plt.title(title)
        plt.axis('off')
        plt.show()

    def preprocess_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"No se pudo cargar: {image_path}")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Binarización SOLO para detectar las líneas de la tabla, no para leer el texto
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 15, 2)
        return img, thresh, gray

    def enhance_cell_for_handwriting(self, cell_img):
        """
        Mejora específica para texto manuscrito:
        1. Zoom
        2. Escala de grises (NO Binarización pura)
        3. Sharpening (Enfoque de bordes)
        """
        # 1. Zoom x3 (Crucial para letras pequeñas)
        zoomed = cv2.resize(cell_img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # 2. Asegurar escala de grises
        if len(zoomed.shape) == 3:
            gray = cv2.cvtColor(zoomed, cv2.COLOR_BGR2GRAY)
        else:
            gray = zoomed

        # 3. Filtro de afilado (Sharpening) para resaltar trazos de pluma
        # Este kernel resalta los bordes y reduce lo borroso
        kernel = np.array([[-1,-1,-1], 
                           [-1, 9,-1], 
                           [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        
        # Retornamos la imagen en grises afilada, sin convertir a blanco/negro puro
        # Esto permite a la IA ver los matices de la tinta
        return sharpened

    def clean_smart(self, text, width, height):
        """
        Limpieza híbrida basada en geometría y contenido
        """
        if not text: return ""
        
        aspect_ratio = width / height
        text = text.strip()

        # Heurística ajustada: 
        # Ratio < 3.0 atrapa días (19), meses (11) y años (2006)
        # Los nombres completos suelen tener ratios mucho mayores (ej: 8.0)
        is_likely_number_col = aspect_ratio < 3.0

        # Verificación secundaria: ¿El texto parece un número?
        # Si el texto original es "2006", aunque el ratio sea límite, lo tratamos como número
        digits = sum(c.isdigit() for c in text)
        letters = sum(c.isalpha() for c in text)
        looks_like_number = digits > letters

        if is_likely_number_col or looks_like_number:
            # --- MODO NÚMEROS (Fechas) ---
            replacements = {
                'O': '0', 'o': '0', 'D': '0', 'Q': '0', 'U': '0', 'C': '0',
                'I': '1', 'l': '1', '|': '1', '/': '1', '!': '1', 'i': '1', 'L': '1', 't': '1', 'f': '1',
                'Z': '2', 'z': '2', '?': '2',
                'S': '5', 's': '5', '$': '5',
                'B': '8', '&': '8',
                'g': '9', 'q': '9', 'A': '4', 'y': '4'
            }
            for char, num in replacements.items():
                text = text.replace(char, num)
            
            # Dejar solo dígitos y separadores de fecha comunes
            text = re.sub(r'[^0-9]', '', text)
            
        else:
            # --- MODO TEXTO (Nombres) ---
            # Eliminar basura común en OCR
            text = re.sub(r'[@_\[\]{}|\\^<>=;:!#$*%€]', '', text)
            
            # Eliminar secuencias numéricas largas que se hayan colado (ruido)
            # pero permitir números romanos o ordinales cortos si fuera el caso
            if len(text) > 3 and text.isdigit():
                text = "" # Probablemente ruido en una columna de texto
                
            text = re.sub(r'\s+', ' ', text).strip()
            text = text.upper() 

        return text

    def get_table_structure(self, binary_img):
        h, w = binary_img.shape
        # Kernels
        h_k_len = max(int(w / 50), 15)
        v_k_len = max(int(h / 50), 15)

        h_mask = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (h_k_len, 1)))
        v_mask = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_k_len)))
        
        # Reparación fuerte de líneas verticales para evitar celdas fusionadas
        v_mask = cv2.dilate(v_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5)), iterations=2)

        grid = cv2.add(h_mask, v_mask)
        grid = cv2.dilate(grid, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)), iterations=1)
        return grid

    def sort_contours(self, cnts, method="top-to-bottom"):
        reverse = False
        i = 0
        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1 
        boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                            key=lambda b: b[1][i], reverse=reverse))
        return cnts, boundingBoxes

    def run(self, img_path):
        print(f"Procesando imagen: {img_path}")
        # Cargamos img (color), binary (para lineas), gray (para texto original)
        img, binary, gray = self.preprocess_image(img_path)
        
        # 1. Detectar Estructura
        structure = self.get_table_structure(binary)
        
        # 2. Extraer Celdas
        contours, _ = cv2.findContours(structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        valid_contours = []
        img_area = img.shape[0] * img.shape[1]
        
        # Debug visual
        debug_img = img.copy()

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            # Filtro de área permisivo para captar celdas pequeñas
            if area > (img_area * 0.0001) and area < (img_area * 0.9):
                valid_contours.append(c)
                cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)

        self.plot_step(cv2.cvtColor(debug_img, cv2.COLOR_BGR2RGB), "Grid Detectado (Verde)")
        
        if not valid_contours:
            print("❌ Error: No se detectó tabla.")
            return []

        # 3. Ordenar y Agrupar
        valid_contours, bounds = self.sort_contours(valid_contours, method="top-to-bottom")
        rows = []
        current_row = []
        avg_height = np.mean([b[3] for b in bounds]) 
        last_y = bounds[0][1]
        
        for cnt, bound in zip(valid_contours, bounds):
            x, y, w, h = bound
            if y > last_y + (avg_height * 0.55): 
                current_row.sort(key=lambda b: b[0]) 
                rows.append(current_row)
                current_row = []
                last_y = y
            
            # Recorte conservador para no perder texto en bordes
            pad_h = max(0, int(h * 0.05))
            pad_w = max(2, int(w * 0.02))
            y1, y2 = min(y + pad_h, img.shape[0]), max(y, min(y + h - pad_h, img.shape[0]))
            x1, x2 = min(x + pad_w, img.shape[1]), max(x, min(x + w - pad_w, img.shape[1]))
            
            # Usamos la imagen GRAY original para recortar, no la binarizada
            roi = gray[y1:y2, x1:x2] 
            if roi.size > 0:
                current_row.append((x, y, w, h, roi))
        
        if current_row:
            current_row.sort(key=lambda b: b[0])
            rows.append(current_row)
            
        print(f"✅ Tabla estructurada: {len(rows)} registros.")

        # 4. OCR Optimizado
        table_data = []
        for i, row in enumerate(rows):
            row_text = []
            if i % 2 == 0: print(f"  > Leyendo fila {i+1}...")
            
            for (x, y, w, h, roi) in row:
                try:
                    # A) Mejora visual (Sharpening + Zoom)
                    enhanced = self.enhance_cell_for_handwriting(roi)
                    
                    # B) Lectura con parámetros ajustados para manuscrito
                    # adjust_contrast=0.7 ayuda con tinta tenue
                    res = self.reader.readtext(enhanced, detail=0, paragraph=True, adjust_contrast=0.7)
                    raw = " ".join(res)
                    
                    # C) Limpieza inteligente por contexto
                    clean = self.clean_smart(raw, w, h)
                except Exception as e:
                    clean = ""
                row_text.append(clean)
            table_data.append(row_text)
            
        return table_data

# --- EJECUCIÓN ---
print("Sube la imagen problemática:")
uploaded = files.upload()

if uploaded:
    filename = list(uploaded.keys())[0]
    digitizer = SacramentalDigitizer()
    try:
        data = digitizer.run(filename)
        if data:
            df = pd.DataFrame(data)
            # Exportar
            out_name = f"{os.path.splitext(filename)[0]}_v3_manuscrito.xlsx"
            df.to_excel(out_name, index=False, header=False)
            print(f"\n✅ EXCEL GENERADO: {out_name}")
            files.download(out_name)
    except Exception as e:
        print(f"Error crítico: {e}")
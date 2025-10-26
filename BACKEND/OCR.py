# Ejecutar en Google Colab
!apt update -qq
!apt install -y -qq tesseract-ocr tesseract-ocr-spa
!pip install -q pytesseract opencv-python-headless pillow matplotlib numpy

import cv2, numpy as np, pytesseract, json
from matplotlib import pyplot as plt
from google.colab import files
from PIL import Image

# -----------------------
# 1) Subir imagen
# -----------------------
uploaded = files.upload()            # sube Prueba1.png o similar
img_path = list(uploaded.keys())[0]
img_bgr = cv2.imread(img_path)
orig_h, orig_w = img_bgr.shape[:2]

# Mostrar original
plt.figure(figsize=(12,6))
plt.imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
plt.title("Imagen original (sin rotación)")
plt.axis('off')
plt.show()

# -----------------------
# 2) Preprocesado global (NO deskew)
# -----------------------
gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 3)

# Binarización invertida (líneas y texto en blanco sobre fondo negro)
th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                           cv2.THRESH_BINARY_INV, 25, 10)

plt.figure(figsize=(10,6))
plt.imshow(th, cmap='gray')
plt.title("Binarizada (invertida)")
plt.axis('off')
plt.show()

# -----------------------
# 3) Detectar líneas horizontales y verticales (morfología) - MEJORADO
# -----------------------
# Ajustar kernels para detectar solo las líneas principales de separación entre registros

# Para líneas horizontales: usar kernel más largo para detectar solo líneas de separación completas
h_kernel_len = max(orig_w // 8, 100)  # Kernel más largo para líneas completas
# Para líneas verticales: mantener detección normal de columnas
v_kernel_len = max(20, orig_h // 30)

print(f"Kernels: horizontal={h_kernel_len}, vertical={v_kernel_len}")

h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_len, 1))
v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_len))

horizontal = cv2.erode(th, h_kernel, iterations=1)
horizontal = cv2.dilate(horizontal, h_kernel, iterations=1)

vertical = cv2.erode(th, v_kernel, iterations=1)
vertical = cv2.dilate(vertical, v_kernel, iterations=1)

# Filtrar líneas horizontales para quedarnos solo con las de separación principales
# Detectar contornos de líneas horizontales
contours_h, _ = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filtrar líneas horizontales por longitud (solo las que cruzan gran parte de la imagen)
filtered_horizontal = np.zeros_like(horizontal)
min_line_length = orig_w * 0.7  # Al menos 70% del ancho de la imagen

for contour in contours_h:
    x, y, w, h = cv2.boundingRect(contour)
    if w >= min_line_length:  # Solo líneas suficientemente largas
        cv2.drawContours(filtered_horizontal, [contour], -1, 255, -1)

# Usar las líneas horizontales filtradas
horizontal = filtered_horizontal

# Mostrar detección
plt.figure(figsize=(12,6))
plt.subplot(1,2,1); plt.imshow(horizontal, cmap='gray'); plt.title("Horizontal"); plt.axis('off')
plt.subplot(1,2,2); plt.imshow(vertical, cmap='gray'); plt.title("Vertical"); plt.axis('off')
plt.show()

# -----------------------
# 4) Obtener líneas de grid mejorado - enfoque en separaciones reales
# -----------------------

def extract_line_positions(line_img, direction='horizontal'):
    """Extrae posiciones de líneas de una imagen binaria"""
    contours, _ = cv2.findContours(line_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    positions = []
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if direction == 'horizontal':
            # Para líneas horizontales, usar el centro Y
            center_y = y + h // 2
            positions.append(center_y)
        else:  # vertical
            # Para líneas verticales, usar el centro X
            center_x = x + w // 2
            positions.append(center_x)
    
    return sorted(positions)

def cluster_lines(positions, min_distance=15):
    """Agrupa líneas cercanas y retorna las posiciones promedio"""
    if not positions:
        return []
    
    clustered = []
    current_cluster = [positions[0]]
    
    for pos in positions[1:]:
        if pos - current_cluster[-1] <= min_distance:
            current_cluster.append(pos)
        else:
            # Finalizar cluster actual y empezar uno nuevo
            clustered.append(int(np.mean(current_cluster)))
            current_cluster = [pos]
    
    # Agregar el último cluster
    clustered.append(int(np.mean(current_cluster)))
    
    return clustered

# Extraer posiciones de líneas horizontales y verticales
print("Extrayendo posiciones de líneas...")

# Líneas horizontales (separaciones entre registros)
ys_raw = extract_line_positions(horizontal, 'horizontal')
print(f"Líneas horizontales detectadas (raw): {len(ys_raw)} -> {ys_raw}")

# Líneas verticales (separaciones entre columnas)  
xs_raw = extract_line_positions(vertical, 'vertical')
print(f"Líneas verticales detectadas (raw): {len(xs_raw)} -> {xs_raw}")

# Agrupar líneas cercanas
min_row_distance = max(20, orig_h // 50)  # Distancia mínima entre filas
min_col_distance = max(10, orig_w // 100)  # Distancia mínima entre columnas

ys = cluster_lines(ys_raw, min_row_distance)
xs = cluster_lines(xs_raw, min_col_distance)

print(f"Después de clustering:")
print(f"  Filas (Y): {len(ys)} -> {ys}")
print(f"  Columnas (X): {len(xs)} -> {xs}")

# Validar que tengamos líneas suficientes
if len(ys) < 2:
    print("¡Advertencia! Muy pocas líneas horizontales detectadas. Usando detección alternativa...")
    # Fallback: dividir la imagen en secciones basadas en altura promedio de registros
    estimated_row_height = orig_h // 12  # Asumir ~10-12 registros
    ys = list(range(0, orig_h, estimated_row_height)) + [orig_h]

if len(xs) < 4:
    print("¡Advertencia! Muy pocas líneas verticales detectadas. Usando detección alternativa...")
    # Fallback: dividir en columnas aproximadas basado en estructura típica
    col_widths = [0.25, 0.08, 0.08, 0.08, 0.25, 0.08, 0.08, 0.18]  # Proporciones típicas
    xs = [0]
    current_x = 0
    for width_ratio in col_widths:
        current_x += int(orig_w * width_ratio)
        xs.append(min(current_x, orig_w))
    if xs[-1] != orig_w:
        xs.append(orig_w)

# Asegurar que tenemos bordes completos
xs = sorted(set(xs))  # Eliminar duplicados
ys = sorted(set(ys))  # Eliminar duplicados

# Asegurar bordes (0 y ancho/alto) para formar celdas completas
if len(xs) == 0 or xs[0] > 10:
    xs = [0] + xs
if len(xs) == 0 or xs[-1] < orig_w - 10:
    xs = xs + [orig_w]

if len(ys) == 0 or ys[0] > 10:
    ys = [0] + ys
if len(ys) == 0 or ys[-1] < orig_h - 10:
    ys = ys + [orig_h]

# Final sorting
xs = sorted(xs)
ys = sorted(ys)

print(f"Grid final: {len(xs)-1} columnas, {len(ys)-1} filas")
print(f"Columnas (X): {xs}")
print(f"Filas (Y): {ys}")

# Dibujar rejilla para verificación (opcional)
vis = img_bgr.copy()
for x in xs: cv2.line(vis, (x,0),(x,orig_h),(0,255,0),1)
for y in ys: cv2.line(vis, (0,y),(orig_w,y),(255,0,0),1)

plt.figure(figsize=(12,8))
plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
plt.title("Grid overlay (sin rotación)")
plt.axis('off')
plt.show()

# -----------------------
# 5) Nuevo enfoque: Procesamiento por tuplas (filas) individuales
# -----------------------

print("Iniciando procesamiento por tuplas individuales...")

# Filtrar y validar filas para registros completos
def analyze_row_content(y1, y2):
    """Analiza si una fila contiene contenido de texto significativo"""
    if y2 - y1 < 25:  # Muy pequeña
        return False
    
    # Extraer región de la fila
    row_region = gray[y1:y2, 0:orig_w]
    
    # Binarizar para análisis
    row_binary = cv2.adaptiveThreshold(row_region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 15, 8)
    
    # Contar píxeles de texto (blancos en imagen binarizada)
    text_pixels = np.sum(row_binary == 255)
    total_pixels = row_binary.shape[0] * row_binary.shape[1]
    text_ratio = text_pixels / total_pixels
    
    # Debe tener suficiente contenido de texto (al menos 5% de la región)
    return text_ratio > 0.05

# Analizar y filtrar filas válidas
valid_rows = []
print("Analizando filas para detectar registros completos...")

for i in range(len(ys)-1):
    y1, y2 = ys[i], ys[i+1]
    height = y2 - y1
    
    print(f"Analizando región Y: {y1}-{y2} (altura: {height})")
    
    # Filtros múltiples:
    # 1. Altura mínima para un registro
    if height < 30:
        print(f"  -> Descartada: muy pequeña (altura {height} < 30)")
        continue
    
    # 2. Altura máxima razonable (evitar regiones que incluyen múltiples registros)
    if height > orig_h // 8:  # No más de 1/8 de la imagen total
        print(f"  -> Descartada: muy grande (altura {height} > {orig_h//8})")
        continue
    
    # 3. Análisis de contenido
    if not analyze_row_content(y1, y2):
        print(f"  -> Descartada: poco contenido de texto")
        continue
    
    valid_rows.append((y1, y2, len(valid_rows)+1))
    print(f"  -> ✓ Válida como registro {len(valid_rows)}")

print(f"\n{'='*60}")
print(f"FILAS VÁLIDAS DETECTADAS: {len(valid_rows)}")
print(f"{'='*60}")

for i, (y1, y2, record_num) in enumerate(valid_rows):
    print(f"  Registro {record_num}: Y={y1}-{y2}, altura={y2-y1}px")

# Si detectamos muy pocas filas, intentar un enfoque alternativo
if len(valid_rows) < 5:
    print(f"\n¡Advertencia! Solo {len(valid_rows)} filas detectadas. Intentando método alternativo...")
    
    # Método alternativo: buscar espacios entre texto para identificar registros
    # Crear proyección horizontal (suma de píxeles por fila)
    row_binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 15, 8)
    horizontal_projection = np.sum(row_binary, axis=1)
    
    # Encontrar valles (líneas con poco texto) que indican separaciones
    threshold = np.mean(horizontal_projection) * 0.3
    separators = []
    
    for i in range(len(horizontal_projection)):
        if horizontal_projection[i] < threshold:
            separators.append(i)
    
    # Agrupar separadores consecutivos y encontrar centros
    if separators:
        separator_groups = []
        current_group = [separators[0]]
        
        for sep in separators[1:]:
            if sep - current_group[-1] <= 3:  # Separadores consecutivos
                current_group.append(sep)
            else:
                separator_groups.append(current_group)
                current_group = [sep]
        separator_groups.append(current_group)
        
        # Usar centros de grupos como separadores de registros
        alternative_ys = [0]
        for group in separator_groups:
            center = int(np.mean(group))
            if center > 20 and center < orig_h - 20:  # No muy cerca de los bordes
                alternative_ys.append(center)
        alternative_ys.append(orig_h)
        
        # Recrear filas válidas con método alternativo
        valid_rows_alt = []
        for i in range(len(alternative_ys)-1):
            y1, y2 = alternative_ys[i], alternative_ys[i+1]
            if y2 - y1 >= 30 and analyze_row_content(y1, y2):
                valid_rows_alt.append((y1, y2, len(valid_rows_alt)+1))
        
        if len(valid_rows_alt) > len(valid_rows):
            print(f"Método alternativo encontró {len(valid_rows_alt)} registros. Usando este resultado.")
            valid_rows = valid_rows_alt
            # Actualizar ys para consistencia
            ys = alternative_ys

# -----------------------
# 6) Funciones de procesamiento por tupla individual
# -----------------------
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def clean_and_enhance_row_image(row_img):
    """Limpieza ultra-suave que preserva la forma original de los caracteres"""
    # NO aplicar filtros que puedan distorsionar caracteres
    # Solo una mejora de contraste muy ligera si es necesario
    
    # Evaluar si necesita mejora de contraste
    mean_val = np.mean(row_img)
    std_val = np.std(row_img)
    
    # Solo mejorar contraste si la imagen está muy plana
    if std_val < 30:  # Muy poco contraste
        # CLAHE ultra-suave solo para casos extremos
        clahe = cv2.createCLAHE(clipLimit=1.1, tileGridSize=(8,8))
        enhanced = clahe.apply(row_img)
    else:
        # Usar imagen original sin modificaciones
        enhanced = row_img.copy()
    
    # Binarización ultra-conservadora que preserve detalles finos
    # Usar parámetros que mantengan la forma original de caracteres
    binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 21, 8)  # Ventana más grande, menos agresivo
    
    # NO aplicar morfología que pueda causar "cortes de sierra"
    # Devolver directamente la imagen binarizada
    return binary

def detect_cells_in_row(row_img, row_xs):
    """Detecta las celdas individuales dentro de una fila"""
    cells_info = []
    
    for i in range(len(row_xs)-1):
        x1, x2 = row_xs[i], row_xs[i+1]
        
        # Padding mínimo para evitar cortar texto
        pad_x = max(1, int((x2-x1)*0.005))
        
        cell_x1 = max(0, x1 + pad_x)
        cell_x2 = min(row_img.shape[1], x2 - pad_x)
        
        if cell_x2 - cell_x1 > 5:  # Solo celdas con ancho mínimo
            cells_info.append({
                'index': i,
                'x1': cell_x1,
                'x2': cell_x2,
                'width': cell_x2 - cell_x1
            })
    
    return cells_info

def create_vectorized_text(img):
    """Crea efecto de texto vectorial suave tipo Photoshop"""
    # Paso 1: Suavizado bilateral que preserva bordes pero suaviza ruido
    bilateral = cv2.bilateralFilter(img, 9, 75, 75)
    
    # Paso 2: Desenfoque gaussiano muy sutil para anti-aliasing
    gaussian = cv2.GaussianBlur(bilateral, (3, 3), 0.5)
    
    # Paso 3: Mejora de contraste localizada muy suave
    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(4, 4))
    contrast_enhanced = clahe.apply(gaussian)
    
    # Paso 4: Sharpening muy sutil para definir bordes
    kernel_sharpen = np.array([[-0.1, -0.1, -0.1],
                              [-0.1,  1.8, -0.1],
                              [-0.1, -0.1, -0.1]])
    sharpened = cv2.filter2D(contrast_enhanced, -1, kernel_sharpen)
    
    # Paso 5: Clamp a rango válido
    vectorized = np.clip(sharpened, 0, 255).astype(np.uint8)
    
    return vectorized

def apply_smart_antialiasing(img):
    """Aplica anti-aliasing inteligente que mejora la legibilidad"""
    # Paso 1: Desenfoque anisotrópico (preserva bordes principales)
    anisotropic = cv2.edgePreservingFilter(img, flags=1, sigma_s=50, sigma_r=0.4)
    
    # Paso 2: Combinación ponderada con original
    # 70% anti-aliasing + 30% original para preservar detalles
    blended = cv2.addWeighted(anisotropic, 0.7, img, 0.3, 0)
    
    # Paso 3: Ajuste de gamma para mejorar percepción
    gamma = 1.1
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 
                     for i in np.arange(0, 256)]).astype("uint8")
    gamma_corrected = cv2.LUT(blended, table)
    
    return gamma_corrected

def enhance_text_edges(img):
    """Mejora los bordes del texto tipo 'unsharp mask' de Photoshop"""
    # Paso 1: Crear máscara desenfocada
    blurred = cv2.GaussianBlur(img, (5, 5), 1.0)
    
    # Paso 2: Crear máscara de contraste (diferencia)
    mask = cv2.subtract(img, blurred)
    
    # Paso 3: Amplificar la máscara (ajustable)
    amplified_mask = cv2.multiply(mask, 1.5)
    
    # Paso 4: Sumar máscara amplificada a imagen original
    enhanced = cv2.add(img, amplified_mask)
    
    # Paso 5: Suavizar resultado para evitar artefactos
    final = cv2.bilateralFilter(enhanced, 5, 50, 50)
    
    # Paso 6: Clamp a rango válido
    result = np.clip(final, 0, 255).astype(np.uint8)
    
    return result

def extract_text_from_cell(cell_img, cell_info):
    """Extrae texto de celda individual con suavizado vectorial para máxima calidad"""
    if cell_img.shape[0] < 5 or cell_img.shape[1] < 5:
        return ""
    
    # Escalado inteligente con suavizado tipo "vectorial"
    height, width = cell_img.shape
    target_height = 64  # Aumentado para mejor calidad
    
    # Siempre escalar para mejorar la calidad (incluso si ya es grande)
    scale = max(target_height / height, 2.0)  # Mínimo 2x para suavizado
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Paso 1: Escalado inicial con LANCZOS para preservar bordes
    cell_upscaled = cv2.resize(cell_img, (new_width, new_height), 
                              interpolation=cv2.INTER_LANCZOS4)
    
    # Crear versiones con suavizado "vectorial"
    image_versions = []
    
    # Versión 1: Suavizado vectorial premium
    vectorized = create_vectorized_text(cell_upscaled)
    image_versions.append(("vectorized", vectorized))
    
    # Versión 2: Anti-aliasing suave
    antialiased = apply_smart_antialiasing(cell_upscaled)
    image_versions.append(("antialiased", antialiased))
    
    # Versión 3: Mejora de bordes tipo Photoshop
    enhanced_edges = enhance_text_edges(cell_upscaled)
    image_versions.append(("enhanced", enhanced_edges))
    
    # Versión 4: Original escalado como fallback
    image_versions.append(("upscaled", cell_upscaled))
    
    # Versión 5: Invertir si está en fondo negro
    if np.mean(cell_upscaled) < 128:
        cell_inverted = 255 - cell_upscaled
        vectorized_inv = create_vectorized_text(cell_inverted)
        image_versions.append(("vectorized_inv", vectorized_inv))
    
    # Configuraciones OCR optimizadas por tipo de celda
    cell_width_ratio = cell_info['width'] / float(orig_w)
    
    if cell_width_ratio < 0.05:  # Celdas muy pequeñas - números únicamente
        configs = [
            '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789'  # PSM 13 para línea de texto sin estructura
        ]
    elif cell_width_ratio < 0.08:  # Celdas pequeñas - números o palabras cortas
        configs = [
            '--oem 3 --psm 8 -l spa',
            '--oem 3 --psm 7 -l spa',
            '--oem 3 --psm 13 -l spa',
            '--oem 3 --psm 6 -l spa'
        ]
    else:  # Celdas grandes - texto completo
        configs = [
            '--oem 3 --psm 6 -l spa',
            '--oem 3 --psm 7 -l spa',
            '--oem 3 --psm 8 -l spa'
        ]
    
    # Estrategia de evaluación: priorizar versiones vectoriales
    best_result = ""
    best_confidence = 0
    best_version_name = ""
    
    # Orden de prioridad: vectorized > enhanced > antialiased > upscaled > vectorized_inv
    priority_order = ["vectorized", "enhanced", "antialiased", "upscaled", "vectorized_inv"]
    
    for img_name, img_version in image_versions:
        # Asignar peso de prioridad
        if img_name in priority_order:
            priority_weight = len(priority_order) - priority_order.index(img_name)
        else:
            priority_weight = 1
        
        for config in configs:
            try:
                text = pytesseract.image_to_string(img_version, config=config)
                cleaned_text = clean_extracted_text(text)
                
                if not cleaned_text:
                    continue
                
                # Calcular "confianza" basada en longitud, caracteres válidos y prioridad
                length_score = min(len(cleaned_text), 20)  # Máximo 20 puntos por longitud
                char_score = sum(1 for c in cleaned_text if c.isalnum()) * 2  # 2 puntos por carácter válido
                priority_score = priority_weight * 5  # Hasta 25 puntos por prioridad
                
                total_confidence = length_score + char_score + priority_score
                
                # Si encontramos un resultado excelente con versión vectorial, úsalo inmediatamente
                if img_name == "vectorized" and len(cleaned_text) > 2:
                    return cleaned_text
                
                # Guardar el mejor resultado general
                if total_confidence > best_confidence:
                    best_result = cleaned_text
                    best_confidence = total_confidence
                    best_version_name = img_name
                
                # Para versiones prioritarias, ser menos estricto
                if img_name in ["vectorized", "enhanced"] and len(cleaned_text) > 1:
                    break
                    
            except Exception as e:
                continue
        
        # Si tenemos un resultado excelente, no probar más versiones
        if best_confidence > 50:  # Umbral de confianza alta
            break
    
    return best_result

def clean_extracted_text(text):
    """Limpieza minimalista que preserva el texto original tanto como sea posible"""
    import re
    
    if not text or len(text.strip()) == 0:
        return ""
    
    # Limpieza básica ultra-conservadora
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)  # Múltiples espacios -> un espacio
    text = text.strip()
    
    if not text:
        return ""
    
    # Análisis de contenido para determinar estrategia
    letters = sum(1 for c in text if c.isalpha())
    digits = sum(1 for c in text if c.isdigit())
    
    # Estrategia para números (fechas, códigos)
    if digits >= letters and digits > 0:
        # Correcciones muy selectivas para números comunes
        specific_corrections = {
            'O': '0', 'o': '0',  # Solo O/o -> 0
            'I': '1', 'l': '1',  # Solo I/l -> 1
            'S': '5', 's': '5'   # Solo S/s -> 5
        }
        
        for old, new in specific_corrections.items():
            text = text.replace(old, new)
        
        # Mantener solo dígitos y espacios para fechas
        text = re.sub(r'[^0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
    
    # Estrategia para texto (nombres, lugares)
    elif letters > digits:
        # Correcciones muy selectivas para texto
        specific_corrections = {
            '0': 'O',  # Solo 0 -> O
            '1': 'I',  # Solo 1 -> I
            '5': 'S'   # Solo 5 -> S (casos evidentes)
        }
        
        # Aplicar solo correcciones evidentes
        for old, new in specific_corrections.items():
            text = text.replace(old, new)
        
        # Preservar caracteres válidos incluyendo acentos
        text = re.sub(r'[^A-ZÁÉÍÓÚÑa-záéíóúñ\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Capitalización inteligente para nombres
        if len(text) > 0:
            # Solo capitalizar si parece ser un nombre propio
            words = text.split()
            capitalized_words = []
            for word in words:
                if len(word) >= 2:  # Solo palabras de 2+ caracteres
                    # Mantener primera letra mayúscula, resto en mayúsculas para consistencia
                    capitalized_words.append(word.upper())
                else:
                    capitalized_words.append(word.upper())
            text = ' '.join(capitalized_words)
    
    # Para contenido mixto: limpieza mínima
    else:
        # Solo eliminar caracteres claramente problemáticos
        text = re.sub(r'[^\w\sÁÉÍÓÚÑáéíóúñ.-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def process_single_row(row_y1, row_y2, row_num):
    """Procesa una sola fila (tupla) de la tabla"""
    print(f"\n{'='*60}")
    print(f"PROCESANDO TUPLA {row_num}")
    print(f"Coordenadas: y={row_y1} a y={row_y2}, altura={row_y2-row_y1}")
    print(f"{'='*60}")
    
    # Extraer la imagen de la fila
    row_img = gray[row_y1:row_y2, 0:orig_w]
    
    # Mostrar imagen original de la fila
    plt.figure(figsize=(15, 3))
    plt.imshow(row_img, cmap='gray')
    plt.title(f"Tupla {row_num} - Imagen Original")
    plt.axis('off')
    plt.show()
    
    # Limpiar y mejorar la imagen de la fila
    cleaned_row = clean_and_enhance_row_image(row_img)
    
    # Mostrar imagen limpia
    plt.figure(figsize=(15, 3))
    plt.imshow(cleaned_row, cmap='gray')
    plt.title(f"Tupla {row_num} - Imagen Limpiada")
    plt.axis('off')
    plt.show()
    
    # Detectar celdas en la fila
    cells_info = detect_cells_in_row(cleaned_row, xs)
    print(f"Celdas detectadas: {len(cells_info)}")
    
    # Extraer texto de cada celda usando AMBAS versiones: original y limpia
    extracted_texts = []
    
    # Mostrar mosaico de celdas individuales para diagnóstico
    num_cells = len(cells_info)
    if num_cells > 0:
        cols = min(num_cells, 8)  # Máximo 8 columnas
        rows = (num_cells + cols - 1) // cols
        
        # Crear figura con comparación lado a lado
        plt.figure(figsize=(25, 4 * rows))
        
        for idx, cell_info in enumerate(cells_info):
            x1, x2 = cell_info['x1'], cell_info['x2']
            
            # Extraer celdas de AMBAS versiones
            cell_img_original = row_img[0:row_img.shape[0], x1:x2]  # De imagen original
            cell_img_cleaned = cleaned_row[0:cleaned_row.shape[0], x1:x2]  # De imagen limpia
            
            # Probar OCR en AMBAS versiones y tomar el mejor resultado
            text_from_original = extract_text_from_cell(cell_img_original, cell_info)
            text_from_cleaned = extract_text_from_cell(cell_img_cleaned, cell_info)
            
            # Elegir el mejor resultado basado en longitud y calidad
            if len(text_from_original) >= len(text_from_cleaned) and text_from_original.strip():
                final_text = text_from_original
                best_source = "original"
                best_img = cell_img_original
            elif text_from_cleaned.strip():
                final_text = text_from_cleaned
                best_source = "cleaned"
                best_img = cell_img_cleaned
            else:
                final_text = text_from_original if text_from_original else text_from_cleaned
                best_source = "original"
                best_img = cell_img_original
            
            extracted_texts.append(final_text)
            
            # Mostrar la celda que dio el mejor resultado
            plt.subplot(rows, cols, idx + 1)
            plt.imshow(best_img, cmap='gray')
            plt.title(f"Celda {idx+1} ({best_source}): '{final_text[:15]}{'...' if len(final_text) > 15 else ''}'", 
                     fontsize=7)
            plt.axis('off')
            
            print(f"  Celda {cell_info['index']+1} (x={x1}-{x2}, w={cell_info['width']}) [{best_source}]: '{final_text}'")
        
        plt.tight_layout()
        plt.show()
    
    # Crear cadena separada por comas
    row_string = ", ".join(extracted_texts)
    
    # Crear JSON para esta tupla
    row_json = {
        "tupla": row_num,
        "celdas": extracted_texts,
        "cadena": row_string,
        "coordenadas": {
            "y1": int(row_y1),
            "y2": int(row_y2),
            "altura": int(row_y2 - row_y1)
        }
    }
    
    print(f"\nResultado de la tupla {row_num}:")
    print(f"Cadena: {row_string}")
    
    return row_json

# -----------------------
# 7) Procesar todas las tuplas
# -----------------------
print(f"\n{'='*80}")
print("INICIANDO PROCESAMIENTO DE TUPLAS INDIVIDUALES")
print(f"{'='*80}")

all_rows_json = []

for i, (y1, y2, row_num) in enumerate(valid_rows):
    try:
        row_result = process_single_row(y1, y2, i+1)
        all_rows_json.append(row_result)
        
        # Guardar resultado individual
        with open(f"tupla_{i+1}.json", "w", encoding="utf-8") as f:
            json.dump(row_result, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"Error procesando tupla {i+1}: {e}")
        continue

print(f"\n{'='*80}")
print("PROCESAMIENTO COMPLETADO")
print(f"{'='*80}")

# Mostrar resumen
print(f"\nTotal de tuplas procesadas exitosamente: {len(all_rows_json)}")
for i, row_data in enumerate(all_rows_json, 1):
    print(f"Tupla {i}: {len(row_data['celdas'])} celdas - '{row_data['cadena'][:80]}{'...' if len(row_data['cadena']) > 80 else ''}'")

print(f"\nGuardado de tuplas individuales completado.")

# -----------------------
# 8) Guardar resultado final consolidado
# -----------------------

# Crear archivo consolidado con todas las tuplas
consolidated_result = {
    "total_tuplas": len(all_rows_json),
    "timestamp": "2025-10-22",
    "metodo": "procesamiento_individual_por_tuplas", 
    "tuplas": all_rows_json
}

# Guardar resultado consolidado
with open("resultado_tuplas_consolidado.json", "w", encoding="utf-8") as f:
    json.dump(consolidated_result, f, indent=2, ensure_ascii=False)

# Mostrar resultado final
print(f"\n{'='*80}")
print("RESULTADO FINAL CONSOLIDADO")
print(f"{'='*80}")
print(json.dumps(consolidated_result, indent=2, ensure_ascii=False))

print(f"\nArchivos generados:")
print(f"  - resultado_tuplas_consolidado.json (archivo principal)")
for i in range(len(all_rows_json)):
    print(f"  - tupla_{i+1}.json (tupla individual)")

print(f"\nResumen del procesamiento:")
print(f"  Total de tuplas procesadas: {len(all_rows_json)}")
print(f"  Método utilizado: Procesamiento individual por tuplas")
print(f"  Archivos individuales: {len(all_rows_json)} archivos JSON")
print(f"  Archivo consolidado: 1 archivo JSON")

# Estadísticas detalladas
if all_rows_json:
    print(f"\nEstadísticas por tupla:")
    for i, tupla in enumerate(all_rows_json, 1):
        celdas_con_contenido = sum(1 for celda in tupla['celdas'] if celda.strip())
        print(f"  Tupla {i}: {len(tupla['celdas'])} celdas totales, {celdas_con_contenido} con contenido")
        print(f"    Cadena: {tupla['cadena'][:100]}{'...' if len(tupla['cadena']) > 100 else ''}")

print(f"\n{'='*80}")
print("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
print(f"{'='*80}")

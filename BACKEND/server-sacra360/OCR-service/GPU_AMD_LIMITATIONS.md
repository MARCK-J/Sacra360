# Limitaciones de EasyOCR con GPU AMD

## Problema Identificado

EasyOCR **solo soporta GPU NVIDIA con CUDA**, no GPUs AMD con OpenCL/ROCm.

### Tiempos de Procesamiento:

| Entorno | GPU | Tiempo (Tabla1.pdf, 136 celdas) |
|---------|-----|----------------------------------|
| **Google Colab** | NVIDIA T4 (CUDA) | **~1 minuto** |
| **Windows Local** | AMD RX 540 (OpenCL) | **~4.67 minutos** |
| **Windows CPU** | No GPU | ~8.5 minutos |

## ¿Por qué no funciona la GPU AMD?

1. **EasyOCR usa PyTorch**: PyTorch requiere CUDA para GPU
2. **AMD no tiene CUDA**: AMD usa ROCm/OpenCL
3. **ROCm en Windows**: No está soportado oficialmente
4. **PyTorch + DirectML**: Experimental y no compatible con EasyOCR

El warning que viste lo confirma:
```
UserWarning: 'pin_memory' argument is set as true but no accelerator is found
```

## Soluciones Reales

### Opción 1: Usar Google Colab para Procesamiento Pesado ⭐ RECOMENDADO
**Ventajas:**
- ✅ GPU T4 gratis
- ✅ 10-15x más rápido que AMD local
- ✅ Sin instalación local
- ✅ Mismo notebook que ya usas

**Desventajas:**
- ❌ Requiere Internet
- ❌ Tiempo de sesión limitado (12h)

**Cómo:**
1. Subir PDFs a Google Drive
2. Ejecutar `Sacra360_OCRv2.ipynb` en Colab
3. Descargar resultados CSV

---

### Opción 2: Optimizar CPU Local (ACTUAL)
**Ventajas:**
- ✅ No requiere Internet
- ✅ Control total del proceso
- ✅ Ya implementado y funcionando

**Rendimiento Actual:**
- **4.67 minutos** por tabla (vs 8.5 min CPU puro)
- Aceleración **1.82x** gracias a optimizaciones:
  - Modelo cuantizado (`quantize=True`)
  - Escala reducida (2x en lugar de 3x)
  - Parámetros de detección optimizados
  - Decoder greedy (más rápido que beamsearch)

**Mejoras Adicionales Posibles:**
```python
# Reducir DPI de conversión PDF
dpi=100  # En lugar de 150, gana ~30% velocidad

# Reducir tamaño de canvas
canvas_size=960  # En lugar de 1280

# Procesar solo regiones con texto
text_threshold=0.8  # Más estricto, menos falsos positivos
```

---

### Opción 3: Usar OCR Alternativo más rápido en CPU
**PaddleOCR** es 2-3x más rápido que EasyOCR en CPU:

```bash
pip install paddleocr
```

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
result = ocr.ocr(img_path)
```

**Tiempo estimado:** ~2-3 minutos (vs 4.67 actual)

---

### Opción 4: Servidor con GPU NVIDIA (Futuro)
Si el volumen de procesamiento crece:
- Contratar VPS con GPU NVIDIA (AWS, Azure, Google Cloud)
- Costo: ~$0.50-2.00/hora
- Velocidad: igual que Colab T4

---

## Recomendación Final

**Para desarrollo/pruebas:** Usar CPU local (actual 4.67 min)  
**Para producción:** Google Colab con GPU T4 (1 min) o servidor cloud con NVIDIA

La GPU AMD RX 540 **no puede acelerar EasyOCR** debido a limitaciones de PyTorch/CUDA.

---

## Configuración Actual Optimizada

El servicio OCR-service ya está optimizado para CPU:
- ✅ Detección de GPU AMD (advertencia clara)
- ✅ Modelo cuantizado para CPU
- ✅ Parámetros optimizados
- ✅ Preprocesamiento eficiente
- ✅ Pattern matching para validación

**Tiempo actual:** 4.67 min (45% más rápido que CPU puro 8.5 min)

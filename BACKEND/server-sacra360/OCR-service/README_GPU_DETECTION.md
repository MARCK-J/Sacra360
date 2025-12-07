# Sacra360 OCR Service - Soporte Multi-GPU

## 🎯 Resumen

El servicio OCR ahora detecta automáticamente el tipo de GPU disponible y se adapta:

- ✅ **GPU NVIDIA con CUDA**: Usa aceleración GPU completa (10-15x más rápido)
- ✅ **GPU AMD/Intel/Otros**: Fallback a CPU optimizado con quantización
- ✅ **Sin GPU**: CPU optimizado

## 🔍 Detección Automática

El sistema verifica en orden:

1. **Hardware GPU físico** (vía OpenCL): AMD, NVIDIA, Intel, etc.
2. **CUDA disponible** (vía PyTorch): Solo NVIDIA
3. **Decisión**: GPU si CUDA disponible, sino CPU optimizado

## 🚀 Modos de Operación

### Modo GPU NVIDIA/CUDA (Más Rápido)
```
Hardware: NVIDIA GTX/RTX/T4/A100
Software: CUDA + PyTorch GPU
Velocidad: ~1 minuto (Tabla1.pdf, 136 celdas)
Optimizaciones: GPU nativa, sin cuantización
```

**Cuándo:**
- GPU NVIDIA detectada físicamente
- `torch.cuda.is_available() == True`
- `use_gpu=True` en TableProcessor

**Logs:**
```
🎮 GPU NVIDIA detectada: Tesla T4
✓ GPU NVIDIA/CUDA disponible, habilitando aceleración GPU
✓ EasyOCR inicializado en 2.5s
  🚀 Modo: GPU NVIDIA/CUDA
  ⚡ Aceleración GPU activa
```

---

### Modo CPU Optimizado (Actual en AMD)
```
Hardware: AMD RX 540 / CPU Intel/AMD
Software: PyTorch CPU + quantización
Velocidad: ~4.67 minutos (Tabla1.pdf, 136 celdas)
Optimizaciones: Modelo quantizado, decoder greedy, canvas reducido
```

**Cuándo:**
- GPU AMD/Intel/otra detectada (no CUDA)
- `torch.cuda.is_available() == False`
- Fallback automático

**Logs:**
```
⚠️  GPU AMD detectada pero EasyOCR requiere NVIDIA/CUDA
   Usando CPU optimizado (quantize=True)
✓ EasyOCR inicializado en 1.81s
  💻 Modo: CPU optimizado (quantized)
  ℹ️  Para GPU se requiere NVIDIA con CUDA
```

---

## 📊 Comparativa de Rendimiento

| Hardware | Modo | Tiempo (Tabla1.pdf) | Aceleración |
|----------|------|---------------------|-------------|
| **NVIDIA T4** (Colab) | GPU/CUDA | ~1 min | **8.5x** |
| **AMD RX 540** (Local) | CPU Optimizado | ~4.67 min | **1.82x** |
| **CPU Puro** (sin optimizar) | CPU Básico | ~8.5 min | 1.0x |

## 🛠️ Uso

### Inicialización Automática
```python
from app.table_processor import TableProcessor

# Se detecta automáticamente el hardware
processor = TableProcessor(
    use_gpu=True,      # Intentará usar GPU si es NVIDIA
    languages=['en'],
    dpi=150,
    num_cols=10
)

# Verificar qué modo se está usando
info = processor.get_info()
print(f"Modo: {info['mode']}")  
# "GPU NVIDIA/CUDA" o "CPU Optimizado"

print(f"CUDA Disponible: {info['cuda_available']}")
print(f"GPU Física: {info['gpu_type']}")
```

### Procesamiento
```python
# Mismo código funciona en GPU NVIDIA o CPU
df = processor.process_pdf(
    pdf_path="path/to/tabla.pdf",
    pattern=['L','N','N','N','L','N','N','N','L','L']
)
```

## 🔧 Optimizaciones Implementadas

### Para GPU NVIDIA/CUDA:
- ✅ Aceleración GPU nativa
- ✅ Batch processing en GPU
- ✅ Sin cuantización (modelo completo)
- ✅ Pin memory habilitado

### Para CPU (AMD/Otros):
- ✅ Modelo quantizado (INT8)
- ✅ Decoder greedy (vs beamsearch)
- ✅ Canvas reducido (1280px)
- ✅ Escala 2x (vs 3x original)
- ✅ Interpolación linear (vs cubic)
- ✅ Thresholds optimizados

## 🌐 Alternativas para Máxima Velocidad

### Google Colab (Recomendado para producción)
```python
# En Google Colab con GPU T4 gratis
!pip install easyocr pdf2image

# Mismo código, detecta NVIDIA T4 automáticamente
processor = TableProcessor(use_gpu=True)
# ✓ GPU NVIDIA/CUDA activada → ~1 minuto
```

### Servidor Cloud con NVIDIA
- AWS EC2 (g4dn.xlarge): NVIDIA T4
- Google Cloud (n1-standard-4 + T4)
- Azure (NC6): NVIDIA K80

## 📝 Información de Detección

El método `get_info()` retorna:

```python
{
    "use_gpu": False,              # GPU activada en EasyOCR
    "mode": "CPU Optimizado",      # o "GPU NVIDIA/CUDA"
    
    "gpu_type": "AMD/Other",       # Hardware físico detectado
    "backend": "OpenCL",           # API de la GPU física
    "vram_gb": 8.0,                # VRAM de la GPU física
    
    "cuda_available": False,       # CUDA disponible (solo NVIDIA)
    "cuda_device": "N/A",          # Nombre del dispositivo CUDA
    
    "languages": ["en"],
    "dpi": 150,
    "num_cols": 10
}
```

## ⚡ Mejoras Futuras

- [ ] Soporte DirectML para GPU AMD en Windows
- [ ] Soporte ROCm para GPU AMD en Linux
- [ ] Apple Metal para GPU M1/M2/M3
- [ ] ONNX Runtime para inferencia multi-GPU
- [ ] PaddleOCR como alternativa más rápida en CPU

## 🆘 Troubleshooting

### "GPU AMD pero usando CPU"
**Normal**: EasyOCR no soporta AMD. El sistema automáticamente usa CPU optimizado.

### "CUDA no disponible"
**Verificar**:
```python
import torch
print(torch.cuda.is_available())  # Debe ser True para NVIDIA
print(torch.cuda.get_device_name(0))  # Nombre de GPU NVIDIA
```

### "Muy lento en mi GPU NVIDIA"
**Verificar**:
1. Drivers NVIDIA actualizados
2. CUDA Toolkit instalado
3. PyTorch versión GPU: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`

## 📚 Referencias

- [EasyOCR GPU Requirements](https://github.com/JaidedAI/EasyOCR#gpu-support)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)
- [Google Colab Free GPU](https://colab.research.google.com/)

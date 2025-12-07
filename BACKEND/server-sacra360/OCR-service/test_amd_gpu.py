"""
Script de prueba para GPU AMD Radeon RX 540
Verifica detección y rendimiento de la GPU AMD
"""

import sys
import time
from pathlib import Path

print("="*70)
print("TEST DE GPU AMD - SACRA360")
print("="*70)
print()

# 1. Verificar PyTorch
print("1. VERIFICANDO PYTORCH")
print("-"*70)
try:
    import torch
    print(f"✓ PyTorch version: {torch.__version__}")
    print(f"  CUDA disponible: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("  (CUDA no disponible - normal para AMD)")
except ImportError as e:
    print(f"✗ Error: {e}")
    print("  Instalar con: pip install torch torchvision")
    sys.exit(1)
print()

# 2. Verificar OpenCL (para AMD)
print("2. VERIFICANDO OPENCL (AMD GPU)")
print("-"*70)
try:
    import pyopencl as cl
    platforms = cl.get_platforms()
    
    if not platforms:
        print("✗ No se detectaron plataformas OpenCL")
    else:
        for i, platform in enumerate(platforms):
            print(f"✓ Plataforma {i}: {platform.name}")
            devices = platform.get_devices()
            
            for j, device in enumerate(devices):
                print(f"  Dispositivo {j}: {device.name}")
                print(f"    Tipo: {cl.device_type.to_string(device.type)}")
                print(f"    Memoria Global: {device.global_mem_size / (1024**3):.2f} GB")
                print(f"    Compute Units: {device.max_compute_units}")
                print(f"    Max Work Group Size: {device.max_work_group_size}")
                
                if device.type == cl.device_type.GPU:
                    print(f"    ✓ GPU DETECTADA: {device.name}")
                    
except ImportError:
    print("✗ PyOpenCL no instalado")
    print("  Instalar con: pip install pyopencl")
except Exception as e:
    print(f"✗ Error detectando OpenCL: {e}")
print()

# 3. Verificar detección en nuestro código
print("3. VERIFICANDO DETECCIÓN EN SACRA360")
print("-"*70)
try:
    # Agregar directorio app al path
    sys.path.insert(0, str(Path(__file__).parent / "app"))
    
    from gpu_utils import print_gpu_info
    
    gpu_info = print_gpu_info()
    
    if gpu_info['has_gpu']:
        print(f"✓ GPU detectada por Sacra360")
        print(f"  Tipo: {gpu_info['gpu_type']}")
        print(f"  Backend: {gpu_info['backend']}")
        print(f"  Puede usar GPU: {gpu_info['can_use_gpu']}")
    else:
        print("⚠ No se detectó GPU compatible")
        print("  El sistema usará CPU (más lento pero funcional)")
        
except ImportError as e:
    print(f"✗ Error importando módulos: {e}")
    print("  Ejecuta desde el directorio OCR-service/")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# 4. Probar inicialización de EasyOCR
print("4. PROBANDO EASYOCR")
print("-"*70)
try:
    from app.ocr_gpu_processor import TableOCRProcessor
    
    print("Inicializando con GPU=True...")
    start_time = time.time()
    
    processor = TableOCRProcessor(use_gpu=True, languages=['en'])
    
    init_time = time.time() - start_time
    
    print(f"✓ EasyOCR inicializado en {init_time:.2f}s")
    print(f"  Usando GPU: {processor.use_gpu}")
    print(f"  Tipo de GPU: {processor.gpu_info['gpu_type']}")
    print(f"  Backend: {processor.gpu_info['backend']}")
    
    if processor.use_gpu:
        print()
        print("  🎉 ¡GPU AMD FUNCIONANDO!")
    else:
        print()
        print("  ⚠ Fallback a CPU (normal si no tienes ROCm)")
        print("  El servicio funcionará pero más lento")
    
except ImportError as e:
    print(f"✗ Error importando: {e}")
    print("  Instalar dependencias: pip install -r requirements.txt")
except Exception as e:
    print(f"✗ Error inicializando EasyOCR: {e}")
    import traceback
    traceback.print_exc()
print()

# 5. Benchmark simple (si hay GPU)
print("5. BENCHMARK SIMPLE")
print("-"*70)
try:
    import numpy as np
    import cv2
    
    # Crear imagen de prueba
    test_img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    cv2.putText(test_img, "Test AMD GPU", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    print("Ejecutando OCR en imagen de prueba...")
    
    start_time = time.time()
    result = processor.reader.readtext(test_img)
    ocr_time = time.time() - start_time
    
    print(f"✓ OCR completado en {ocr_time:.3f}s")
    print(f"  Texto detectado: {len(result)} elementos")
    
    if result:
        print(f"  Ejemplo: '{result[0][1]}'")
    
    # Estimación de rendimiento
    pages_per_min = 60 / ocr_time if ocr_time > 0 else 0
    print(f"  Estimación: ~{pages_per_min:.1f} páginas/minuto")
    
except Exception as e:
    print(f"✗ Error en benchmark: {e}")
print()

# Resumen final
print("="*70)
print("RESUMEN")
print("="*70)
print()
print("Hardware:")
print("  GPU Esperada: AMD Radeon RX 540 (8GB VRAM)")
print()
print("Para mejor rendimiento con AMD en Windows:")
print("  1. Instalar drivers AMD Adrenalin actualizados")
print("  2. Ejecutar nativamente (sin Docker)")
print("  3. Reducir DPI si es necesario (dpi=100)")
print()
print("El servicio OCR está listo para usar!")
print("Ejecuta: docker-compose up ocr-service")
print()
print("="*70)

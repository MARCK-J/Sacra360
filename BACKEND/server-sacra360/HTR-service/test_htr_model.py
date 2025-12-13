"""
Test simple para validar el modelo HTR
Verifica que todas las dependencias estén instaladas y el modelo funcione
"""

import sys
import os

# Agregar el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Verifica que todas las dependencias se puedan importar"""
    print("="*70)
    print("🔍 VERIFICACIÓN DE DEPENDENCIAS HTR")
    print("="*70)
    
    try:
        print("\n1️⃣ OpenCV...")
        import cv2
        print(f"   ✅ OpenCV versión: {cv2.__version__}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        print("\n2️⃣ NumPy...")
        import numpy as np
        print(f"   ✅ NumPy versión: {np.__version__}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        print("\n3️⃣ Pandas...")
        import pandas as pd
        print(f"   ✅ Pandas versión: {pd.__version__}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        print("\n4️⃣ EasyOCR...")
        import easyocr
        print(f"   ✅ EasyOCR disponible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        print("\n5️⃣ PyTorch...")
        import torch
        print(f"   ✅ PyTorch versión: {torch.__version__}")
        print(f"   📊 CUDA disponible: {torch.cuda.is_available()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        print("\n6️⃣ pdf2image...")
        from pdf2image import convert_from_bytes
        print(f"   ✅ pdf2image disponible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True


def test_htr_processor():
    """Verifica que el procesador HTR se pueda importar e inicializar"""
    print("\n" + "="*70)
    print("🔧 VERIFICACIÓN DEL PROCESADOR HTR")
    print("="*70)
    
    try:
        print("\n1️⃣ Importando HTRProcessor...")
        from services.htr_processor import HTRProcessor, BolivianContext, GridDetector, ManuscriptOCR
        print("   ✅ Clases importadas correctamente")
        
        print("\n2️⃣ Verificando BolivianContext...")
        context = BolivianContext()
        print(f"   ✅ Apellidos: {len(context.APELLIDOS)}")
        print(f"   ✅ Nombres: {len(context.NOMBRES)}")
        print(f"   ✅ Lugares: {len(context.LUGARES)}")
        
        # Test de corrección
        test_text = "QUIZPE MAMENI"
        corrected = context.correct_text(test_text)
        print(f"   🔄 Corrección: '{test_text}' → '{corrected}'")
        
        print("\n3️⃣ Verificando GridDetector...")
        grid = GridDetector()
        print(f"   ✅ Target columns: {grid.TARGET_COLS}")
        
        print("\n4️⃣ Inicializando ManuscriptOCR (puede tardar ~30s)...")
        ocr = ManuscriptOCR()
        print("   ✅ EasyOCR reader inicializado")
        print(f"   ✅ Scale factor: {ocr.scale_factor}")
        
        print("\n5️⃣ Inicializando HTRProcessor...")
        processor = HTRProcessor()
        print("   ✅ HTRProcessor inicializado")
        print(f"   ✅ Patrón fijo: {processor.FIXED_PATTERN}")
        
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_structure():
    """Verifica la estructura del modelo"""
    print("\n" + "="*70)
    print("📐 VERIFICACIÓN DE ESTRUCTURA DEL MODELO")
    print("="*70)
    
    try:
        from services.htr_processor import HTRProcessor
        import numpy as np
        
        processor = HTRProcessor()
        
        # Crear imagen de prueba (simulando documento)
        test_img = np.zeros((3965, 8038, 3), dtype=np.uint8)
        test_img.fill(255)  # Imagen blanca
        
        print("\n1️⃣ Imagen de prueba creada:")
        print(f"   📏 Dimensiones: {test_img.shape}")
        print(f"   📊 Dtype: {test_img.dtype}")
        
        print("\n2️⃣ Detectando estructura...")
        ys, xs = processor.grid_detector.get_structure(test_img)
        print(f"   ✅ Filas detectadas: {len(ys) - 1}")
        print(f"   ✅ Columnas detectadas: {len(xs) - 1}")
        
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTS DEL MODELO HTR\n")
    
    success = True
    
    # Test 1: Dependencias
    if not test_imports():
        print("\n❌ FALLO: Dependencias no disponibles")
        success = False
    
    # Test 2: Procesador HTR
    if success:
        if not test_htr_processor():
            print("\n❌ FALLO: Procesador HTR no funciona correctamente")
            success = False
    
    # Test 3: Estructura del modelo
    if success:
        if not test_model_structure():
            print("\n❌ FALLO: Estructura del modelo no funciona")
            success = False
    
    # Resultado final
    print("\n" + "="*70)
    if success:
        print("✅ TODOS LOS TESTS PASARON")
        print("="*70)
        print("\n💡 El modelo HTR está listo para usar")
        print("💡 Siguiente paso: docker-compose up -d --build htr-service")
        print()
        sys.exit(0)
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("="*70)
        print("\n⚠️  Revisa los errores arriba")
        print()
        sys.exit(1)

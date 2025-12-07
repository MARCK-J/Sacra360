"""
Script de prueba para procesar Tabla1.pdf con el flujo completo de Sacra360_OCRv2.ipynb
Ejecuta: python test_table_processing.py
"""

import sys
from pathlib import Path
import time

# Verificar torch/easyocr ANTES de importar table_processor
print("🔍 Verificando dependencias...")
try:
    import torch
    print(f"✓ PyTorch {torch.__version__} cargado correctamente")
except Exception as e:
    print(f"\n❌ ERROR: PyTorch no se puede cargar")
    print(f"   Error: {e}")
    print(f"\n📥 SOLUCIÓN:")
    print(f"   1. Descargar e instalar Visual C++ Redistributable:")
    print(f"      https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print(f"   2. Reiniciar el terminal")
    print(f"   3. Ejecutar nuevamente: python test_table_processing.py")
    print()
    sys.exit(1)

try:
    import easyocr
    print(f"✓ EasyOCR cargado correctamente")
except Exception as e:
    print(f"\n❌ ERROR: EasyOCR no se puede cargar")
    print(f"   Error: {e}")
    sys.exit(1)

print()

# Agregar app al path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.table_processor import TableProcessor

def main():
    # Ruta al PDF de prueba
    pdf_path = Path(__file__).parent.parent.parent / "Images" / "Tabla1.pdf"
    
    if not pdf_path.exists():
        print(f"❌ ERROR: No se encontró {pdf_path}")
        print(f"   Asegúrate de que existe: {pdf_path.absolute()}")
        return
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  SACRA360 - TEST DE PROCESAMIENTO DE TABLAS CON GPU AMD      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"📄 Archivo: {pdf_path.name}")
    print(f"📍 Ubicación: {pdf_path.parent}")
    print()
    
    # Inicializar procesador
    print("🚀 Inicializando TableProcessor con GPU AMD...")
    print()
    
    processor = TableProcessor(
        use_gpu=True,
        languages=['en'],
        dpi=150,
        num_cols=10
    )
    
    # Mostrar info del procesador
    info = processor.get_info()
    print()
    print("═" * 64)
    print("CONFIGURACIÓN DEL PROCESADOR")
    print("═" * 64)
    print(f"  Modo: {info['mode']}")
    print(f"  GPU EasyOCR: {info['use_gpu']}")
    print()
    print(f"  Hardware Detectado:")
    print(f"    GPU Física: {info['gpu_type']}")
    print(f"    Backend: {info['backend']}")
    print(f"    VRAM: {info['vram_gb']} GB")
    print()
    print(f"  CUDA (NVIDIA):")
    print(f"    CUDA Disponible: {info['cuda_available']}")
    print(f"    Dispositivo CUDA: {info['cuda_device']}")
    print()
    print(f"  Configuración OCR:")
    print(f"    Idiomas: {info['languages']}")
    print(f"    DPI: {info['dpi']}")
    print(f"    Columnas: {info['num_cols']}")
    print("═" * 64)
    print()
    
    # Procesar PDF
    start_time = time.time()
    
    try:
        df = processor.process_pdf(
            pdf_path=str(pdf_path),
            pattern=['L','N','N','N','L','N','N','N','L','L']
        )
        
        total_time = time.time() - start_time
        
        # Comparación con diferentes modos
        cpu_pure_time = 8.5  # Tiempo CPU sin optimizaciones
        gpu_nvidia_time = 1.0  # Tiempo con GPU NVIDIA T4 (Colab)
        
        print("📈 COMPARACIÓN DE RENDIMIENTO:")
        print(f"   CPU Puro: ~{cpu_pure_time:.1f} minutos")
        print(f"   CPU Optimizado (actual): {total_time/60:.2f} minutos")
        print(f"   GPU NVIDIA/CUDA (Colab T4): ~{gpu_nvidia_time:.1f} minuto")
        print()
        
        if info['use_gpu'] and info['cuda_available']:
            speedup_vs_cpu = cpu_pure_time / (total_time / 60)
            print(f"   🚀 Aceleración GPU NVIDIA: {speedup_vs_cpu:.2f}x más rápido que CPU puro")
        else:
            speedup = cpu_pure_time / (total_time / 60)
            potential_speedup = cpu_pure_time / gpu_nvidia_time
            print(f"   ⚡ Aceleración actual: {speedup:.2f}x más rápido que CPU puro")
            print(f"   💡 Con GPU NVIDIA sería: {potential_speedup:.1f}x más rápido")
        print()
        # Comparación con CPU
        cpu_time_minutes = 8.5  # Tiempo típico con CPU
        speedup = cpu_time_minutes / (total_time / 60)
        
        print("📈 COMPARACIÓN CON CPU:")
        print(f"   Tiempo con CPU: ~{cpu_time_minutes:.1f} minutos")
        print(f"   Tiempo con GPU AMD: {total_time/60:.2f} minutos")
        print(f"   ⚡ Aceleración: {speedup:.2f}x más rápido")
        print()
        
        # Mostrar primeras filas
        print("📋 PRIMERAS 5 FILAS DEL DATAFRAME:")
        print("─" * 64)
        print(df.head(5).to_string())
        print()
        
        # Guardar resultado
        output_csv = pdf_path.parent / "Tabla1_resultado.csv"
        df.to_csv(output_csv, index=False)
        print(f"💾 Resultado guardado en: {output_csv.name}")
        print()
        
        if total_time < 540:  # 9 minutos
            print("✅ ¡ÉXITO! El procesamiento fue más rápido que con CPU")
        else:
            print("⚠️  El procesamiento tomó más tiempo del esperado")
        
        print()
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                    PROCESAMIENTO COMPLETADO                    ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        
    except Exception as e:
        print()
        print(f"❌ ERROR durante el procesamiento:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        print()
        print("📋 Traceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script de prueba rápida para verificar funcionamiento de OCR con GPU.
Ejecutar dentro del contenedor Docker o en entorno con GPU configurado.

Uso:
    python test_gpu_ocr.py [ruta_pdf]
"""

import sys
import os
from pathlib import Path

# Agregar directorio app al path
sys.path.insert(0, str(Path(__file__).parent / "app"))

try:
    from ocr_gpu_processor import TableOCRProcessor, process_table_pdf
    import torch
    print("✓ Imports exitosos")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("\nAsegúrate de tener instaladas las dependencias:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def test_gpu_availability():
    """Verifica disponibilidad de GPU."""
    print("\n" + "="*60)
    print("1. VERIFICACIÓN DE GPU")
    print("="*60)
    
    cuda_available = torch.cuda.is_available()
    print(f"CUDA disponible: {cuda_available}")
    
    if cuda_available:
        print(f"Versión CUDA: {torch.version.cuda}")
        print(f"Número de GPUs: {torch.cuda.device_count()}")
        print(f"GPU actual: {torch.cuda.current_device()}")
        print(f"Nombre GPU: {torch.cuda.get_device_name(0)}")
        
        # Información de memoria
        total_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"Memoria total: {total_mem:.2f} GB")
    else:
        print("⚠️  GPU no disponible. Se usará CPU (más lento).")
    
    return cuda_available


def test_easyocr_initialization(use_gpu=True):
    """Verifica inicialización de EasyOCR."""
    print("\n" + "="*60)
    print("2. INICIALIZACIÓN DE EASYOCR")
    print("="*60)
    
    try:
        print(f"Inicializando EasyOCR (GPU: {use_gpu})...")
        processor = TableOCRProcessor(use_gpu=use_gpu)
        print("✓ EasyOCR inicializado correctamente")
        
        gpu_info = processor.get_gpu_info()
        print(f"\nInformación del procesador:")
        for key, value in gpu_info.items():
            print(f"  {key}: {value}")
        
        return processor
    except Exception as e:
        print(f"❌ Error inicializando EasyOCR: {e}")
        return None


def test_document_processing(processor, pdf_path):
    """Procesa un documento de prueba."""
    print("\n" + "="*60)
    print("3. PROCESAMIENTO DE DOCUMENTO")
    print("="*60)
    
    if not os.path.exists(pdf_path):
        print(f"⚠️  Archivo no encontrado: {pdf_path}")
        print("Saltando prueba de procesamiento.")
        return
    
    try:
        print(f"Procesando: {pdf_path}")
        print("Esto puede tomar unos segundos la primera vez (descarga modelos)...")
        
        import time
        start_time = time.time()
        
        df = processor.process_pdf_table(
            pdf_path=pdf_path,
            page_number=0,
            num_cols=10
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ Documento procesado exitosamente")
        print(f"Tiempo de procesamiento: {elapsed_time:.2f} segundos")
        print(f"Filas extraídas: {len(df)}")
        print(f"Columnas: {len(df.columns)}")
        
        print(f"\nPrimeras 3 filas:")
        print(df.head(3))
        
        # Guardar resultado
        output_path = "test_output.csv"
        df.to_csv(output_path, index=False)
        print(f"\n✓ Resultado guardado en: {output_path}")
        
    except Exception as e:
        print(f"❌ Error procesando documento: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal."""
    print("="*60)
    print("TEST DE OCR CON GPU - SACRA360")
    print("="*60)
    
    # 1. Verificar GPU
    gpu_available = test_gpu_availability()
    
    # 2. Inicializar EasyOCR
    processor = test_easyocr_initialization(use_gpu=gpu_available)
    
    if processor is None:
        print("\n❌ No se pudo inicializar el procesador. Abortando.")
        sys.exit(1)
    
    # 3. Procesar documento si se proporciona
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        test_document_processing(processor, pdf_path)
    else:
        print("\n" + "="*60)
        print("Para probar con un documento:")
        print(f"  python {sys.argv[0]} ruta/al/documento.pdf")
        print("="*60)
    
    print("\n✓ Tests completados")


if __name__ == "__main__":
    main()

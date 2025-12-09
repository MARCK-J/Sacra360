"""
Test simple del OCRv2 con CPU
Prueba el procesamiento del archivo Tabla1.pdf
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno antes de importar
os.environ['DATABASE_URL'] = 'postgresql://postgres:lolsito101@localhost:5433/sacra360'
os.environ['MINIO_ENDPOINT'] = 'localhost:9000'
os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
os.environ['MINIO_SECRET_KEY'] = 'minioadmin123'
os.environ['MINIO_BUCKET_NAME'] = 'documents'
os.environ['MINIO_SECURE'] = 'False'

def main():
    print("=" * 70)
    print("🧪 TEST OCRv2 CON CPU - Tabla1.pdf")
    print("=" * 70)
    print()
    
    # Archivo de prueba
    test_file = Path(r"d:\MARCK-J\TRABAJOS\GITHUB\Sacra360\BACKEND\Images\Tabla1.pdf")
    
    if not test_file.exists():
        print(f"❌ Error: Archivo no encontrado")
        print(f"   Buscado en: {test_file}")
        return
    
    print(f"📄 Archivo: {test_file.name}")
    print()
    
    try:
        # Importar después de configurar variables de entorno
        from app.services.ocr_v2_processor import OcrV2Processor
        import time
        
        print("🔧 Inicializando OCRv2Processor...")
        processor = OcrV2Processor()
        print("✅ Procesador inicializado")
        print()
        
        # Leer archivo
        with open(test_file, 'rb') as f:
            pdf_bytes = f.read()
        
        print("🚀 Iniciando procesamiento OCRv2...")
        print("⏱️  Midiendo tiempo de ejecución...")
        print()
        
        start_time = time.time()
        
        # Procesar
        result = processor.procesar_documento_completo(
            archivo_bytes=pdf_bytes,
            es_pdf=True
        )
        
        elapsed = time.time() - start_time
        
        print()
        print("=" * 70)
        print("✅ PROCESAMIENTO COMPLETADO")
        print("=" * 70)
        print()
        print(f"⏱️  Tiempo: {elapsed:.2f} segundos ({elapsed/60:.2f} minutos)")
        print()
        print("📊 Resultados:")
        print(f"   Total tuplas: {result.get('total_tuplas', 0)}")
        print(f"   Estado: {result.get('estado', 'desconocido')}")
        print()
        
        if result.get('tuplas') and len(result['tuplas']) > 0:
            print("🎯 Primeras 5 tuplas extraídas:")
            for i, tupla in enumerate(result['tuplas'][:5], 1):
                print(f"   {i}. {tupla}")
            print()
            
            if len(result['tuplas']) > 5:
                print(f"   ... y {len(result['tuplas']) - 5} tuplas más")
                print()
        
        print("=" * 70)
        print("📈 Evaluación de rendimiento:")
        print("=" * 70)
        
        if elapsed < 60:
            print(f"   ✅ Excelente: {elapsed:.2f}s (< 1 minuto)")
        elif elapsed < 120:
            print(f"   ✅ Bueno: {elapsed:.2f}s (< 2 minutos)")
        elif elapsed < 300:
            print(f"   ⚠️  Aceptable: {elapsed:.2f}s (< 5 minutos)")
        else:
            print(f"   ⚠️  Lento: {elapsed:.2f}s ({elapsed/60:.1f} minutos)")
        
        print()
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print()
        print("❌ ERROR durante el procesamiento:")
        print(f"   {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    print()
    input("Presiona Enter para salir...")
    sys.exit(0 if success else 1)

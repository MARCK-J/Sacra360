"""
Ejemplo de uso del modelo HTR_Sacra360
Demuestra cómo usar el procesador HTR de forma independiente
"""

import sys
import os
import json

# Agregar el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.htr_processor import HTRProcessor
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ejemplo_basico(pdf_path: str):
    """
    Ejemplo básico de procesamiento HTR
    
    Args:
        pdf_path: Ruta al archivo PDF a procesar
    """
    print("\n" + "="*70)
    print("🚀 EJEMPLO BÁSICO: Procesamiento HTR")
    print("="*70)
    
    # 1. Inicializar procesador
    print("\n[1/4] Inicializando HTRProcessor...")
    processor = HTRProcessor()
    print("✅ Procesador inicializado")
    
    # 2. Leer archivo PDF
    print(f"\n[2/4] Leyendo PDF: {pdf_path}")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    print(f"✅ Archivo leído: {len(pdf_bytes)} bytes")
    
    # 3. Procesar con HTR
    print("\n[3/4] Procesando con HTR...")
    resultados = processor.process_pdf(pdf_bytes)
    print(f"✅ Procesamiento completado: {len(resultados)} tuplas extraídas")
    
    # 4. Mostrar resultados
    print("\n[4/4] Resultados:")
    print("="*70)
    for tupla in resultados[:3]:  # Mostrar solo las primeras 3
        print(f"\n📋 Tupla #{tupla['tupla_numero']}:")
        datos = tupla['datos_ocr']
        for col, valor in datos.items():
            print(f"   {col}: {valor}")
    
    if len(resultados) > 3:
        print(f"\n... y {len(resultados) - 3} tuplas más")
    
    return resultados


def ejemplo_con_callback(pdf_path: str):
    """
    Ejemplo con callback de progreso
    
    Args:
        pdf_path: Ruta al archivo PDF a procesar
    """
    print("\n" + "="*70)
    print("🚀 EJEMPLO CON CALLBACK: Progreso en tiempo real")
    print("="*70)
    
    # Función callback para reportar progreso
    def callback_progreso(celda_actual: int, total_celdas: int):
        porcentaje = (celda_actual / total_celdas) * 100
        print(f"📊 Progreso: {celda_actual}/{total_celdas} celdas ({porcentaje:.1f}%)")
    
    # Inicializar y procesar
    print("\n[1/2] Inicializando procesador...")
    processor = HTRProcessor()
    
    print(f"\n[2/2] Procesando con callback de progreso...")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    resultados = processor.process_pdf(
        pdf_bytes=pdf_bytes,
        progress_callback=callback_progreso
    )
    
    print(f"\n✅ Completado: {len(resultados)} tuplas")
    return resultados


def ejemplo_exportar_json(pdf_path: str, output_path: str = "resultado_htr.json"):
    """
    Ejemplo de exportación a JSON
    
    Args:
        pdf_path: Ruta al archivo PDF a procesar
        output_path: Ruta donde guardar el JSON
    """
    print("\n" + "="*70)
    print("🚀 EJEMPLO: Exportar resultados a JSON")
    print("="*70)
    
    # Procesar
    processor = HTRProcessor()
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    resultados = processor.process_pdf(pdf_bytes)
    
    # Exportar
    print(f"\n💾 Guardando resultados en: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Guardado exitosamente")
    print(f"📂 Tamaño del archivo: {os.path.getsize(output_path)} bytes")
    
    return output_path


def ejemplo_dataframe(pdf_path: str):
    """
    Ejemplo de conversión a DataFrame de pandas
    
    Args:
        pdf_path: Ruta al archivo PDF a procesar
    """
    print("\n" + "="*70)
    print("🚀 EJEMPLO: Conversión a Pandas DataFrame")
    print("="*70)
    
    # Procesar
    processor = HTRProcessor()
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    resultados = processor.process_pdf(pdf_bytes)
    
    # Convertir a DataFrame
    print("\n📊 Convirtiendo a DataFrame...")
    df = processor.to_dataframe(resultados)
    
    print(f"✅ DataFrame creado:")
    print(f"   Filas: {len(df)}")
    print(f"   Columnas: {len(df.columns)}")
    print(f"\n{df.head()}")
    
    # Guardar como CSV
    csv_path = "resultado_htr.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\n💾 Guardado en: {csv_path}")
    
    return df


def ejemplo_validacion_estructura():
    """
    Ejemplo de validación de estructura del modelo
    """
    print("\n" + "="*70)
    print("🔍 EJEMPLO: Validación de Estructura del Modelo")
    print("="*70)
    
    from services.htr_processor import BolivianContext, GridDetector, ManuscriptOCR
    
    # 1. BolivianContext
    print("\n[1/3] BolivianContext:")
    context = BolivianContext()
    
    test_cases = [
        ("QUIZPE MAMENI", "Apellidos mal escritos"),
        ("JUAM PEREZ", "Nombre mal escrito"),
        ("LA PAZ", "Lugar correcto"),
        ("SAN PEDRA", "Lugar mal escrito")
    ]
    
    for text, descripcion in test_cases:
        corrected = context.correct_text(text)
        print(f"   '{text}' → '{corrected}' ({descripcion})")
    
    # 2. GridDetector
    print("\n[2/3] GridDetector:")
    grid = GridDetector()
    print(f"   ✅ Target columns: {grid.TARGET_COLS}")
    print(f"   ✅ Debug mode: {grid.debug_mode}")
    
    # 3. ManuscriptOCR
    print("\n[3/3] ManuscriptOCR:")
    print("   (Inicialización puede tardar ~30 segundos...)")
    ocr = ManuscriptOCR()
    print(f"   ✅ Scale factor: {ocr.scale_factor}")
    print(f"   ✅ Reader inicializado: {ocr.reader is not None}")
    
    print("\n✅ Todos los componentes validados")


def main():
    """Función principal con menú interactivo"""
    
    # Ejemplo de uso: cambiar esta ruta por tu PDF
    PDF_EJEMPLO = "../../../uploads/documento_test.pdf"
    
    print("\n" + "="*70)
    print("📚 EJEMPLOS DE USO: HTR_Sacra360")
    print("="*70)
    print("\nOpciones:")
    print("  1. Ejemplo básico")
    print("  2. Ejemplo con callback de progreso")
    print("  3. Ejemplo de exportación a JSON")
    print("  4. Ejemplo de conversión a DataFrame")
    print("  5. Ejemplo de validación de estructura")
    print("  0. Salir")
    
    try:
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == "1":
            if not os.path.exists(PDF_EJEMPLO):
                print(f"\n⚠️  Archivo no encontrado: {PDF_EJEMPLO}")
                print("💡 Cambia la variable PDF_EJEMPLO en el código")
                return
            ejemplo_basico(PDF_EJEMPLO)
        
        elif opcion == "2":
            if not os.path.exists(PDF_EJEMPLO):
                print(f"\n⚠️  Archivo no encontrado: {PDF_EJEMPLO}")
                return
            ejemplo_con_callback(PDF_EJEMPLO)
        
        elif opcion == "3":
            if not os.path.exists(PDF_EJEMPLO):
                print(f"\n⚠️  Archivo no encontrado: {PDF_EJEMPLO}")
                return
            ejemplo_exportar_json(PDF_EJEMPLO)
        
        elif opcion == "4":
            if not os.path.exists(PDF_EJEMPLO):
                print(f"\n⚠️  Archivo no encontrado: {PDF_EJEMPLO}")
                return
            ejemplo_dataframe(PDF_EJEMPLO)
        
        elif opcion == "5":
            ejemplo_validacion_estructura()
        
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            return
        
        else:
            print("\n❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

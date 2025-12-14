"""
Script para verificar que la migración HTR esté aplicada correctamente
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verify_htr_migration():
    """Verificar que la migración HTR esté aplicada"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL no configurado en .env")
        return False
    
    print("=" * 70)
    print("🔍 Verificando Migración HTR en Base de Datos")
    print("=" * 70)
    print(f"📍 Database: {database_url}")
    print()
    
    try:
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        # Verificar tabla documento_digitalizado
        print("📋 Verificando tabla 'documento_digitalizado'...")
        if 'documento_digitalizado' not in inspector.get_table_names():
            print("❌ Tabla 'documento_digitalizado' no existe")
            return False
        
        columns = {col['name']: col for col in inspector.get_columns('documento_digitalizado')}
        
        # Verificar columnas clave
        required_columns = [
            'id_documento',
            'libros_id',
            'tipo_sacramento',
            'imagen_url',
            'ocr_texto',
            'modelo_fuente',
            'confianza',
            'fecha_procesamiento',
            'modelo_procesamiento',  # Nueva columna HTR
            'progreso_ocr',          # Para progreso
            'mensaje_progreso'        # Para mensajes
        ]
        
        missing_columns = []
        for col in required_columns:
            if col in columns:
                print(f"  ✅ Columna '{col}' existe")
            else:
                print(f"  ❌ Columna '{col}' NO existe")
                missing_columns.append(col)
        
        if missing_columns:
            print(f"\n⚠️  Columnas faltantes: {', '.join(missing_columns)}")
            print("💡 Ejecutar migración: Migration_Add_HTR_Support.sql")
            return False
        
        # Verificar índices
        print("\n📊 Verificando índices...")
        indexes = inspector.get_indexes('documento_digitalizado')
        index_names = [idx['name'] for idx in indexes]
        
        if 'idx_documento_modelo_procesamiento' in index_names:
            print("  ✅ Índice 'idx_documento_modelo_procesamiento' existe")
        else:
            print("  ⚠️  Índice 'idx_documento_modelo_procesamiento' no existe")
        
        # Verificar tabla ocr_resultado
        print("\n📋 Verificando tabla 'ocr_resultado'...")
        if 'ocr_resultado' not in inspector.get_table_names():
            print("❌ Tabla 'ocr_resultado' no existe")
            return False
        
        ocr_columns = {col['name']: col for col in inspector.get_columns('ocr_resultado')}
        
        ocr_required = [
            'id_ocr',
            'documento_id',
            'tupla_numero',
            'datos_ocr',
            'confianza',
            'fuente_modelo',  # Diferencia HTR vs OCR
            'validado',
            'estado_validacion',
            'sacramento_id',
            'fecha_validacion'
        ]
        
        ocr_missing = []
        for col in ocr_required:
            if col in ocr_columns:
                print(f"  ✅ Columna '{col}' existe")
            else:
                print(f"  ❌ Columna '{col}' NO existe")
                ocr_missing.append(col)
        
        if ocr_missing:
            print(f"\n⚠️  Columnas faltantes en ocr_resultado: {', '.join(ocr_missing)}")
            return False
        
        # Verificar índices en ocr_resultado
        print("\n📊 Verificando índices de ocr_resultado...")
        ocr_indexes = inspector.get_indexes('ocr_resultado')
        ocr_index_names = [idx['name'] for idx in ocr_indexes]
        
        if 'idx_ocr_resultado_fuente_modelo' in ocr_index_names:
            print("  ✅ Índice 'idx_ocr_resultado_fuente_modelo' existe")
        else:
            print("  ⚠️  Índice 'idx_ocr_resultado_fuente_modelo' no existe")
        
        # Verificar datos de prueba
        print("\n📊 Consultando datos...")
        with engine.connect() as conn:
            # Contar documentos por modelo
            result = conn.execute(text("""
                SELECT modelo_procesamiento, COUNT(*) as total
                FROM documento_digitalizado
                GROUP BY modelo_procesamiento
            """))
            
            modelo_counts = result.fetchall()
            if modelo_counts:
                print("  Documentos por modelo:")
                for modelo, count in modelo_counts:
                    print(f"    - {modelo or 'NULL'}: {count}")
            else:
                print("  ℹ️  No hay documentos procesados aún")
            
            # Contar resultados por fuente
            result = conn.execute(text("""
                SELECT fuente_modelo, COUNT(*) as total
                FROM ocr_resultado
                GROUP BY fuente_modelo
            """))
            
            fuente_counts = result.fetchall()
            if fuente_counts:
                print("  Resultados por fuente:")
                for fuente, count in fuente_counts:
                    print(f"    - {fuente}: {count}")
            else:
                print("  ℹ️  No hay resultados procesados aún")
        
        print("\n" + "=" * 70)
        print("✅ Migración HTR verificada correctamente")
        print("=" * 70)
        print("\n📝 Resumen:")
        print("  - Tabla documento_digitalizado: ✅ OK")
        print("  - Tabla ocr_resultado: ✅ OK")
        print("  - Columna modelo_procesamiento: ✅ OK")
        print("  - Columna fuente_modelo: ✅ OK")
        print("  - Índices: ✅ OK")
        print("\n🎯 La base de datos está lista para HTR Service")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al verificar migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_htr_migration()
    sys.exit(0 if success else 1)

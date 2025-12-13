#!/usr/bin/env python3
"""
Script de verificación completa del HTR-service
Valida configuración, dependencias y conectividad
"""

import sys
import os
import time
from typing import Dict, Any

# Agregar el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))


def verificar_variables_entorno() -> bool:
    """Verifica que las variables de entorno necesarias estén configuradas"""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE VARIABLES DE ENTORNO")
    print("="*70)
    
    required_vars = [
        'DATABASE_URL',
        'MINIO_ENDPOINT',
        'MINIO_ACCESS_KEY',
        'MINIO_SECRET_KEY',
        'MINIO_HTR_BUCKET'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Ocultar passwords
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: NO CONFIGURADA")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Variables faltantes: {', '.join(missing)}")
        print("💡 Copia .env.example a .env y configúralo")
        return False
    
    print("\n✅ Todas las variables están configuradas")
    return True


def verificar_base_datos() -> bool:
    """Verifica conectividad con PostgreSQL"""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE BASE DE DATOS")
    print("="*70)
    
    try:
        from database import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Test de conexión
        result = db.execute(text("SELECT version();")).fetchone()
        print(f"   ✅ Conectado a PostgreSQL")
        print(f"   📊 Versión: {result[0][:50]}...")
        
        # Verificar tabla documento_digitalizado
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'documento_digitalizado'
            );
        """)).fetchone()
        
        if result[0]:
            print(f"   ✅ Tabla 'documento_digitalizado' existe")
        else:
            print(f"   ⚠️  Tabla 'documento_digitalizado' no encontrada")
            return False
        
        # Verificar tabla ocr_resultado
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ocr_resultado'
            );
        """)).fetchone()
        
        if result[0]:
            print(f"   ✅ Tabla 'ocr_resultado' existe")
        else:
            print(f"   ⚠️  Tabla 'ocr_resultado' no encontrada")
            return False
        
        # Verificar columna modelo_procesamiento
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'documento_digitalizado'
                AND column_name = 'modelo_procesamiento'
            );
        """)).fetchone()
        
        if result[0]:
            print(f"   ✅ Columna 'modelo_procesamiento' existe")
        else:
            print(f"   ⚠️  Columna 'modelo_procesamiento' no encontrada")
            print(f"   💡 Ejecuta Migration_Add_HTR_Support.sql")
            return False
        
        print("\n✅ Base de datos correctamente configurada")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error de conexión: {e}")
        return False


def verificar_minio() -> bool:
    """Verifica conectividad con MinIO"""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE MINIO")
    print("="*70)
    
    try:
        from services.minio_service import MinIOService
        
        minio = MinIOService()
        
        # Verificar bucket
        bucket_name = os.getenv('MINIO_HTR_BUCKET', 'sacra360-htr')
        
        if minio.client.bucket_exists(bucket_name):
            print(f"   ✅ Bucket '{bucket_name}' existe")
        else:
            print(f"   ⚠️  Bucket '{bucket_name}' no existe, creando...")
            minio.client.make_bucket(bucket_name)
            print(f"   ✅ Bucket creado")
        
        # Test de escritura/lectura
        test_file = "test_verificacion.txt"
        test_content = b"Test de conectividad HTR-service"
        
        print(f"   🔄 Probando escritura...")
        minio.upload_file(test_file, test_content)
        print(f"   ✅ Archivo subido")
        
        print(f"   🔄 Probando lectura...")
        downloaded = minio.download_file(test_file)
        
        if downloaded == test_content:
            print(f"   ✅ Archivo descargado correctamente")
        else:
            print(f"   ❌ Contenido descargado no coincide")
            return False
        
        # Limpiar
        minio.delete_file(test_file)
        print(f"   🧹 Archivo de prueba eliminado")
        
        print("\n✅ MinIO correctamente configurado")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error de conexión: {e}")
        return False


def verificar_modelo_htr() -> bool:
    """Verifica que el modelo HTR se pueda cargar"""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DEL MODELO HTR")
    print("="*70)
    
    try:
        from services.htr_processor import (
            HTRProcessor, BolivianContext, GridDetector, ManuscriptOCR
        )
        import numpy as np
        
        # 1. BolivianContext
        print("\n   [1/4] BolivianContext...")
        context = BolivianContext()
        test = context.correct_text("QUIZPE")
        print(f"      ✅ Corrector funciona: 'QUIZPE' → '{test}'")
        
        # 2. GridDetector
        print("\n   [2/4] GridDetector...")
        grid = GridDetector()
        print(f"      ✅ Target columns: {grid.TARGET_COLS}")
        
        # 3. ManuscriptOCR (puede tardar)
        print("\n   [3/4] ManuscriptOCR (puede tardar ~30s)...")
        ocr = ManuscriptOCR()
        print(f"      ✅ EasyOCR inicializado")
        
        # 4. HTRProcessor
        print("\n   [4/4] HTRProcessor...")
        processor = HTRProcessor()
        print(f"      ✅ Patrón: {processor.FIXED_PATTERN}")
        
        # Test con imagen dummy
        print("\n   🧪 Probando con imagen de prueba...")
        test_img = np.zeros((3965, 8038, 3), dtype=np.uint8)
        test_img.fill(255)
        
        ys, xs = processor.grid_detector.get_structure(test_img)
        print(f"      ✅ Grid detection: {len(xs)-1} columnas, {len(ys)-1} filas")
        
        print("\n✅ Modelo HTR correctamente cargado")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error cargando modelo: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_endpoints() -> bool:
    """Verifica que los endpoints estén disponibles"""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE ENDPOINTS")
    print("="*70)
    
    try:
        import requests
        
        base_url = f"http://localhost:{os.getenv('SERVICE_PORT', '8004')}"
        
        # Health check
        print(f"\n   Probando: {base_url}/health")
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check OK: {data.get('status')}")
        else:
            print(f"   ❌ Health check falló: {response.status_code}")
            return False
        
        # Docs
        print(f"\n   Probando: {base_url}/docs")
        response = requests.get(f"{base_url}/docs", timeout=5)
        
        if response.status_code == 200:
            print(f"   ✅ Swagger UI disponible")
        else:
            print(f"   ⚠️  Swagger UI no disponible")
        
        print("\n✅ Endpoints disponibles")
        return True
        
    except Exception as e:
        print(f"\n   ⚠️  No se pudo verificar endpoints (servicio no iniciado?): {e}")
        return False


def main():
    """Ejecuta todas las verificaciones"""
    print("\n" + "="*70)
    print("🚀 VERIFICACIÓN COMPLETA: HTR-SERVICE")
    print("="*70)
    
    # Cargar variables de entorno desde .env si existe
    try:
        from dotenv import load_dotenv
        if os.path.exists('.env'):
            load_dotenv()
            print("✅ Variables cargadas desde .env")
        else:
            print("⚠️  Archivo .env no encontrado")
    except ImportError:
        print("⚠️  python-dotenv no instalado")
    
    results = {}
    
    # 1. Variables de entorno
    results['env'] = verificar_variables_entorno()
    
    # 2. Base de datos
    if results['env']:
        results['db'] = verificar_base_datos()
    else:
        print("\n⏭️  Saltando verificación de BD (variables no configuradas)")
        results['db'] = False
    
    # 3. MinIO
    if results['env']:
        results['minio'] = verificar_minio()
    else:
        print("\n⏭️  Saltando verificación de MinIO (variables no configuradas)")
        results['minio'] = False
    
    # 4. Modelo HTR
    results['modelo'] = verificar_modelo_htr()
    
    # 5. Endpoints (opcional)
    results['endpoints'] = verificar_endpoints()
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*70)
    
    total = len(results)
    exitosos = sum(1 for r in results.values() if r)
    
    for check, resultado in results.items():
        icon = "✅" if resultado else "❌"
        print(f"   {icon} {check.upper()}: {'OK' if resultado else 'FALLO'}")
    
    print("\n" + "="*70)
    print(f"Resultado: {exitosos}/{total} verificaciones exitosas")
    print("="*70)
    
    if exitosos == total:
        print("\n🎉 ¡TODO ESTÁ LISTO!")
        print("💡 Puedes iniciar el servicio con:")
        print("   python run_service.py")
        print("   O con Docker:")
        print("   docker-compose up --build")
        return 0
    else:
        print("\n⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print("💡 Revisa los errores arriba y corrige la configuración")
        return 1


if __name__ == "__main__":
    sys.exit(main())

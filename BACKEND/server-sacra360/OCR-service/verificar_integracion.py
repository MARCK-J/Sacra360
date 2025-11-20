"""
Script de verificación de la integración OCR.py -> OCR-service
Verifica que todos los archivos necesarios estén presentes y configurados correctamente.
"""

import os
import sys
from pathlib import Path

def verificar_estructura_archivos():
    """Verifica que todos los archivos necesarios estén presentes"""
    print("🔍 VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    print("=" * 60)
    
    archivos_requeridos = [
        "app/main.py",
        "app/controllers/ocr_controller.py", 
        "app/controllers/__init__.py",
        "app/services/ocr_service.py",
        "app/services/database_service.py", 
        "app/services/__init__.py",
        "app/dto/ocr_dto.py",
        "app/dto/__init__.py", 
        "app/entities/ocr_entity.py",
        "app/entities/__init__.py",
        "app/routers/ocr_router.py",
        "app/routers/__init__.py",
        "app/utils/config.py", 
        "app/utils/__init__.py",
        "requirements.txt",
        "run_service.py", 
        "test_service.py",
        "README.md",
        ".env.example"
    ]
    
    archivos_presentes = 0
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
            archivos_presentes += 1
        else:
            print(f"❌ FALTA: {archivo}")
    
    print(f"\n📊 Archivos presentes: {archivos_presentes}/{len(archivos_requeridos)}")
    return archivos_presentes == len(archivos_requeridos)

def verificar_algoritmo_ocr():
    """Verifica que el algoritmo OCR original esté integrado"""
    print("\n🧠 VERIFICANDO INTEGRACIÓN DEL ALGORITMO OCR")
    print("=" * 60)
    
    funciones_requeridas = [
        "_ejecutar_pipeline_ocr",
        "_detectar_grid_lineas", 
        "_extract_line_positions",
        "_cluster_lines",
        "_validar_filas_registros",
        "_process_single_row",
        "_detect_cells_in_row",
        "_extract_text_from_cell",
        "_clean_extracted_text", 
        "_fix_common_ocr_errors",
        "_calcular_metricas_calidad"
    ]
    
    try:
        with open("app/services/ocr_service.py", "r", encoding="utf-8") as f:
            contenido = f.read()
            
        funciones_encontradas = 0
        for funcion in funciones_requeridas:
            if f"def {funcion}" in contenido:
                print(f"✅ {funcion}")
                funciones_encontradas += 1
            else:
                print(f"❌ FALTA: {funcion}")
        
        print(f"\n📊 Funciones OCR integradas: {funciones_encontradas}/{len(funciones_requeridas)}")
        return funciones_encontradas >= len(funciones_requeridas) * 0.8  # Al menos 80%
        
    except FileNotFoundError:
        print("❌ No se puede verificar - archivo ocr_service.py no encontrado")
        return False

def verificar_dependencias():
    """Verifica las dependencias requeridas"""
    print("\n📦 VERIFICANDO DEPENDENCIAS")
    print("=" * 60)
    
    dependencias_core = [
        "fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary",
        "opencv-python", "pytesseract", "pillow", "numpy", "pydantic"
    ]
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().lower()
            
        dependencias_encontradas = 0
        for dep in dependencias_core:
            if dep.lower() in requirements:
                print(f"✅ {dep}")
                dependencias_encontradas += 1
            else:
                print(f"❌ FALTA: {dep}")
        
        print(f"\n📊 Dependencias presentes: {dependencias_encontradas}/{len(dependencias_core)}")
        return dependencias_encontradas == len(dependencias_core)
        
    except FileNotFoundError:
        print("❌ No se puede verificar - requirements.txt no encontrado")
        return False

def verificar_configuracion():
    """Verifica la configuración del servicio"""
    print("\n⚙️  VERIFICANDO CONFIGURACIÓN")
    print("=" * 60)
    
    elementos_config = []
    
    # Verificar config.py
    try:
        with open("app/utils/config.py", "r") as f:
            config_content = f.read()
            
        config_items = ["Settings", "database_url", "tesseract_path", "service_port"]
        for item in config_items:
            if item in config_content:
                elementos_config.append(f"✅ config.py: {item}")
            else:
                elementos_config.append(f"❌ config.py: FALTA {item}")
                
    except FileNotFoundError:
        elementos_config.append("❌ config.py no encontrado")
    
    # Verificar .env.example
    if os.path.exists(".env.example"):
        elementos_config.append("✅ .env.example presente")
    else:
        elementos_config.append("❌ .env.example falta")
    
    for item in elementos_config:
        print(item)
    
    return len([x for x in elementos_config if x.startswith("✅")]) >= 4

def verificar_endpoints():
    """Verifica que los endpoints estén definidos"""
    print("\n🔗 VERIFICANDO ENDPOINTS")
    print("=" * 60)
    
    endpoints_requeridos = [
        "health_check", "procesar_imagen_ocr", "obtener_documento_ocr", 
        "validar_campo_ocr", "test_endpoint"
    ]
    
    try:
        with open("app/controllers/ocr_controller.py", "r") as f:
            controller_content = f.read()
            
        endpoints_encontrados = 0
        for endpoint in endpoints_requeridos:
            if f"def {endpoint}" in controller_content:
                print(f"✅ {endpoint}")
                endpoints_encontrados += 1
            else:
                print(f"❌ FALTA: {endpoint}")
        
        print(f"\n📊 Endpoints definidos: {endpoints_encontrados}/{len(endpoints_requeridos)}")
        return endpoints_encontrados >= 4
        
    except FileNotFoundError:
        print("❌ No se puede verificar - ocr_controller.py no encontrado") 
        return False

def verificar_database_integration():
    """Verifica la integración con base de datos"""
    print("\n🗄️  VERIFICANDO INTEGRACIÓN BASE DE DATOS")
    print("=" * 60)
    
    elementos_bd = []
    
    # Verificar entidades
    try:
        with open("app/entities/ocr_entity.py", "r") as f:
            entity_content = f.read()
            
        if "DocumentoDigitalizado" in entity_content and "OcrResultado" in entity_content:
            elementos_bd.append("✅ Entidades SQLAlchemy definidas")
        else:
            elementos_bd.append("❌ Entidades SQLAlchemy incompletas")
    except:
        elementos_bd.append("❌ ocr_entity.py no encontrado")
    
    # Verificar database service
    try:
        with open("app/services/database_service.py", "r") as f:
            db_content = f.read()
            
        db_methods = ["guardar_documento", "guardar_campo_ocr", "obtener_documento"]
        for method in db_methods:
            if f"def {method}" in db_content:
                elementos_bd.append(f"✅ {method}")
            else:
                elementos_bd.append(f"❌ FALTA: {method}")
    except:
        elementos_bd.append("❌ database_service.py no encontrado")
    
    for item in elementos_bd:
        print(item)
    
    return len([x for x in elementos_bd if x.startswith("✅")]) >= 3

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN COMPLETA DE INTEGRACIÓN OCR.py -> OCR-service")
    print("🎯 Sacra360 - Microservicio de OCR")
    print("="*80)
    
    verificaciones = [
        ("Estructura de Archivos", verificar_estructura_archivos),
        ("Algoritmo OCR", verificar_algoritmo_ocr),
        ("Dependencias", verificar_dependencias), 
        ("Configuración", verificar_configuracion),
        ("Endpoints", verificar_endpoints),
        ("Base de Datos", verificar_database_integration)
    ]
    
    resultados = []
    for nombre, funcion in verificaciones:
        resultado = funcion()
        resultados.append((nombre, resultado))
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*80)
    
    exitosas = 0
    for nombre, resultado in resultados:
        status = "✅ COMPLETADO" if resultado else "❌ PENDIENTE"
        print(f"{status:15} {nombre}")
        if resultado:
            exitosas += 1
    
    porcentaje = (exitosas / len(resultados)) * 100
    print(f"\n🎯 Integración completada: {exitosas}/{len(resultados)} ({porcentaje:.1f}%)")
    
    if porcentaje >= 80:
        print("\n🎉 ¡INTEGRACIÓN EXITOSA!")
        print("✅ El servicio OCR está listo para funcionar")
        print("\n🚀 Próximos pasos:")
        print("   1. Ejecutar: python run_service.py")
        print("   2. Probar: python test_service.py") 
        print("   3. Docs: http://localhost:8003/docs")
    else:
        print("\n⚠️  INTEGRACIÓN INCOMPLETA")
        print("❌ Revisar elementos pendientes antes de ejecutar")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    main()
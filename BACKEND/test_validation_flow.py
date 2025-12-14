"""
Script para probar el flujo de validación completo con OCR V2
Verifica que el frontend pueda cargar y validar tuplas procesadas con OCR V2
"""
import requests
import json

BASE_URL_DOCS = "http://localhost:8002"
DOCUMENTO_ID = 42  # Tabla1.pdf procesado con OCR V2

def test_get_tuplas_pendientes():
    """Prueba 1: Obtener tuplas pendientes de validación"""
    print("\n" + "="*80)
    print("PRUEBA 1: Obtener tuplas pendientes")
    print("="*80)
    
    url = f"{BASE_URL_DOCS}/api/v1/validacion/tuplas-pendientes/{DOCUMENTO_ID}"
    print(f"GET {url}")
    
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Respuesta exitosa")
        print(f"Tuplas obtenidas: {len(data)}")
        
        if len(data) > 0:
            primera_tupla = data[0]
            print(f"\nPrimera tupla:")
            print(f"  - Tupla número: {primera_tupla.get('tupla_numero')}")
            print(f"  - Estado: {primera_tupla.get('estado_validacion')}")
            print(f"  - Total campos: {len(primera_tupla.get('campos_ocr', []))}")
            
            # Mostrar primeros 3 campos
            campos = primera_tupla.get('campos_ocr', [])[:3]
            print(f"\n  Primeros campos:")
            for campo in campos:
                print(f"    • {campo.get('campo')}: {campo.get('valor_extraido', '')[:50]}...")
            
            return data
        else:
            print("⚠️ No hay tuplas pendientes (posiblemente ya validadas)")
            return []
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_get_tupla_especifica(tupla_numero=1):
    """Prueba 2: Obtener una tupla específica"""
    print("\n" + "="*80)
    print(f"PRUEBA 2: Obtener tupla específica (tupla {tupla_numero})")
    print("="*80)
    
    url = f"{BASE_URL_DOCS}/api/v1/validacion/tupla/{DOCUMENTO_ID}/{tupla_numero}"
    print(f"GET {url}")
    
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Tupla obtenida correctamente")
        print(f"\nDetalles:")
        print(f"  - Tupla número: {data.get('tupla_numero')}")
        print(f"  - Documento ID: {data.get('documento_id')}")
        print(f"  - Estado: {data.get('estado_validacion')}")
        print(f"  - Total campos: {len(data.get('campos_ocr', []))}")
        
        # Mostrar todos los campos
        campos = data.get('campos_ocr', [])
        print(f"\n  Campos OCR:")
        for campo in campos:
            valor = campo.get('valor_extraido', '')
            confianza = campo.get('confianza', 0)
            print(f"    • {campo.get('campo'):20s}: {valor:30s} (confianza: {confianza:.2%})")
        
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_validar_tupla_simulada(tupla_numero=1):
    """Prueba 3: Simular validación de tupla (sin realmente validar)"""
    print("\n" + "="*80)
    print(f"PRUEBA 3: Estructura de validación (SIMULACIÓN)")
    print("="*80)
    
    # Primero obtener la tupla para ver su estructura
    url_get = f"{BASE_URL_DOCS}/api/v1/validacion/tupla/{DOCUMENTO_ID}/{tupla_numero}"
    response = requests.get(url_get)
    
    if response.status_code != 200:
        print(f"❌ No se pudo obtener la tupla: {response.text}")
        return None
    
    tupla_data = response.json()
    campos = tupla_data.get('campos_ocr', [])
    
    # Construir datos_validados (valores originales del OCR)
    datos_validados = {}
    for campo in campos:
        datos_validados[campo['campo']] = campo['valor_extraido']
    
    # Estructura de la petición de validación
    validacion_request = {
        "documento_id": DOCUMENTO_ID,
        "tupla_numero": tupla_numero,
        "usuario_validador_id": 4,  # Usuario de prueba
        "institucion_id": 1,  # Institución de prueba
        "persona_id_existente": None,  # Nueva persona
        "datos_validados": datos_validados,
        "observaciones": "Validación de prueba desde script",
        "accion": "aprobar"
    }
    
    print("Estructura de validación construida:")
    print(json.dumps(validacion_request, indent=2, ensure_ascii=False))
    
    print("\n⚠️  NOTA: Esta es solo una SIMULACIÓN.")
    print("    Para validar realmente, descomenta la sección de POST abajo.")
    print("    Esto creará registros en las tablas personas y sacramentos.")
    
    # DESCOMENTA LAS SIGUIENTES LÍNEAS PARA VALIDAR REALMENTE
    # print("\n¿Deseas ejecutar la validación real? (escribe 'SI' para confirmar)")
    # confirmacion = input("> ")
    # 
    # if confirmacion.strip().upper() == 'SI':
    #     url_post = f"{BASE_URL_DOCS}/api/v1/validacion/validar-tupla"
    #     response = requests.post(url_post, json=validacion_request)
    #     
    #     print(f"\nStatus: {response.status_code}")
    #     if response.status_code == 200:
    #         resultado = response.json()
    #         print(f"✅ Tupla validada correctamente")
    #         print(json.dumps(resultado, indent=2, ensure_ascii=False))
    #     else:
    #         print(f"❌ Error: {response.text}")
    # else:
    #     print("Validación cancelada")
    
    return validacion_request

def test_estado_validacion():
    """Prueba 4: Obtener estado de validación del documento"""
    print("\n" + "="*80)
    print("PRUEBA 4: Estado de validación del documento")
    print("="*80)
    
    url = f"{BASE_URL_DOCS}/api/v1/validacion/estado/{DOCUMENTO_ID}"
    print(f"GET {url}")
    
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Estado obtenido")
        print(f"\nEstadísticas:")
        print(f"  - Total tuplas: {data.get('total_tuplas')}")
        print(f"  - Validadas: {data.get('tuplas_validadas')}")
        print(f"  - Pendientes: {data.get('tuplas_pendientes')}")
        print(f"  - Rechazadas: {data.get('tuplas_rechazadas')}")
        print(f"  - Progreso: {data.get('progreso_porcentaje')}%")
        print(f"  - Estado general: {data.get('estado_general')}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("TEST DE FLUJO DE VALIDACIÓN - OCR V2")
    print("="*80)
    print(f"Documento ID: {DOCUMENTO_ID}")
    print(f"Base URL: {BASE_URL_DOCS}")
    print("="*80)
    
    try:
        # Prueba 1: Obtener tuplas pendientes
        tuplas = test_get_tuplas_pendientes()
        
        if tuplas and len(tuplas) > 0:
            # Prueba 2: Obtener primera tupla específica
            primera_tupla_num = tuplas[0].get('tupla_numero', 1)
            tupla_detalle = test_get_tupla_especifica(primera_tupla_num)
            
            # Prueba 3: Simular validación
            if tupla_detalle:
                test_validar_tupla_simulada(primera_tupla_num)
        
        # Prueba 4: Estado general
        test_estado_validacion()
        
        print("\n" + "="*80)
        print("RESUMEN DE PRUEBAS")
        print("="*80)
        print("✅ Las pruebas se completaron.")
        print("📝 Revisa los resultados arriba para verificar compatibilidad.")
        print("\nPróximos pasos:")
        print("1. Si los campos se muestran correctamente, el backend está OK")
        print("2. Prueba desde el frontend (ValidacionOCRModal.jsx)")
        print("3. Si quieres validar realmente, descomenta la sección en test_validar_tupla_simulada()")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor.")
        print(f"   Verifica que Documents-service esté corriendo en {BASE_URL_DOCS}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

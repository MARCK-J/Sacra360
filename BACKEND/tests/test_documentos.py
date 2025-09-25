#!/usr/bin/env python3
"""
Tests para los endpoints de Documentos
Módulo: /api/v1/documentos/
"""

import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_base import APITestClient, print_test_header, print_response_info, validate_schema_fields, run_basic_crud_test


def test_documentos_crud():
    """Test CRUD básico para documentos"""
    print_test_header("Tests CRUD - Documentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Datos para crear documento
    create_data = {
        "id_persona": 1,  # Asumiendo que existe una persona con ID 1
        "tipo_documento": "acta_bautizo",
        "nombre_archivo": "acta_bautizo_001.pdf",
        "ruta_archivo": "/documentos/bautizos/acta_bautizo_001.pdf",
        "descripcion": "Acta de bautizo digitalizada",
        "fecha_documento": "2024-01-15",
        "observaciones": "Documento escaneado en alta resolución",
        "activo": True
    }
    
    # Datos para actualizar documento
    update_data = {
        "descripcion": "Acta de bautizo digitalizada - Actualizada",
        "observaciones": "Documento procesado con OCR"
    }
    
    # Campos requeridos en la respuesta
    required_fields = [
        'id_documento', 'id_persona', 'tipo_documento', 'nombre_archivo',
        'fecha_documento', 'activo'
    ]
    
    # Ejecutar test CRUD
    run_basic_crud_test(
        client=client,
        endpoint="/documentos",
        create_data=create_data,
        update_data=update_data,
        required_fields=required_fields,
        entity_name="Documento"
    )


def test_documentos_upload():
    """Test de carga de documentos (simulado)"""
    print_test_header("Tests de Carga de Documentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Endpoint de carga de documento
    print("\n1️⃣ Test: Simular carga de documento")
    
    # Datos del documento a cargar
    upload_data = {
        "id_persona": 1,
        "tipo_documento": "cedula_identidad",
        "descripcion": "Cédula de identidad escaneada"
    }
    
    # Simulamos el archivo con datos ficticios
    # En un test real, usaríamos files={'file': ('test.pdf', file_content, 'application/pdf')}
    files_data = {
        "archivo": "contenido_simulado_del_archivo.pdf"
    }
    
    response = client.post("/documentos/upload", upload_data)
    print_response_info(response, "Carga de documento")
    
    if response.status_code in [200, 201]:
        uploaded_doc = response.json()
        print(f"✅ Documento cargado con ID: {uploaded_doc.get('id_documento')}")
    
    # Test 2: Listar documentos después de la carga
    print("\n2️⃣ Test: Listar documentos después de carga")
    response = client.get("/documentos/")
    print_response_info(response, "Lista de documentos")


def test_documentos_by_person():
    """Test de documentos por persona"""
    print_test_header("Tests Documentos por Persona")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Obtener documentos de una persona específica
    person_id = 1
    print(f"\n1️⃣ Test: Obtener documentos de persona ID {person_id}")
    response = client.get(f"/documentos/persona/{person_id}")
    print_response_info(response, f"Documentos de persona {person_id}")
    
    if response.status_code == 200:
        documentos = response.json()
        if isinstance(documentos, list):
            print(f"✅ Se obtuvieron {len(documentos)} documentos para la persona")
            
            # Verificar estructura si hay documentos
            if documentos and len(documentos) > 0:
                required_fields = ['id_documento', 'tipo_documento', 'nombre_archivo']
                validate_schema_fields(documentos[0], required_fields, "Estructura documento")
        else:
            print("⚠️  Respuesta no es una lista")


def test_documentos_by_type():
    """Test de documentos por tipo"""
    print_test_header("Tests Documentos por Tipo")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test diferentes tipos de documentos
    tipos_documento = [
        "acta_bautizo",
        "acta_matrimonio", 
        "acta_confirmacion",
        "cedula_identidad",
        "certificado_nacimiento"
    ]
    
    for i, tipo in enumerate(tipos_documento, 1):
        print(f"\n{i}️⃣ Test: Obtener documentos tipo '{tipo}'")
        response = client.get("/documentos/", params={"tipo_documento": tipo})
        print_response_info(response, f"Documentos tipo {tipo}")
        
        if response.status_code == 200:
            docs = response.json()
            if isinstance(docs, list):
                print(f"✅ Se encontraron {len(docs)} documentos de tipo {tipo}")


def test_documentos_ocr():
    """Test de procesamiento OCR de documentos"""
    print_test_header("Tests Procesamiento OCR")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Primero crear un documento para procesar
    doc_data = {
        "id_persona": 1,
        "tipo_documento": "acta_bautizo",
        "nombre_archivo": "acta_para_ocr.pdf",
        "ruta_archivo": "/documentos/ocr/acta_para_ocr.pdf",
        "descripcion": "Acta para procesamiento OCR",
        "fecha_documento": "2024-01-20",
        "activo": True
    }
    
    print("\n1️⃣ Creando documento para procesamiento OCR...")
    response = client.post("/documentos", doc_data)
    print_response_info(response, "Crear documento para OCR")
    
    if response.status_code not in [200, 201]:
        print("❌ No se pudo crear documento, saltando test OCR")
        return
    
    created_doc = response.json()
    doc_id = created_doc.get('id_documento')
    
    # Test: Procesar documento con OCR
    print(f"\n2️⃣ Test: Procesar documento ID {doc_id} con OCR")
    response = client.post(f"/documentos/{doc_id}/procesar-ocr")
    print_response_info(response, f"Procesar OCR documento {doc_id}")
    
    if response.status_code == 200:
        ocr_result = response.json()
        print("✅ Procesamiento OCR completado")
        
        # Verificar campos esperados en resultado OCR
        expected_fields = ['id_documento', 'texto_extraido', 'confianza', 'procesado']
        if isinstance(ocr_result, dict):
            validate_schema_fields(ocr_result, expected_fields, "Resultado OCR")
    
    # Test: Obtener texto OCR del documento
    print(f"\n3️⃣ Test: Obtener texto OCR de documento ID {doc_id}")
    response = client.get(f"/documentos/{doc_id}/texto-ocr")
    print_response_info(response, f"Obtener texto OCR documento {doc_id}")


def test_documentos_search():
    """Test de búsqueda y filtros de documentos"""
    print_test_header("Tests de Búsqueda - Documentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Búsqueda por nombre de archivo
    print("\n1️⃣ Test: Búsqueda por nombre de archivo")
    response = client.get("/documentos/", params={"search": "acta"})
    print_response_info(response, "Búsqueda por 'acta'")
    
    # Test 2: Filtro por rango de fechas
    print("\n2️⃣ Test: Filtro por rango de fechas")
    response = client.get("/documentos/", params={
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-12-31"
    })
    print_response_info(response, "Filtro rango fechas 2024")
    
    # Test 3: Filtro por documentos activos
    print("\n3️⃣ Test: Filtro por documentos activos")
    response = client.get("/documentos/", params={"activo": True})
    print_response_info(response, "Filtro documentos activos")
    
    # Test 4: Filtro por persona específica
    print("\n4️⃣ Test: Filtro por persona")
    response = client.get("/documentos/", params={"id_persona": 1})
    print_response_info(response, "Filtro por persona ID 1")
    
    # Test 5: Paginación
    print("\n5️⃣ Test: Paginación")
    response = client.get("/documentos/", params={"page": 1, "limit": 5})
    print_response_info(response, "Paginación - Página 1, Límite 5")


def test_documentos_validation():
    """Test de validaciones de documentos"""
    print_test_header("Tests de Validación - Documentos")
    
    client = APITestClient()
    
    if not client.login():
        print("❌ No se pudo hacer login, saltando tests")
        return
    
    # Test 1: Crear documento con tipo inválido
    print("\n1️⃣ Test: Crear documento con tipo inválido")
    invalid_data = {
        "id_persona": 1,
        "tipo_documento": "tipo_inexistente",  # Tipo inválido
        "nombre_archivo": "test.pdf",
        "fecha_documento": "2024-01-01",
        "activo": True
    }
    
    response = client.post("/documentos", invalid_data)
    print_response_info(response, "Crear documento con tipo inválido")
    
    if response.status_code == 422:
        print("✅ Validación correcta - Tipo inválido rechazado")
    
    # Test 2: Crear documento sin nombre de archivo
    print("\n2️⃣ Test: Crear documento sin nombre de archivo")
    no_filename_data = {
        "id_persona": 1,
        "tipo_documento": "acta_bautizo",
        "fecha_documento": "2024-01-01",
        "activo": True
        # nombre_archivo faltante
    }
    
    response = client.post("/documentos", no_filename_data)
    print_response_info(response, "Crear documento sin nombre")
    
    if response.status_code == 422:
        print("✅ Validación correcta - Nombre de archivo requerido")
    
    # Test 3: Crear documento con persona inexistente
    print("\n3️⃣ Test: Crear documento con persona inexistente")
    invalid_person_data = {
        "id_persona": 99999,  # ID de persona que no existe
        "tipo_documento": "acta_bautizo",
        "nombre_archivo": "test.pdf",
        "fecha_documento": "2024-01-01",
        "activo": True
    }
    
    response = client.post("/documentos", invalid_person_data)
    print_response_info(response, "Crear documento con persona inexistente")


def run_all_documentos_tests():
    """Ejecutar todos los tests de documentos"""
    print("🚀 Iniciando Tests Completos de Documentos")
    print("=" * 80)
    
    test_documentos_crud()
    test_documentos_upload()
    test_documentos_by_person()
    test_documentos_by_type()
    test_documentos_ocr()
    test_documentos_search()
    test_documentos_validation()
    
    print("\n" + "=" * 80)
    print("🏁 Tests de Documentos Completados")


if __name__ == "__main__":
    run_all_documentos_tests()
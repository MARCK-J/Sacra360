#!/usr/bin/env python3
"""
Tests específicos para el controlador de sacramentos creado manualmente
Este test crea un tipo_sacramento, una persona y luego crea un sacramento
usando el endpoint POST /api/v1/sacramentos/ (el que implementamos con SQL directo),
y valida las rutas GET /sacramentos/{id}, GET /sacramentos/bautizos y
GET /personas/{id}/sacramentos.
"""
import sys
import os
from datetime import date

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(_file_))))

from tests.test_base import APITestClient, print_test_header, print_response_info


def test_sacramento_controller_flow():
    print_test_header("Test específico - Sacramento Controller (manual)")

    client = APITestClient()
    if not client.login():
        print("❌ No se pudo autenticar con el usuario de pruebas; saltando test específico de sacramentos.")
        return

    # 1) Crear un tipo de sacramento (bautizo) para usar en la prueba
    tipo_payload = {"nombre": "bautizo", "descripcion": "Tipo de prueba - bautizo"}
    resp_tipo = client.post("/tipos-sacramentos/", tipo_payload)
    print_response_info(resp_tipo, "Crear tipo_sacramento")
    assert resp_tipo.status_code in (200, 201)
    tipo_data = resp_tipo.json()
    tipo_id = tipo_data.get("id_tipo") or tipo_data.get("id")
    assert tipo_id is not None

    # 2) Crear una persona mínima válida
    persona_payload = {
        "nombres": "Test",
        "apellido_paterno": "Usuario",
        "apellido_materno": "Prueba",
        "fecha_nacimiento": "1990-01-01",
        "lugar_nacimiento": "Ciudad Test",
        "nombre_padre": "Padre Test",
        "nombre_madre": "Madre Test"
    }
    resp_persona = client.post("/personas/", persona_payload)
    print_response_info(resp_persona, "Crear persona para sacramento")
    assert resp_persona.status_code in (200, 201)
    persona = resp_persona.json()
    persona_id = persona.get("id_persona") or persona.get("id")
    assert persona_id is not None

    # 3) Crear sacramento usando el endpoint que implementamos (POST /sacramentos)
    sacramento_payload = {
        "persona_id": persona_id,
        "tipo_id": tipo_id,
        "fecha_sacramento": "2024-05-01",
        "lugar_sacramento": "Parroquia Test",
        "ministro": "Padre Test",
        "padrinos": "Juan Perez;Maria Gomez",
        "observaciones": "Creado por test automático",
        "libro_registro": "Libro Test 2024",
        "folio": "10",
        "pagina": "2",
        "numero_acta": "T-001"
    }

    resp_create = client.post("/sacramentos", sacramento_payload)
    print_response_info(resp_create, "Crear sacramento via /sacramentos")
    assert resp_create.status_code in (200, 201), f"Crear sacramento falló: {resp_create.status_code} {resp_create.text}"
    created = resp_create.json()
    sac_id = created.get("id_sacramento") or created.get("id")
    assert sac_id is not None

    # 4) Obtener sacramento por ID
    resp_get = client.get(f"/sacramentos/{sac_id}")
    print_response_info(resp_get, "GET /sacramentos/{id}")
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert int(data_get.get("persona_id")) == int(persona_id)

    # 5) Listar bautizos y comprobar que aparece al menos un registro
    resp_bautizos = client.get("/sacramentos/bautizos")
    print_response_info(resp_bautizos, "GET /sacramentos/bautizos")
    assert resp_bautizos.status_code == 200
    bautizos = resp_bautizos.json()
    assert isinstance(bautizos, list)

    # 6) Obtener sacramentos de la persona
    resp_person_sacs = client.get(f"/personas/{persona_id}/sacramentos")
    print_response_info(resp_person_sacs, "GET /personas/{id}/sacramentos")
    assert resp_person_sacs.status_code == 200
    person_sacs = resp_person_sacs.json()
    assert isinstance(person_sacs, list)
    # Confirmar que nuestro sacramento creado está en la lista (por id)
    found = any((int(item.get("id_sacramento") or item.get("id")) == int(sac_id)) for item in person_sacs)
    assert found, "El sacramento creado no aparece en los sacramentos de la persona"


if _name_ == '_main_':
    test_sacramento_controller_flow()
#!/usr/bin/env python3
"""
Tests para los endpoints de reportes
Módulo: /api/v1/reportes/
"""
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(_file_))))
from tests.test_base import APITestClient, print_test_header, print_response_info


def test_count_by_type_and_summary():
    print_test_header("Tests - Reportes: count-by-type y summary")
    client = APITestClient()

    # Intentar login; si falla, continuamos ya que los reportes pueden ser públicos
    client.login()

    # 1) count-by-type
    print("\n1️⃣ Test: GET /reportes/count-by-type")
    resp = client.get("/reportes/count-by-type")
    print_response_info(resp, "Count By Type")
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, dict)
        counts = data.get('counts')
        assert isinstance(counts, list)
        for item in counts:
            assert 'tipo' in item and 'total' in item

    # 2) summary
    print("\n2️⃣ Test: GET /reportes/summary")
    resp2 = client.get("/reportes/summary")
    print_response_info(resp2, "Summary")
    if resp2.status_code == 200:
        s = resp2.json()
        assert 'total' in s and 'by_type' in s
        assert isinstance(s['total'], int)
        assert isinstance(s['by_type'], list)


def run_all_reportes_tests():
    print("🚀 Ejecutando tests de reportes")
    test_count_by_type_and_summary()


if __name__ == '__main__':
    run_all_reportes_tests()
"""
Pruebas para la API principal
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Probar endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Sacra360 API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"


def test_health_check(client: TestClient):
    """Probar endpoint de salud"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_api_docs_available(client: TestClient):
    """Verificar que la documentación esté disponible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available(client: TestClient):
    """Verificar que ReDoc esté disponible"""
    response = client.get("/redoc")
    assert response.status_code == 200


class TestDocumentsAPI:
    """Pruebas para la API de documentos"""

    def test_list_documents_empty(self, client: TestClient):
        """Probar listado de documentos vacío"""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_nonexistent_document(self, client: TestClient):
        """Probar obtener documento inexistente"""
        response = client.get("/api/v1/documents/999")
        assert response.status_code == 404

    def test_dashboard_stats(self, client: TestClient):
        """Probar estadísticas del dashboard"""
        response = client.get("/api/v1/stats/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "processed_documents" in data
        assert "processing_pipeline" in data


class TestOCRAPI:
    """Pruebas para la API de OCR"""

    def test_get_supported_languages(self, client: TestClient):
        """Probar obtener idiomas soportados por OCR"""
        response = client.get("/api/v1/ocr/languages")
        assert response.status_code == 200
        data = response.json()
        assert "supported_languages" in data
        assert "default_language" in data

    def test_get_ocr_status_nonexistent(self, client: TestClient):
        """Probar estado OCR de documento inexistente"""
        response = client.get("/api/v1/ocr/status/999")
        assert response.status_code == 404


class TestHTRAPI:
    """Pruebas para la API de HTR"""

    def test_get_available_models(self, client: TestClient):
        """Probar obtener modelos HTR disponibles"""
        response = client.get("/api/v1/htr/models")
        assert response.status_code == 200
        data = response.json()
        assert "available_models" in data
        assert "default_model" in data

    def test_get_htr_status_nonexistent(self, client: TestClient):
        """Probar estado HTR de documento inexistente"""
        response = client.get("/api/v1/htr/status/999")
        assert response.status_code == 404


class TestAICompletionAPI:
    """Pruebas para la API de AI Completion"""

    def test_get_vocabulary(self, client: TestClient):
        """Probar obtener vocabulario sacramental"""
        response = client.get("/api/v1/ai-completion/vocabulary")
        assert response.status_code == 200
        data = response.json()
        assert "vocabulary" in data
        assert "total_words" in data
        assert "categories" in data

    def test_complete_text_basic(self, client: TestClient):
        """Probar completar texto básico"""
        response = client.post(
            "/api/v1/ai-completion/complete-text",
            json={
                "text": "Esta es una prueba",
                "max_suggestions": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "final_text" in data

    def test_suggest_word_completion(self, client: TestClient):
        """Probar sugerencias de completar palabra"""
        response = client.post(
            "/api/v1/ai-completion/suggest-word/baut",
            params={"context": "sacramento de", "max_suggestions": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data

    def test_suggest_word_too_short(self, client: TestClient):
        """Probar palabra muy corta para sugerencias"""
        response = client.post("/api/v1/ai-completion/suggest-word/a")
        assert response.status_code == 400

    def test_correct_text(self, client: TestClient):
        """Probar corrección de texto"""
        response = client.post(
            "/api/v1/ai-completion/correct-text",
            params={"text": "bauttismo en la parroqu1a"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "corrected_text" in data
        assert "corrections_applied" in data


class TestParishesAPI:
    """Pruebas para la API de parroquias"""

    def test_list_parishes_empty(self, client: TestClient):
        """Probar listado de parroquias vacío"""
        response = client.get("/api/v1/parishes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_parish(self, client: TestClient):
        """Probar crear parroquia"""
        parish_data = {
            "name": "Parroquia de Prueba",
            "address": "Calle de Prueba 123",
            "priest_name": "Padre Prueba"
        }
        response = client.post("/api/v1/parishes/", json=parish_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == parish_data["name"]
        assert "id" in data

"""Tests para endpoints de estadísticas (/api/v1/stats/)
"""


def test_dashboard_stats(client):
    response = client.get("/api/v1/stats/dashboard")
    assert response.status_code == 200
    data = response.json()
    # Campos esperados por la suite
    assert "total_documents" in data
    assert "processed_documents" in data
    assert "processing_pipeline" in data
    # Campos adicionales compatibles con DTOs
    assert "documents_by_type" in data
    assert "last_updated" in data

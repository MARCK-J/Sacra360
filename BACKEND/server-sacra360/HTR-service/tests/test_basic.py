"""
Tests básicos para el servicio HTR
"""

import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(test_app):
    """Test del endpoint raíz"""
    client = TestClient(test_app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "HTR Service"
    assert data["version"] == "1.0.0"
    assert data["port"] == 8004

def test_health_check(test_app):
    """Test del health check"""
    client = TestClient(test_app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "htr-service"

def test_config_settings():
    """Test de configuración"""
    from app.utils.config import settings
    assert settings.service_name == "HTR Service - Sacra360"
    assert settings.service_version == "1.0.0"
    assert settings.service_port == 8004
    assert settings.htr_confidence_threshold >= 0.0
    assert settings.htr_confidence_threshold <= 1.0

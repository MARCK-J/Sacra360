"""
Configuración de pytest para HTR Service
"""

import pytest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_app():
    """Fixture para obtener la aplicación FastAPI para testing"""
    from app.main import app
    return app

@pytest.fixture
def sample_image_path():
    """Fixture con ruta a imagen de prueba"""
    return os.path.join(os.path.dirname(__file__), "test_data", "sample_image.jpg")

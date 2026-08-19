"""
Configuración compartida para las pruebas de MedLab Platform.
"""

import pytest

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    Crea un cliente HTTP para realizar peticiones
    contra nuestra aplicación FastAPI.
    """

    with TestClient(app) as test_client:
        yield test_client
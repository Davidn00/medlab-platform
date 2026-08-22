"""
Configuración compartida para las pruebas de MedLab Platform.
"""

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


# ==========================================================
# Cliente HTTP
# ==========================================================

@pytest.fixture
def client():
    """
    Crea un cliente HTTP para realizar peticiones
    contra nuestra aplicación FastAPI.
    """

    with TestClient(app) as test_client:
        yield test_client


# ==========================================================
# Usuario administrador para pruebas
# ==========================================================

@pytest.fixture(scope="session", autouse=True)
def create_test_admin():
    """
    Crea automáticamente el usuario administrador utilizado
    por los tests.

    Usuario:
        admin@medlab.com

    Contraseña:
        admin123
    """

    db: Session = SessionLocal()

    try:
        # --------------------------------------------------
        # Comprobar si el usuario ya existe
        # --------------------------------------------------

        existing_user = (
            db.query(User)
            .filter(User.email == "admin@medlab.com")
            .first()
        )

        # --------------------------------------------------
        # Si no existe, crearlo
        # --------------------------------------------------

        if not existing_user:

            admin = User(
                full_name="Administrador de Pruebas",
                email="admin@medlab.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )

            db.add(admin)
            db.commit()

    finally:
        db.close()
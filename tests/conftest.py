"""
Configuración compartida para las pruebas de MedLab Platform.
"""

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.biomedical_equipment import BiomedicalEquipment
from app.models.calibration import Calibration
from app.core.security import hash_password


# ==========================================================
# Limpieza de datos de prueba
# ==========================================================

@pytest.fixture(autouse=True)
def clean_test_data():
    """
    Limpia los datos creados por las pruebas antes de cada test.

    Solamente elimina equipos cuyo número de serie comienza
    con TEST-, evitando modificar datos reales.
    """

    db: Session = SessionLocal()

    try:
        # --------------------------------------------------
        # Obtener los IDs de los equipos de prueba
        # --------------------------------------------------

        equipment_ids = [
            equipment_id
            for (equipment_id,) in (
                db.query(BiomedicalEquipment.id)
                .filter(
                    BiomedicalEquipment.serial_number.like(
                        "TEST-%"
                    )
                )
                .all()
            )
        ]

        # --------------------------------------------------
        # Eliminar calibraciones de los equipos de prueba
        # --------------------------------------------------

        if equipment_ids:
            (
                db.query(Calibration)
                .filter(
                    Calibration.equipment_id.in_(
                        equipment_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

        # --------------------------------------------------
        # Eliminar equipos de prueba
        # --------------------------------------------------

        (
            db.query(BiomedicalEquipment)
            .filter(
                BiomedicalEquipment.serial_number.like(
                    "TEST-%"
                )
            )
            .delete(
                synchronize_session=False
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================================
# Cliente HTTP
# ==========================================================

@pytest.fixture
def client():
    """
    Crea un cliente HTTP para realizar peticiones
    contra la aplicación FastAPI.
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
        existing_user = (
            db.query(User)
            .filter(
                User.email == "admin@medlab.com"
            )
            .first()
        )

        if existing_user is None:
            admin = User(
                full_name="Administrador de Pruebas",
                email="admin@medlab.com",
                hashed_password=hash_password(
                    "admin123"
                ),
                role=UserRole.ADMIN,
                is_active=True,
            )

            db.add(admin)
            db.commit()

    finally:
        db.close()



# """
# Configuración compartida para las pruebas de MedLab Platform.
# """

# import pytest

# from fastapi.testclient import TestClient
# from sqlalchemy.orm import Session

# from app.main import app
# from app.db.session import SessionLocal
# from app.models.user import User, UserRole
# from app.core.security import hash_password


# # ==========================================================
# # Cliente HTTP
# # ==========================================================

# @pytest.fixture
# def client():
#     """
#     Crea un cliente HTTP para realizar peticiones
#     contra nuestra aplicación FastAPI.
#     """

#     with TestClient(app) as test_client:
#         yield test_client


# # ==========================================================
# # Usuario administrador para pruebas
# # ==========================================================

# @pytest.fixture(scope="session", autouse=True)
# def create_test_admin():
#     """
#     Crea automáticamente el usuario administrador utilizado
#     por los tests.

#     Usuario:
#         admin@medlab.com

#     Contraseña:
#         admin123
#     """

#     db: Session = SessionLocal()

#     try:
#         # --------------------------------------------------
#         # Comprobar si el usuario ya existe
#         # --------------------------------------------------

#         existing_user = (
#             db.query(User)
#             .filter(User.email == "admin@medlab.com")
#             .first()
#         )

#         # --------------------------------------------------
#         # Si no existe, crearlo
#         # --------------------------------------------------

#         if not existing_user:

#             admin = User(
#                 full_name="Administrador de Pruebas",
#                 email="admin@medlab.com",
#                 hashed_password=hash_password("admin123"),
#                 role=UserRole.ADMIN,
#                 is_active=True,
#             )

#             db.add(admin)
#             db.commit()

#     finally:
#         db.close()

"""
Pruebas de versionado de la API.

Verifica que:

1. La API v2 está disponible.
2. La API v1 mantiene sus endpoints existentes.
3. La incorporación de v2 no rompe v1.
4. Los endpoints protegidos de v1 siguen exigiendo autenticación.

Autor: David
Proyecto: MedLab Platform
"""

from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.main import app


# ==========================================================
# Contrato de rutas API v1
# ==========================================================

EXPECTED_V1_ROUTES = {
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/patients"),
    ("GET", "/api/v1/patients"),
    ("GET", "/api/v1/patients/{patient_id}"),
    ("PATCH", "/api/v1/patients/{patient_id}"),
    ("DELETE", "/api/v1/patients/{patient_id}"),
    ("POST", "/api/v1/samples"),
    ("GET", "/api/v1/samples"),
    ("GET", "/api/v1/samples/{sample_id}"),
    ("GET", "/api/v1/samples/patient/{patient_id}"),
    ("PATCH", "/api/v1/samples/{sample_id}"),
    ("DELETE", "/api/v1/samples/{sample_id}"),
    ("POST", "/api/v1/laboratory-tests"),
    ("GET", "/api/v1/laboratory-tests/{test_id}"),
    ("GET", "/api/v1/laboratory-tests/sample/{sample_id}"),
    ("PATCH", "/api/v1/laboratory-tests/{test_id}"),
    ("DELETE", "/api/v1/laboratory-tests/{test_id}"),
    ("POST", "/api/v1/laboratory-tests/{test_id}/process"),
    ("POST", "/api/v1/reports/sample/{sample_id}"),
    ("GET", "/api/v1/reports/tasks/{task_id}"),
    ("GET", "/api/v1/audit/logs"),
    ("POST", "/api/v1/tasks/test"),
    ("GET", "/api/v1/tasks/{task_id}"),
    ("POST", "/api/v1/equipment"),
    ("GET", "/api/v1/equipment"),
    ("GET", "/api/v1/equipment/{equipment_id}"),
    ("PUT", "/api/v1/equipment/{equipment_id}"),
    ("DELETE", "/api/v1/equipment/{equipment_id}"),
    ("GET", "/api/v1/equipment/{equipment_id}/calibrations"),
    ("POST", "/api/v1/calibrations"),
    ("GET", "/api/v1/calibrations"),
    ("GET", "/api/v1/calibrations/expiring"),
    ("GET", "/api/v1/calibrations/expired"),
    ("GET", "/api/v1/calibrations/{calibration_id}"),
    ("PUT", "/api/v1/calibrations/{calibration_id}"),
    ("DELETE", "/api/v1/calibrations/{calibration_id}"),
    ("GET", "/api/v1/notifications"),
    ("PATCH", "/api/v1/notifications/{notification_id}/read"),
}


# ==========================================================
# Utilidades
# ==========================================================

def get_api_routes(application):
    routes = set()

    def normalize_path(path):
        if path != "/" and path.endswith("/"):
            return path.rstrip("/")
        return path

    for route in application.routes:
        # Rutas directamente registradas en FastAPI.
        if isinstance(route, APIRoute):
            path = normalize_path(route.path)

            for method in route.methods:
                routes.add((method, path))

            continue

        # FastAPI 0.141.x representa los routers incluidos
        # mediante _IncludedRouter.
        if hasattr(route, "original_router"):
            include_context = route.include_context
            include_prefix = (
                getattr(include_context, "prefix", "") or ""
            )

            original_router = route.original_router

            for nested_route in original_router.routes:
                if not isinstance(nested_route, APIRoute):
                    continue

                # nested_route.path ya contiene el prefix del
                # APIRouter original. Solo debemos agregar el
                # prefix utilizado al incluir el router.
                path = (
                    f"{include_prefix.rstrip('/')}"
                    f"{nested_route.path}"
                )

                if not path.startswith("/"):
                    path = f"/{path}"

                path = normalize_path(path)

                for method in nested_route.methods:
                    routes.add((method, path))

    return routes


# ==========================================================
# Parte 19 - API v2
# ==========================================================

def test_api_v2_version_endpoint(client):
    """
    Verifica que la API v2 está disponible.
    """
    response = client.get("/api/v2/version")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "api_version": "v2",
        "status": "available",
    }


def test_api_v2_version_is_independent_from_v1(client):
    """
    Verifica que v2 tiene un namespace independiente
    de v1.
    """
    response_v2 = client.get("/api/v2/version")
    response_v1 = client.get("/api/v1/patients")

    assert response_v2.status_code == 200

    # /api/v1/patients continúa protegido.
    assert response_v1.status_code == 401


# ==========================================================
# Compatibilidad API v1
# ==========================================================

def test_all_existing_v1_routes_are_preserved():
    """
    Comprueba que todos los endpoints v1 existentes
    continúan registrados después de introducir v2.
    """
    actual_routes = get_api_routes(app)

    missing_routes = EXPECTED_V1_ROUTES - actual_routes

    assert not missing_routes, (
        "Se detectaron endpoints v1 desaparecidos: "
        f"{sorted(missing_routes)}"
    )


def test_v1_does_not_expose_v2_endpoint():
    """
    Comprueba que el endpoint exclusivo de v2 no está
    accidentalmente registrado dentro de /api/v1.
    """
    actual_routes = get_api_routes(app)

    assert ("GET", "/api/v2/version") in actual_routes

    v1_routes = {
        route
        for route in actual_routes
        if route[1].startswith("/api/v1")
    }

    assert ("GET", "/api/v2/version") not in v1_routes


# ==========================================================
# Compatibilidad funcional mínima
# ==========================================================

def test_v1_patients_requires_authentication(client):
    """
    Verifica que la incorporación de v2 no modifica
    la protección JWT existente en v1.
    """
    response = client.get("/api/v1/patients")

    assert response.status_code == 401


def test_v1_authentication_endpoint_still_exists(client):
    """
    Verifica que el endpoint de autenticación v1
    continúa disponible.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "usuario_inexistente@example.com",
            "password": "password_incorrecto",
        },
    )

    assert response.status_code == 401


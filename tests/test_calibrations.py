"""
Pruebas de integración para Calibration.

Proyecto: MedLab Platform
"""

from fastapi.testclient import TestClient


def create_test_equipment(
    client: TestClient,
):
    """
    Crea un equipo utilizado por las pruebas
    de calibración.
    """

    response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Equipo de calibración",
            "manufacturer": "MedLab",
            "model": "CAL-001",
            "serial_number": "TEST-CAL-EQUIPMENT-001",
            "location": "Laboratorio",
            "status": "ACTIVE",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_calibration(
    client: TestClient,
):
    """
    Debe crear una calibración asociada a un equipo.
    """

    equipment_id = create_test_equipment(client)

    response = client.post(
        "/api/v1/calibrations",
        json={
            "equipment_id": equipment_id,
            "calibration_date": (
                "2026-08-01T10:00:00Z"
            ),
            "next_calibration_date": (
                "2027-08-01T10:00:00Z"
            ),
            "performed_by": "Técnico MedLab",
            "certificate_number": "CERT-001",
            "status": "VALID",
            "notes": "Calibración inicial.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["equipment_id"] == equipment_id
    assert data["performed_by"] == "Técnico MedLab"
    assert data["certificate_number"] == "CERT-001"

def test_create_calibration_nonexistent_equipment(
    client: TestClient,
):
    """
    No debe permitirse una calibración para
    un equipo inexistente.
    """

    response = client.post(
        "/api/v1/calibrations",
        json={
            "equipment_id": (
                "550e8400-e29b-41d4-a716-446655440000"
            ),
            "calibration_date": (
                "2026-08-01T10:00:00Z"
            ),
            "next_calibration_date": (
                "2027-08-01T10:00:00Z"
            ),
            "performed_by": "Técnico MedLab",
            "certificate_number": "CERT-002",
            "status": "VALID",
        },
    )

    assert response.status_code == 404

def test_invalid_calibration_dates(
    client: TestClient,
):
    """
    La próxima calibración debe ser posterior
    a la calibración actual.
    """

    equipment_id = create_test_equipment(client)

    response = client.post(
        "/api/v1/calibrations",
        json={
            "equipment_id": equipment_id,
            "calibration_date": (
                "2026-08-20T10:00:00Z"
            ),
            "next_calibration_date": (
                "2026-08-10T10:00:00Z"
            ),
            "performed_by": "Técnico MedLab",
            "certificate_number": "CERT-003",
            "status": "VALID",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "La próxima fecha de calibración "
        "debe ser posterior a la fecha de calibración."
    )

def test_equal_calibration_dates(
    client: TestClient,
):
    """
    Las fechas de calibración no pueden ser iguales.
    """

    equipment_id = create_test_equipment(client)

    response = client.post(
        "/api/v1/calibrations",
        json={
            "equipment_id": equipment_id,
            "calibration_date": (
                "2026-08-20T10:00:00Z"
            ),
            "next_calibration_date": (
                "2026-08-20T10:00:00Z"
            ),
            "performed_by": "Técnico MedLab",
            "status": "VALID",
        },
    )

    assert response.status_code == 400

def test_get_calibrations_by_equipment(
    client: TestClient,
):
    """
    Debe devolver las calibraciones asociadas
    a un equipo.
    """

    equipment_id = create_test_equipment(client)

    response = client.post(
        "/api/v1/calibrations",
        json={
            "equipment_id": equipment_id,
            "calibration_date": (
                "2026-08-01T10:00:00Z"
            ),
            "next_calibration_date": (
                "2027-08-01T10:00:00Z"
            ),
            "performed_by": "Técnico",
            "status": "VALID",
        },
    )

    assert response.status_code == 201

    response = client.get(
        f"/api/v1/equipment/{equipment_id}/calibrations"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["equipment_id"] == equipment_id


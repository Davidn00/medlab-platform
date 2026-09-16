"""
Pruebas del historial de calibraciones.

Proyecto: MedLab Platform
"""


def admin_headers(client):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@medlab.com",
            "password": "Admin123!SecurePassword",
        },
    )

    assert response.status_code == 200

    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_equipment(client):

    response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Equipo Calibration History",
            "manufacturer": "MedLab",
            "model": "CH-001",
            "serial_number": "TEST-CAL-HISTORY-001",
            "location": "Laboratorio",
            "status": "ACTIVE",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_calibration(
    client,
    equipment_id,
    date,
    next_date,
):

    response = client.post(
        "/api/v1/calibrations",
        json={
            "equipment_id": equipment_id,
            "calibration_date": date,
            "next_calibration_date": next_date,
            "performed_by": "Técnico MedLab",
            "status": "VALID",
        },
    )

    assert response.status_code == 201


def test_calibration_history(
    client,
):

    headers = admin_headers(client)

    equipment_id = create_equipment(client)

    create_calibration(
        client,
        equipment_id,
        "2025-01-01T10:00:00Z",
        "2026-01-01T10:00:00Z",
    )

    create_calibration(
        client,
        equipment_id,
        "2026-01-01T10:00:00Z",
        "2027-01-01T10:00:00Z",
    )

    response = client.get(
        f"/api/v2/calibrations/equipment/{equipment_id}/history",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["equipment_id"] == equipment_id

    assert len(data["calibrations"]) == 2

    assert data["metrics"]["total_calibrations"] == 2

    assert data["metrics"]["last_calibration"] == "2026-01-01T10:00:00+00:00"

    assert data["metrics"]["calibration_frequency_days"] == 365.0

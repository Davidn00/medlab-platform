"""
Pruebas del ciclo de vida de equipos.

Proyecto: MedLab Platform
"""

from datetime import datetime


def admin_headers(client):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@medlab.com",
            "password": "Admin123!SecurePassword",
        },
    )

    assert response.status_code == 200

    return {
        "Authorization":
            f"Bearer {response.json()['access_token']}"
    }


def create_equipment(client):

    response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Equipo Lifecycle",
            "manufacturer": "MedLab",
            "model": "LC-001",
            "serial_number": "TEST-LIFECYCLE-001",
            "location": "Laboratorio",
            "status": "ACTIVE",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_change_equipment_status(
    client,
):

    equipment_id = create_equipment(client)

    response = client.patch(
        f"/api/v2/equipment/{equipment_id}/status",
        json={
            "status": "MAINTENANCE",
        },
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "MAINTENANCE"


def test_invalid_equipment_transition(
    client,
):

    equipment_id = create_equipment(client)

    response = client.patch(
        f"/api/v2/equipment/{equipment_id}/status",
        json={
            "status": "RETIRED",
        },
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v2/equipment/{equipment_id}/status",
        json={
            "status": "ACTIVE",
        },
        headers=admin_headers(client),
    )

    assert response.status_code == 409


def test_equipment_lifecycle_event(
    client,
):

    equipment_id = create_equipment(client)

    response = client.post(
        f"/api/v2/equipment/{equipment_id}/lifecycle-events",
        json={
            "event_type": "VALIDATION",
            "description": (
                "Validación funcional completada."
            ),
            "performed_by": "Técnico MedLab",
        },
        headers=admin_headers(client),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_type"] == "VALIDATION"
    assert data["equipment_id"] == equipment_id


def test_get_equipment_lifecycle(
    client,
):

    equipment_id = create_equipment(client)

    response = client.post(
        f"/api/v2/equipment/{equipment_id}/lifecycle-events",
        json={
            "event_type": "VALIDATION",
            "description": "Validación inicial.",
            "performed_by": "Técnico",
        },
        headers=admin_headers(client),
    )

    assert response.status_code == 201

    response = client.get(
        f"/api/v2/equipment/{equipment_id}/lifecycle",
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
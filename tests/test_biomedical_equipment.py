"""
Pruebas de integración para BiomedicalEquipment.

Proyecto: MedLab Platform
"""

from fastapi.testclient import TestClient


def test_create_equipment(client: TestClient):
    """
    Debe crear correctamente un equipo biomédico.
    """

    response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Analizador hematológico",
            "manufacturer": "Sysmex",
            "model": "XN-1000",
            "serial_number": "TEST-XN1000-001",
            "location": "Hematología",
            "status": "ACTIVE",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Analizador hematológico"
    assert data["manufacturer"] == "Sysmex"
    assert data["model"] == "XN-1000"
    assert data["serial_number"] == "TEST-XN1000-001"

    assert "id" in data
    assert "created_at" in data


def test_get_equipment(client: TestClient):
    """
    Debe devolver la lista de equipos.
    """

    create_response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Centrífuga",
            "manufacturer": "Eppendorf",
            "model": "5804R",
            "serial_number": "TEST-CENT-001",
            "location": "Laboratorio Central",
            "status": "ACTIVE",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/equipment"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_equipment_by_id(client: TestClient):
    """
    Debe obtener un equipo por UUID.
    """

    create_response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Microscopio",
            "manufacturer": "Olympus",
            "model": "CX23",
            "serial_number": "TEST-MICRO-001",
            "location": "Microbiología",
            "status": "ACTIVE",
        },
    )

    assert create_response.status_code == 201

    equipment_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/equipment/{equipment_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == equipment_id
    assert data["serial_number"] == "TEST-MICRO-001"

def test_get_nonexistent_equipment(
    client: TestClient,
):
    """
    Un equipo inexistente debe devolver 404.
    """

    equipment_id = (
        "550e8400-e29b-41d4-a716-446655440000"
    )

    response = client.get(
        f"/api/v1/equipment/{equipment_id}"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Equipo biomédico no encontrado."
    )

def test_duplicate_equipment_serial_number(
    client: TestClient,
):
    """
    No deben existir dos equipos con el mismo
    número de serie.
    """

    payload = {
        "name": "Analizador",
        "manufacturer": "Roche",
        "model": "Cobas",
        "serial_number": "TEST-DUPLICATE-001",
        "location": "Química Clínica",
        "status": "ACTIVE",
    }

    first_response = client.post(
        "/api/v1/equipment",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/equipment",
        json=payload,
    )

    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "Ya existe un equipo con ese número de serie."
    )


def test_update_equipment(
    client: TestClient,
):
    """
    Debe actualizar correctamente un equipo.
    """

    create_response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Balanza",
            "manufacturer": "Sartorius",
            "model": "Entris II",
            "serial_number": "TEST-BAL-001",
            "location": "Laboratorio",
            "status": "ACTIVE",
        },
    )

    assert create_response.status_code == 201

    equipment_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/equipment/{equipment_id}",
        json={
            "location": "Laboratorio de Pesaje",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["location"] == "Laboratorio de Pesaje"

def test_delete_equipment(
    client: TestClient,
):
    """
    Debe eliminar correctamente un equipo.
    """

    create_response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Equipo temporal",
            "manufacturer": "Test",
            "model": "TEST-01",
            "serial_number": "TEST-DELETE-001",
            "location": "Testing",
            "status": "ACTIVE",
        },
    )

    assert create_response.status_code == 201

    equipment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/equipment/{equipment_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/equipment/{equipment_id}"
    )

    assert get_response.status_code == 404

def test_cannot_delete_equipment_with_calibrations(
    client: TestClient,
):
    """
    Un equipo con historial de calibraciones no debe
    eliminarse físicamente.
    """

    equipment_response = client.post(
        "/api/v1/equipment",
        json={
            "name": "Equipo con historial",
            "manufacturer": "MedLab",
            "model": "TEST-HISTORY",
            "serial_number": "TEST-HISTORY-001",
            "location": "Laboratorio",
            "status": "ACTIVE",
        },
    )

    assert equipment_response.status_code == 201

    equipment_id = equipment_response.json()["id"]

    calibration_response = client.post(
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
            "status": "VALID",
        },
    )

    assert calibration_response.status_code == 201

    delete_response = client.delete(
        f"/api/v1/equipment/{equipment_id}"
    )

    assert delete_response.status_code == 409
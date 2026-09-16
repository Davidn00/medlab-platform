"""
Pruebas de mantenimiento biomédico.

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
            "name": "Equipo Maintenance",
            "manufacturer": "MedLab",
            "model": "MT-001",
            "serial_number": "TEST-MAINTENANCE-001",
            "location": "Laboratorio",
            "status": "ACTIVE",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_maintenance(client):

    headers = admin_headers(client)

    equipment_id = create_equipment(client)

    response = client.post(
        "/api/v2/maintenance",
        json={
            "equipment_id": equipment_id,
            "title": "Mantenimiento preventivo",
            "maintenance_type": "PREVENTIVE",
            "status": "SCHEDULED",
            "scheduled_date": "2026-10-01T10:00:00Z",
            "description": "Mantenimiento preventivo anual.",
            "assigned_to": "Técnico MedLab",
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["equipment_id"] == equipment_id
    assert data["maintenance_type"] == "PREVENTIVE"


def test_start_maintenance(client):

    headers = admin_headers(client)

    equipment_id = create_equipment(client)

    response = client.post(
        "/api/v2/maintenance",
        json={
            "equipment_id": equipment_id,
            "title": "Mantenimiento correctivo",
            "maintenance_type": "CORRECTIVE",
            "status": "SCHEDULED",
        },
        headers=headers,
    )

    assert response.status_code == 201

    maintenance_id = response.json()["id"]

    response = client.patch(
        f"/api/v2/maintenance/{maintenance_id}/status",
        params={
            "new_status": "IN_PROGRESS",
        },
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json()["status"] == ("IN_PROGRESS")


def test_create_maintenance_record(client):

    headers = admin_headers(client)

    equipment_id = create_equipment(client)

    response = client.post(
        "/api/v2/maintenance",
        json={
            "equipment_id": equipment_id,
            "title": "Inspección técnica",
            "maintenance_type": "INSPECTION",
            "status": "COMPLETED",
        },
        headers=headers,
    )

    assert response.status_code == 201

    maintenance_id = response.json()["id"]

    response = client.post(
        "/api/v2/maintenance/records",
        json={
            "maintenance_id": maintenance_id,
            "equipment_id": equipment_id,
            "performed_at": "2026-09-10T10:00:00Z",
            "performed_by": "Técnico MedLab",
            "action": "Inspección general del equipo.",
            "findings": "Equipo en condiciones normales.",
            "parts_replaced": None,
            "notes": "Sin observaciones.",
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["maintenance_id"] == maintenance_id
    assert data["equipment_id"] == equipment_id

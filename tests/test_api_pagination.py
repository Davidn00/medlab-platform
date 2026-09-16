"""
Pruebas de integración para Parte 20.
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

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_v2_patients_pagination(
    client,
):
    response = client.get(
        "/api/v2/patients?page=1&limit=20",
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data) == {
        "items",
        "page",
        "limit",
        "total",
        "pages",
    }

    assert data["page"] == 1
    assert data["limit"] == 20

    assert data["total"] >= 0
    assert data["pages"] >= 0

    assert isinstance(
        data["items"],
        list,
    )


def test_v2_samples_filters(
    client,
):
    response = client.get(
        "/api/v2/samples"
        "?page=1"
        "&limit=10"
        "&search=TEST"
        "&sort_by=sample_code"
        "&sort_order=asc",
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    assert isinstance(
        response.json()["items"],
        list,
    )


def test_v2_calibrations_status_filter(
    client,
):
    response = client.get(
        "/api/v2/calibrations?page=1&limit=10&status=expired",
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    assert isinstance(
        response.json()["items"],
        list,
    )


def test_v2_equipment_search(
    client,
):
    response = client.get(
        "/api/v2/equipment?page=1&limit=10&search=TEST",
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    assert isinstance(
        response.json()["items"],
        list,
    )


def test_v2_laboratory_tests_filter(
    client,
):
    response = client.get(
        "/api/v2/laboratory-tests?page=1&limit=10&status=pending",
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    assert isinstance(
        response.json()["items"],
        list,
    )


def test_v2_requires_authentication(
    client,
):
    response = client.get("/api/v2/patients")

    assert response.status_code == 401

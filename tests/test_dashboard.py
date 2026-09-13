"""
Pruebas de integración para Parte 21.
"""


def admin_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username":
                "admin@medlab.com",
            "password":
                "Admin123!SecurePassword",
        },
    )

    assert response.status_code == 200

    token = response.json()[
        "access_token"
    ]

    return {
        "Authorization":
            f"Bearer {token}"
    }


def test_dashboard_statistics(
    client,
):
    response = client.get(
        "/api/v1/dashboard/statistics",
        headers=admin_headers(client),
    )

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "patients",
        "samples",
        "tests",
        "equipment",
        "calibrations",
        "expired_calibrations",
        "pending_tests",
    }

    assert set(data) == expected_fields

    for value in data.values():
        assert isinstance(
            value,
            int,
        )

        assert value >= 0


def test_dashboard_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/dashboard/statistics"
    )

    assert response.status_code == 401
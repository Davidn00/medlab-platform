"""
Pruebas iniciales de autenticación.
"""


def test_root(client):
    """
    Verifica que la API esté funcionando.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "message" in data
    

def test_login_invalid_credentials(client):
    """
    Un usuario con credenciales incorrectas no debe
    poder autenticarse.
    """

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "usuario_inexistente@example.com",
            "password": "password_incorrecto",
        },
    )

    assert response.status_code == 401



def test_protected_endpoint_without_token(client):
    """
    Un usuario sin JWT no debe poder acceder a endpoints
    que requieren autenticación.
    """

    response = client.get("/api/v1/patients")

    assert response.status_code == 401

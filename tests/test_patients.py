def test_create_patient_invalid_email(client):
    """
    Verifica que Pydantic rechace un email inválido.
    """

    # 1. Autenticarse
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@medlab.com",
            "password": "admin123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # 2. Intentar crear paciente con email inválido
    response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "first_name": "Carlos",
            "last_name": "Martínez",
            "date_of_birth": "1985-06-15",
            "gender": "male",
            "medical_record": "MED-TEST-001",
            "email": "email-invalido",
        },
    )

    assert response.status_code == 422



def test_create_patient_missing_required_fields(client):
    """
    Verifica que los campos obligatorios sean validados.
    """
    # 1. Autenticarse
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@medlab.com",
            "password": "admin123",
        },
    )
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]

    # Intentar crear un paciente sin los campos obligatorios
    response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "first_name": "Carlos",
        },
    )
    # FastAPI/Pydantic debe rechazar la solicitud
    assert response.status_code == 422
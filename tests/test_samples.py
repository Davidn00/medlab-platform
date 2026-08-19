"""
Pruebas automatizadas para la gestión de muestras.
"""

from uuid import uuid4


def login_as_admin(client):
    """
    Autentica un usuario administrador y devuelve el JWT.
    """

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@medlab.com",
            "password": "admin123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_patient(client, token):
    """
    Crea un paciente de prueba y devuelve su ID.
    """

    patient_data = {
        "first_name": "Paciente",
        "last_name": "SampleTest",
        "birth_date": "1990-01-15",
        "gender": "male",
        "medical_record": f"MED-{uuid4().hex[:10]}",
        "email": f"sample-{uuid4().hex[:8]}@example.com",
    }

    response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=patient_data,
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_sample(client):
    """
    Verifica que un usuario autorizado pueda crear una muestra.
    """

    token = login_as_admin(client)

    patient_id = create_patient(client, token)

    sample_data = {
        "patient_id": patient_id,
        "sample_type": "blood",
        "sample_code": f"SMP-{uuid4().hex[:10]}",
    }

    response = client.post(
        "/api/v1/samples",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=sample_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["patient_id"] == patient_id
    assert data["sample_type"] == "blood"
    assert data["status"] == "collected"
    assert data["sample_code"] == sample_data["sample_code"]


def test_create_sample_without_token(client):
    """
    Verifica que una muestra no pueda crearse sin autenticación.
    """

    response = client.post(
        "/api/v1/samples",
        json={
            "patient_id": str(uuid4()),
            "sample_type": "blood",
            "sample_code": f"SMP-{uuid4().hex[:10]}",
        },
    )

    assert response.status_code == 401


def test_create_sample_invalid_type(client):
    """
    Verifica que Pydantic rechace un tipo de muestra inválido.
    """

    token = login_as_admin(client)

    patient_id = create_patient(client, token)

    response = client.post(
        "/api/v1/samples",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "patient_id": patient_id,
            "sample_type": "invalid_sample_type",
            "sample_code": f"SMP-{uuid4().hex[:10]}",
        },
    )

    assert response.status_code == 422


def test_create_sample_missing_required_fields(client):
    """
    Verifica que los campos obligatorios de una muestra
    sean validados correctamente.
    """

    token = login_as_admin(client)

    response = client.post(
        "/api/v1/samples",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sample_type": "blood",
        },
    )

    assert response.status_code == 422


def test_get_sample(client):
    """
    Verifica que una muestra existente pueda consultarse.
    """

    token = login_as_admin(client)

    patient_id = create_patient(client, token)

    sample_data = {
        "patient_id": patient_id,
        "sample_type": "urine",
        "sample_code": f"SMP-{uuid4().hex[:10]}",
    }

    create_response = client.post(
        "/api/v1/samples",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=sample_data,
    )

    assert create_response.status_code == 201

    sample_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/samples/{sample_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == sample_id
    assert data["patient_id"] == patient_id
    assert data["sample_type"] == "urine"


def test_get_samples_by_patient(client):
    """
    Verifica que puedan consultarse las muestras asociadas
    a un paciente.
    """

    token = login_as_admin(client)

    patient_id = create_patient(client, token)

    sample_data = {
        "patient_id": patient_id,
        "sample_type": "saliva",
        "sample_code": f"SMP-{uuid4().hex[:10]}",
    }

    create_response = client.post(
        "/api/v1/samples",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=sample_data,
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/api/v1/samples/patient/{patient_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    assert any(
        sample["id"] == create_response.json()["id"]
        for sample in data
    )
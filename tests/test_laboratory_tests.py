"""
Pruebas automatizadas para las pruebas de laboratorio.
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

    response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "first_name": "Paciente",
            "last_name": "LaboratoryTest",
            "birth_date": "1988-05-20",
            "gender": "female",
            "medical_record": f"MED-{uuid4().hex[:10]}",
            "email": f"lab-{uuid4().hex[:8]}@example.com",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_sample(client, token):
    """
    Crea un paciente y una muestra de prueba.
    Devuelve el ID de la muestra.
    """

    patient_id = create_patient(client, token)

    response = client.post(
        "/api/v1/samples",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "patient_id": patient_id,
            "sample_type": "blood",
            "sample_code": f"SMP-{uuid4().hex[:10]}",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_laboratory_test(client):
    """
    Verifica que un usuario autorizado pueda crear
    una prueba de laboratorio.
    """

    token = login_as_admin(client)

    sample_id = create_sample(client, token)

    test_data = {
        "sample_id": sample_id,
        "test_name": "Hemoglobina",
        "unit": "g/dL",
        "reference_range": "12-17",
    }

    response = client.post(
        "/api/v1/laboratory-tests",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=test_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["sample_id"] == sample_id
    assert data["test_name"] == "Hemoglobina"
    assert data["unit"] == "g/dL"
    assert data["reference_range"] == "12-17"
    assert data["status"] == "pending"
    assert data["result_value"] is None
    assert data["comments"] is None


def test_create_laboratory_test_without_token(client):
    """
    Verifica que una prueba de laboratorio no pueda
    crearse sin autenticación.
    """

    response = client.post(
        "/api/v1/laboratory-tests",
        json={
            "sample_id": str(uuid4()),
            "test_name": "Hemoglobina",
            "unit": "g/dL",
            "reference_range": "12-17",
        },
    )

    assert response.status_code == 401


def test_create_laboratory_test_missing_required_fields(client):
    """
    Verifica que los campos obligatorios sean validados.
    """

    token = login_as_admin(client)

    response = client.post(
        "/api/v1/laboratory-tests",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "test_name": "Hemoglobina",
        },
    )

    assert response.status_code == 422


def test_create_laboratory_test_invalid_name(client):
    """
    Verifica que el nombre de la prueba respete la longitud
    mínima definida en el schema Pydantic.
    """

    token = login_as_admin(client)

    sample_id = create_sample(client, token)

    response = client.post(
        "/api/v1/laboratory-tests",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sample_id": sample_id,
            "test_name": "A",
            "unit": "g/dL",
            "reference_range": "12-17",
        },
    )

    assert response.status_code == 422


def test_get_laboratory_test(client):
    """
    Verifica que una prueba de laboratorio existente
    pueda consultarse.
    """

    token = login_as_admin(client)

    sample_id = create_sample(client, token)

    create_response = client.post(
        "/api/v1/laboratory-tests",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sample_id": sample_id,
            "test_name": "Glucosa",
            "unit": "mg/dL",
            "reference_range": "70-100",
        },
    )

    assert create_response.status_code == 201

    test_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/laboratory-tests/{test_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_id
    assert data["sample_id"] == sample_id
    assert data["test_name"] == "Glucosa"


def test_get_laboratory_tests_by_sample(client):
    """
    Verifica que puedan consultarse las pruebas asociadas
    a una muestra.
    """

    token = login_as_admin(client)

    sample_id = create_sample(client, token)

    create_response = client.post(
        "/api/v1/laboratory-tests",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "sample_id": sample_id,
            "test_name": "Colesterol",
            "unit": "mg/dL",
            "reference_range": "125-200",
        },
    )

    assert create_response.status_code == 201

    test_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/laboratory-tests/sample/{sample_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        laboratory_test["id"] == test_id
        for laboratory_test in data
    )

def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_database_health(client):
    response = client.get("/health/db")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_redis_health(client):
    response = client.get("/health/redis")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
"""
Pruebas de monitoring y health checks.

Autor: David
Proyecto: MedLab Platform
"""


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "MedLab Platform"


def test_liveness(client):
    response = client.get("/health/live")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["check"] == "liveness"


def test_database_health(client):
    response = client.get("/health/db")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "postgresql"


def test_redis_health(client):
    response = client.get("/health/redis")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "redis"


def test_readiness(client):
    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["ready"] is True

    checks = data["checks"]

    assert checks["fastapi"]["status"] == "ok"
    assert checks["postgresql"]["status"] == "ok"
    assert checks["redis"]["status"] == "ok"
    assert checks["celery"]["status"] == "ok"


def test_readiness_contains_all_dependencies(client):
    response = client.get("/health/ready")

    assert response.status_code == 200

    checks = response.json()["checks"]

    assert set(checks.keys()) == {
        "fastapi",
        "postgresql",
        "redis",
        "celery",
    }

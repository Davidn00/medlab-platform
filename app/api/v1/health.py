"""
Health checks de MedLab Platform.

Incluye:

- Liveness
- Readiness
- PostgreSQL
- Redis
- Celery Worker

Autor: David
Proyecto: MedLab Platform
"""

from fastapi import APIRouter, logger
from fastapi.responses import JSONResponse
from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.workers.celery_app import celery_app

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


# ==========================================================
# Liveness
# ==========================================================


@router.get("")
def health():
    """
    Health check principal.

    No comprueba dependencias externas.

    Su objetivo es determinar si el proceso
    FastAPI está vivo.
    """

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/live")
def liveness():
    """
    Liveness probe.

    Indica que el proceso FastAPI está ejecutándose.
    """

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "check": "liveness",
    }


# ==========================================================
# PostgreSQL
# ==========================================================


def check_database() -> dict:
    """
    Comprueba la conectividad con PostgreSQL.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "service": "postgresql",
        }

    except Exception:
        return {
            "status": "error",
            "service": "postgresql",
        }


@router.get("/db")
def database_health():
    """
    Health check específico de PostgreSQL.
    """

    result = check_database()

    if result["status"] != "ok":
        return JSONResponse(
            status_code=503,
            content=result,
        )

    return result


# ==========================================================
# Redis
# ==========================================================


def check_redis() -> dict:
    """
    Comprueba la conectividad con Redis.
    """

    client = None

    try:
        if settings.redis_url:
            client = Redis.from_url(
                settings.redis_url,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
        else:
            client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.REDIS_PASSWORD,
                db=settings.redis_db,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

        client.ping()

        return {
            "status": "ok",
            "service": "redis",
        }

    except Exception:
        return {
            "status": "error",
            "service": "redis",
        }

    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                logger.debug("Error closing Redis client", exc_info=True)


@router.get("/redis")
def redis_health():
    """
    Health check específico de Redis.
    """

    result = check_redis()

    if result["status"] != "ok":
        return JSONResponse(
            status_code=503,
            content=result,
        )

    return result


# ==========================================================
# Celery
# ==========================================================


def check_celery() -> dict:
    """
    Comprueba que al menos un Celery Worker responde
    al comando ping.
    """

    try:
        inspector = celery_app.control.inspect(timeout=1.0)

        response = inspector.ping()

        if not response:
            return {
                "status": "error",
                "service": "celery",
            }

        return {
            "status": "ok",
            "service": "celery",
            "workers": len(response),
        }

    except Exception:
        return {
            "status": "error",
            "service": "celery",
        }


# ==========================================================
# Readiness
# ==========================================================


@router.get("/ready")
def readiness():
    """
    Readiness probe.

    Comprueba que todos los servicios necesarios
    para procesar peticiones están disponibles.

    Servicios:

    - FastAPI
    - PostgreSQL
    - Redis
    - Celery Worker
    """

    database = check_database()
    redis = check_redis()
    celery = check_celery()

    checks = {
        "fastapi": {
            "status": "ok",
        },
        "postgresql": database,
        "redis": redis,
        "celery": celery,
    }

    ready = all(check["status"] == "ok" for check in checks.values())

    response = {
        "status": "ok" if ready else "error",
        "ready": ready,
        "checks": checks,
    }

    if not ready:
        return JSONResponse(
            status_code=503,
            content=response,
        )

    return response

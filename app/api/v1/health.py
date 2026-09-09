"""
Health checks de MedLab Platform.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health():
    """
    Health check básico.
    """

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/db")
def database_health():
    """
    Comprueba PostgreSQL.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "postgresql",
        }

    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "postgresql",
            },
        )


@router.get("/redis")
def redis_health():
    """
    Comprueba Redis.
    """

    try:
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
            "redis": "connected",
        }

    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "redis": "unavailable",
            },
        )


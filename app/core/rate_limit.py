"""
Rate limiting basado en Redis.
"""

import logging

from redis import Redis

from app.core.config import settings

logger = logging.getLogger("medlab.security")

def get_redis_client() -> Redis:
    if settings.redis_url:
        return Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )

def check_login_rate_limit(identifier: str) -> bool:
    """
    Devuelve True si el intento está permitido.

    El límite se aplica por identificador.
    """

    key = f"medlab:login:attempts:{identifier}"

    try:
        redis = get_redis_client()

        attempts = redis.incr(key)

        if attempts == 1:
            redis.expire(
                key,
                settings.LOGIN_RATE_WINDOW_SECONDS,
            )

        return attempts <= settings.LOGIN_RATE_LIMIT

    except Exception:
        # Fail-open para no dejar fuera de servicio
        # toda la autenticación si Redis está caído.
        logger.warning("Redis unavailable during login rate limiting")

        return True


def clear_login_rate_limit(identifier: str) -> None:
    """
    Elimina el contador después de un login exitoso.
    """

    try:
        redis = get_redis_client()

        redis.delete(f"medlab:login:attempts:{identifier}")

    except Exception:
        logger.warning("Unable to clear login rate limit")

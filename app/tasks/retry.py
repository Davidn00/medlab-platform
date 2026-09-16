"""
Políticas de reintento para tareas Celery de MedLab Platform.

Autor: David
Proyecto: MedLab Platform
"""

from kombu.exceptions import OperationalError as KombuOperationalError
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
)
from redis.exceptions import (
    TimeoutError as RedisTimeoutError,
)
from sqlalchemy.exc import (
    DisconnectionError,
    InterfaceError,
)
from sqlalchemy.exc import (
    OperationalError as SQLAlchemyOperationalError,
)

from app.core.config import settings

# Excepciones que normalmente representan fallos temporales de
# infraestructura. No incluimos Exception/ValueError porque los errores
# de lógica, validación o datos no deben reintentarse automáticamente.
TRANSIENT_TASK_ERRORS = (
    SQLAlchemyOperationalError,
    InterfaceError,
    DisconnectionError,
    KombuOperationalError,
    RedisConnectionError,
    RedisTimeoutError,
    TimeoutError,
    ConnectionError,
)


TASK_RETRY_KWARGS = {
    "max_retries": settings.celery_task_max_retries,
}

TASK_RETRY_BACKOFF = settings.celery_task_retry_backoff
TASK_RETRY_BACKOFF_MAX = settings.celery_task_retry_backoff_max
TASK_RETRY_JITTER = settings.celery_task_retry_jitter

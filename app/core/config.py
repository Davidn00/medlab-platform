"""
Módulo de configuración de MedLab Platform.

Este archivo carga todas las variables definidas en el archivo .env
y las convierte en atributos de un objeto de configuración.

De esta forma evitamos utilizar variables globales dispersas
por todo el proyecto.

Autor: David
Proyecto: MedLab Platform
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Clase principal de configuración.

    Cada atributo corresponde a una variable del archivo .env.
    Pydantic se encarga automáticamente de leer el archivo
    y convertir los valores al tipo correcto.
    """

    # ======================================
    # Configuración general
    # ======================================

    APP_NAME: str
    APP_VERSION: str
    ENVIRONMENT: str

    # ======================================
    # Seguridad
    # ======================================

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # ==========================================================
    # Usuario administrador inicial
    # ==========================================================

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_FULL_NAME: str

    # ======================================
    # Base de datos
    # ======================================

    DATABASE_URL: str

    # ======================================
    # Celery & Redis
    # ======================================

    REDIS_PASSWORD: str | None = None

    redis_host: str = Field(
        default="redis",
        validation_alias="REDIS_HOST",
    )

    redis_port: int = Field(
        default=6379,
        validation_alias="REDIS_PORT",
    )

    redis_db: int = Field(
        default=0,
        validation_alias="REDIS_DB",
    )

    celery_broker_url: str = Field(
        default="redis://redis:6379/0",
        validation_alias="CELERY_BROKER_URL",
    )

    celery_result_backend: str = Field(
        default="redis://redis:6379/1",
        validation_alias="CELERY_RESULT_BACKEND",
    )

    # Política de reintentos de tareas Celery
    celery_task_max_retries: int = Field(
        default=5,
        validation_alias="CELERY_TASK_MAX_RETRIES",
    )

    celery_task_retry_backoff: int = Field(
        default=10,
        validation_alias="CELERY_TASK_RETRY_BACKOFF",
    )

    celery_task_retry_backoff_max: int = Field(
        default=300,
        validation_alias="CELERY_TASK_RETRY_BACKOFF_MAX",
    )

    celery_task_retry_jitter: bool = Field(
        default=True,
        validation_alias="CELERY_TASK_RETRY_JITTER",
    )

    # ======================================
    # Configuración del modelo
    # ======================================

    model_config = SettingsConfigDict(
        env_file=".env",  # Archivo que contiene las variables
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignora variables no definidas en la clase
    )

    # ======================================
    # Seguridad avanzada
    # ======================================

    JWT_ISSUER: str = "medlab-platform"

    CORS_ORIGINS: str = ""

    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    ENABLE_DOCS: bool = True

    LOGIN_RATE_LIMIT: int = 5

    LOGIN_RATE_WINDOW_SECONDS: int = 60

    reports_dir: str = "/app/reports"


# Creamos una única instancia de configuración.
#
# Todo el proyecto importará este mismo objeto.

settings = Settings()

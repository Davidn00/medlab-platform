"""
Módulo de configuración de MedLab Platform.

Este archivo carga todas las variables definidas en el archivo .env
y las convierte en atributos de un objeto de configuración.

De esta forma evitamos utilizar variables globales dispersas
por todo el proyecto.

Autor: David
Proyecto: MedLab Platform
"""

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
    
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    
    # ======================================
    # Configuración del modelo
    # ======================================
    
    model_config = SettingsConfigDict(
        env_file=".env",          # Archivo que contiene las variables
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignora variables no definidas en la clase
    )
    
    reports_dir: str = "/app/reports"


# Creamos una única instancia de configuración.
#
# Todo el proyecto importará este mismo objeto.

settings = Settings()
"""
Módulo de conexión a la base de datos.

Este archivo crea el motor (engine) de SQLAlchemy y proporciona
las sesiones que utilizará toda la aplicación para comunicarse
con PostgreSQL.

Autor: David
Proyecto: MedLab Platform
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# ==========================================================
# Motor de conexión (Engine)
# ==========================================================
#
# El engine representa la conexión principal con PostgreSQL.
# SQLAlchemy administrará automáticamente un pool de conexiones.
#
engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # Muestra todas las consultas SQL en la terminal
)


# ==========================================================
# Fábrica de sesiones
# ==========================================================
#
# Cada operación sobre la base de datos utilizará una sesión.
#
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================================
# Dependencia para FastAPI
# ==========================================================
#
# Esta función abrirá una sesión para cada petición HTTP
# y la cerrará automáticamente cuando termine.
#
def get_db():
    """
    Proporciona una sesión de base de datos.

    Uso futuro:

        def endpoint(db: Session = Depends(get_db)):
            ...

    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
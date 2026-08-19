from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.config import settings

from app.db.base import Base
from app.models.user import User
from app.models.patient import Patient
from app.models.sample import Sample
from app.models.laboratory_test import LaboratoryTest
from app.models.audit_log import AuditLog


# ---------------------------------------------------------
# Configuración de Alembic
# ---------------------------------------------------------

config = context.config


# Configuración de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ---------------------------------------------------------
# Metadata de SQLAlchemy
# ---------------------------------------------------------
#
# Importamos User arriba para que SQLAlchemy registre
# la tabla "users" dentro de Base.metadata.
#

target_metadata = Base.metadata


# ---------------------------------------------------------
# Migraciones OFFLINE
# ---------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Ejecuta las migraciones en modo offline.

    En este modo no se crea una conexión real a PostgreSQL.
    """

    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# Migraciones ONLINE
# ---------------------------------------------------------

def run_migrations_online() -> None:
    """
    Ejecuta las migraciones conectándose realmente
    a PostgreSQL.
    """

    configuration = config.get_section(
        config.config_ini_section
    )

    # Utilizamos la misma URL definida en .env
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()
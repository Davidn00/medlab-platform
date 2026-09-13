
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

from app.core.logging import configure_logging
from app.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)

from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.laboratory import router as laboratory_router
from app.api.v1.patients import router as patients_router
from app.api.v1.samples import router as samples_router
from app.api.v1.laboratory_tests import router as laboratory_tests_router
from app.api.v1.reports import router as reports_router
from app.api.v1.audit import router as audit_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.biomedical_equipment import router as biomedical_equipment_router
from app.api.v1.calibration import router as calibration_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.health import router as health_router
from app.api.v1.metrics import router as metrics_router
from app.api.v2.router import router as api_v2_router
from app.api.v1.dashboard import router as dashboard_router


# Configurar logging
configure_logging()


# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)


# -------------------------------------------------------------------
# Configuración de seguridad
# -------------------------------------------------------------------

allowed_hosts = [
    host.strip()
    for host in settings.ALLOWED_HOSTS.split(",")
    if host.strip()
]

cors_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]


# Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


# -------------------------------------------------------------------
# Middleware de la aplicación
# -------------------------------------------------------------------

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# -------------------------------------------------------------------
# Endpoints generales
# -------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "MedLab Platform",
        "status": "Funcionando",
        "version": "1.0.0",
    }


@app.get("/health/db")
def database_health():
    """
    Verifica que PostgreSQL responde correctamente.
    """

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.scalar()

    return {
        "status": "ok",
        "database": "connected",
        "version": version,
    }


# -------------------------------------------------------------------
# Registrar routers
# -------------------------------------------------------------------

app.include_router(users_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(laboratory_router)
app.include_router(patients_router, prefix="/api/v1")
app.include_router(samples_router, prefix="/api/v1")
app.include_router(laboratory_tests_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(
    biomedical_equipment_router,
    prefix="/api/v1",
)
app.include_router(
    calibration_router,
    prefix="/api/v1",
)
app.include_router(
    notifications_router,
    prefix="/api/v1",
)
app.include_router(
    health_router,
)
app.include_router(
    metrics_router,
)
app.include_router(
    api_v2_router,
)
app.include_router(
    dashboard_router,
    prefix="/api/v1",
)
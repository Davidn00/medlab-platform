
from fastapi import FastAPI

from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.laboratory import router as laboratory_router
from app.api.v1.patients import router as patients_router
from app.api.v1.samples import router as samples_router
from app.api.v1.laboratory_tests import router as laboratory_tests_router
from app.api.v1.reports import router as reports_router
from app.api.v1.audit import router as audit_router
from app.api.v1.tasks import router as tasks_router

# ...

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


@app.get("/")
def root():
    return {"message": "MedLab Platform",
            "status": "Funcionando",
            "version": "1.0.0",
            }


@app.get("/health/db")
def database_health():
    """
    Verifica que PostgreSQL responde correctamente.
    """

    with engine.connect() as connection:

        result = connection.execute(text("SELECT version();"))

        version = result.scalar()

    return {
        "database": "connected",
        "version": version
    }



# Registrar routers
app.include_router(users_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(laboratory_router)
app.include_router(patients_router, prefix="/api/v1")
app.include_router(samples_router, prefix="/api/v1")
app.include_router(laboratory_tests_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
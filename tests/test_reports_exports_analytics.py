"""
Pruebas de Etapa 5.

Reportes
Exportaciones
Analytics
"""

from io import BytesIO

from app.db.session import SessionLocal
from app.services.export_service import ExportService

# ==========================================================
# ExportService - JSON
# ==========================================================


def test_export_service_json():
    db = SessionLocal()

    try:
        service = ExportService(db)

        content = service.to_json(
            [
                {
                    "id": "1",
                    "name": "Test",
                }
            ]
        )

        assert content
        assert b'"id": "1"' in content

    finally:
        db.close()


# ==========================================================
# ExportService - CSV
# ==========================================================


def test_export_service_csv():
    db = SessionLocal()

    try:
        service = ExportService(db)

        content = service.to_csv(
            [
                {
                    "id": "1",
                    "name": "Test",
                }
            ]
        )

        assert content
        assert b"id,name" in content

    finally:
        db.close()


# ==========================================================
# ExportService - XLSX
# ==========================================================


def test_export_service_xlsx():
    db = SessionLocal()

    try:
        service = ExportService(db)

        content = service.to_xlsx(
            [
                {
                    "id": "1",
                    "name": "Test",
                }
            ]
        )

        assert content

        workbook = BytesIO(content)

        assert workbook.getbuffer().nbytes > 0

    finally:
        db.close()


# ==========================================================
# ExportService - PDF
# ==========================================================


def test_export_service_pdf():
    db = SessionLocal()

    try:
        service = ExportService(db)

        content = service.to_pdf(
            [
                {
                    "id": "1",
                    "name": "Test",
                }
            ]
        )

        assert content
        assert content.startswith(b"%PDF")

    finally:
        db.close()


# ==========================================================
# Analytics - autenticación
# ==========================================================


def test_analytics_requires_authentication(client):
    response = client.get("/api/v1/analytics")

    assert response.status_code in (
        401,
        403,
    )


# ==========================================================
# Exports - autenticación
# ==========================================================


def test_export_requires_authentication(client):
    response = client.get("/api/v1/exports/patients")

    assert response.status_code in (
        401,
        403,
    )


# ==========================================================
# Sample PDF - autenticación
# ==========================================================


def test_sample_pdf_requires_authentication(client):
    response = client.get(
        "/api/v1/reports/sample/00000000-0000-0000-0000-000000000000/pdf"
    )

    assert response.status_code in (
        401,
        403,
    )

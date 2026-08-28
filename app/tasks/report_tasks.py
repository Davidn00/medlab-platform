"""
Tareas asíncronas relacionadas con reportes.

Autor: David
Proyecto: MedLab Platform
"""

from pathlib import Path
from uuid import UUID

from app.db.session import SessionLocal
from app.services.report_service import ReportService
from app.workers.celery_app import celery_app


# Directorio donde se almacenarán los reportes generados.
REPORTS_DIR = Path("reports")

# Crear el directorio si no existe.
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@celery_app.task(
    bind=True,
    name="medlab.tasks.generate_report",
)
def generate_report(
    self,
    sample_id: str,
) -> dict:
    """
    Genera de forma asíncrona el PDF correspondiente
    a una muestra de laboratorio.

    Parameters
    ----------
    sample_id:
        UUID de la muestra expresado como cadena.

    Returns
    -------
    dict
        Información sobre el reporte generado.
    """

    db = SessionLocal()

    try:
        sample_uuid = UUID(sample_id)

        service = ReportService(db)

        # Generar el PDF.
        pdf = service.generate_sample_report(sample_uuid)

        # Nombre del archivo.
        filename = f"sample_{sample_id}.pdf"

        # Ruta final del archivo.
        file_path = REPORTS_DIR / filename

        # Guardar el PDF.
        file_path.write_bytes(pdf)

        return {
            "sample_id": sample_id,
            "status": "generated",
            "pdf_size": len(pdf),
            "filename": filename,
            "file_path": str(file_path),
        }

    finally:
        db.close()


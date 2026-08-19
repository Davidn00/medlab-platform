"""
Servicio de generación de reportes clínicos en PDF.

Genera un documento PDF con la información del paciente,
la muestra y las pruebas de laboratorio asociadas.
"""

from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.repositories.sample_repository import SampleRepository


class ReportService:

    def __init__(self, db: Session):
        self.db = db
        self.sample_repository = SampleRepository(db)

    def generate_sample_report(
        self,
        sample_id: UUID,
    ) -> bytes:
        """
        Genera un PDF para una muestra específica.
        """

        sample = self.sample_repository.get_by_id(sample_id)

        if sample is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Muestra no encontrada.",
            )

        patient = sample.patient
        tests = sample.laboratory_tests

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=(21 * cm, 29.7 * cm),  # A4
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        # --------------------------------------------------
        # Encabezado
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>MEDLAB PLATFORM</b>",
                styles["Title"],
            )
        )

        story.append(
            Paragraph(
                "Clinical Laboratory Report",
                styles["Heading2"],
            )
        )

        story.append(Spacer(1, 0.5 * cm))

        # --------------------------------------------------
        # Datos del paciente
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>Patient Information</b>",
                styles["Heading3"],
            )
        )

        patient_data = [
            [
                "Name",
                f"{patient.first_name} {patient.last_name}",
            ],
            [
                "Medical Record",
                patient.medical_record,
            ],
            [
                "Date of Birth",
                patient.birth_date.isoformat(),
            ],
            [
                "Gender",
                patient.gender,
            ],
        ]

        patient_table = Table(
            patient_data,
            colWidths=[5 * cm, 10 * cm],
        )

        patient_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica",
                    ),
                ]
            )
        )

        story.append(patient_table)

        story.append(Spacer(1, 0.5 * cm))

        # --------------------------------------------------
        # Datos de la muestra
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>Sample Information</b>",
                styles["Heading3"],
            )
        )

        sample_data = [
            [
                "Sample Code",
                sample.sample_code,
            ],
            [
                "Type",
                sample.sample_type.value,
            ],
            [
                "Status",
                sample.status.value,
            ],
            [
                "Collected",
                sample.collected_at.strftime(
                    "%Y-%m-%d %H:%M UTC"
                ),
            ],
        ]

        sample_table = Table(
            sample_data,
            colWidths=[5 * cm, 10 * cm],
        )

        sample_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica",
                    ),
                ]
            )
        )

        story.append(sample_table)

        story.append(Spacer(1, 0.7 * cm))

        # --------------------------------------------------
        # Resultados
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b>Laboratory Results</b>",
                styles["Heading3"],
            )
        )

        table_data = [
            [
                "Test",
                "Result",
                "Unit",
                "Reference Range",
                "Status",
            ]
        ]

        for test in tests:
            table_data.append(
                [
                    test.test_name,
                    test.result_value or "-",
                    test.unit or "-",
                    test.reference_range or "-",
                    test.status.value,
                ]
            )

        results_table = Table(
            table_data,
            colWidths=[
                5 * cm,
                2.5 * cm,
                2.5 * cm,
                3.5 * cm,
                2.5 * cm,
            ],
        )

        results_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.darkblue,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (0, 1),
                        (-1, -1),
                        "Helvetica",
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, 0),
                        8,
                    ),
                ]
            )
        )

        story.append(results_table)

        story.append(Spacer(1, 1 * cm))

        # --------------------------------------------------
        # Firma
        # --------------------------------------------------

        story.append(
            Paragraph(
                "Validated by: ________________________________",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.3 * cm))

        generated = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        )

        story.append(
            Paragraph(
                f"Generated: {generated}",
                styles["Normal"],
            )
        )

        doc.build(story)

        pdf = buffer.getvalue()

        buffer.close()

        return pdf
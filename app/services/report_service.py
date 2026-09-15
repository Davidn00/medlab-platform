"""
Servicio de generación de reportes clínicos profesionales.
Genera un documento PDF con la información del paciente,
la muestra y las pruebas de laboratorio asociadas.

Autor: David
Proyecto: MedLab Platform
"""


from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from sqlalchemy.orm import Session

from app.repositories.sample_repository import SampleRepository
from app.repositories.audit_repository import AuditRepository

from app.models.calibration import Calibration
from app.models.biomedical_equipment import BiomedicalEquipment


class ReportService:
    """
    Servicio encargado de generar reportes clínicos.
    """

    def __init__(self, db: Session):
        self.db = db
        self.sample_repository = SampleRepository(db)
        self.audit_repository = AuditRepository(db)

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def _format_datetime(value) -> str:
        if value is None:
            return "-"

        return value.strftime(
            "%Y-%m-%d %H:%M UTC"
        )

    def _latest_calibration(
        self,
        equipment_id: UUID,
    ) -> Calibration | None:
        """
        Obtiene la calibración más reciente del equipo.
        """

        return (
            self.db.query(Calibration)
            .filter(
                Calibration.equipment_id
                == equipment_id
            )
            .order_by(
                Calibration.next_calibration_date.desc()
            )
            .first()
        )

    # ======================================================
    # Reporte principal
    # ======================================================

    def generate_sample_report(
        self,
        sample_id: UUID,
    ) -> bytes:
        """
        Genera un reporte PDF profesional para una muestra.

        Incluye:

        - paciente
        - muestra
        - pruebas
        - resultados
        - rangos de referencia
        - equipo
        - calibración
        - auditoría
        """

        sample = (
            self.sample_repository
            .get_by_id(sample_id)
        )

        if sample is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Muestra no encontrada.",
            )

        patient = sample.patient
        tests = sample.laboratory_tests

        # --------------------------------------------------
        # Auditoría
        # --------------------------------------------------

        audit_logs = (
            self.audit_repository
            .get_by_entity(
                "Sample",
                str(sample.id),
            )
        )

        for test in tests:
            audit_logs.extend(
                self.audit_repository
                .get_by_entity(
                    "LaboratoryTest",
                    str(test.id),
                )
            )

        audit_logs.sort(
            key=lambda item: item.created_at
        )

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=8,
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Heading2"],
            alignment=TA_CENTER,
            fontSize=11,
            spaceAfter=15,
        )

        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading3"],
            spaceBefore=10,
            spaceAfter=6,
        )

        small_style = ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontSize=8,
        )

        story = []

        # ==================================================
        # HEADER
        # ==================================================

        story.append(
            Paragraph(
                "MEDLAB PLATFORM",
                title_style,
            )
        )

        story.append(
            Paragraph(
                "Clinical Laboratory Report",
                subtitle_style,
            )
        )

        story.append(
            Paragraph(
                f"Report ID: {sample.id}",
                small_style,
            )
        )

        story.append(Spacer(1, 0.4 * cm))

        # ==================================================
        # PATIENT
        # ==================================================

        story.append(
            Paragraph(
                "Patient Information",
                section_style,
            )
        )

        patient_data = [
            ["Name", f"{patient.first_name} {patient.last_name}"],
            ["Medical Record", patient.medical_record],
            ["Date of Birth", patient.birth_date.isoformat()],
            ["Gender", patient.gender],
            ["Email", patient.email],
        ]

        patient_table = Table(
            patient_data,
            colWidths=[
                5 * cm,
                11 * cm,
            ],
        )

        patient_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )

        story.append(patient_table)

        # ==================================================
        # SAMPLE
        # ==================================================

        story.append(
            Paragraph(
                "Sample Information",
                section_style,
            )
        )

        sample_data = [
            ["Sample Code", sample.sample_code],
            ["Sample Type", sample.sample_type.value],
            ["Status", sample.status.value],
            [
                "Collected",
                self._format_datetime(
                    sample.collected_at
                ),
            ],
            [
                "Received",
                self._format_datetime(
                    sample.received_at
                ),
            ],
        ]

        sample_table = Table(
            sample_data,
            colWidths=[
                5 * cm,
                11 * cm,
            ],
        )

        sample_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )

        story.append(sample_table)

        # ==================================================
        # LABORATORY RESULTS
        # ==================================================

        story.append(
            Paragraph(
                "Laboratory Results",
                section_style,
            )
        )

        result_data = [
            [
                "Test",
                "Result",
                "Unit",
                "Reference",
                "Status",
            ]
        ]

        for test in tests:
            result_data.append(
                [
                    test.test_name,
                    test.result_value or "-",
                    test.unit or "-",
                    test.reference_range or "-",
                    test.status.value,
                ]
            )

        result_table = Table(
            result_data,
            colWidths=[
                4.4 * cm,
                2.7 * cm,
                2.1 * cm,
                4.0 * cm,
                2.5 * cm,
            ],
            repeatRows=1,
        )

        result_table.setStyle(
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
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                ]
            )
        )

        story.append(result_table)

        # ==================================================
        # EQUIPMENT AND CALIBRATION
        # ==================================================

        story.append(
            Paragraph(
                "Equipment and Calibration",
                section_style,
            )
        )

        equipment_data = [
            [
                "Equipment",
                "Manufacturer",
                "Model",
                "Serial",
                "Calibration",
            ]
        ]

        equipment_ids = set()

        for test in tests:
            if test.equipment is not None:
                equipment_ids.add(
                    test.equipment.id
                )

        for equipment_id in equipment_ids:
            equipment = (
                self.db.query(
                    BiomedicalEquipment
                )
                .filter(
                    BiomedicalEquipment.id == equipment_id
                )
                .first()
            )

            if equipment is None:
                continue

            calibration = self._latest_calibration(
                equipment.id
            )

            calibration_status = (
                calibration.status.value
                if calibration
                else "not_available"
            )

            equipment_data.append(
                [
                    equipment.name,
                    equipment.manufacturer,
                    equipment.model,
                    equipment.serial_number,
                    calibration_status,
                ]
            )

        if len(equipment_data) == 1:
            equipment_data.append(
                [
                    "No equipment assigned",
                    "-",
                    "-",
                    "-",
                    "-",
                ]
            )

        equipment_table = Table(
            equipment_data,
            colWidths=[
                4 * cm,
                3.5 * cm,
                3 * cm,
                3.5 * cm,
                3 * cm,
            ],
            repeatRows=1,
        )

        equipment_table.setStyle(
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
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                ]
            )
        )

        story.append(equipment_table)

        # ==================================================
        # AUDIT
        # ==================================================

        story.append(
            Paragraph(
                "Audit Information",
                section_style,
            )
        )

        audit_data = [
            [
                "Date",
                "Entity",
                "Action",
                "User",
                "Description",
            ]
        ]

        for log in audit_logs:
            user_name = (
                log.user.full_name
                if log.user
                else "System"
            )

            audit_data.append(
                [
                    self._format_datetime(
                        log.created_at
                    ),
                    log.entity_name,
                    log.action.value,
                    user_name,
                    log.description or "-",
                ]
            )

        if len(audit_data) == 1:
            audit_data.append(
                [
                    "-",
                    "-",
                    "-",
                    "-",
                    "No audit information available",
                ]
            )

        audit_table = Table(
            audit_data,
            colWidths=[
                3 * cm,
                3 * cm,
                2.5 * cm,
                3.5 * cm,
                5 * cm,
            ],
            repeatRows=1,
        )

        audit_table.setStyle(
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
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(audit_table)

        # ==================================================
        # FOOTER
        # ==================================================

        story.append(Spacer(1, 0.7 * cm))

        generated = datetime.now(
            timezone.utc
        )

        story.append(
            Paragraph(
                "Generated: "
                + generated.strftime(
                    "%Y-%m-%d %H:%M UTC"
                ),
                small_style,
            )
        )

        story.append(
            Paragraph(
                "MedLab Platform — Laboratory Information Management System",
                small_style,
            )
        )

        document.build(story)

        pdf = buffer.getvalue()

        buffer.close()

        return pdf
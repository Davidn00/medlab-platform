"""
Servicio de exportación de información.

Soporta:

- CSV
- Excel
- PDF
- JSON

Autor: David
Proyecto: MedLab Platform
"""

import csv
import json
from io import BytesIO, StringIO
from uuid import UUID

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.models.biomedical_equipment import (
    BiomedicalEquipment,
)
from app.models.calibration import Calibration
from app.models.laboratory_test import LaboratoryTest
from app.models.patient import Patient
from app.models.sample import Sample


class ExportService:
    """
    Servicio encargado de generar archivos de exportación.
    """

    def __init__(self, db: Session):
        self.db = db

    # ======================================================
    # Obtención de registros
    # ======================================================

    def get_records(
        self,
        resource: str,
        ids: list[UUID] | None = None,
    ) -> list[dict]:

        models = {
            "patients": Patient,
            "samples": Sample,
            "laboratory-tests": LaboratoryTest,
            "equipment": BiomedicalEquipment,
            "calibrations": Calibration,
        }

        model = models[resource]

        query = self.db.query(model)

        if ids:
            query = query.filter(model.id.in_(ids))

        records = query.all()

        return [
            self._serialize(
                resource,
                record,
            )
            for record in records
        ]

    # ======================================================
    # Serialización
    # ======================================================

    @staticmethod
    def _serialize(
        resource: str,
        record,
    ) -> dict:

        if resource == "patients":
            return {
                "id": str(record.id),
                "medical_record": record.medical_record,
                "first_name": record.first_name,
                "last_name": record.last_name,
                "birth_date": record.birth_date.isoformat(),
                "gender": record.gender,
                "email": record.email,
                "created_at": record.created_at.isoformat(),
            }

        if resource == "samples":
            return {
                "id": str(record.id),
                "sample_code": record.sample_code,
                "patient_id": str(record.patient_id),
                "sample_type": record.sample_type.value,
                "status": record.status.value,
                "collected_at": record.collected_at.isoformat(),
                "received_at": (
                    record.received_at.isoformat() if record.received_at else None
                ),
            }

        if resource == "laboratory-tests":
            return {
                "id": str(record.id),
                "sample_id": str(record.sample_id),
                "equipment_id": (
                    str(record.equipment_id) if record.equipment_id else None
                ),
                "test_name": record.test_name,
                "result_value": record.result_value,
                "unit": record.unit,
                "reference_range": record.reference_range,
                "comments": record.comments,
                "status": record.status.value,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
            }

        if resource == "equipment":
            return {
                "id": str(record.id),
                "name": record.name,
                "manufacturer": record.manufacturer,
                "model": record.model,
                "serial_number": record.serial_number,
                "location": record.location,
                "status": record.status.value,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
            }

        if resource == "calibrations":
            return {
                "id": str(record.id),
                "equipment_id": str(record.equipment_id),
                "calibration_date": (record.calibration_date.isoformat()),
                "next_calibration_date": (record.next_calibration_date.isoformat()),
                "performed_by": record.performed_by,
                "certificate_number": record.certificate_number,
                "status": record.status.value,
                "notes": record.notes,
                "created_at": record.created_at.isoformat(),
            }

        raise ValueError(f"Unsupported resource: {resource}")

    # ======================================================
    # JSON
    # ======================================================

    def to_json(
        self,
        records: list[dict],
    ) -> bytes:

        return json.dumps(
            records,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

    # ======================================================
    # CSV
    # ======================================================

    def to_csv(
        self,
        records: list[dict],
    ) -> bytes:

        if not records:
            return b""

        output = StringIO()

        fieldnames = list(records[0].keys())

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(records)

        return output.getvalue().encode("utf-8-sig")

    # ======================================================
    # Excel
    # ======================================================

    def to_xlsx(
        self,
        records: list[dict],
    ) -> bytes:

        workbook = Workbook()

        worksheet = workbook.active
        worksheet.title = "MedLab Export"

        if records:
            headers = list(records[0].keys())

            worksheet.append(headers)

            for record in records:
                worksheet.append([record.get(header) for header in headers])

            for column in worksheet.columns:
                max_length = 0

                column_letter = column[0].column_letter

                for cell in column:
                    value = str(cell.value) if cell.value is not None else ""

                    max_length = max(
                        max_length,
                        len(value),
                    )

                worksheet.column_dimensions[column_letter].width = min(
                    max_length + 2,
                    50,
                )

        buffer = BytesIO()

        workbook.save(buffer)

        return buffer.getvalue()

    # ======================================================
    # PDF
    # ======================================================

    def to_pdf(
        self,
        records: list[dict],
    ) -> bytes:

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        if not records:
            data = [["No records"]]

        else:
            headers = list(records[0].keys())

            data = [headers]

            for record in records:
                data.append(
                    [
                        str(
                            record.get(header) if record.get(header) is not None else ""
                        )
                        for header in headers
                    ]
                )

        table = Table(
            data,
            repeatRows=1,
        )

        table.setStyle(
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
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        7,
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

        document.build([table])

        return buffer.getvalue()

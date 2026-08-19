"""
Servicio de muestras.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sample import Sample, SampleStatus
from app.repositories.patient_repository import PatientRepository
from app.repositories.sample_repository import SampleRepository
from app.schemas.sample import SampleCreate, SampleUpdate
from app.models.audit_log import AuditAction
from app.services.audit_service import AuditService


class SampleService:

    def __init__(self, db: Session):
        self.repository = SampleRepository(db)
        self.patient_repository = PatientRepository(db)
        self.audit = AuditService(db)

    def create_sample(
        self,
        sample_data: SampleCreate,
        user_id: UUID,
    ) -> Sample:
        """
        Registra una nueva muestra.
        """

        patient = self.patient_repository.get_by_id(
            sample_data.patient_id
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado.",
            )

        existing = self.repository.get_by_code(
            sample_data.sample_code
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El código de muestra ya existe.",
            )

        sample = Sample(
            patient_id=sample_data.patient_id,
            sample_type=sample_data.sample_type,
            sample_code=sample_data.sample_code,
        )
        sample = self.repository.create(sample)

        self.audit.log(
            user_id=user_id,
            entity_name="Sample",
            entity_id=str(sample.id),
            action=AuditAction.CREATE,
            description=f"Sample {sample.sample_code} created",
        )
        return sample
    

    def get_sample(
        self,
        sample_id: UUID,
    ) -> Sample:

        sample = self.repository.get_by_id(sample_id)

        if sample is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Muestra no encontrada.",
            )

        return sample

    def get_samples(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Sample]:

        return self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    def get_samples_by_patient(
        self,
        patient_id: UUID,
    ) -> list[Sample]:

        return self.repository.get_by_patient(patient_id)

    def update_sample(
        self,
        sample_id: UUID,
        sample_data: SampleUpdate,
    ) -> Sample:

        sample = self.get_sample(sample_id)

        update_data = sample_data.model_dump(
            exclude_unset=True
        )

        # Si cambia a RECEIVED y no existe fecha,
        # registrar automáticamente la recepción.
        if (
            update_data.get("status") == SampleStatus.RECEIVED
            and sample.received_at is None
        ):
            update_data["received_at"] = datetime.now(
                timezone.utc
            )

        for field, value in update_data.items():
            setattr(sample, field, value)

        sample = self.repository.update(sample)
        self.audit.log(
            user_id=None,
            entity_name="Sample",
            entity_id=str(sample.id),
            action=AuditAction.UPDATE,
            description=f"Sample {sample.sample_code} updated",
        )
        return sample


    def delete_sample(
        self,
        sample_id: UUID,
    ) -> None:

        sample = self.get_sample(sample_id)

        self.repository.delete(sample)
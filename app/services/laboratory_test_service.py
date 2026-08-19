"""
Servicio de pruebas de laboratorio.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.laboratory_test import LaboratoryTest,LabTestStatus
from app.repositories.laboratory_test_repository import LaboratoryTestRepository
from app.repositories.sample_repository import SampleRepository
from app.schemas.laboratory_test import LaboratoryTestCreate, LaboratoryTestUpdate
from app.models.audit_log import AuditAction
from app.services.audit_service import AuditService



class LaboratoryTestService:

    def __init__(self, db: Session):
        self.repository = LaboratoryTestRepository(db)
        self.sample_repository = SampleRepository(db)
        self.audit = AuditService(db)

    def create_test(
        self,
        test_data: LaboratoryTestCreate,
        user_id: UUID,
    ) -> LaboratoryTest:
        """
        Registra una nueva prueba para una muestra.
        """

        sample = self.sample_repository.get_by_id(
            test_data.sample_id
        )

        if sample is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Muestra no encontrada.",
            )

        test = LaboratoryTest(
            sample_id=test_data.sample_id,
            test_name=test_data.test_name,
            unit=test_data.unit,
            reference_range=test_data.reference_range,
        )
        test = self.repository.create(test)

        self.audit.log(
            user_id=user_id,
            entity_name="LaboratoryTest",
            entity_id=str(test.id),
            action=AuditAction.CREATE,
            description=f"Test {test.test_name} created",
        )
        return test
  

    def get_test(
        self,
        test_id: UUID,
    ) -> LaboratoryTest:

        test = self.repository.get_by_id(test_id)

        if test is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prueba no encontrada.",
            )

        return test

    def get_tests_by_sample(
        self,
        sample_id: UUID,
    ) -> list[LaboratoryTest]:

        return self.repository.get_by_sample(sample_id)

    def update_test(
        self,
        test_id: UUID,
        test_data: LaboratoryTestUpdate,
         user_id: UUID,
    ) -> LaboratoryTest:
        """
        Actualiza una prueba.

        Si se registra un resultado y el estado era PENDING,
        cambia automáticamente a COMPLETED.
        """

        test = self.get_test(test_id)

        update_data = test_data.model_dump(
            exclude_unset=True
        )

        if (
            "result_value" in update_data
            and test.status == LabTestStatus.PENDING
        ):
            update_data["status"] = LabTestStatus.COMPLETED

        for field, value in update_data.items():
            setattr(test, field, value)

        test = self.repository.update(test)

        action = (
            AuditAction.VALIDATE
            if test.status == LabTestStatus.VALIDATED
            else AuditAction.UPDATE
        )

        self.audit.log(
            user_id=user_id,
            entity_name="LaboratoryTest",
            entity_id=str(test.id),
            action=action,
            description=f"Test {test.test_name} updated",
        )
        return test
        

    def delete_test(
        self,
        test_id: UUID,
    ) -> None:

        test = self.get_test(test_id)

        self.repository.delete(test)
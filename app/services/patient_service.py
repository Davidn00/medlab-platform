"""
Servicio de pacientes.

Esta capa contiene las reglas de negocio relacionadas
con pacientes.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientCreate, PatientUpdate
from app.models.audit_log import AuditAction
from app.services.audit_service import AuditService
from uuid import UUID



class PatientService:
    """
    Contiene la lógica de negocio de pacientes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = PatientRepository(db)
        self.audit = AuditService(db)

    def create_patient(
        self,
        patient_data: PatientCreate,
        user_id: UUID,
    ) -> Patient:
        """
        Crea un nuevo paciente.
        """

        existing_patient = (
            self.repository.get_by_medical_record(
                patient_data.medical_record
            )
        )

        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Ya existe un paciente con ese "
                    "número de expediente."
                ),
            )

        patient = Patient(
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            birth_date=patient_data.birth_date,
            gender=patient_data.gender,
            medical_record=patient_data.medical_record,
            email=patient_data.email,
        )

        patient = self.repository.create(patient)

        self.audit.log(
            user_id=user_id,  
            entity_name="Patient",
            entity_id=str(patient.id),
            action=AuditAction.CREATE,
            description=f"Patient {patient.medical_record} created",
        )

        return patient
    

    def get_patient(
        self,
        patient_id: UUID,
    ) -> Patient:
        """
        Obtiene un paciente por UUID.
        """

        patient = self.repository.get_by_id(patient_id)

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado.",
            )

        return patient

    def get_patients(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Patient]:
        """
        Obtiene una lista de pacientes.
        """

        return self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    def update_patient(
        self,
        patient_id: UUID,
        patient_data: PatientUpdate,
    ) -> Patient:
        """
        Actualiza un paciente.
        """

        patient = self.get_patient(patient_id)

        update_data = patient_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(patient, field, value)

        patient = self.repository.update(patient)

        self.audit.log(
            user_id=None,
            entity_name="Patient",
            entity_id=str(patient.id),
            action=AuditAction.UPDATE,
            description=f"Patient {patient.medical_record} updated",
        )

        return patient
        

    def delete_patient(
        self,
        patient_id: UUID,
    ) -> None:
        """
        Elimina un paciente.
        """

        patient = self.get_patient(patient_id)

        self.repository.delete(patient)

        self.audit.log(
            user_id=None,
            entity_name="Patient",
            entity_id=str(patient.id),
            action=AuditAction.DELETE,
            description=f"Patient {patient.medical_record} deleted",
        )
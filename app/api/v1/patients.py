"""
Endpoints REST para la gestión de pacientes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.patient import Patient
from app.models.user import UserRole
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.services.patient_service import PatientService
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                    UserRole.TECHNICIAN,
                ]
            )
        )
    ],
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea un nuevo paciente.

    Permitido para:
    - ADMIN
    - TECHNICIAN
    """

    service = PatientService(db)

    return service.create_patient(
        patient_data,
        current_user.id,
    )


@router.get(
    "",
    response_model=list[PatientResponse],
dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                    UserRole.TECHNICIAN,
                    UserRole.DOCTOR,
                ]
            )
        )
    ],
)
def list_patients(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista de pacientes.
    """

    service = PatientService(db)

    return service.get_patients(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                    UserRole.TECHNICIAN,
                    UserRole.DOCTOR,
                ]
            )
        )
    ],
)
def get_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtiene un paciente por UUID.
    """

    service = PatientService(db)

    return service.get_patient(patient_id)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                    UserRole.TECHNICIAN,
                ]
            )
        )
    ]
)
def update_patient(
    patient_id: UUID,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza parcialmente un paciente.
    """

    service = PatientService(db)

    return service.update_patient(
        patient_id,
        patient_data,
    )


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                ]
            )
        )
    ]
)
def delete_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Elimina un paciente.
    """

    service = PatientService(db)

    service.delete_patient(patient_id)

    return None
"""
Endpoints REST para la gestión de muestras.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.sample import SampleCreate, SampleResponse, SampleUpdate
from app.services.sample_service import SampleService
from app.api.deps import get_current_user


router = APIRouter(
    prefix="/samples",
    tags=["Samples"],
)


@router.post(
    "",
    response_model=SampleResponse,
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
def create_sample(
    sample_data: SampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SampleService(db)

    return service.create_sample(
        sample_data,
        current_user.id,
    )


@router.get(
    "",
    response_model=list[SampleResponse],
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
def list_samples(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = SampleService(db)

    return service.get_samples(skip=skip, limit=limit)


@router.get(
    "/{sample_id}",
    response_model=SampleResponse,
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
def get_sample(
    sample_id: UUID,
    db: Session = Depends(get_db),
):
    service = SampleService(db)

    return service.get_sample(sample_id)


@router.get(
    "/patient/{patient_id}",
    response_model=list[SampleResponse],
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
def get_samples_by_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
):
    service = SampleService(db)

    return service.get_samples_by_patient(patient_id)


@router.patch(
    "/{sample_id}",
    response_model=SampleResponse,
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
def update_sample(
    sample_id: UUID,
    sample_data: SampleUpdate,
    db: Session = Depends(get_db),
):
    service = SampleService(db)

    return service.update_sample(sample_id, sample_data)


@router.delete(
    "/{sample_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
            )
        )
    ],
)
def delete_sample(
    sample_id: UUID,
    db: Session = Depends(get_db),
):
    service = SampleService(db)

    service.delete_sample(sample_id)

    return None
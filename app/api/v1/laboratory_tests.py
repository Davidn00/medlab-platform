"""
Endpoints REST para pruebas de laboratorio.
"""

from uuid import UUID


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import UserRole, User 
from app.schemas.laboratory_test import LaboratoryTestCreate, LaboratoryTestResponse, LaboratoryTestUpdate
from app.services.laboratory_test_service import LaboratoryTestService

from app.api.deps import get_current_user


router = APIRouter(
    prefix="/laboratory-tests",
    tags=["Laboratory Tests"],
)


@router.post(
    "",
    response_model=LaboratoryTestResponse,
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
def create_test(
    test_data: LaboratoryTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LaboratoryTestService(db)

    return service.create_test(test_data, current_user.id)


@router.get(
    "/{test_id}",
    response_model=LaboratoryTestResponse,
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
def get_test(
    test_id: UUID,
    db: Session = Depends(get_db),
):
    service = LaboratoryTestService(db)

    return service.get_test(test_id)


@router.get(
    "/sample/{sample_id}",
    response_model=list[LaboratoryTestResponse],
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
def get_tests_by_sample(
    sample_id: UUID,
    db: Session = Depends(get_db),
):
    service = LaboratoryTestService(db)

    return service.get_tests_by_sample(sample_id)


@router.patch(
    "/{test_id}",
    response_model=LaboratoryTestResponse,
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
def update_test(
    test_id: UUID,
    test_data: LaboratoryTestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LaboratoryTestService(db)

    return service.update_test(
        test_id,
        test_data,
        current_user.id, 
    )


@router.delete(
    "/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            require_roles(
                [
                    UserRole.ADMIN,
                ]
            )   
        )
    ],
)
def delete_test(
    test_id: UUID,
    db: Session = Depends(get_db),
):
    service = LaboratoryTestService(db)

    service.delete_test(test_id)

    return None
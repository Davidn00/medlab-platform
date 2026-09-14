"""
Endpoints v2 para ciclo de vida de equipos.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    EquipmentNotFoundError,
    InvalidEquipmentStatusTransitionError,
)
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.biomedical_equipment import EquipmentStatus
from app.models.equipment_lifecycle_event import (
    EquipmentEventType,
)
from app.models.user import User, UserRole
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.equipment_lifecycle_repository import (
    EquipmentLifecycleRepository,
)
from app.schemas.biomedical_equipment import (
    BiomedicalEquipmentResponse,
)
from app.services.equipment_lifecycle_service import (
    EquipmentLifecycleService,
)
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/equipment",
    tags=["Equipment Lifecycle v2"],
)


class EquipmentStatusUpdate(BaseModel):
    status: EquipmentStatus


class LifecycleEventCreate(BaseModel):

    event_type: EquipmentEventType

    description: str = Field(
        ...,
        min_length=1,
    )

    performed_by: str | None = None

    reference_id: UUID | None = None


def get_lifecycle_service(
    db: Session = Depends(get_db),
) -> EquipmentLifecycleService:

    return EquipmentLifecycleService(
        db=db,
        equipment_repository=(
            BiomedicalEquipmentRepository(db)
        ),
        lifecycle_repository=(
            EquipmentLifecycleRepository(db)
        ),
    )


@router.patch(
    "/{equipment_id}/status",
    response_model=BiomedicalEquipmentResponse,
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
def change_equipment_status(
    equipment_id: UUID,
    data: EquipmentStatusUpdate,
    service: EquipmentLifecycleService = Depends(
        get_lifecycle_service
    ),
    current_user: User = Depends(get_current_user),
):

    try:
        return service.change_status(
            equipment_id=equipment_id,
            new_status=data.status,
            user_id=current_user.id,
        )

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except InvalidEquipmentStatusTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/{equipment_id}/lifecycle-events",
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
def create_lifecycle_event(
    equipment_id: UUID,
    data: LifecycleEventCreate,
    service: EquipmentLifecycleService = Depends(
        get_lifecycle_service
    ),
    current_user: User = Depends(get_current_user),
):

    try:
        return service.record_event(
            equipment_id=equipment_id,
            event_type=data.event_type,
            description=data.description,
            performed_by=data.performed_by,
            reference_id=data.reference_id,
            user_id=current_user.id,
        )

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{equipment_id}/lifecycle",
)
def get_equipment_lifecycle(
    equipment_id: UUID,
    service: EquipmentLifecycleService = Depends(
        get_lifecycle_service
    ),
    _: User = Depends(get_current_user),
):

    try:
        return service.get_history(
            equipment_id
        )

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
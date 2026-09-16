"""
Endpoints v2 de mantenimiento.

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
from app.core.exceptions import EquipmentNotFoundError
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.maintenance import MaintenanceStatus
from app.models.user import User, UserRole
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.equipment_lifecycle_repository import (
    EquipmentLifecycleRepository,
)
from app.repositories.maintenance_record_repository import (
    MaintenanceRecordRepository,
)
from app.repositories.maintenance_repository import (
    MaintenanceRepository,
)
from app.repositories.maintenance_schedule_repository import (
    MaintenanceScheduleRepository,
)
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceResponse,
)
from app.schemas.maintenance_record import (
    MaintenanceRecordCreate,
    MaintenanceRecordResponse,
)
from app.schemas.maintenance_schedule import (
    MaintenanceScheduleCreate,
    MaintenanceScheduleResponse,
)
from app.services.maintenance_schedule_service import (
    MaintenanceScheduleService,
)
from app.services.maintenance_service import (
    MaintenanceService,
)

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance v2"],
)


def get_maintenance_service(
    db: Session = Depends(get_db),
) -> MaintenanceService:

    return MaintenanceService(
        db=db,
        maintenance_repository=(MaintenanceRepository(db)),
        record_repository=(MaintenanceRecordRepository(db)),
        equipment_repository=(BiomedicalEquipmentRepository(db)),
        lifecycle_repository=(EquipmentLifecycleRepository(db)),
    )


@router.post(
    "",
    response_model=MaintenanceResponse,
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
def create_maintenance(
    data: MaintenanceCreate,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_user),
):

    try:
        return service.create(
            equipment_id=data.equipment_id,
            title=data.title,
            maintenance_type=data.maintenance_type,
            status=data.status,
            scheduled_date=data.scheduled_date,
            description=data.description,
            assigned_to=data.assigned_to,
            user_id=current_user.id,
        )

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[MaintenanceResponse],
)
def get_maintenance(
    service: MaintenanceService = Depends(get_maintenance_service),
    _: User = Depends(get_current_user),
):

    return service.get_all()


@router.get(
    "/equipment/{equipment_id}",
    response_model=list[MaintenanceResponse],
)
def get_equipment_maintenance(
    equipment_id: UUID,
    service: MaintenanceService = Depends(get_maintenance_service),
    _: User = Depends(get_current_user),
):

    try:
        return service.get_by_equipment_id(equipment_id)

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{maintenance_id}/status",
    response_model=MaintenanceResponse,
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
def update_maintenance_status(
    maintenance_id: UUID,
    new_status: MaintenanceStatus,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_user),
):

    try:
        result = service.update_status(
            maintenance_id=maintenance_id,
            new_status=new_status,
            user_id=current_user.id,
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mantenimiento no encontrado.",
            )

        return result

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/records",
    response_model=MaintenanceRecordResponse,
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
def create_maintenance_record(
    data: MaintenanceRecordCreate,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_user),
):

    try:
        return service.create_record(
            maintenance_id=data.maintenance_id,
            equipment_id=data.equipment_id,
            performed_at=data.performed_at,
            performed_by=data.performed_by,
            action=data.action,
            findings=data.findings,
            parts_replaced=data.parts_replaced,
            notes=data.notes,
            user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/records/{maintenance_id}",
    response_model=list[MaintenanceRecordResponse],
)
def get_maintenance_records(
    maintenance_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):

    repository = MaintenanceRecordRepository(db)

    return repository.get_by_maintenance_id(maintenance_id)


def get_schedule_service(
    db: Session = Depends(get_db),
) -> MaintenanceScheduleService:

    return MaintenanceScheduleService(
        db=db,
        repository=MaintenanceScheduleRepository(db),
        equipment_repository=(BiomedicalEquipmentRepository(db)),
    )


@router.post(
    "/schedules",
    response_model=MaintenanceScheduleResponse,
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
def create_maintenance_schedule(
    data: MaintenanceScheduleCreate,
    service: MaintenanceScheduleService = Depends(get_schedule_service),
):

    try:
        return service.create(
            equipment_id=data.equipment_id,
            name=data.name,
            maintenance_type=data.maintenance_type,
            frequency_days=data.frequency_days,
            next_due_date=data.next_due_date,
            description=data.description,
        )

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/schedules/equipment/{equipment_id}",
    response_model=list[MaintenanceScheduleResponse],
)
def get_maintenance_schedules(
    equipment_id: UUID,
    service: MaintenanceScheduleService = Depends(get_schedule_service),
):

    try:
        return service.get_by_equipment_id(equipment_id)

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

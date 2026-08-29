"""
Router para calibraciones.

Autor: David
Proyecto: MedLab Platform
"""

    
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.calibration_repository import (
    CalibrationRepository,
)
from app.schemas.calibration import (
    CalibrationCreate,
    CalibrationResponse,
    CalibrationUpdate,
)

from app.services.calibration_service import (
    CalibrationService,
)


router = APIRouter(
    prefix="/calibrations",
    tags=["Calibrations"],
)


def get_calibration_service(
    db: Session = Depends(get_db),
) -> CalibrationService:
    """
    Construye el Service de calibraciones.
    """

    calibration_repository = CalibrationRepository(db)

    equipment_repository = BiomedicalEquipmentRepository(db)

    return CalibrationService(
        calibration_repository=calibration_repository,
        equipment_repository=equipment_repository,
    )


@router.post(
    "",
    response_model=CalibrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_calibration(
    data: CalibrationCreate,
    service: CalibrationService = Depends(
        get_calibration_service
    ),
):
    """
    Registra una nueva calibración.
    """

    try:
        return service.create(data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[CalibrationResponse],
)
def get_calibrations(
    service: CalibrationService = Depends(
        get_calibration_service
    ),
):
    """
    Obtiene todas las calibraciones.
    """

    return service.get_all()


@router.get(
    "/expiring",
    response_model=list[CalibrationResponse],
)
def get_expiring_calibrations(
    days: int = 30,
    service: CalibrationService = Depends(
        get_calibration_service
    ),
):
    """
    Obtiene calibraciones próximas a vencer.

    Por defecto se consideran los próximos 30 días.
    """

    try:
        return service.get_expiring_calibrations(days)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/expired",
    response_model=list[CalibrationResponse],
)
def get_expired_calibrations(
    service: CalibrationService = Depends(
        get_calibration_service
    ),
):
    """
    Obtiene calibraciones vencidas.
    """

    return service.get_expired_calibrations()


@router.get(
    "/{calibration_id}",
    response_model=CalibrationResponse,
)
def get_calibration_by_id(
    calibration_id: UUID,
    service: CalibrationService = Depends(
        get_calibration_service
    ),
):
    """
    Obtiene una calibración por UUID.
    """

    calibration = service.get_by_id(
        calibration_id
    )

    if calibration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibración no encontrada.",
        )

    return calibration


@router.put(
    "/{calibration_id}",
    response_model=CalibrationResponse,
)
def update_calibration(
    calibration_id: UUID,
    data: CalibrationUpdate,
    service: CalibrationService = Depends(
        get_calibration_service
    ),
):
    """
    Actualiza una calibración.
    """

    try:
        calibration = service.update(
            calibration_id,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if calibration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibración no encontrada.",
        )

    return calibration


@router.delete(
    "/{calibration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_calibration(
    calibration_id: UUID,
    service: CalibrationService = Depends(
        get_calibration_service
    ),
):
    """
    Elimina una calibración.
    """

    deleted = service.delete(calibration_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibración no encontrada.",
        )

    return None
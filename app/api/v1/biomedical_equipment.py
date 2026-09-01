"""
Router para equipos biomédicos.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exc
from sqlalchemy.orm import Session
from app.core.exceptions import EquipmentNotFoundError
from app.core.exceptions import EquipmentNotFoundError

from app.db.session import get_db
from app.repositories.biomedical_equipment_repository import (
    BiomedicalEquipmentRepository,
)
from app.repositories.calibration_repository import (
    CalibrationRepository,
)
from app.schemas.biomedical_equipment import (
    BiomedicalEquipmentCreate,
    BiomedicalEquipmentResponse,
    BiomedicalEquipmentUpdate,
)
from app.core.exceptions import (
    EquipmentAlreadyExistsError,
    EquipmentHasCalibrationsError,
    EquipmentNotFoundError,
)
from app.services.biomedical_equipment_service import BiomedicalEquipmentService
from app.services.calibration_service import CalibrationService
from app.repositories.calibration_repository import CalibrationRepository
from app.schemas.calibration import CalibrationResponse


router = APIRouter(
    prefix="/equipment",
    tags=["Biomedical Equipment"],
)


def get_equipment_service(
    db: Session = Depends(get_db),
) -> BiomedicalEquipmentService:
    """
    Construye el Service de equipos biomédicos
    utilizando la sesión de base de datos.
    """

    equipment_repository = BiomedicalEquipmentRepository(db)
    calibration_repository = CalibrationRepository(db)

    return BiomedicalEquipmentService(
        equipment_repository=equipment_repository,
        calibration_repository=calibration_repository
    )


@router.post(
    "",
    response_model=BiomedicalEquipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_equipment(
    data: BiomedicalEquipmentCreate,
    service: BiomedicalEquipmentService = Depends(
        get_equipment_service
    ),
):
    """
    Registra un nuevo equipo biomédico.
    """

    try:
        return service.create(data)

    except EquipmentAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[BiomedicalEquipmentResponse],
)
def get_equipment(
    service: BiomedicalEquipmentService = Depends(
        get_equipment_service
    ),
):
    """
    Obtiene todos los equipos biomédicos.
    """

    return service.get_all()


@router.get(
    "/{equipment_id}",
    response_model=BiomedicalEquipmentResponse,
)
def get_equipment_by_id(
    equipment_id: UUID,
    service: BiomedicalEquipmentService = Depends(
        get_equipment_service
    ),
):
    """
    Obtiene un equipo por UUID.
    """

    equipment = service.get_by_id(equipment_id)

    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo biomédico no encontrado.",
        )

    return equipment


@router.put(
    "/{equipment_id}",
    response_model=BiomedicalEquipmentResponse,
)
def update_equipment(
    equipment_id: UUID,
    data: BiomedicalEquipmentUpdate,
    service: BiomedicalEquipmentService = Depends(
        get_equipment_service
    ),
):
    """
    Actualiza un equipo biomédico.
    """

    try:
        equipment = service.update(
            equipment_id,
            data,
        )

    except EquipmentNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo biomédico no encontrado.",
            ) from exc
    
    except EquipmentAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

   
    return equipment


@router.delete(
    "/{equipment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_equipment(
    equipment_id: UUID,
    service: BiomedicalEquipmentService = Depends(
        get_equipment_service
    ),
):
    """
    Elimina un equipo biomédico.
    """

    try:
        service.delete(equipment_id)

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo biomédico no encontrado.",
        ) from exc

    except EquipmentHasCalibrationsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El equipo biomédico tiene calibraciones asociadas.",
        ) from exc

@router.get(
    "/{equipment_id}/calibrations",
    response_model=list[CalibrationResponse],
)
def get_equipment_calibrations(
    equipment_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtiene las calibraciones asociadas
    a un equipo biomédico.
    """

    equipment_repository = BiomedicalEquipmentRepository(
        db
    )

    calibration_repository = CalibrationRepository(
        db
    )

    service = CalibrationService(
        calibration_repository=calibration_repository,
        equipment_repository=equipment_repository,
    )

    try:
        return service.get_by_equipment_id(
            equipment_id
        )

    except EquipmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
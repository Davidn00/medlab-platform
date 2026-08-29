"""
Servicio para procesamiento y validación de resultados
de pruebas de laboratorio.

Autor: David
Proyecto: MedLab Platform
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.laboratory_test import LaboratoryTest


class LaboratoryResultService:
    """
    Contiene la lógica de negocio relacionada con
    resultados de pruebas de laboratorio.
    """

    def __init__(self, db: Session):
        self.db = db

    def process_result(
        self,
        test_id: UUID,
    ) -> LaboratoryTest:
        """
        Valida y procesa el resultado de una prueba.

        Parameters
        ----------
        test_id:
            UUID de la prueba de laboratorio.

        Returns
        -------
        LaboratoryTest
            Prueba actualizada.

        Raises
        ------
        ValueError
            Si la prueba no existe o no tiene resultado.
        """

        test = (
            self.db.query(LaboratoryTest)
            .filter(LaboratoryTest.id == test_id)
            .first()
        )

        if test is None:
            raise ValueError(
                f"LaboratoryTest {test_id} no encontrado."
            )

        if test.result_value is None:
            raise ValueError(
                "La prueba no tiene un resultado para procesar."
            )

        if not str(test.result_value).strip():
            raise ValueError(
                "El resultado de la prueba está vacío."
            )

        test.status = "COMPLETED"

        self.db.commit()
        self.db.refresh(test)

        return test
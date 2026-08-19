"""
Servicio de usuarios.

Contiene la lógica de negocio relacionada con usuarios.

Autor: David
Proyecto: MedLab Platform
"""

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    """
    Lógica de negocio de usuarios.
    """

    def __init__(self):
        self.repository = UserRepository()

    # ------------------------------------------------------
    # Crear usuario
    # ------------------------------------------------------

    def create_user(self, db: Session, user_data: UserCreate):
        """
        Crea un nuevo usuario.

        Por ahora almacenaremos la contraseña tal como llega.
        En la siguiente parte implementaremos hashing.
        """

        existing = self.repository.get_by_email(db, user_data.email)

        if existing:
            raise ValueError("Ya existe un usuario con ese email")

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
           hashed_password=hash_password(user_data.password),
            role=user_data.role,
        )

        return self.repository.create(db, user)

    # ------------------------------------------------------
    # Obtener usuario
    # ------------------------------------------------------

    def get_user(self, db: Session, user_id):
        return self.repository.get_by_id(db, user_id)

    # ------------------------------------------------------
    # Listar usuarios
    # ------------------------------------------------------

    def get_users(self, db: Session):
        return self.repository.get_all(db)
"""
Repositorio de usuarios.

Esta capa contiene exclusivamente operaciones relacionadas
con la base de datos.

Autor: David
Proyecto: MedLab Platform
"""

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Operaciones CRUD sobre la tabla users.
    """

    # ------------------------------------------------------
    # Obtener por ID
    # ------------------------------------------------------

    def get_by_id(self, db: Session, user_id):
        return db.get(User, user_id)

    # ------------------------------------------------------
    # Obtener por email
    # ------------------------------------------------------

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    # ------------------------------------------------------
    # Listar usuarios
    # ------------------------------------------------------

    def get_all(self, db: Session):
        return db.query(User).all()

    # ------------------------------------------------------
    # Crear usuario
    # ------------------------------------------------------

    def create(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # ------------------------------------------------------
    # Actualizar usuario
    # ------------------------------------------------------

    def update(self, db: Session, user: User):
        db.commit()
        db.refresh(user)
        return user

    # ------------------------------------------------------
    # Eliminar usuario
    # ------------------------------------------------------

    def delete(self, db: Session, user: User):
        db.delete(user)
        db.commit()
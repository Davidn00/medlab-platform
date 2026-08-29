"""
Datos iniciales de MedLab Platform.

Crea los usuarios necesarios para iniciar el sistema.

Autor: David
Proyecto: MedLab Platform
"""

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole


def seed_admin() -> None:
    """
    Crea el usuario administrador si todavía no existe.
    """

    db = SessionLocal()

    try:
        existing_admin = (
            db.query(User)
            .filter(User.email == settings.ADMIN_EMAIL)
            .first()
        )

        if existing_admin:
            print(
                f"El usuario administrador ya existe: "
                f"{settings.ADMIN_EMAIL}"
            )
            return

        admin = User(
            full_name=settings.ADMIN_FULL_NAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(
                settings.ADMIN_PASSWORD
            ),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(
            f"Usuario administrador creado correctamente: "
            f"{settings.ADMIN_EMAIL}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
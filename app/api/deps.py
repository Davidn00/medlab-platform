"""
Dependencias compartidas de FastAPI.
"""

from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

repository = UserRepository()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Obtiene el usuario autenticado a partir del JWT.
    """

    try:
        payload = decode_access_token(token)

        user_id = UUID(payload["sub"])

    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = repository.get_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user
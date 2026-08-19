"""
Endpoints de autenticación.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token


router = APIRouter(prefix="/auth", tags=["Authentication"])

repository = UserRepository()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login mediante email y contraseña.
    """

    user = repository.get_by_email(db, form_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(str(user.id))

    return Token(access_token=token)
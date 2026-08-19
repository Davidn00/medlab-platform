"""
Funciones de seguridad de MedLab Platform.

Este módulo implementa:

- Hashing de contraseñas
- Verificación de contraseñas
- Generación de JWT
- Decodificación de JWT
"""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


# ==========================================================
# Argon2
# ==========================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Genera un hash seguro usando Argon2.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    """
    return password_hash.verify(password, hashed_password)


# ==========================================================
# JWT
# ==========================================================

ALGORITHM = "HS256"


def create_access_token(subject: str) -> str:
    """
    Crea un token JWT para un usuario.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str):
    """
    Decodifica un token JWT.
    """

    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
    )
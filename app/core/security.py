"""
Funciones de seguridad de MedLab Platform.

Este módulo implementa:

- Hashing de contraseñas
- Verificación de contraseñas
- Generación de JWT
- Decodificación de JWT
"""

import re
from datetime import UTC, datetime, timedelta

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
    Crea un JWT firmado para un usuario.
    """

    now = datetime.now(UTC)

    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str):
    """
    Valida y decodifica un JWT.
    """

    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer=settings.JWT_ISSUER,
        options={
            "require": [
                "sub",
                "iat",
                "exp",
                "iss",
            ]
        },
    )


def validate_password_strength(password: str) -> None:
    """
    Valida la fortaleza mínima de una contraseña.

    Requisitos:

    - mínimo 12 caracteres
    - mayúscula
    - minúscula
    - número
    - carácter especial
    """

    if len(password) < 12:
        raise ValueError("La contraseña debe tener al menos 12 caracteres.")

    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe contener al menos una mayúscula.")

    if not re.search(r"[a-z]", password):
        raise ValueError("La contraseña debe contener al menos una minúscula.")

    if not re.search(r"\d", password):
        raise ValueError("La contraseña debe contener al menos un número.")

    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("La contraseña debe contener al menos un carácter especial.")

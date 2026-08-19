"""
Esquemas relacionados con autenticación JWT.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """
    Respuesta devuelta por /auth/login
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Contenido interno del JWT.
    """

    sub: str
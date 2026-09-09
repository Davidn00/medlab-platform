import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    validate_password_strength,
    verify_password,
)


def test_password_hash_and_verify():
    password = "StrongPassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password(
        "WrongPassword123!",
        hashed,
    )


def test_password_policy_accepts_strong_password():
    validate_password_strength(
        "StrongPassword123!"
    )


@pytest.mark.parametrize(
    "password",
    [
        "short",
        "alllowercase123!",
        "ALLUPPERCASE123!",
        "NoNumbers!!!!!!",
        "NoSpecial123456",
    ],
)
def test_password_policy_rejects_weak_password(password):
    with pytest.raises(ValueError):
        validate_password_strength(password)


def test_jwt_contains_required_claims():
    token = create_access_token(
        "00000000-0000-0000-0000-000000000001"
    )

    payload = decode_access_token(token)

    assert payload["sub"]
    assert payload["iat"]
    assert payload["exp"]
    assert payload["iss"]
    assert payload["type"] == "access"
import bcrypt

from core.config import settings


def hash_password(password: str) -> bytes:
    salt: bytes = bcrypt.gensalt()
    password_bytes = password.encode()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password


def verify_password(password: str, correct_password: bytes) -> bool:
    password_bytes = password.encode()
    return bcrypt.checkpw(password_bytes, correct_password)


def validate_token_type(token_payload: dict, expected_type: str) -> bool:
    token_type = token_payload.get(settings.jwt_auth.token_type_payload_key)
    return token_type == expected_type

import secrets
from io import BytesIO
from pathlib import Path

import bcrypt
from PIL import Image
from fastapi import UploadFile

from core.config import settings


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password_bytes = password.encode()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password


def verify_password(password: str, correct_password: bytes) -> bool:
    password_bytes = password.encode()
    return bcrypt.checkpw(password_bytes, correct_password)


def validate_token_type(token_payload: dict, expected_type: str) -> bool:
    token_type = token_payload.get(settings.jwt_auth.token_type_payload_key)
    return token_type == expected_type


def generate_email_token(length: int = settings.email_tokens.token_length) -> str:
    email_verification_token = "".join(secrets.choice(settings.email_tokens.token_symbols) for _ in range(length)) # fmt: skip
    return email_verification_token


def validate_avatar_extension(avatar: UploadFile) -> bool:
    avatar_extension = Path(avatar.filename).suffix.lower()
    return avatar_extension in settings.avatar.allowed_extensions_to_mime.keys()


async def validate_avatar_size(avatar: UploadFile) -> bool:
    content = await avatar.read()
    image = Image.open(BytesIO(content))
    await avatar.seek(0)
    return image.size == settings.avatar.size

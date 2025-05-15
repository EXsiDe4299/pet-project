import datetime

import jwt

from core.config import settings
from core.models import User


def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt_auth.private_key_path.read_text(),
    algorithm: str = settings.jwt_auth.algorithm,
    expire_minutes: int = settings.jwt_auth.access_token_expire_minutes,
) -> str:
    to_encode = payload.copy()
    now = datetime.datetime.now(datetime.UTC)
    expire = now + datetime.timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.jwt_auth.public_key_path.read_text(),
    algorithm: str = settings.jwt_auth.algorithm,
) -> dict:
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int,
) -> str:
    payload = {settings.jwt_auth.token_type_payload_key: token_type}
    payload.update(token_data)
    return encode_jwt(
        payload=payload,
        expire_minutes=expire_minutes,
    )


def create_access_token(user: User):
    access_token_payload = {
        "sub": user.username,
        "username": user.username,
    }
    return create_jwt(
        token_type=settings.jwt_auth.access_token_type,
        token_data=access_token_payload,
        expire_minutes=settings.jwt_auth.access_token_expire_minutes,
    )


def create_refresh_token(user: User):
    refresh_token_payload = {
        "sub": user.username,
    }
    return create_jwt(
        token_type=settings.jwt_auth.refresh_token_type,
        token_data=refresh_token_payload,
        expire_minutes=settings.jwt_auth.refresh_token_expire_minutes,
    )

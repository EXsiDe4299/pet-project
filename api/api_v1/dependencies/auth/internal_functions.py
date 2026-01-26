from jwt import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.exceptions.http_exceptions import (
    InvalidJWT,
    InvalidJWTType,
    InactiveUser,
    InvalidEmail,
)
from api.api_v1.utils.cache import is_token_in_blacklist
from api.api_v1.utils.database import get_user_by_username_or_email
from api.api_v1.utils.jwt_auth import decode_jwt
from api.api_v1.utils.security import validate_token_type
from core.models import User


async def _validate_and_decode_token(
    token: str,
    token_type: str,
    cache: Redis,
) -> dict:
    try:
        token_payload = decode_jwt(token=token)
    except InvalidTokenError:
        raise InvalidJWT()
    if not validate_token_type(token_payload=token_payload, expected_type=token_type):
        raise InvalidJWTType()

    jti = token_payload.get("jti")
    if jti is None or await is_token_in_blacklist(jti=jti, cache=cache):
        raise InvalidJWT()

    return token_payload


async def _get_user_from_token(
    token: str,
    token_type: str,
    session: AsyncSession,
    cache: Redis,
) -> User:
    token_payload = await _validate_and_decode_token(
        token=token,
        token_type=token_type,
        cache=cache,
    )
    email = token_payload.get("sub")
    if email is None:
        raise InvalidJWT()

    user = await get_user_by_username_or_email(email=email, session=session)
    if user is None:
        raise InvalidJWT()

    if not user.is_active:
        raise InactiveUser()
    if not user.is_email_verified:
        raise InvalidEmail()

    return user

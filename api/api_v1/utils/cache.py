from api.api_v1.dependencies.log_helper import LogHelper
from api.api_v1.exceptions.http_exceptions import InvalidJWT
from redis.asyncio import Redis

logger = LogHelper.get_app_logger()


async def add_token_to_blacklist(
    payload: dict,
    cache: Redis,
) -> None:
    sub = payload.get("sub")
    jti = payload.get("jti")
    exp = payload.get("exp")

    logger.debug(
        "Adding JWT to blacklist. Sub=%r, JTI=%r",
        sub,
        jti,
    )

    if jti is None or exp is None:
        logger.warning(
            "Adding JWT to blacklist failed. Token missing JTI or EXP. Sub=%r, Payload keys=%s",
            sub,
            payload.keys(),
        )
        raise InvalidJWT()
    await cache.set(name=jti, value="", exat=exp)
    logger.debug(
        "JWT added to blacklist successfully. Sub=%r, JTI=%r",
        sub,
        jti,
    )


async def is_token_in_blacklist(jti: str, cache: Redis) -> bool:
    jti = await cache.get(jti)
    return True if jti is not None else False

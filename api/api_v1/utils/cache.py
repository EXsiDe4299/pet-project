import datetime

from redis.asyncio import Redis


async def add_token_to_blacklist(
    payload: dict,
    cache: Redis,
) -> None:
    jti = payload.get("jti")
    now = int(datetime.datetime.now(datetime.UTC).timestamp())
    exp = payload.get("exp")
    ex = exp - now
    await cache.set(name=jti, value="", ex=ex)


async def is_token_in_blacklist(jti: str, cache: Redis) -> bool:
    jti = await cache.get(jti)
    return True if jti is not None else False

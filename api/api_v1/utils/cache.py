from redis.asyncio import Redis


async def add_token_to_blacklist(
    payload: dict,
    cache: Redis,
) -> None:
    jti = payload.get("jti")
    exp = payload.get("exp")
    await cache.set(name=jti, value="", exat=exp)


async def is_token_in_blacklist(jti: str, cache: Redis) -> bool:
    jti = await cache.get(jti)
    return True if jti is not None else False

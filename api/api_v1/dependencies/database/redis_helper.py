from redis.asyncio import ConnectionPool, Redis

from core.config import settings


class RedisHelper:
    def __init__(
        self,
        url: str,
    ):
        self.pool = ConnectionPool.from_url(url=url)

    def get_redis(self) -> Redis:
        return Redis(connection_pool=self.pool)


redis_helper: RedisHelper = RedisHelper(url=str(settings.redis.url))

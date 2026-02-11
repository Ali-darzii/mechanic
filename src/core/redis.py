from redis.asyncio import Redis
from src.config import setting

redis_client: Redis | None = None

async def get_redis() -> Redis:
    global redis_client
    if not redis_client:
        redis_client = Redis.from_url(setting.REDIS_CACHE_URL, decode_responses=True)
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        await redis_client.connection_pool.disconnect()
        redis_client = None



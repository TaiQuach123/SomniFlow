from redis.asyncio import Redis
from backend.config import Config


redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)


async def close_redis():
    await redis_client.close()

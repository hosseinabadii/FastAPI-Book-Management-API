import redis.asyncio as redis
from loguru import logger
from redis import ConnectionError

from app.config import Config

REDIS_MOCK = set()
token_blocklist = None


async def init_redis():
    global token_blocklist
    try:
        token_blocklist = redis.from_url(Config.REDIS_URL)
        await token_blocklist.ping()
        logger.info("Successfully connected to Redis")
    except ConnectionError as e:
        logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
        token_blocklist = None


async def add_jti_to_blocklist(jti: str) -> None:
    if token_blocklist:
        try:
            await token_blocklist.set(name=jti, value="", ex=Config.REDIS_JTI_EXPIRY)
            logger.debug(f"JTI '{jti}' added to Redis blocklist")
            return
        except ConnectionError:
            logger.error("Redis error while adding JTI")
    # Fallback logic (only runs if Redis failed or unavailable)
    REDIS_MOCK.add(jti)
    logger.debug(f"JTI '{jti}' added to in-memory blocklist (fallback)")


async def token_in_blocklist(jti: str) -> bool:
    if token_blocklist:
        try:
            result = await token_blocklist.get(jti)
            return result is not None
        except ConnectionError:
            logger.error("Redis error while checking JTI")
    # Fallback logic
    return jti in REDIS_MOCK


def reset_redis_mock():
    global REDIS_MOCK
    REDIS_MOCK = set()
    logger.info("In-memory Redis mock has been reset")

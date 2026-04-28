import json
import hashlib
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# -----------------------
# REDIS CLIENT (SINGLETON)
# -----------------------
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


# -----------------------
# KEY GENERATOR
# -----------------------
def make_cache_key(prefix: str, data: str) -> str:
    """
    Create deterministic cache key using hash
    """
    hashed = hashlib.sha256(data.encode()).hexdigest()
    return f"{prefix}:{hashed}"


# -----------------------
# GET CACHE
# -----------------------
async def get_cache(key: str) -> Optional[Any]:
    try:
        value = await redis_client.get(key)

        if value:
            return json.loads(value)

    except Exception as e:
        logger.warning(f"Cache GET failed: {e}")

    return None


# -----------------------
# SET CACHE
# -----------------------
async def set_cache(
    key: str,
    value: Any,
    ttl: int = 3600
):
    try:
        await redis_client.set(
            key,
            json.dumps(value),
            ex=ttl
        )

    except Exception as e:
        logger.warning(f"Cache SET failed: {e}")


# -----------------------
# DELETE CACHE (optional)
# -----------------------
async def delete_cache(key: str):
    try:
        await redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Cache DELETE failed: {e}")
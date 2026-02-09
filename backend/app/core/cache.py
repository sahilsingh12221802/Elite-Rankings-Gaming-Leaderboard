"""
Redis cache management for high-performance leaderboard caching.
Implements cache invalidation strategies and atomic operations.
"""
import json
import logging
from typing import Any, Dict, List, Optional

import redis
from redis import Redis

from .config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages Redis cache operations with automatic key prefixing."""

    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.prefix = settings.REDIS_KEY_PREFIX

    def connect(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            self.redis_client.ping()
            logger.info("Redis connection established")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _make_key(self, key: str) -> str:
        """Create a prefixed cache key."""
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        try:
            data = self.redis_client.get(self._make_key(key))
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        if not self.redis_client:
            return False
        try:
            ttl = ttl or settings.LEADERBOARD_CACHE_TTL
            self.redis_client.setex(
                self._make_key(key),
                ttl,
                json.dumps(value, default=str),
            )
            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.delete(self._make_key(key)))
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if not self.redis_client:
            return 0
        try:
            keys = self.redis_client.keys(self._make_key(pattern))
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.exists(self._make_key(key)))
        except Exception as e:
            logger.warning(f"Cache exists error for {key}: {e}")
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        """Atomically increment a counter."""
        if not self.redis_client:
            return 0
        try:
            return self.redis_client.incrby(self._make_key(key), amount)
        except Exception as e:
            logger.warning(f"Cache increment error for {key}: {e}")
            return 0

    def lpush(self, key: str, *values) -> int:
        """Push values to left of a list."""
        if not self.redis_client:
            return 0
        try:
            return self.redis_client.lpush(self._make_key(key), *values)
        except Exception as e:
            logger.warning(f"Cache lpush error for {key}: {e}")
            return 0

    def lrange(self, key: str, start: int, stop: int) -> List[str]:
        """Get range from list."""
        if not self.redis_client:
            return []
        try:
            return self.redis_client.lrange(self._make_key(key), start, stop)
        except Exception as e:
            logger.warning(f"Cache lrange error for {key}: {e}")
            return []

    def zadd(self, key: str, mapping: Dict[str, float], **kwargs) -> int:
        """Add members to a sorted set."""
        if not self.redis_client:
            return 0
        try:
            self.redis_client.zadd(self._make_key(key), mapping, **kwargs)
            self.redis_client.expire(self._make_key(key), settings.LEADERBOARD_CACHE_TTL)
            return len(mapping)
        except Exception as e:
            logger.warning(f"Cache zadd error for {key}: {e}")
            return 0

    def zrange(self, key: str, start: int, stop: int, withscores: bool = False):
        """Get range from sorted set in score order."""
        if not self.redis_client:
            return []
        try:
            return self.redis_client.zrange(
                self._make_key(key), start, stop, withscores=withscores, byscore=False
            )
        except Exception as e:
            logger.warning(f"Cache zrange error for {key}: {e}")
            return []

    def clear_all(self) -> int:
        """Clear all cache keys with the prefix."""
        if not self.redis_client:
            return 0
        return self.delete_pattern("*")

    def close(self):
        """Close Redis connection."""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis connection closed")


# Global cache manager instance
cache_manager = CacheManager()

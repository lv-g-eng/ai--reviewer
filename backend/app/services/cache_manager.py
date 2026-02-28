"""
Cache manager with Redis support

Provides distributed caching functionality using Redis with connection pooling,
cache decorators, and automatic TTL management.

Validates Requirements: 2.7, 10.4, 12.6
"""
import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-based cache manager with fallback to in-memory cache
    
    Provides distributed caching with:
    - Redis connection pooling (configured in redis_db.py)
    - 5-minute TTL for cached data (per requirement 10.4)
    - Cache decorator for frequently accessed data
    - Graceful fallback to in-memory cache when Redis unavailable
    
    Validates Requirements: 2.7, 10.4, 12.6
    """
    
    DEFAULT_TTL = 300  # 5 minutes (per requirement 10.4)
    
    def __init__(self, use_redis: bool = True):
        """
        Initialize cache manager
        
        Args:
            use_redis: Whether to use Redis (True) or in-memory cache (False)
        """
        self._in_memory_cache: dict[str, Any] = {}
        self._use_redis = use_redis
        self._redis_available = False
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
        logger.info(f"Cache manager initialized (Redis: {use_redis})")
    
    async def _get_redis(self):
        """Get Redis client with availability check"""
        if not self._use_redis:
            return None
        
        try:
            from app.database.redis_db import get_redis
            redis_client = await get_redis()
            self._redis_available = True
            return redis_client
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory cache: {e}")
            self._redis_available = False
            return None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from arguments
        
        Args:
            prefix: Cache key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a deterministic string from args and kwargs
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        key_string = ":".join(key_parts)
        
        # Hash for consistent length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (Redis with in-memory fallback)
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        # Try Redis first
        redis_client = await self._get_redis()
        if redis_client:
            try:
                value = await redis_client.get(key)
                if value is not None:
                    self._stats["hits"] += 1
                    logger.debug(f"Redis cache hit for key: {key}")
                    # Deserialize JSON if possible
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return value
                else:
                    self._stats["misses"] += 1
                    logger.debug(f"Redis cache miss for key: {key}")
                    return None
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Redis get error for key {key}: {e}")
                # Fall through to in-memory cache
        
        # Fallback to in-memory cache
        value = self._in_memory_cache.get(key)
        if value is not None:
            self._stats["hits"] += 1
            logger.debug(f"In-memory cache hit for key: {key}")
        else:
            self._stats["misses"] += 1
            logger.debug(f"In-memory cache miss for key: {key}")
        return value
    
    async def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL):
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 300 = 5 minutes per requirement 10.4)
        """
        # Try Redis first
        redis_client = await self._get_redis()
        if redis_client:
            try:
                # Serialize to JSON if not a string
                if not isinstance(value, str):
                    value = json.dumps(value)
                await redis_client.set(key, value, ex=ttl)
                logger.debug(f"Redis cache set for key: {key} (TTL: {ttl}s)")
                return
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Redis set error for key {key}: {e}")
                # Fall through to in-memory cache
        
        # Fallback to in-memory cache (no TTL support in simple dict)
        self._in_memory_cache[key] = value
        logger.debug(f"In-memory cache set for key: {key}")
    
    async def delete(self, key: str):
        """
        Delete value from cache
        
        Args:
            key: Cache key
        """
        # Try Redis first
        redis_client = await self._get_redis()
        if redis_client:
            try:
                await redis_client.delete(key)
                logger.debug(f"Redis cache deleted for key: {key}")
                return
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Redis delete error for key {key}: {e}")
                # Fall through to in-memory cache
        
        # Fallback to in-memory cache
        if key in self._in_memory_cache:
            del self._in_memory_cache[key]
            logger.debug(f"In-memory cache deleted for key: {key}")
    
    async def clear(self):
        """Clear all cache entries"""
        # Try Redis first
        redis_client = await self._get_redis()
        if redis_client:
            try:
                await redis_client.flushdb()
                logger.info("Redis cache cleared")
                return
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Redis clear error: {e}")
                # Fall through to in-memory cache
        
        # Fallback to in-memory cache
        self._in_memory_cache.clear()
        logger.info("In-memory cache cleared")
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        # Try Redis first
        redis_client = await self._get_redis()
        if redis_client:
            try:
                return await redis_client.exists(key) > 0
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Redis exists error for key {key}: {e}")
                # Fall through to in-memory cache
        
        # Fallback to in-memory cache
        return key in self._in_memory_cache
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Cache statistics including hit rate
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "errors": self._stats["errors"],
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "redis_available": self._redis_available,
            "in_memory_entries": len(self._in_memory_cache)
        }
    
    def reset_stats(self):
        """Reset statistics counters"""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
        logger.info("Cache statistics reset")
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching a pattern
        
        Useful for invalidating related cache entries on data updates.
        For example, invalidate all user-related caches when user data changes.
        
        Args:
            pattern: Redis pattern (e.g., "user:*", "project:123:*")
            
        Returns:
            Number of keys deleted
            
        Validates Requirement: 10.4 (cache invalidation on data updates)
        """
        redis_client = await self._get_redis()
        if redis_client:
            try:
                keys = []
                async for key in redis_client.scan_iter(match=pattern):
                    keys.append(key)
                
                if keys:
                    deleted = await redis_client.delete(*keys)
                    logger.info(f"Invalidated {deleted} cache keys matching pattern: {pattern}")
                    return deleted
                return 0
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Redis invalidate pattern error for {pattern}: {e}")
                return 0
        
        # Fallback to in-memory cache (simple prefix matching)
        deleted = 0
        keys_to_delete = [k for k in self._in_memory_cache.keys() if self._matches_pattern(k, pattern)]
        for key in keys_to_delete:
            del self._in_memory_cache[key]
            deleted += 1
        
        if deleted > 0:
            logger.info(f"Invalidated {deleted} in-memory cache keys matching pattern: {pattern}")
        return deleted
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for in-memory cache (supports * wildcard)"""
        import re
        regex_pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", key))
    
    async def warm_cache(self, data_loader: Callable, keys: list[tuple[str, Any]], ttl: int = DEFAULT_TTL):
        """
        Warm cache with critical data
        
        Pre-loads frequently accessed data into cache to improve performance.
        Useful for warming cache on application startup or after cache invalidation.
        
        Args:
            data_loader: Async function that loads data given a key
            keys: List of (cache_key, loader_arg) tuples
            ttl: Time to live in seconds (default: 300 = 5 minutes)
            
        Example:
            async def load_user(user_id):
                return await db.get_user(user_id)
            
            await cache_manager.warm_cache(
                load_user,
                [("user:1", 1), ("user:2", 2)],
                ttl=300
            )
        
        Validates Requirement: 10.4 (cache warming for critical data)
        """
        logger.info(f"Warming cache with {len(keys)} entries")
        
        for cache_key, loader_arg in keys:
            try:
                # Check if already cached
                if await self.exists(cache_key):
                    logger.debug(f"Cache key already exists, skipping: {cache_key}")
                    continue
                
                # Load data
                data = await data_loader(loader_arg)
                
                # Store in cache
                if data is not None:
                    await self.set(cache_key, data, ttl=ttl)
                    logger.debug(f"Cache warmed for key: {cache_key}")
            except Exception as e:
                logger.error(f"Error warming cache for key {cache_key}: {e}")
                # Continue with other keys
        
        logger.info(f"Cache warming completed")
    
    async def invalidate_on_update(self, entity_type: str, entity_id: str):
        """
        Invalidate cache entries related to an entity after update
        
        Automatically invalidates all cache keys related to an entity
        when that entity is updated in the database.
        
        Args:
            entity_type: Type of entity (e.g., "user", "project", "pr")
            entity_id: ID of the entity
            
        Example:
            # After updating user data
            await cache_manager.invalidate_on_update("user", "123")
            # Invalidates: user:123:*, analysis:*:user:123, etc.
        
        Validates Requirement: 10.4 (invalidate cache on data updates)
        """
        patterns = [
            f"{entity_type}:{entity_id}:*",  # Direct entity caches
            f"*:{entity_type}:{entity_id}:*",  # Nested entity caches
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await self.invalidate_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Invalidated {total_deleted} cache entries for {entity_type}:{entity_id}")
        return total_deleted


def cached(
    prefix: str,
    ttl: int = CacheManager.DEFAULT_TTL,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results
    
    Caches the result of async functions with automatic key generation
    and 5-minute TTL (per requirement 10.4).
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        key_builder: Optional custom function to build cache key from args/kwargs
    
    Example:
        @cached(prefix="user_data", ttl=300)
        async def get_user_data(user_id: str):
            # Expensive operation
            return fetch_from_database(user_id)
    
    Validates Requirement: 10.4
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Generate cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for {func.__name__}: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                await cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Singleton instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def reset_cache_manager():
    """Reset cache manager instance (for testing)"""
    global _cache_manager
    _cache_manager = None

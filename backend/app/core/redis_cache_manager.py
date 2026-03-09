"""
Redis Cache Manager for Advanced Caching Strategies

Provides intelligent caching with:
- TTL-based cache invalidation
- Cache warming strategies
- Memory optimization
- Performance monitoring
- Distributed caching patterns
"""

import json
import time
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
import redis.asyncio as redis
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCacheManager:
    """Advanced Redis cache management with intelligent strategies"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        self.default_ttl = 300  # 5 minutes
        self.max_memory_usage = 0.8  # 80% of available memory
    
    async def initialize(self):
        """Initialize Redis connection with optimized settings"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=100,
                retry_on_timeout=True,
                socket_timeout=30,
                socket_connect_timeout=10,
                health_check_interval=30,
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache manager initialized successfully")
            
            # Configure memory optimization
            await self._configure_memory_optimization()
            
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    async def _configure_memory_optimization(self):
        """Configure Redis for optimal memory usage"""
        try:
            # Set memory policy for automatic eviction
            await self.redis_client.config_set('maxmemory-policy', 'allkeys-lru')
            
            # Enable compression for large values
            await self.redis_client.config_set('hash-max-ziplist-entries', '512')
            await self.redis_client.config_set('hash-max-ziplist-value', '64')
            
            logger.info("Redis memory optimization configured")
            
        except Exception as e:
            logger.warning(f"Redis memory optimization failed: {e}")
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache keys"""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(str(hash(json.dumps(arg, sort_keys=True))))
            else:
                key_parts.append(str(arg))
        
        # Add keyword arguments
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(str(hash(json.dumps(sorted_kwargs))))
        
        return ":".join(key_parts)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with statistics tracking"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value is not None:
                self.cache_stats["hits"] += 1
                return json.loads(value)
            else:
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            ttl = ttl or self.default_ttl
            
            await self.redis_client.setex(key, ttl, serialized_value)
            self.cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            if result:
                self.cache_stats["deletes"] += 1
            return bool(result)
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                self.cache_stats["deletes"] += deleted
                return deleted
            return 0
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache pattern delete error for pattern {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False
        
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists check error for key {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get TTL for a key"""
        if not self.redis_client:
            return -1
        
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL check error for key {key}: {e}")
            return -1
    
    async def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Extend TTL for a key"""
        if not self.redis_client:
            return False
        
        try:
            current_ttl = await self.get_ttl(key)
            if current_ttl > 0:
                new_ttl = current_ttl + additional_seconds
                return bool(await self.redis_client.expire(key, new_ttl))
            return False
            
        except Exception as e:
            logger.error(f"Cache TTL extend error for key {key}: {e}")
            return False
    
    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get Redis memory usage statistics"""
        if not self.redis_client:
            return {}
        
        try:
            info = await self.redis_client.info('memory')
            return {
                "used_memory": info.get('used_memory', 0),
                "used_memory_human": info.get('used_memory_human', '0B'),
                "used_memory_peak": info.get('used_memory_peak', 0),
                "used_memory_peak_human": info.get('used_memory_peak_human', '0B'),
                "memory_fragmentation_ratio": info.get('mem_fragmentation_ratio', 0),
                "maxmemory": info.get('maxmemory', 0),
                "maxmemory_human": info.get('maxmemory_human', '0B'),
            }
            
        except Exception as e:
            logger.error(f"Memory usage check error: {e}")
            return {}
    
    async def warm_cache(self, warm_functions: List[Callable]) -> Dict[str, Any]:
        """Warm cache with frequently accessed data"""
        results = {"warmed": 0, "failed": 0, "errors": []}
        
        for func in warm_functions:
            try:
                await func()
                results["warmed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{func.__name__}: {str(e)}")
                logger.error(f"Cache warming failed for {func.__name__}: {e}")
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }
    
    def reset_stats(self):
        """Reset cache statistics"""
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }

# Global cache manager instance
cache_manager = RedisCacheManager()

def cached(
    prefix: str = "",
    ttl: int = 300,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_cache_key(
                    prefix or func.__name__, *args, **kwargs
                )
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Cache warming functions
async def warm_project_cache():
    """Warm cache with popular projects"""
    from app.database.optimizations import DatabaseOptimizer
    from app.database.postgresql import get_db
    
    async with get_db() as db:
        optimizer = DatabaseOptimizer()
        # Cache top projects for different users
        for user_id in range(1, 6):  # Top 5 users
            await optimizer.get_projects_optimized(db, user_id, limit=10)

async def warm_library_cache():
    """Warm cache with popular libraries"""
    # Implementation would cache popular libraries
    pass

async def warm_analytics_cache():
    """Warm cache with project analytics"""
    from app.database.optimizations import DatabaseOptimizer
    from app.database.postgresql import get_db
    
    async with get_db() as db:
        optimizer = DatabaseOptimizer()
        # Cache analytics for active projects
        for project_id in range(1, 11):
            try:
                await optimizer.get_project_analytics(db, project_id)
            except Exception as e:
                logger.debug(f"Skipping project {project_id}: {e}")
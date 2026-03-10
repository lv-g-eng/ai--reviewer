"""
Tests for Redis caching layer

Tests cache hit/miss behavior, cache invalidation, cache warming,
and integration with Redis.

Validates Requirements: 10.4, 13.5
"""
import pytest
from unittest.mock import patch
from app.shared.cache_manager import (
    CacheManager,
    cached,
    reset_cache_manager
)


@pytest.fixture
def cache_manager():
    """Create cache manager instance for testing"""
    reset_cache_manager()
    manager = CacheManager(use_redis=False)  # Use in-memory for unit tests
    return manager


class TestCacheManagerBasics:
    """Test basic cache operations"""
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_manager):
        """Test setting and getting cache values"""
        await cache_manager.set("test_key", "test_value")
        value = await cache_manager.get("test_key")
        
        assert value == "test_value"
        stats = cache_manager.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0
    
    @pytest.mark.asyncio
    async def test_get_miss(self, cache_manager):
        """Test cache miss"""
        value = await cache_manager.get("nonexistent_key")
        
        assert value is None
        stats = cache_manager.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 1
    
    @pytest.mark.asyncio
    async def test_delete(self, cache_manager):
        """Test deleting cache entries"""
        await cache_manager.set("test_key", "test_value")
        await cache_manager.delete("test_key")
        value = await cache_manager.get("test_key")
        
        assert value is None
    
    @pytest.mark.asyncio
    async def test_exists(self, cache_manager):
        """Test checking key existence"""
        await cache_manager.set("test_key", "test_value")
        
        assert await cache_manager.exists("test_key") is True
        assert await cache_manager.exists("nonexistent") is False
    
    @pytest.mark.asyncio
    async def test_clear(self, cache_manager):
        """Test clearing all cache entries"""
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key2", "value2")
        await cache_manager.clear()
        
        assert await cache_manager.get("key1") is None
        assert await cache_manager.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_ttl_parameter(self, cache_manager):
        """Test that TTL parameter is accepted (actual expiration tested with Redis)"""
        # Should not raise an error
        await cache_manager.set("test_key", "test_value", ttl=60)
        value = await cache_manager.get("test_key")
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_default_ttl(self, cache_manager):
        """Test default TTL is 5 minutes (300 seconds)"""
        assert CacheManager.DEFAULT_TTL == 300


class TestCacheStatistics:
    """Test cache statistics and metrics"""
    
    @pytest.mark.asyncio
    async def test_hit_rate_calculation(self, cache_manager):
        """Test hit rate calculation"""
        # Set some values
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key2", "value2")
        
        # 2 hits
        await cache_manager.get("key1")
        await cache_manager.get("key2")
        
        # 1 miss
        await cache_manager.get("key3")
        
        stats = cache_manager.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_requests"] == 3
        assert stats["hit_rate_percent"] == pytest.approx(66.67, rel=0.01)
    
    @pytest.mark.asyncio
    async def test_reset_stats(self, cache_manager):
        """Test resetting statistics"""
        await cache_manager.set("key1", "value1")
        await cache_manager.get("key1")
        
        cache_manager.reset_stats()
        stats = cache_manager.get_stats()
        
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["total_requests"] == 0


class TestCacheInvalidation:
    """Test cache invalidation functionality (Requirement 10.4)"""
    
    @pytest.mark.asyncio
    async def test_invalidate_pattern(self, cache_manager):
        """Test invalidating cache keys by pattern"""
        # Set multiple keys
        await cache_manager.set("user:1:profile", "data1")
        await cache_manager.set("user:2:profile", "data2")
        await cache_manager.set("project:1:data", "data3")
        
        # Invalidate user keys
        deleted = await cache_manager.invalidate_pattern("user:*")
        
        assert deleted == 2
        assert await cache_manager.get("user:1:profile") is None
        assert await cache_manager.get("user:2:profile") is None
        assert await cache_manager.get("project:1:data") == "data3"
    
    @pytest.mark.asyncio
    async def test_invalidate_on_update(self, cache_manager):
        """Test invalidating cache on entity update"""
        # Set entity-related caches
        await cache_manager.set("user:123:profile", "profile_data")
        await cache_manager.set("user:123:settings", "settings_data")
        await cache_manager.set("analysis:pr:user:123:data", "analysis_data")
        
        # Invalidate on user update
        deleted = await cache_manager.invalidate_on_update("user", "123")
        
        assert deleted >= 2  # At least the direct user caches
        assert await cache_manager.get("user:123:profile") is None
        assert await cache_manager.get("user:123:settings") is None
    
    @pytest.mark.asyncio
    async def test_invalidate_empty_pattern(self, cache_manager):
        """Test invalidating with pattern that matches nothing"""
        await cache_manager.set("key1", "value1")
        
        deleted = await cache_manager.invalidate_pattern("nonexistent:*")
        
        assert deleted == 0
        assert await cache_manager.get("key1") == "value1"


class TestCacheWarming:
    """Test cache warming functionality (Requirement 10.4)"""
    
    @pytest.mark.asyncio
    async def test_warm_cache(self, cache_manager):
        """Test warming cache with critical data"""
        # Mock data loader
        async def load_user(user_id):
            return {"id": user_id, "name": f"User {user_id}"}
        
        # Warm cache
        keys = [
            ("user:1", 1),
            ("user:2", 2),
            ("user:3", 3)
        ]
        await cache_manager.warm_cache(load_user, keys, ttl=300)
        
        # Verify data is cached
        user1 = await cache_manager.get("user:1")
        assert user1 == {"id": 1, "name": "User 1"}
        
        user2 = await cache_manager.get("user:2")
        assert user2 == {"id": 2, "name": "User 2"}
    
    @pytest.mark.asyncio
    async def test_warm_cache_skips_existing(self, cache_manager):
        """Test cache warming skips already cached keys"""
        # Pre-populate one key
        await cache_manager.set("user:1", {"id": 1, "name": "Existing User"})
        
        # Mock data loader (should not be called for user:1)
        call_count = 0
        async def load_user(user_id):
            nonlocal call_count
            call_count += 1
            return {"id": user_id, "name": f"New User {user_id}"}
        
        # Warm cache
        keys = [("user:1", 1), ("user:2", 2)]
        await cache_manager.warm_cache(load_user, keys)
        
        # Verify existing key was not overwritten
        user1 = await cache_manager.get("user:1")
        assert user1 == {"id": 1, "name": "Existing User"}
        
        # Verify new key was loaded
        user2 = await cache_manager.get("user:2")
        assert user2 == {"id": 2, "name": "New User 2"}
        
        # Verify loader was called only once (for user:2)
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_warm_cache_handles_errors(self, cache_manager):
        """Test cache warming continues on errors"""
        # Mock data loader that fails for some keys
        async def load_user(user_id):
            if user_id == 2:
                raise Exception("Load failed")
            return {"id": user_id, "name": f"User {user_id}"}
        
        # Warm cache
        keys = [("user:1", 1), ("user:2", 2), ("user:3", 3)]
        await cache_manager.warm_cache(load_user, keys)
        
        # Verify successful loads
        assert await cache_manager.get("user:1") is not None
        assert await cache_manager.get("user:3") is not None
        
        # Verify failed load was skipped
        assert await cache_manager.get("user:2") is None


class TestCacheDecorator:
    """Test @cached decorator functionality"""
    
    @pytest.mark.asyncio
    async def test_cached_decorator_basic(self):
        """Test basic cached decorator functionality"""
        reset_cache_manager()
        call_count = 0
        
        @cached(prefix="test_func", ttl=300)
        async def expensive_function(arg1, arg2):
            nonlocal call_count
            call_count += 1
            return f"{arg1}_{arg2}"
        
        # First call - cache miss
        result1 = await expensive_function("a", "b")
        assert result1 == "a_b"
        assert call_count == 1
        
        # Second call - cache hit
        result2 = await expensive_function("a", "b")
        assert result2 == "a_b"
        assert call_count == 1  # Function not called again
        
        # Different args - cache miss
        result3 = await expensive_function("c", "d")
        assert result3 == "c_d"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_cached_decorator_with_kwargs(self):
        """Test cached decorator with keyword arguments"""
        reset_cache_manager()
        call_count = 0
        
        @cached(prefix="test_func", ttl=300)
        async def function_with_kwargs(arg1, arg2=None):
            nonlocal call_count
            call_count += 1
            return f"{arg1}_{arg2}"
        
        # Call with kwargs
        result1 = await function_with_kwargs("a", arg2="b")
        assert call_count == 1
        
        # Same call - cache hit
        result2 = await function_with_kwargs("a", arg2="b")
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_cached_decorator_none_result(self):
        """Test cached decorator does not cache None results"""
        reset_cache_manager()
        call_count = 0
        
        @cached(prefix="test_func", ttl=300)
        async def function_returns_none():
            nonlocal call_count
            call_count += 1
            return None
        
        # First call
        result1 = await function_returns_none()
        assert result1 is None
        assert call_count == 1
        
        # Second call - should call function again (None not cached)
        result2 = await function_returns_none()
        assert result2 is None
        assert call_count == 2


class TestRedisIntegration:
    """Test Redis integration behavior"""
    
    @pytest.mark.asyncio
    async def test_redis_unavailable_fallback(self):
        """Test fallback to in-memory cache when Redis is unavailable"""
        reset_cache_manager()
        
        # Create manager with Redis enabled but unavailable
        with patch('app.database.redis_db.get_redis', side_effect=RuntimeError("Redis client not initialized")):
            manager = CacheManager(use_redis=True)
            
            # Should fall back to in-memory cache
            await manager.set("test_key", "test_value")
            value = await manager.get("test_key")
            
            assert value == "test_value"
            assert manager._redis_available is False
    
    @pytest.mark.asyncio
    async def test_in_memory_mode(self):
        """Test cache manager in in-memory mode"""
        reset_cache_manager()
        manager = CacheManager(use_redis=False)
        
        # Set and get values
        await manager.set("key1", "value1")
        await manager.set("key2", {"data": "value2"})
        
        assert await manager.get("key1") == "value1"
        assert await manager.get("key2") == {"data": "value2"}
        
        # Test invalidation
        await manager.set("user:1:profile", "data1")
        await manager.set("user:2:profile", "data2")
        deleted = await manager.invalidate_pattern("user:*")
        
        assert deleted == 2
        assert await manager.get("user:1:profile") is None


class TestCacheKeyGeneration:
    """Test cache key generation"""
    
    @pytest.mark.asyncio
    async def test_generate_key_with_args(self, cache_manager):
        """Test key generation with positional arguments"""
        key1 = cache_manager._generate_key("prefix", "arg1", "arg2")
        key2 = cache_manager._generate_key("prefix", "arg1", "arg2")
        key3 = cache_manager._generate_key("prefix", "arg1", "arg3")
        
        # Same args should generate same key
        assert key1 == key2
        
        # Different args should generate different key
        assert key1 != key3
    
    @pytest.mark.asyncio
    async def test_generate_key_with_kwargs(self, cache_manager):
        """Test key generation with keyword arguments"""
        key1 = cache_manager._generate_key("prefix", a="1", b="2")
        key2 = cache_manager._generate_key("prefix", b="2", a="1")  # Different order
        key3 = cache_manager._generate_key("prefix", a="1", b="3")
        
        # Same kwargs (different order) should generate same key
        assert key1 == key2
        
        # Different kwargs should generate different key
        assert key1 != key3


# Integration test for requirement 13.5
class TestCachingIntegration:
    """Integration tests for Redis caching (Requirement 13.5)"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_miss_behavior(self, cache_manager):
        """
        Test cache hit/miss behavior
        
        Validates Requirement: 13.5
        """
        # Cache miss
        result = await cache_manager.get("nonexistent")
        assert result is None
        
        # Set value
        await cache_manager.set("key1", {"data": "value1"})
        
        # Cache hit
        result = await cache_manager.get("key1")
        assert result == {"data": "value1"}
        
        # Verify statistics
        stats = cache_manager.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_integration(self, cache_manager):
        """
        Test cache invalidation on data updates
        
        Validates Requirement: 13.5
        """
        # Populate cache
        await cache_manager.set("user:1:profile", {"name": "User 1"})
        await cache_manager.set("user:1:settings", {"theme": "dark"})
        await cache_manager.set("user:2:profile", {"name": "User 2"})
        
        # Simulate data update - invalidate user 1 caches
        deleted = await cache_manager.invalidate_on_update("user", "1")
        
        # Verify user 1 caches are invalidated
        assert await cache_manager.get("user:1:profile") is None
        assert await cache_manager.get("user:1:settings") is None
        
        # Verify user 2 cache is intact
        assert await cache_manager.get("user:2:profile") is not None
    
    @pytest.mark.asyncio
    async def test_cache_warming_integration(self, cache_manager):
        """
        Test cache warming for critical data
        
        Validates Requirement: 13.5
        """
        # Mock critical data loader
        async def load_critical_data(item_id):
            return {"id": item_id, "critical": True}
        
        # Warm cache with critical data
        critical_items = [
            ("critical:1", 1),
            ("critical:2", 2),
            ("critical:3", 3)
        ]
        await cache_manager.warm_cache(load_critical_data, critical_items, ttl=300)
        
        # Verify all critical data is cached
        for i in range(1, 4):
            data = await cache_manager.get(f"critical:{i}")
            assert data is not None
            assert data["critical"] is True

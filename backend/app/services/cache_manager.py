"""
Cache manager for architectural analysis results
"""
import json
from typing import Any, Optional, Dict, List
import hashlib

from app.database.redis_db import cache_get, cache_set, cache_delete
from app.core.logging_config import logger

class AnalysisCacheManager:
    """
    Manages caching for expensive architectural analysis operations.
    
    Provides methods for:
    - Generating unique cache keys based on analysis parameters
    - Storing and retrieving analysis results
    - Invalidating project-specific cache entries
    """
    
    CACHE_PREFIX = "arch_analysis"
    DEFAULT_EXPIRATION = 3600 * 24  # 24 hours
    
    @staticmethod
    def _generate_key(project_id: str, analysis_type: str, params: Optional[Dict] = None) -> str:
        """Generate a unique cache key"""
        param_str = json.dumps(params, sort_keys=True) if params else ""
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{AnalysisCacheManager.CACHE_PREFIX}:{project_id}:{analysis_type}:{param_hash}"
    
    async def get_cached_result(
        self, 
        project_id: str, 
        analysis_type: str, 
        params: Optional[Dict] = None
    ) -> Optional[Any]:
        """Retrieve cached analysis result"""
        key = self._generate_key(project_id, analysis_type, params)
        try:
            cached_data = await cache_get(key)
            if cached_data:
                logger.debug(f"Cache hit for {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
        
        return None
    
    async def set_cached_result(
        self, 
        project_id: str, 
        analysis_type: str, 
        result: Any, 
        params: Optional[Dict] = None,
        expiration: Optional[int] = None
    ):
        """Store analysis result in cache"""
        key = self._generate_key(project_id, analysis_type, params)
        exp = expiration or self.DEFAULT_EXPIRATION
        try:
            await cache_set(key, json.dumps(result), expiration=exp)
            logger.debug(f"Cached result for {key}")
        except Exception as e:
            logger.error(f"Error storing in cache: {e}")
            
    async def invalidate_project_cache(self, project_id: str):
        """Invalidate all cached results for a project"""
        # Note: Redis scanning for keys can be slow; in production, 
        # consider keeping a set of keys per project.
        # For now, we'll implement a simple prefix search if possible, 
        # or just wait for natural expiration.
        logger.info(f"Invalidating cache for project {project_id}")
        # Implementation depends on Redis client's ability to scan/keys
        pass

# Global instance
analysis_cache = AnalysisCacheManager()

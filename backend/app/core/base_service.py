"""
Base Service Class with Performance Optimizations

Provides common patterns for all services including:
- Generic CRUD operations
- Centralized error handling
- Intelligent caching
- Query optimization
- Metrics collection
- Circuit breaker pattern
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta

from sqlalchemy import select, update, delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from pydantic import BaseModel
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge

from app.core.config import settings
from app.core.logging_config import get_logger
from app.database.redis_db import get_redis

# Type variables for generic service
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)

# Metrics
service_requests_total = Counter('service_requests_total', 'Total service requests', ['service', 'method', 'status'])
service_request_duration = Histogram('service_request_duration_seconds', 'Service request duration', ['service', 'method'])
service_cache_hits = Counter('service_cache_hits_total', 'Cache hits', ['service'])
service_cache_misses = Counter('service_cache_misses_total', 'Cache misses', ['service'])
service_active_connections = Gauge('service_active_connections', 'Active database connections', ['service'])

class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """Circuit breaker implementation for service resilience"""
    
    def __init__(self, failure
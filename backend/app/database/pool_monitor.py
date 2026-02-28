"""
Database connection pool monitoring utilities

This module provides utilities to monitor and report on the health
and performance of the SQLAlchemy connection pool.

Requirements: 10.6 - Connection pooling for PostgreSQL with pool size of 20 connections
"""
from typing import Dict, Any
from sqlalchemy.pool import Pool


def get_pool_status(pool: Pool) -> Dict[str, Any]:
    """
    Get current status of the connection pool
    
    Args:
        pool: SQLAlchemy connection pool
        
    Returns:
        Dictionary with pool statistics
    """
    return {
        "pool_size": pool.size(),
        "checked_in_connections": pool.checkedin(),
        "checked_out_connections": pool.checkedout(),
        "overflow_connections": pool.overflow(),
        "total_connections": pool.checkedin() + pool.checkedout(),
        "available_connections": pool.size() - pool.checkedout(),
        "pool_timeout": pool._timeout if hasattr(pool, '_timeout') else None,
        "pool_recycle": pool._recycle if hasattr(pool, '_recycle') else None,
    }


def format_pool_status(status: Dict[str, Any]) -> str:
    """
    Format pool status for logging
    
    Args:
        status: Pool status dictionary from get_pool_status
        
    Returns:
        Formatted string representation
    """
    return (
        f"Connection Pool Status:\n"
        f"  Pool Size: {status['pool_size']}\n"
        f"  Checked In: {status['checked_in_connections']}\n"
        f"  Checked Out: {status['checked_out_connections']}\n"
        f"  Overflow: {status['overflow_connections']}\n"
        f"  Total: {status['total_connections']}\n"
        f"  Available: {status['available_connections']}\n"
        f"  Timeout: {status['pool_timeout']}s\n"
        f"  Recycle: {status['pool_recycle']}s"
    )


def check_pool_health(pool: Pool) -> Dict[str, Any]:
    """
    Check if the connection pool is healthy
    
    Args:
        pool: SQLAlchemy connection pool
        
    Returns:
        Dictionary with health status and warnings
    """
    status = get_pool_status(pool)
    warnings = []
    
    # Check if pool is exhausted
    if status['available_connections'] == 0:
        warnings.append("Pool exhausted: No available connections")
    
    # Check if pool is near capacity
    utilization = status['checked_out_connections'] / status['pool_size']
    if utilization > 0.8:
        warnings.append(f"High pool utilization: {utilization:.1%}")
    
    # Check if overflow is being used
    if status['overflow_connections'] > 0:
        warnings.append(f"Using overflow connections: {status['overflow_connections']}")
    
    return {
        "healthy": len(warnings) == 0,
        "status": status,
        "warnings": warnings,
        "utilization_percent": utilization * 100
    }


async def log_pool_status(engine):
    """
    Log current pool status (for debugging/monitoring)
    
    Args:
        engine: SQLAlchemy async engine
    """
    pool = engine.pool
    status = get_pool_status(pool)
    print(format_pool_status(status))
    
    health = check_pool_health(pool)
    if not health['healthy']:
        print("\n⚠️  Pool Health Warnings:")
        for warning in health['warnings']:
            print(f"  - {warning}")
    else:
        print("\n✅ Pool is healthy")

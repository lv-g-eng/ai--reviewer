"""
PostgreSQL database connection and session management
"""
import logging
logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings

# Create async engine with optimized connection pooling
# Requirements: 10.6 - Connection pooling for PostgreSQL with pool size of 20 connections
engine = create_async_engine(
    settings.postgres_url,
    echo=True,
    future=True,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=20,  # Core pool size (requirement 10.6)
    max_overflow=10,  # Additional connections beyond pool_size
    pool_timeout=30,  # Timeout for getting connection from pool (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
    pool_use_lifo=True,  # Use LIFO to reduce connection churn
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_postgres():
    """Initialize PostgreSQL database"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Instrument SQLAlchemy for OpenTelemetry tracing (Requirement 18.1)
    from app.core.config import settings
    if settings.is_tracing_enabled():
        from app.core.tracing import get_tracing_config
        tracing_config = get_tracing_config()
        if tracing_config:
            tracing_config.instrument_sqlalchemy(engine)
    
    logger.info("✅ PostgreSQL initialized")


async def close_postgres():
    """Close PostgreSQL connections"""
    await engine.dispose()
    logger.info("✅ PostgreSQL connections closed")


async def test_postgres_connection():
    """Test PostgreSQL connection"""
    from sqlalchemy import text
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        logger.info("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        logger.info("❌ PostgreSQL connection failed: {e}")
        return False

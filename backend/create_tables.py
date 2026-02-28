#!/usr/bin/env python3
"""Create database tables"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.core.config import settings

async def create_tables():
    """Create all database tables"""
    engine = create_async_engine(settings.postgres_url, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())

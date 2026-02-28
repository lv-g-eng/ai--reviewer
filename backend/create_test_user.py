#!/usr/bin/env python3
"""Create a test user"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.core.config import settings
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    """Create test user"""
    engine = create_async_engine(settings.postgres_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    from sqlalchemy import text
    
    async with async_session() as session:
        # Delete existing user
        await session.execute(
            text("DELETE FROM users WHERE email = 'admin@example.com'")
        )
        await session.commit()
        
        # Create new user
        password_hash = pwd_context.hash("admin123")
        print(f"Password hash: {password_hash}")
        
        await session.execute(
            text("""
            INSERT INTO users (id, email, password_hash, role, full_name, is_active, created_at, updated_at)
            VALUES (:id, :email, :password_hash, :role, :full_name, :is_active, :created_at, :updated_at)
            """),
            {
                "id": str(uuid.uuid4()),
                "email": "admin@example.com",
                "password_hash": password_hash,
                "role": "admin",
                "full_name": "Admin User",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        await session.commit()
        print("✅ User created successfully!")
        print("Email: admin@example.com")
        print("Password: admin123")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_user())

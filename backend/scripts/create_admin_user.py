#!/usr/bin/env python3
"""
Create default admin user for the AI Code Review Platform.

This script creates an admin user with email and password.
Run this after database initialization to create the first admin account.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database.postgresql import get_db, init_db
from app.models import User, UserRole
from app.utils.password import hash_password
import uuid


async def create_admin_user(
    email: str = "admin@example.com",
    password: str = "Admin123!",
    full_name: str = "System Administrator"
):
    """
    Create a default admin user.
    
    Args:
        email: Admin email address
        password: Admin password (must meet strength requirements)
        full_name: Admin full name
    """
    print("=" * 60)
    print("AI Code Review Platform - Admin User Creation")
    print("=" * 60)
    print()
    
    # Initialize database
    print("Initializing database connection...")
    await init_db()
    
    async for db in get_db():
        try:
            # Check if admin already exists
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ Admin user with email '{email}' already exists!")
                print(f"   User ID: {existing_user.id}")
                print(f"   Role: {existing_user.role.value}")
                print(f"   Created: {existing_user.created_at}")
                print()
                print("If you need to reset the password, use the password reset feature.")
                return False
            
            # Hash password
            print(f"Creating admin user: {email}")
            password_hash = hash_password(password)
            
            # Create admin user
            admin_user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=password_hash,
                role=UserRole.admin,
                full_name=full_name,
                is_active=True
            )
            
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)
            
            print()
            print("✅ Admin user created successfully!")
            print()
            print("=" * 60)
            print("LOGIN CREDENTIALS")
            print("=" * 60)
            print(f"Email:    {email}")
            print(f"Password: {password}")
            print(f"Role:     {admin_user.role.value}")
            print(f"User ID:  {admin_user.id}")
            print("=" * 60)
            print()
            print("⚠️  IMPORTANT SECURITY NOTICE:")
            print("   1. Change this password immediately after first login")
            print("   2. Do not share these credentials")
            print("   3. Enable MFA if available")
            print("   4. This password should only be used in development")
            print()
            print("Login at: http://localhost:3000/login")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            await db.rollback()
            return False


async def main():
    """Main function to create admin user."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create admin user for AI Code Review Platform"
    )
    parser.add_argument(
        "--email",
        default="admin@example.com",
        help="Admin email address (default: admin@example.com)"
    )
    parser.add_argument(
        "--password",
        default="Admin123!",
        help="Admin password (default: Admin123!)"
    )
    parser.add_argument(
        "--name",
        default="System Administrator",
        help="Admin full name (default: System Administrator)"
    )
    
    args = parser.parse_args()
    
    success = await create_admin_user(
        email=args.email,
        password=args.password,
        full_name=args.name
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

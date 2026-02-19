"""
Database initialization script with default admin user creation.
"""
import uuid
import bcrypt
from sqlalchemy.orm import Session
from .database import init_db, get_db
from .models import User, Role
from .config import settings


def create_default_admin(db: Session, username: str = "admin", password: str = "admin123") -> User:
    """
    Create a default admin user if no admin exists.
    
    Args:
        db: Database session
        username: Admin username (default: "admin")
        password: Admin password (default: "admin123")
    
    Returns:
        The created or existing admin user
    """
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.username == username).first()
    if existing_admin:
        print(f"Admin user '{username}' already exists.")
        return existing_admin
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(settings.bcrypt_rounds)).decode('utf-8')
    
    # Create admin user
    admin_user = User(
        id=str(uuid.uuid4()),
        username=username,
        password_hash=password_hash,
        role=Role.ADMIN,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"Created default admin user: {username}")
    print(f"Password: {password}")
    print("IMPORTANT: Change this password immediately in production!")
    
    return admin_user


def initialize_database(create_admin: bool = True) -> None:
    """
    Initialize the database and optionally create a default admin user.
    
    Args:
        create_admin: Whether to create a default admin user (default: True)
    """
    print("Initializing database...")
    init_db()
    print("Database tables created successfully.")
    
    if create_admin:
        with get_db() as db:
            create_default_admin(db)
    
    print("Database initialization complete.")


if __name__ == "__main__":
    initialize_database()

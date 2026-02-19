"""
Verify database initialization.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override database URL to use test SQLite database
os.environ['DATABASE_URL'] = 'sqlite:///../test_enterprise_rbac.db'

from enterprise_rbac_auth.database import get_db
from enterprise_rbac_auth.models import User, Project, Session as SessionModel, AuditLog

if __name__ == "__main__":
    print("Verifying database...")
    
    with get_db() as db:
        # Check users
        users = db.query(User).all()
        print(f"\nFound {len(users)} user(s):")
        for user in users:
            print(f"  - {user.username} (Role: {user.role.value}, Active: {user.is_active})")
        
        # Check tables exist
        print("\nVerifying tables exist:")
        print(f"  ✓ Users table: {db.query(User).count()} records")
        print(f"  ✓ Projects table: {db.query(Project).count()} records")
        print(f"  ✓ Sessions table: {db.query(SessionModel).count()} records")
        print(f"  ✓ Audit logs table: {db.query(AuditLog).count()} records")
    
    print("\n✅ Database verification complete!")

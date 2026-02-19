"""
Test script to verify database initialization works.
"""
import os
import sys

# Override database URL to use SQLite for testing
os.environ['DATABASE_URL'] = 'sqlite:///./test_enterprise_rbac.db'

from enterprise_rbac_auth.init_db import initialize_database

if __name__ == "__main__":
    print("Testing database initialization with SQLite...")
    initialize_database()
    print("\nTest completed successfully!")
    print("Database file created: test_enterprise_rbac.db")

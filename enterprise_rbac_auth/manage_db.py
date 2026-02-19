#!/usr/bin/env python3
"""
Database management CLI for Enterprise RBAC Authentication System.
"""
import sys
import argparse
from .database import init_db, drop_db
from .init_db import initialize_database, create_default_admin, get_db


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Database management for Enterprise RBAC Auth")
    parser.add_argument(
        "command",
        choices=["init", "reset", "create-admin"],
        help="Command to execute"
    )
    parser.add_argument(
        "--username",
        default="admin",
        help="Admin username (for create-admin command)"
    )
    parser.add_argument(
        "--password",
        default="admin123",
        help="Admin password (for create-admin command)"
    )
    parser.add_argument(
        "--no-admin",
        action="store_true",
        help="Skip creating default admin user (for init command)"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        print("Initializing database...")
        initialize_database(create_admin=not args.no_admin)
        print("Done!")
    
    elif args.command == "reset":
        confirm = input("WARNING: This will delete all data. Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            print("Dropping all tables...")
            drop_db()
            print("Reinitializing database...")
            initialize_database(create_admin=not args.no_admin)
            print("Database reset complete!")
        else:
            print("Reset cancelled.")
    
    elif args.command == "create-admin":
        with get_db() as db:
            create_default_admin(db, username=args.username, password=args.password)
        print("Done!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Database Connection Test Script
================================
Tests connectivity to all required databases:
- PostgreSQL
- Neo4j
- Redis

This script is used by the production environment validation process.
"""

import os
import sys
import time
from typing import Dict, Tuple

# Color codes for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def log_info(message: str) -> None:
    """Log an info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def log_success(message: str) -> None:
    """Log a success message."""
    print(f"{Colors.GREEN}[✓]{Colors.NC} {message}")


def log_error(message: str) -> None:
    """Log an error message."""
    print(f"{Colors.RED}[✗]{Colors.NC} {message}")


def log_warning(message: str) -> None:
    """Log a warning message."""
    print(f"{Colors.YELLOW}[⚠]{Colors.NC} {message}")


def test_postgresql() -> Tuple[bool, str]:
    """
    Test PostgreSQL database connection.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        import psycopg2
        from psycopg2 import OperationalError
    except ImportError:
        return False, "psycopg2 library not installed (pip install psycopg2-binary)"
    
    # Get connection parameters from environment
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', '')
    database = os.getenv('POSTGRES_DB', 'postgres')
    
    if not password:
        return False, "POSTGRES_PASSWORD environment variable not set"
    
    try:
        log_info(f"Connecting to PostgreSQL at {host}:{port}...")
        
        # Attempt connection with timeout
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=10
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Connected successfully (PostgreSQL {version.split()[1]})"
        
    except OperationalError as e:
        return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def test_neo4j() -> Tuple[bool, str]:
    """
    Test Neo4j database connection.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        from neo4j import GraphDatabase
        from neo4j.exceptions import ServiceUnavailable, AuthError
    except ImportError:
        return False, "neo4j library not installed (pip install neo4j)"
    
    # Get connection parameters from environment
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', '')
    
    if not password:
        return False, "NEO4J_PASSWORD environment variable not set"
    
    try:
        log_info(f"Connecting to Neo4j at {uri}...")
        
        # Create driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verify connectivity
        driver.verify_connectivity()
        
        # Test query
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            record = result.single()
            version = record["versions"][0] if record else "unknown"
            edition = record["edition"] if record else "unknown"
        
        driver.close()
        
        return True, f"Connected successfully (Neo4j {version} {edition})"
        
    except AuthError:
        return False, "Authentication failed - check NEO4J_USER and NEO4J_PASSWORD"
    except ServiceUnavailable as e:
        return False, f"Service unavailable: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def test_redis() -> Tuple[bool, str]:
    """
    Test Redis connection.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        import redis
        from redis.exceptions import ConnectionError, AuthenticationError
    except ImportError:
        return False, "redis library not installed (pip install redis)"
    
    # Get connection parameters from environment
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', '6379'))
    password = os.getenv('REDIS_PASSWORD', '')
    db = int(os.getenv('REDIS_DB', '0'))
    
    if not password:
        return False, "REDIS_PASSWORD environment variable not set"
    
    try:
        log_info(f"Connecting to Redis at {host}:{port}...")
        
        # Create Redis client
        client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            socket_connect_timeout=10,
            socket_timeout=10
        )
        
        # Test connection
        client.ping()
        
        # Get server info
        info = client.info()
        version = info.get('redis_version', 'unknown')
        
        client.close()
        
        return True, f"Connected successfully (Redis {version})"
        
    except AuthenticationError:
        return False, "Authentication failed - check REDIS_PASSWORD"
    except ConnectionError as e:
        return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def main() -> int:
    """
    Main function to test all database connections.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("")
    print("=" * 50)
    print("Database Connection Tests")
    print("=" * 50)
    print("")
    
    results: Dict[str, Tuple[bool, str]] = {}
    
    # Test PostgreSQL
    log_info("Testing PostgreSQL connection...")
    success, message = test_postgresql()
    results['PostgreSQL'] = (success, message)
    if success:
        log_success(f"PostgreSQL: {message}")
    else:
        log_error(f"PostgreSQL: {message}")
    print("")
    
    # Test Neo4j
    log_info("Testing Neo4j connection...")
    success, message = test_neo4j()
    results['Neo4j'] = (success, message)
    if success:
        log_success(f"Neo4j: {message}")
    else:
        log_error(f"Neo4j: {message}")
    print("")
    
    # Test Redis
    log_info("Testing Redis connection...")
    success, message = test_redis()
    results['Redis'] = (success, message)
    if success:
        log_success(f"Redis: {message}")
    else:
        log_error(f"Redis: {message}")
    print("")
    
    # Summary
    print("=" * 50)
    print("Connection Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for success, _ in results.values() if success)
    failed_tests = total_tests - successful_tests
    
    for db_name, (success, message) in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if success else f"{Colors.RED}✗ FAIL{Colors.NC}"
        print(f"{db_name:15} {status}")
    
    print("")
    print(f"Total: {total_tests} | Passed: {Colors.GREEN}{successful_tests}{Colors.NC} | Failed: {Colors.RED}{failed_tests}{Colors.NC}")
    print("")
    
    if failed_tests > 0:
        log_error(f"{failed_tests} database connection(s) failed")
        print("")
        print("Troubleshooting tips:")
        print("1. Ensure all database services are running")
        print("2. Check that environment variables are correctly set")
        print("3. Verify network connectivity to database hosts")
        print("4. Check firewall rules and security groups")
        print("5. Verify credentials are correct")
        print("")
        return 1
    else:
        log_success("All database connections successful!")
        print("")
        return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

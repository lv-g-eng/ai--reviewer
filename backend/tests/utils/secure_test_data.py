"""
Secure test data utilities

Provides secure test data generation without hardcoded secrets.
All test passwords and sensitive data are generated dynamically.
"""
import os
import secrets
import string
from typing import Dict, Any
from unittest.mock import MagicMock


class SecureTestDataGenerator:
    """Generates secure test data without hardcoded secrets"""
    
    def __init__(self):
        """Initialize with secure random seed"""
        self._seed = secrets.randbits(32)
        self._passwords_cache = {}
    
    def get_test_password(self, identifier: str = "default") -> str:
        """
        Get a secure test password for the given identifier
        
        Args:
            identifier: Unique identifier for the password (e.g., "user1", "admin")
            
        Returns:
            Secure test password (consistent for same identifier)
        """
        if identifier not in self._passwords_cache:
            # Generate a secure password that meets requirements
            # Use identifier as seed for consistency in tests
            seed_value = hash(f"{self._seed}:{identifier}") % (2**32)
            
            # Create deterministic but secure password
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            password_parts = [
                secrets.choice(string.ascii_uppercase),  # At least one uppercase
                secrets.choice(string.ascii_lowercase),  # At least one lowercase  
                secrets.choice(string.digits),           # At least one digit
                secrets.choice("!@#$%^&*"),             # At least one special char
            ]
            
            # Add random characters to reach minimum length
            for _ in range(8):  # Total length will be 12
                password_parts.append(secrets.choice(chars))
            
            # Shuffle the parts
            secrets.SystemRandom().shuffle(password_parts)
            
            self._passwords_cache[identifier] = ''.join(password_parts)
        
        return self._passwords_cache[identifier]
    
    def get_test_email(self, identifier: str = "default") -> str:
        """
        Get a test email address
        
        Args:
            identifier: Unique identifier for the email
            
        Returns:
            Test email address
        """
        return f"test_{identifier}@example.com"
    
    def get_test_username(self, identifier: str = "default") -> str:
        """
        Get a test username
        
        Args:
            identifier: Unique identifier for the username
            
        Returns:
            Test username
        """
        return f"test_user_{identifier}"
    
    def get_test_database_config(self) -> Dict[str, Any]:
        """
        Get test database configuration
        
        Returns:
            Test database configuration dictionary
        """
        return {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": self.get_test_password("database")
        }
    
    def get_test_redis_config(self) -> Dict[str, Any]:
        """
        Get test Redis configuration
        
        Returns:
            Test Redis configuration dictionary
        """
        return {
            "host": "localhost", 
            "port": 6379,
            "db": 0,
            "password": self.get_test_password("redis")
        }
    
    def get_test_neo4j_config(self) -> Dict[str, Any]:
        """
        Get test Neo4j configuration
        
        Returns:
            Test Neo4j configuration dictionary
        """
        return {
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": self.get_test_password("neo4j"),
            "database": "neo4j"
        }
    
    def get_test_jwt_secret(self) -> str:
        """
        Get test JWT secret
        
        Returns:
            Test JWT secret (32+ characters)
        """
        return secrets.token_urlsafe(32)
    
    def get_test_api_key(self, service: str = "default") -> str:
        """
        Get test API key for a service
        
        Args:
            service: Service name (e.g., "openai", "github")
            
        Returns:
            Test API key
        """
        prefix_map = {
            "openai": "sk-",
            "github": "ghp_",
            "anthropic": "sk-ant-",
            "default": "test_"
        }
        
        prefix = prefix_map.get(service, "test_")
        return f"{prefix}{secrets.token_urlsafe(32)}"
    
    def get_mock_environment_variables(self) -> Dict[str, MagicMock]:
        """
        Get mock environment variables for testing
        
        Returns:
            Dictionary of mock environment variables
        """
        return {
            "POSTGRES_HOST": MagicMock(value="localhost"),
            "POSTGRES_PORT": MagicMock(value=5432),
            "POSTGRES_USER": MagicMock(value=self.get_test_username("postgres")),
            "POSTGRES_PASSWORD": MagicMock(value=self.get_test_password("postgres")),
            "POSTGRES_DB": MagicMock(value="test_db"),
            
            "REDIS_HOST": MagicMock(value="localhost"),
            "REDIS_PORT": MagicMock(value=6379),
            "REDIS_PASSWORD": MagicMock(value=self.get_test_password("redis")),
            
            "NEO4J_URI": MagicMock(value="bolt://localhost:7687"),
            "NEO4J_USER": MagicMock(value="neo4j"),
            "NEO4J_PASSWORD": MagicMock(value=self.get_test_password("neo4j")),
            
            "JWT_SECRET": MagicMock(value=self.get_test_jwt_secret()),
            "SECRET_KEY": MagicMock(value=self.get_test_jwt_secret()),
            
            "OPENAI_API_KEY": MagicMock(value=self.get_test_api_key("openai")),
            "GITHUB_TOKEN": MagicMock(value=self.get_test_api_key("github")),
            "ANTHROPIC_API_KEY": MagicMock(value=self.get_test_api_key("anthropic")),
            
            "NEXT_PUBLIC_API_URL": MagicMock(value="http://localhost:8000/api/v1"),
            "NEXTAUTH_URL": MagicMock(value="http://localhost:3000"),
            "NEXTAUTH_SECRET": MagicMock(value=self.get_test_jwt_secret()),
        }
    
    def create_test_user_data(self, identifier: str = "default") -> Dict[str, Any]:
        """
        Create test user data
        
        Args:
            identifier: Unique identifier for the user
            
        Returns:
            Test user data dictionary
        """
        return {
            "email": self.get_test_email(identifier),
            "password": self.get_test_password(identifier),
            "username": self.get_test_username(identifier),
            "full_name": f"Test User {identifier.title()}",
            "is_active": True
        }


# Global instance for consistent test data
_test_data_generator = SecureTestDataGenerator()


def get_test_password(identifier: str = "default") -> str:
    """Get a secure test password"""
    return _test_data_generator.get_test_password(identifier)


def get_test_email(identifier: str = "default") -> str:
    """Get a test email address"""
    return _test_data_generator.get_test_email(identifier)


def get_test_username(identifier: str = "default") -> str:
    """Get a test username"""
    return _test_data_generator.get_test_username(identifier)


def get_test_database_config() -> Dict[str, Any]:
    """Get test database configuration"""
    return _test_data_generator.get_test_database_config()


def get_test_redis_config() -> Dict[str, Any]:
    """Get test Redis configuration"""
    return _test_data_generator.get_test_redis_config()


def get_test_neo4j_config() -> Dict[str, Any]:
    """Get test Neo4j configuration"""
    return _test_data_generator.get_test_neo4j_config()


def get_test_jwt_secret() -> str:
    """Get test JWT secret"""
    return _test_data_generator.get_test_jwt_secret()


def get_test_api_key(service: str = "default") -> str:
    """Get test API key"""
    return _test_data_generator.get_test_api_key(service)


def get_mock_environment_variables() -> Dict[str, MagicMock]:
    """Get mock environment variables"""
    return _test_data_generator.get_mock_environment_variables()


def create_test_user_data(identifier: str = "default") -> Dict[str, Any]:
    """Create test user data"""
    return _test_data_generator.create_test_user_data(identifier)


# Constants for backward compatibility (but using secure generation)
TEST_PASSWORD = get_test_password("legacy")
TEST_USER = get_test_username("legacy") 
TEST_DB = "test_database_db"
TEST_API_KEY = get_test_api_key("legacy")
TEST_TOKEN = get_test_jwt_secret()[:24]  # Truncate for token format
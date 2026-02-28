"""
Unit tests for error_sanitizer utility
"""
import pytest
from app.utils.error_sanitizer import (
    sanitize_password_error,
    get_generic_auth_error,
    get_generic_password_error,
    sanitize_exception_message,
    is_safe_error_message
)


class TestErrorSanitizer:
    """Test suite for error_sanitizer utility"""
    
    def test_sanitize_password_error_with_bcrypt(self):
        """Test sanitizing error containing bcrypt details"""
        error_msg = "bcrypt hash verification failed"
        
        sanitized = sanitize_password_error(error_msg)
        
        assert 'bcrypt' not in sanitized.lower()
        assert 'error occurred' in sanitized.lower()
    
    def test_sanitize_password_error_with_salt(self):
        """Test sanitizing error containing salt information"""
        error_msg = "Invalid salt value provided"
        
        sanitized = sanitize_password_error(error_msg)
        
        assert 'salt' not in sanitized.lower()
    
    def test_sanitize_password_error_with_hash(self):
        """Test sanitizing error containing hash information"""
        error_msg = "Hash algorithm not supported"
        
        sanitized = sanitize_password_error(error_msg)
        
        assert 'hash' not in sanitized.lower()
    
    def test_sanitize_password_error_safe_message(self):
        """Test that safe messages pass through"""
        error_msg = "Password must be at least 8 characters"
        
        sanitized = sanitize_password_error(error_msg)
        
        assert sanitized == error_msg
    
    def test_get_generic_auth_error(self):
        """Test getting generic authentication error"""
        error = get_generic_auth_error()
        
        assert 'email' in error.lower() or 'password' in error.lower()
        assert 'incorrect' in error.lower()
    
    def test_get_generic_password_error(self):
        """Test getting generic password error"""
        error = get_generic_password_error()
        
        assert 'error occurred' in error.lower()
        assert 'password' in error.lower()
    
    def test_sanitize_exception_message_with_traceback(self):
        """Test sanitizing exception with traceback"""
        exception = Exception("Traceback (most recent call last): File 'test.py'")
        
        sanitized = sanitize_exception_message(exception)
        
        assert 'Traceback' not in sanitized
        assert 'error occurred' in sanitized.lower()
    
    def test_sanitize_exception_message_with_bcrypt(self):
        """Test sanitizing exception with bcrypt details"""
        exception = Exception("bcrypt error in password verification")
        
        sanitized = sanitize_exception_message(exception)
        
        assert 'bcrypt' not in sanitized.lower()
    
    def test_sanitize_exception_message_safe(self):
        """Test sanitizing safe exception message"""
        exception = Exception("Invalid input provided")
        
        sanitized = sanitize_exception_message(exception)
        
        assert sanitized == "Invalid input provided"
    
    def test_is_safe_error_message_with_bcrypt(self):
        """Test checking unsafe message with bcrypt"""
        message = "bcrypt hash failed"
        
        is_safe = is_safe_error_message(message)
        
        assert is_safe is False
    
    def test_is_safe_error_message_with_salt(self):
        """Test checking unsafe message with salt"""
        message = "Invalid salt rounds"
        
        is_safe = is_safe_error_message(message)
        
        assert is_safe is False
    
    def test_is_safe_error_message_safe(self):
        """Test checking safe message"""
        message = "Password must be at least 8 characters"
        
        is_safe = is_safe_error_message(message)
        
        assert is_safe is True
    
    def test_sanitize_password_error_with_algorithm(self):
        """Test sanitizing error with algorithm details"""
        error_msg = "Unsupported algorithm specified"
        
        sanitized = sanitize_password_error(error_msg)
        
        assert 'algorithm' not in sanitized.lower()
    
    def test_sanitize_password_error_with_rounds(self):
        """Test sanitizing error with rounds information"""
        error_msg = "Invalid rounds parameter"
        
        sanitized = sanitize_password_error(error_msg)
        
        assert 'rounds' not in sanitized.lower()
    
    def test_sanitize_exception_message_with_file_path(self):
        """Test sanitizing exception with file path"""
        exception = Exception('File "/app/auth.py", line 42')
        
        sanitized = sanitize_exception_message(exception)
        
        assert 'File "' not in sanitized
    
    def test_is_safe_error_message_with_traceback(self):
        """Test checking unsafe message with traceback"""
        message = "Traceback: error in module"
        
        is_safe = is_safe_error_message(message)
        
        assert is_safe is False
    
    def test_is_safe_error_message_empty(self):
        """Test checking empty message"""
        message = ""
        
        is_safe = is_safe_error_message(message)
        
        assert is_safe is True

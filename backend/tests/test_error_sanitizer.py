"""
Tests for error sanitization utilities
Validates that error messages don't expose implementation details (Requirement 2.5)
"""
import pytest
from app.utils.error_sanitizer import (
    sanitize_password_error,
    get_generic_auth_error,
    get_generic_password_error,
    sanitize_exception_message,
    is_safe_error_message
)


class TestErrorSanitization:
    """Test error message sanitization (Requirement 2.5)"""
    
    def test_sanitize_bcrypt_error(self):
        """Test that bcrypt-related errors are sanitized"""
        error_messages = [
            "bcrypt error occurred",
            "Invalid bcrypt hash",
            "Bcrypt rounds must be between 4 and 31",
            "Error in bcrypt algorithm",
        ]
        
        for error in error_messages:
            sanitized = sanitize_password_error(error)
            assert "bcrypt" not in sanitized.lower(), \
                f"Sanitized error should not contain 'bcrypt': {sanitized}"
            assert sanitized == "An error occurred during password processing. Please try again.", \
                f"Should return generic error message"
    
    def test_sanitize_salt_error(self):
        """Test that salt-related errors are sanitized"""
        error_messages = [
            "Invalid salt value",
            "Salt generation failed",
            "Error with salt rounds",
        ]
        
        for error in error_messages:
            sanitized = sanitize_password_error(error)
            assert "salt" not in sanitized.lower(), \
                f"Sanitized error should not contain 'salt': {sanitized}"
    
    def test_sanitize_hash_error(self):
        """Test that hash-related errors are sanitized"""
        error_messages = [
            "Hash verification failed",
            "Invalid hash format",
            "Hash algorithm error",
            "$2b$12$invalid_hash_here",
        ]
        
        for error in error_messages:
            sanitized = sanitize_password_error(error)
            assert "hash" not in sanitized.lower(), \
                f"Sanitized error should not contain 'hash': {sanitized}"
    
    def test_sanitize_rounds_error(self):
        """Test that rounds-related errors are sanitized"""
        error_messages = [
            "Invalid rounds value",
            "Rounds must be at least 12",
            "Error with round configuration",
        ]
        
        for error in error_messages:
            sanitized = sanitize_password_error(error)
            assert "round" not in sanitized.lower(), \
                f"Sanitized error should not contain 'round': {sanitized}"
    
    def test_sanitize_algorithm_error(self):
        """Test that algorithm-related errors are sanitized"""
        error_messages = [
            "Algorithm not supported",
            "Invalid algorithm configuration",
            "Error in hashing algorithm",
        ]
        
        for error in error_messages:
            sanitized = sanitize_password_error(error)
            assert "algorithm" not in sanitized.lower(), \
                f"Sanitized error should not contain 'algorithm': {sanitized}"
    
    def test_sanitize_passlib_error(self):
        """Test that passlib-related errors are sanitized"""
        error_messages = [
            "passlib.exc.InvalidHashError",
            "Error in passlib context",
            "CryptContext configuration error",
        ]
        
        for error in error_messages:
            sanitized = sanitize_password_error(error)
            assert "passlib" not in sanitized.lower(), \
                f"Sanitized error should not contain 'passlib': {sanitized}"
            assert "cryptcontext" not in sanitized.lower(), \
                f"Sanitized error should not contain 'cryptcontext': {sanitized}"
    
    def test_sanitize_exception_details(self):
        """Test that exception details are sanitized"""
        error_messages = [
            "ValueError: Invalid password",
            "Exception occurred in password processing",
            "Traceback (most recent call last):",
            'File "/app/utils/password.py", line 42',
        ]
        
        for error in error_messages:
            sanitized = sanitize_password_error(error)
            assert "ValueError" not in sanitized, \
                f"Sanitized error should not contain 'ValueError': {sanitized}"
            assert "Exception" not in sanitized, \
                f"Sanitized error should not contain 'Exception': {sanitized}"
            assert "Traceback" not in sanitized, \
                f"Sanitized error should not contain 'Traceback': {sanitized}"
            assert "File" not in sanitized or "line" not in sanitized, \
                f"Sanitized error should not contain stack trace: {sanitized}"
    
    def test_safe_error_messages_pass_through(self):
        """Test that safe error messages are not modified"""
        safe_messages = [
            "Password must be at least 8 characters long",
            "Password must contain at least one uppercase letter",
            "Password must contain at least one digit",
            "Password must contain at least one special character",
        ]
        
        for message in safe_messages:
            sanitized = sanitize_password_error(message)
            assert sanitized == message, \
                f"Safe message should pass through unchanged: {message}"


class TestGenericErrorMessages:
    """Test generic error message functions"""
    
    def test_generic_auth_error(self):
        """Test generic authentication error message"""
        error = get_generic_auth_error()
        
        assert error == "Incorrect email or password", \
            "Should return generic auth error"
        assert "email" in error.lower() and "password" in error.lower(), \
            "Should mention both email and password to prevent enumeration"
    
    def test_generic_password_error(self):
        """Test generic password error message"""
        error = get_generic_password_error()
        
        assert "error occurred" in error.lower(), \
            "Should indicate an error occurred"
        assert "try again" in error.lower(), \
            "Should suggest trying again"
        # Should not contain technical details
        assert "bcrypt" not in error.lower()
        assert "hash" not in error.lower()
        assert "salt" not in error.lower()


class TestExceptionSanitization:
    """Test exception message sanitization"""
    
    def test_sanitize_exception_with_sensitive_info(self):
        """Test sanitizing exceptions with sensitive information"""
        exceptions = [
            ValueError("bcrypt error"),
            RuntimeError("Invalid hash format"),
            Exception("Salt generation failed"),
        ]
        
        for exc in exceptions:
            sanitized = sanitize_exception_message(exc)
            assert sanitized == get_generic_password_error(), \
                f"Exception with sensitive info should return generic error: {exc}"
    
    def test_sanitize_exception_with_stack_trace(self):
        """Test sanitizing exceptions with stack traces"""
        error_with_trace = """Traceback (most recent call last):
  File "/app/utils/password.py", line 42, in hash_password
    return pwd_context.hash(password)
ValueError: Invalid password"""
        
        exc = ValueError(error_with_trace)
        sanitized = sanitize_exception_message(exc)
        
        assert "Traceback" not in sanitized, \
            "Sanitized message should not contain stack trace"
        assert sanitized == get_generic_password_error(), \
            "Should return generic error for stack traces"
    
    def test_sanitize_safe_exception(self):
        """Test that safe exceptions are preserved"""
        safe_exceptions = [
            ValueError("Password too short"),
            ValueError("Missing required field"),
        ]
        
        for exc in safe_exceptions:
            sanitized = sanitize_exception_message(exc)
            assert sanitized == str(exc), \
                f"Safe exception should be preserved: {exc}"


class TestSafeErrorMessageCheck:
    """Test safe error message checking"""
    
    def test_unsafe_messages_detected(self):
        """Test that unsafe messages are detected"""
        unsafe_messages = [
            "bcrypt error",
            "Invalid salt",
            "Hash verification failed",
            "Algorithm not supported",
            "passlib exception",
            "CryptContext error",
            "$2b$12$hash",
            "ValueError occurred",
            "Traceback:",
        ]
        
        for message in unsafe_messages:
            assert not is_safe_error_message(message), \
                f"Message should be detected as unsafe: {message}"
    
    def test_safe_messages_detected(self):
        """Test that safe messages are detected"""
        safe_messages = [
            "Password must be at least 8 characters long",
            "Password must contain at least one uppercase letter",
            "Password must contain at least one lowercase letter",
            "Password must contain at least one digit",
            "Password must contain at least one special character",
            "Incorrect email or password",
            "User account is inactive",
        ]
        
        for message in safe_messages:
            assert is_safe_error_message(message), \
                f"Message should be detected as safe: {message}"
    
    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive"""
        messages = [
            "BCRYPT error",
            "Invalid SALT",
            "Hash VERIFICATION failed",
        ]
        
        for message in messages:
            assert not is_safe_error_message(message), \
                f"Detection should be case-insensitive: {message}"


class TestUserEnumerationPrevention:
    """Test that error messages prevent user enumeration"""
    
    def test_login_error_same_for_invalid_email_and_password(self):
        """Test that login errors don't reveal if email exists"""
        # Both invalid email and invalid password should return same error
        error = get_generic_auth_error()
        
        # Error should not distinguish between:
        # - Email doesn't exist
        # - Email exists but password is wrong
        assert "email" in error.lower() and "password" in error.lower(), \
            "Error should mention both email and password"
        assert "incorrect" in error.lower(), \
            "Error should use generic 'incorrect' term"
    
    def test_no_user_exists_hint(self):
        """Test that errors don't hint if user exists"""
        error = get_generic_auth_error()
        
        # Should not contain phrases that reveal user existence
        forbidden_phrases = [
            "user not found",
            "email not found",
            "account does not exist",
            "no such user",
            "invalid email",
            "wrong password",
        ]
        
        error_lower = error.lower()
        for phrase in forbidden_phrases:
            assert phrase not in error_lower, \
                f"Error should not contain '{phrase}' to prevent enumeration"


class TestSecurityRequirements:
    """Test that security requirements are met"""
    
    def test_requirement_2_5_no_bcrypt_exposure(self):
        """Test Requirement 2.5: Don't expose bcrypt details"""
        errors = [
            "bcrypt rounds error",
            "Invalid bcrypt configuration",
            "$2b$12$salthashhere",
        ]
        
        for error in errors:
            sanitized = sanitize_password_error(error)
            assert "bcrypt" not in sanitized.lower(), \
                "Requirement 2.5: Should not expose bcrypt details"
            assert "$2" not in sanitized, \
                "Requirement 2.5: Should not expose bcrypt hash format"
    
    def test_requirement_2_5_no_salt_exposure(self):
        """Test Requirement 2.5: Don't expose salt information"""
        errors = [
            "Salt generation failed",
            "Invalid salt rounds",
            "Salt value error",
        ]
        
        for error in errors:
            sanitized = sanitize_password_error(error)
            assert "salt" not in sanitized.lower(), \
                "Requirement 2.5: Should not expose salt information"
    
    def test_requirement_2_5_no_implementation_details(self):
        """Test Requirement 2.5: Don't expose implementation details"""
        errors = [
            "passlib.exc.InvalidHashError",
            "CryptContext configuration error",
            "pwd_context.hash() failed",
        ]
        
        for error in errors:
            sanitized = sanitize_password_error(error)
            assert "passlib" not in sanitized.lower(), \
                "Requirement 2.5: Should not expose passlib details"
            assert "cryptcontext" not in sanitized.lower(), \
                "Requirement 2.5: Should not expose CryptContext details"
            assert "pwd_context" not in sanitized.lower(), \
                "Requirement 2.5: Should not expose internal variable names"
    
    def test_requirement_2_5_user_enumeration_prevention(self):
        """Test Requirement 2.5: Prevent user enumeration"""
        # Generic auth error should not reveal if email exists
        error = get_generic_auth_error()
        
        # Should be generic enough to not distinguish between:
        # - User doesn't exist
        # - User exists but password wrong
        assert error == "Incorrect email or password", \
            "Requirement 2.5: Should use generic error to prevent enumeration"

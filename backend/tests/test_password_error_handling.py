"""
Tests for secure error handling in password operations
Validates Requirement 2.5: Secure error handling for password operations
"""
import pytest
from unittest.mock import patch
from app.utils.password import hash_password, verify_password
from app.utils.error_sanitizer import get_generic_password_error
from backend.tests.utils.secure_test_data import get_test_password, get_test_jwt_secret, get_test_api_key


class TestPasswordHashingErrorHandling:
    """Test error handling in password hashing (Requirement 2.5)"""
    
    def test_hash_password_handles_exception_gracefully(self):
        """Test that hash_password handles exceptions without exposing details"""
        # Mock pwd_context.hash to raise an exception
        with patch('app.utils.password.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = ValueError("bcrypt rounds must be between 4 and 31")
            
            # Should raise ValueError with sanitized message
            with pytest.raises(ValueError) as exc_info:
                hash_password("TestPassword123!")
            
            # Error message should be generic, not expose bcrypt details
            error_message = str(exc_info.value)
            assert "bcrypt" not in error_message.lower(), \
                "Error should not expose bcrypt details"
            assert "rounds" not in error_message.lower(), \
                "Error should not expose rounds information"
            assert error_message == get_generic_password_error(), \
                "Should return generic password error"
    
    def test_hash_password_handles_runtime_error(self):
        """Test that hash_password handles RuntimeError gracefully"""
        with patch('app.utils.password.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = RuntimeError("Internal hashing error with salt")
            
            with pytest.raises(ValueError) as exc_info:
                hash_password("TestPassword123!")
            
            error_message = str(exc_info.value)
            assert "salt" not in error_message.lower(), \
                "Error should not expose salt information"
            assert "RuntimeError" not in error_message, \
                "Error should not expose exception type"
    
    def test_hash_password_handles_generic_exception(self):
        """Test that hash_password handles any exception gracefully"""
        with patch('app.utils.password.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = Exception("Unexpected error in passlib")
            
            with pytest.raises(ValueError) as exc_info:
                hash_password("TestPassword123!")
            
            error_message = str(exc_info.value)
            assert "passlib" not in error_message.lower(), \
                "Error should not expose passlib details"
            assert error_message == get_generic_password_error(), \
                "Should return generic password error"
    
    def test_hash_password_logs_error_without_exposing(self):
        """Test that errors are logged server-side but not exposed to user"""
        with patch('app.utils.password.pwd_context.hash') as mock_hash, \
             patch('app.utils.password.logger') as mock_logger:
            mock_hash.side_effect = ValueError("bcrypt configuration error")
            
            with pytest.raises(ValueError):
                hash_password("TestPassword123!")
            
            # Logger should be called (server-side logging)
            assert mock_logger.error.called, \
                "Error should be logged server-side"
            
            # But the raised exception should have generic message
            # (verified in other tests)


class TestPasswordVerificationErrorHandling:
    """Test error handling in password verification (Requirement 2.5)"""
    
    def test_verify_password_handles_invalid_hash_gracefully(self):
        """Test that verify_password returns False for invalid hash"""
        # Invalid hash formats should return False, not raise
        invalid_hashes = [
            "not_a_valid_hash",
            "$2b$invalid",
            "plaintext_password",
            "",
            "$2a$10$tooshort",
        ]
        
        for invalid_hash in invalid_hashes:
            result = verify_password("TestPassword123!", invalid_hash)
            assert result is False, \
                f"Invalid hash should return False, not raise: {invalid_hash}"
    
    def test_verify_password_handles_exception_gracefully(self):
        """Test that verify_password handles exceptions without exposing details"""
        with patch('app.utils.password.pwd_context.verify') as mock_verify:
            mock_verify.side_effect = ValueError("Invalid bcrypt hash format")
            
            # Should return False, not raise
            result = verify_password("TestPassword123!", "$2b$12$somehash")
            
            assert result is False, \
                "Exception should be caught and return False"
    
    def test_verify_password_handles_runtime_error(self):
        """Test that verify_password handles RuntimeError gracefully"""
        with patch('app.utils.password.pwd_context.verify') as mock_verify:
            mock_verify.side_effect = RuntimeError("Hash verification failed")
            
            result = verify_password("TestPassword123!", "$2b$12$somehash")
            
            assert result is False, \
                "RuntimeError should be caught and return False"
    
    def test_verify_password_logs_error_without_exposing(self):
        """Test that verification errors are logged but not exposed"""
        with patch('app.utils.password.pwd_context.verify') as mock_verify, \
             patch('app.utils.password.logger') as mock_logger:
            mock_verify.side_effect = ValueError("bcrypt error")
            
            result = verify_password("TestPassword123!", "$2b$12$somehash")
            
            # Should return False
            assert result is False
            
            # Logger should be called (server-side logging)
            assert mock_logger.warning.called, \
                "Error should be logged server-side"
    
    def test_verify_password_no_timing_attack_on_error(self):
        """Test that errors don't create timing attack vectors"""
        # Both invalid hash and exception should return False quickly
        # (We can't test timing directly, but we verify behavior is consistent)
        
        invalid_hash = "not_a_hash"
        result1 = verify_password("TestPassword123!", invalid_hash)
        
        with patch('app.utils.password.pwd_context.verify') as mock_verify:
            mock_verify.side_effect = ValueError("error")
            result2 = verify_password("TestPassword123!", "$2b$12$hash")
        
        # Both should return False
        assert result1 is False
        assert result2 is False


class TestErrorHandlingIntegration:
    """Integration tests for error handling in password operations"""
    
    def test_hash_and_verify_with_error_recovery(self):
        """Test that system recovers gracefully from errors"""
        # First attempt fails
        with patch('app.utils.password.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = ValueError("error")
            
            with pytest.raises(ValueError):
                hash_password("TestPassword123!")
        
        # Second attempt succeeds (mock is removed)
        # This simulates transient errors
        hashed = hash_password("TestPassword123!")
        assert hashed is not None
        assert verify_password("TestPassword123!", hashed)
    
    def test_verify_with_corrupted_hash(self):
        """Test verification with corrupted hash data"""
        # Create a valid hash
        password = get_test_password("test_password")
        hashed = hash_password(password)
        
        # Corrupt the hash
        corrupted_hashes = [
            hashed[:-5],  # Truncated
            hashed + "extra",  # Extended
            hashed.replace('$', '#'),  # Modified delimiter
            hashed[:30] + "X" * 30,  # Partially corrupted
        ]
        
        for corrupted in corrupted_hashes:
            result = verify_password(password, corrupted)
            assert result is False, \
                f"Corrupted hash should return False: {corrupted[:20]}..."


class TestSecurityRequirements:
    """Test that security requirements are met"""
    
    def test_requirement_2_5_generic_error_on_hash_failure(self):
        """Test Requirement 2.5: Return generic error on hash failure"""
        with patch('app.utils.password.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = ValueError("bcrypt rounds error")
            
            with pytest.raises(ValueError) as exc_info:
                hash_password("TestPassword123!")
            
            error = str(exc_info.value)
            # Should not expose bcrypt, rounds, salt, etc.
            assert "bcrypt" not in error.lower()
            assert "rounds" not in error.lower()
            assert "salt" not in error.lower()
            assert error == get_generic_password_error()
    
    def test_requirement_2_5_no_exception_details_exposed(self):
        """Test Requirement 2.5: Don't expose exception details"""
        with patch('app.utils.password.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = RuntimeError("Internal error in passlib.hash.bcrypt")
            
            with pytest.raises(ValueError) as exc_info:
                hash_password("TestPassword123!")
            
            error = str(exc_info.value)
            # Should not expose internal details
            assert "RuntimeError" not in error
            assert "passlib" not in error.lower()
            assert "internal" not in error.lower()
    
    def test_requirement_2_5_verify_returns_false_not_exception(self):
        """Test Requirement 2.5: verify_password returns False, not exception"""
        with patch('app.utils.password.pwd_context.verify') as mock_verify:
            mock_verify.side_effect = ValueError("Invalid hash")
            
            # Should not raise, should return False
            result = verify_password("TestPassword123!", "$2b$12$hash")
            assert result is False
    
    def test_requirement_2_5_no_information_disclosure(self):
        """Test Requirement 2.5: No information disclosure in errors"""
        # Test various error scenarios
        error_scenarios = [
            ("bcrypt error", "bcrypt"),
            ("salt generation failed", "salt"),
            ("invalid hash format", "hash"),
            ("algorithm not supported", "algorithm"),
        ]
        
        for error_msg, forbidden_word in error_scenarios:
            with patch('app.utils.password.pwd_context.hash') as mock_hash:
                mock_hash.side_effect = ValueError(error_msg)
                
                with pytest.raises(ValueError) as exc_info:
                    hash_password("TestPassword123!")
                
                error = str(exc_info.value)
                assert forbidden_word not in error.lower(), \
                    f"Error should not contain '{forbidden_word}': {error}"


class TestErrorLogging:
    """Test that errors are properly logged for debugging"""
    
    def test_hash_error_logged_with_type(self):
        """Test that hash errors are logged with exception type"""
        with patch('app.utils.password.pwd_context.hash') as mock_hash, \
             patch('app.utils.password.logger') as mock_logger:
            mock_hash.side_effect = ValueError("error")
            
            with pytest.raises(ValueError):
                hash_password("TestPassword123!")
            
            # Should log the error type for debugging
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "ValueError" in call_args, \
                "Should log exception type for debugging"
    
    def test_verify_error_logged_with_type(self):
        """Test that verify errors are logged with exception type"""
        with patch('app.utils.password.pwd_context.verify') as mock_verify, \
             patch('app.utils.password.logger') as mock_logger:
            mock_verify.side_effect = RuntimeError("error")
            
            verify_password("TestPassword123!", "$2b$12$hash")
            
            # Should log the error type for debugging
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            assert "RuntimeError" in call_args, \
                "Should log exception type for debugging"
    
    def test_logging_does_not_include_password(self):
        """Test that logging never includes the password"""
        with patch('app.utils.password.pwd_context.hash') as mock_hash, \
             patch('app.utils.password.logger') as mock_logger:
            mock_hash.side_effect = ValueError("error")
            
            password = get_test_password("secret_password")
            with pytest.raises(ValueError):
                hash_password(password)
            
            # Check that password is not in any log call
            for call in mock_logger.error.call_args_list:
                log_message = str(call)
                assert password not in log_message, \
                    "Password should never be logged"

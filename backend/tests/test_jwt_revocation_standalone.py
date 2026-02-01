"""
Standalone tests for JWT token revocation
These tests can run independently without full app setup
"""
import pytest
import sys
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
)


class TestJWTRevocationLogic:
    """Test JWT token revocation logic with mocked Redis"""
    
    @pytest.mark.asyncio
    async def test_revoke_token_stores_jti_in_redis(self):
        """Test that revoking a token stores JTI in Redis with correct TTL"""
        from app.utils.jwt import revoke_token
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            jti = "test-jti-12345"
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            
            # Revoke the token
            await revoke_token(jti, expires_at)
            
            # Verify Redis set was called with correct parameters
            mock_redis.set.assert_called_once()
            call_args = mock_redis.set.call_args
            
            # Check key format
            assert call_args[0][0] == f"revoked:jti:{jti}"
            # Check value
            assert call_args[0][1] == "1"
            # Check TTL is approximately 1 hour (3600 seconds, allow some tolerance)
            assert 3595 <= call_args[1]['ex'] <= 3605
    
    @pytest.mark.asyncio
    async def test_is_token_revoked_checks_redis(self):
        """Test that is_token_revoked checks Redis for JTI"""
        from app.utils.jwt import is_token_revoked
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)  # Token exists (revoked)
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            jti = "test-jti-12345"
            
            # Check if token is revoked
            is_revoked = await is_token_revoked(jti)
            
            # Should return True
            assert is_revoked is True
            
            # Verify Redis exists was called with correct key
            mock_redis.exists.assert_called_once_with(f"revoked:jti:{jti}")
    
    @pytest.mark.asyncio
    async def test_is_token_revoked_returns_false_when_not_in_redis(self):
        """Test that is_token_revoked returns False when JTI not in Redis"""
        from app.utils.jwt import is_token_revoked
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)  # Token doesn't exist (not revoked)
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            jti = "non-existent-jti"
            
            # Check if token is revoked
            is_revoked = await is_token_revoked(jti)
            
            # Should return False
            assert is_revoked is False
    
    @pytest.mark.asyncio
    async def test_verify_token_with_revocation_rejects_revoked_token(self):
        """Test that verify_token_with_revocation rejects revoked tokens"""
        from app.utils.jwt import verify_token_with_revocation
        
        # Create a token
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        # Mock Redis to indicate token is revoked
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)  # Token is revoked
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            # Token should be rejected
            verified = await verify_token_with_revocation(token, "access")
            assert verified is None, "Revoked token should be rejected"
    
    @pytest.mark.asyncio
    async def test_verify_token_with_revocation_accepts_non_revoked_token(self):
        """Test that verify_token_with_revocation accepts non-revoked tokens"""
        from app.utils.jwt import verify_token_with_revocation
        
        # Create a token
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        # Mock Redis to indicate token is not revoked
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)  # Token is not revoked
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            # Token should be accepted
            verified = await verify_token_with_revocation(token, "access")
            assert verified is not None, "Non-revoked token should be accepted"
            assert verified["sub"] == data["sub"]
            assert verified["user_id"] == data["user_id"]
    
    @pytest.mark.asyncio
    async def test_verify_token_with_revocation_checks_token_type(self):
        """Test that verify_token_with_revocation still validates token type"""
        from app.utils.jwt import verify_token_with_revocation
        
        # Create an access token
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Mock Redis to indicate token is not revoked
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            # Try to verify as refresh token (wrong type)
            verified = await verify_token_with_revocation(token, "refresh")
            assert verified is None, "Token type mismatch should be rejected"
    
    @pytest.mark.asyncio
    async def test_revoke_token_skips_expired_tokens(self):
        """Test that already-expired tokens are not added to Redis"""
        from app.utils.jwt import revoke_token
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            jti = "expired-token-jti"
            expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # Already expired
            
            # Try to revoke the expired token
            await revoke_token(jti, expires_at)
            
            # Redis set should NOT be called (no point storing expired tokens)
            mock_redis.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_revoke_token_handles_redis_errors_gracefully(self):
        """Test that revoke_token handles Redis errors without raising"""
        from app.utils.jwt import revoke_token
        
        # Mock Redis to raise an error
        with patch('app.utils.jwt.get_redis', side_effect=Exception("Redis connection failed")):
            jti = "test-error-handling"
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            
            # Should not raise an exception
            try:
                await revoke_token(jti, expires_at)
            except Exception:
                pytest.fail("revoke_token should handle Redis errors gracefully")
    
    @pytest.mark.asyncio
    async def test_is_token_revoked_fails_closed_on_redis_error(self):
        """Test that is_token_revoked returns True (fail closed) on Redis errors"""
        from app.utils.jwt import is_token_revoked
        
        # Mock Redis to raise an error
        with patch('app.utils.jwt.get_redis', side_effect=Exception("Redis connection failed")):
            jti = "test-fail-closed"
            
            # Should return True (fail closed for security)
            is_revoked = await is_token_revoked(jti)
            assert is_revoked is True, "Should fail closed on Redis errors"
    
    @pytest.mark.asyncio
    async def test_revoke_token_calculates_correct_ttl(self):
        """Test that TTL is calculated correctly based on expiration time"""
        from app.utils.jwt import revoke_token
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            jti = "test-ttl-calculation"
            # Token expires in 2 hours
            expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
            
            # Revoke the token
            await revoke_token(jti, expires_at)
            
            # Check TTL is approximately 2 hours (7200 seconds, allow some tolerance)
            call_args = mock_redis.set.call_args
            ttl = call_args[1]['ex']
            assert 7195 <= ttl <= 7205, f"Expected TTL ~7200s, got {ttl}s"
    
    @pytest.mark.asyncio
    async def test_verify_token_with_revocation_handles_token_without_jti(self):
        """Test that verify_token_with_revocation handles tokens without JTI gracefully"""
        from app.utils.jwt import verify_token_with_revocation
        from jose import jwt as jose_jwt
        from app.core.config import settings
        
        # Create a token without JTI (manually)
        data = {
            "sub": "test@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "type": "access"
            # No JTI field
        }
        token = jose_jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            # Should still validate (JTI is optional for backward compatibility)
            verified = await verify_token_with_revocation(token, "access")
            assert verified is not None, "Token without JTI should still be accepted"
            
            # Redis should not be checked if JTI is missing
            mock_redis.exists.assert_not_called()


class TestJWTRevocationIntegration:
    """Integration tests for JWT revocation with actual token flow"""
    
    @pytest.mark.asyncio
    async def test_full_revocation_flow(self):
        """Test complete flow: create token -> verify -> revoke -> verify again"""
        from app.utils.jwt import revoke_token, verify_token_with_revocation
        
        # Create a token
        data = {"sub": "test@example.com", "user_id": "123", "role": "user"}
        token = create_access_token(data)
        
        # Decode to get JTI and expiration
        payload = decode_token(token)
        jti = payload["jti"]
        exp_timestamp = payload["exp"]
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        mock_redis.exists = AsyncMock(side_effect=[0, 1])  # First call: not revoked, second: revoked
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            # Step 1: Token should be valid before revocation
            verified = await verify_token_with_revocation(token, "access")
            assert verified is not None, "Token should be valid before revocation"
            assert verified["sub"] == data["sub"]
            
            # Step 2: Revoke the token
            await revoke_token(jti, expires_at)
            
            # Step 3: Token should be rejected after revocation
            verified = await verify_token_with_revocation(token, "access")
            assert verified is None, "Revoked token should be rejected"
    
    @pytest.mark.asyncio
    async def test_multiple_tokens_independent_revocation(self):
        """Test that multiple tokens can be revoked independently"""
        from app.utils.jwt import revoke_token, is_token_revoked
        
        # Create multiple tokens
        data = {"sub": "test@example.com"}
        token1 = create_access_token(data)
        token2 = create_access_token(data)
        token3 = create_access_token(data)
        
        payload1 = decode_token(token1)
        payload2 = decode_token(token2)
        payload3 = decode_token(token3)
        
        jti1 = payload1["jti"]
        jti2 = payload2["jti"]
        jti3 = payload3["jti"]
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Mock Redis to track which JTIs are revoked
        revoked_jtis = set()
        
        async def mock_set(key, value, ex):
            jti = key.split(":")[-1]
            revoked_jtis.add(jti)
        
        async def mock_exists(key):
            jti = key.split(":")[-1]
            return 1 if jti in revoked_jtis else 0
        
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(side_effect=mock_set)
        mock_redis.exists = AsyncMock(side_effect=mock_exists)
        
        with patch('app.utils.jwt.get_redis', return_value=mock_redis):
            # Revoke only token1 and token3
            await revoke_token(jti1, expires_at)
            await revoke_token(jti3, expires_at)
            
            # Check revocation status
            assert await is_token_revoked(jti1) is True
            assert await is_token_revoked(jti2) is False
            assert await is_token_revoked(jti3) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

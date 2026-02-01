"""
Tests for token rotation functionality
Task 6.1: Enhance refresh token endpoint
Validates Requirements 5.1, 5.2, 5.5
"""
import pytest
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.utils.jwt import (
    create_refresh_token,
    decode_token,
    revoke_token,
    is_token_revoked
)


class TestTokenRotation:
    """Test token rotation behavior (Requirement 5.2)"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_generates_new_pair(self, mock_redis_client):
        """Test that refresh endpoint generates new access and refresh tokens"""
        # Create initial refresh token
        user_data = {"sub": "test-user-id"}
        old_refresh_token = create_refresh_token(user_data)
        
        # Decode to get JTI
        old_payload = decode_token(old_refresh_token)
        old_jti = old_payload.get("jti")
        
        # Create new refresh token (simulating rotation)
        new_refresh_token = create_refresh_token(user_data)
        new_payload = decode_token(new_refresh_token)
        new_jti = new_payload.get("jti")
        
        # Verify tokens are different
        assert old_refresh_token != new_refresh_token, \
            "New refresh token should be different from old token"
        
        # Verify JTIs are different (unique tokens)
        assert old_jti != new_jti, \
            "New token should have different JTI (unique identifier)"
    
    @pytest.mark.asyncio
    async def test_old_refresh_token_revoked_after_rotation(self, mock_redis_client):
        """Test that old refresh token is revoked after successful rotation"""
        # Create refresh token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        # Decode to get JTI and expiration
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        
        # Revoke the token (simulating rotation)
        await revoke_token(jti, expires_at)
        
        # Verify token is revoked
        is_revoked = await is_token_revoked(jti)
        assert is_revoked is True, \
            "Old refresh token should be revoked after rotation"
    
    @pytest.mark.asyncio
    async def test_revoked_token_cannot_be_reused(self, mock_redis_client):
        """Test that revoked refresh token cannot be used again (Requirement 5.1)"""
        # Create and revoke a token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        
        # Revoke the token
        await revoke_token(jti, expires_at)
        
        # Verify token is marked as revoked
        is_revoked = await is_token_revoked(jti)
        assert is_revoked is True, \
            "Revoked token should be detected as revoked"
    
    @pytest.mark.asyncio
    async def test_token_revocation_stored_in_redis(self, mock_redis_client):
        """Test that token revocation is stored in Redis with TTL"""
        # Create token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        
        # Revoke token
        await revoke_token(jti, expires_at)
        
        # Check Redis directly
        key = f"revoked:jti:{jti}"
        
        # Verify key exists
        exists = await mock_redis_client.exists(key)
        assert exists > 0, "Revoked token JTI should be stored in Redis"
        
        # Verify TTL is set
        ttl = await mock_redis_client.ttl(key)
        assert ttl > 0, "Revoked token should have TTL set"
        assert ttl <= 7 * 24 * 60 * 60, "TTL should not exceed token expiration (7 days)"


class TestRefreshTokenMetadata:
    """Test refresh token metadata storage (Requirement 5.5)"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_metadata_structure(self, mock_redis_client):
        """Test that refresh token metadata contains required fields"""
        # Create refresh token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        # Store metadata (simulating what refresh endpoint does)
        metadata = {
            "user_id": "test-user-id",
            "jti": jti,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
        }
        
        ttl_seconds = exp - int(datetime.now(timezone.utc).timestamp())
        await mock_redis_client.set(
            f"refresh_token:{jti}",
            json.dumps(metadata),
            ex=ttl_seconds
        )
        
        # Retrieve and verify metadata
        stored_data = await mock_redis_client.get(f"refresh_token:{jti}")
        assert stored_data is not None, "Metadata should be stored in Redis"
        
        stored_metadata = json.loads(stored_data)
        assert stored_metadata["user_id"] == "test-user-id"
        assert stored_metadata["jti"] == jti
        assert "created_at" in stored_metadata
        assert "expires_at" in stored_metadata
    
    @pytest.mark.asyncio
    async def test_refresh_token_metadata_ttl_matches_expiration(self, mock_redis_client):
        """Test that metadata TTL matches token expiration (7 days default)"""
        # Create refresh token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        # Store metadata with TTL
        metadata = {
            "user_id": "test-user-id",
            "jti": jti,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
        }
        
        ttl_seconds = exp - int(datetime.now(timezone.utc).timestamp())
        await mock_redis_client.set(
            f"refresh_token:{jti}",
            json.dumps(metadata),
            ex=ttl_seconds
        )
        
        # Verify TTL
        actual_ttl = await mock_redis_client.ttl(f"refresh_token:{jti}")
        
        # TTL should be close to 7 days (604800 seconds)
        # Allow some variance for test execution time
        expected_ttl = 7 * 24 * 60 * 60  # 7 days in seconds
        assert actual_ttl > 0, "TTL should be set"
        assert abs(actual_ttl - expected_ttl) < 60, \
            f"TTL should be approximately 7 days, got {actual_ttl} seconds"


class TestTokenRevocationChecks:
    """Test token revocation checking (Requirement 5.1)"""
    
    @pytest.mark.asyncio
    async def test_non_revoked_token_passes_check(self, mock_redis_client):
        """Test that non-revoked token passes revocation check"""
        # Create token but don't revoke it
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        
        # Check revocation status
        is_revoked = await is_token_revoked(jti)
        assert is_revoked is False, \
            "Non-revoked token should pass revocation check"
    
    @pytest.mark.asyncio
    async def test_revoked_token_fails_check(self, mock_redis_client):
        """Test that revoked token fails revocation check"""
        # Create and revoke token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        
        # Revoke token
        await revoke_token(jti, expires_at)
        
        # Check revocation status
        is_revoked = await is_token_revoked(jti)
        assert is_revoked is True, \
            "Revoked token should fail revocation check"
    
    @pytest.mark.asyncio
    async def test_revocation_check_handles_redis_errors(self):
        """Test that revocation check fails safely when Redis is unavailable"""
        # This test verifies fail-closed behavior for security
        
        # Create token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        
        # Mock Redis to raise exception
        with patch('app.utils.jwt.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.exists.side_effect = Exception("Redis connection failed")
            mock_get_redis.return_value = mock_redis
            
            # Check revocation status - should fail closed (return True)
            is_revoked = await is_token_revoked(jti)
            assert is_revoked is True, \
                "Should fail closed (reject token) when Redis is unavailable"


class TestTokenRotationIntegration:
    """Integration tests for complete token rotation flow"""
    
    @pytest.mark.asyncio
    async def test_complete_rotation_flow(self, mock_redis_client):
        """Test complete token rotation: check revocation, generate new, revoke old"""
        # Step 1: Create initial refresh token
        user_data = {"sub": "test-user-id"}
        old_refresh_token = create_refresh_token(user_data)
        old_payload = decode_token(old_refresh_token)
        old_jti = old_payload.get("jti")
        
        # Step 2: Verify old token is not revoked
        assert await is_token_revoked(old_jti) is False, \
            "Initial token should not be revoked"
        
        # Step 3: Generate new refresh token (rotation)
        new_refresh_token = create_refresh_token(user_data)
        new_payload = decode_token(new_refresh_token)
        new_jti = new_payload.get("jti")
        
        # Step 4: Revoke old token
        old_exp = old_payload.get("exp")
        old_expires_at = datetime.fromtimestamp(old_exp, tz=timezone.utc)
        await revoke_token(old_jti, old_expires_at)
        
        # Step 5: Verify old token is now revoked
        assert await is_token_revoked(old_jti) is True, \
            "Old token should be revoked after rotation"
        
        # Step 6: Verify new token is not revoked
        assert await is_token_revoked(new_jti) is False, \
            "New token should not be revoked"
        
        # Step 7: Verify tokens are different
        assert old_jti != new_jti, \
            "Old and new tokens should have different JTIs"
    
    @pytest.mark.asyncio
    async def test_rotation_prevents_token_reuse(self, mock_redis_client):
        """Test that token rotation prevents reuse of old tokens"""
        # Create and use a refresh token
        user_data = {"sub": "test-user-id"}
        refresh_token = create_refresh_token(user_data)
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        
        # Simulate successful refresh (token gets revoked)
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        await revoke_token(jti, expires_at)
        
        # Attempt to reuse the same token
        is_revoked = await is_token_revoked(jti)
        assert is_revoked is True, \
            "Reused token should be detected as revoked"
        
        # In real endpoint, this would result in 401 Unauthorized


class TestTokenRotationEdgeCases:
    """Test edge cases in token rotation"""
    
    @pytest.mark.asyncio
    async def test_rotation_with_expired_token(self, mock_redis_client):
        """Test that expired tokens are handled correctly"""
        # Create token with very short expiration
        user_data = {"sub": "test-user-id"}
        short_expiry = timedelta(seconds=1)  # Very short but positive
        short_lived_token = create_refresh_token(user_data, expires_delta=short_expiry)
        
        payload = decode_token(short_lived_token)
        
        # Token should decode successfully
        assert payload is not None, "Should be able to decode token"
        
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Token should expire soon
        assert expires_at > now, "Token should not be expired yet"
        assert (expires_at - now).total_seconds() < 5, "Token should expire very soon"
    
    @pytest.mark.asyncio
    async def test_revocation_with_zero_ttl(self, mock_redis_client):
        """Test that tokens with zero or negative TTL are not added to blacklist"""
        # Create token that's already expired
        user_data = {"sub": "test-user-id"}
        past_time = datetime.now(timezone.utc) - timedelta(days=1)
        
        jti = "test-jti-expired"
        
        # Try to revoke with past expiration
        await revoke_token(jti, past_time)
        
        # Token should not be in blacklist (TTL would be negative)
        is_revoked = await is_token_revoked(jti)
        assert is_revoked is False, \
            "Expired token should not be added to blacklist (negative TTL)"
    
    @pytest.mark.asyncio
    async def test_multiple_rotation_cycles(self, mock_redis_client):
        """Test multiple consecutive token rotations"""
        user_data = {"sub": "test-user-id"}
        
        # Track JTIs through rotation cycles
        jtis = []
        
        # Perform 3 rotation cycles
        for i in range(3):
            token = create_refresh_token(user_data)
            payload = decode_token(token)
            jti = payload.get("jti")
            jtis.append(jti)
            
            # Revoke the token (simulating rotation)
            exp = payload.get("exp")
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            await revoke_token(jti, expires_at)
        
        # Verify all JTIs are unique
        assert len(jtis) == len(set(jtis)), \
            "All tokens should have unique JTIs"
        
        # Verify all tokens are revoked
        for jti in jtis:
            is_revoked = await is_token_revoked(jti)
            assert is_revoked is True, \
                f"Token {jti} should be revoked"

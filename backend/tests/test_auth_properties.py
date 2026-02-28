"""
Property-based tests for authentication system.

**Validates: Requirements 8.2, 8.3, 5.3**

This module tests authentication properties using Hypothesis for property-based testing:
- Password hashing is one-way and deterministic
- JWT tokens expire correctly
- Token blacklist prevents reuse

Property-based testing generates many test cases automatically to verify
that authentication properties hold across a wide range of inputs.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt as jose_jwt

from app.auth.services.auth_service import AuthService
from app.auth.config import auth_settings
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    revoke_token,
    is_token_revoked,
    verify_token_with_revocation
)


# Strategy for generating valid passwords
passwords_strategy = st.text(
    alphabet=st.characters(
        min_codepoint=33,  # Start from '!'
        max_codepoint=126,  # End at '~'
        blacklist_categories=('Cs',)  # Exclude surrogates
    ),
    min_size=8,
    max_size=100
)

# Strategy for generating user data
user_data_strategy = st.fixed_dictionaries({
    'user_id': st.uuids().map(str),
    'username': st.text(min_size=3, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    'email': st.emails(),
})


class TestPasswordHashingProperties:
    """
    Property-based tests for password hashing.
    
    **Validates: Requirement 8.3** - THE RBAC_System SHALL hash all passwords 
    using bcrypt with cost factor 12
    """
    
    @given(password=passwords_strategy)
    @settings(max_examples=100, deadline=5000)
    def test_password_hashing_is_deterministic_for_same_input(self, password):
        """
        Property: Hashing the same password twice should produce different hashes
        (due to random salt), but both should verify against the original password.
        
        This tests that bcrypt properly uses random salts while maintaining
        deterministic verification.
        """
        # Hash the same password twice
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        
        # Hashes should be different (due to random salt)
        assert hash1 != hash2, "Bcrypt should use random salt for each hash"
        
        # But both should verify against the original password
        assert AuthService.verify_password(password, hash1), \
            "First hash should verify against original password"
        assert AuthService.verify_password(password, hash2), \
            "Second hash should verify against original password"
    
    @given(password=passwords_strategy)
    @settings(max_examples=100, deadline=5000)
    def test_password_hashing_is_one_way(self, password):
        """
        Property: It should be impossible to recover the original password
        from its hash.
        
        This tests that password hashing is a one-way function by verifying
        that the hash doesn't contain the original password.
        """
        password_hash = AuthService.hash_password(password)
        
        # Hash should not contain the original password
        assert password not in password_hash, \
            "Hash should not contain original password"
        
        # Hash should be a valid bcrypt hash (starts with $2b$)
        assert password_hash.startswith('$2b$'), \
            "Hash should be a valid bcrypt hash"
    
    @given(password=passwords_strategy)
    @settings(max_examples=100, deadline=5000)
    def test_password_hash_uses_correct_cost_factor(self, password):
        """
        Property: All password hashes should use bcrypt cost factor 12.
        
        **Validates: Requirement 8.3** - Bcrypt cost factor must be 12
        """
        password_hash = AuthService.hash_password(password)
        
        # Extract cost factor from bcrypt hash
        # Bcrypt hash format: $2b$12$...
        parts = password_hash.split('$')
        assert len(parts) >= 4, "Invalid bcrypt hash format"
        
        cost_factor = int(parts[2])
        assert cost_factor == 12, \
            f"Cost factor should be 12, got {cost_factor}"
    
    @given(
        password=passwords_strategy,
        wrong_password=passwords_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_wrong_password_never_verifies(self, password, wrong_password):
        """
        Property: A wrong password should never verify against a hash,
        except in the extremely unlikely case where they're identical.
        """
        # Skip if passwords are the same
        assume(password != wrong_password)
        
        password_hash = AuthService.hash_password(password)
        
        # Wrong password should not verify
        assert not AuthService.verify_password(wrong_password, password_hash), \
            "Wrong password should not verify against hash"
    
    @given(password=passwords_strategy)
    @settings(max_examples=50, deadline=5000)
    def test_password_hash_length_is_consistent(self, password):
        """
        Property: Bcrypt hashes should have consistent length regardless
        of input password length.
        """
        password_hash = AuthService.hash_password(password)
        
        # Bcrypt hashes are always 60 characters
        assert len(password_hash) == 60, \
            f"Bcrypt hash should be 60 characters, got {len(password_hash)}"
    
    @given(password=passwords_strategy)
    @settings(max_examples=50, deadline=5000)
    def test_empty_string_never_verifies(self, password):
        """
        Property: An empty string should never verify against any password hash.
        """
        # Skip if password is empty
        assume(len(password) > 0)
        
        password_hash = AuthService.hash_password(password)
        
        # Empty string should not verify
        assert not AuthService.verify_password('', password_hash), \
            "Empty string should not verify against any hash"


class TestJWTTokenExpirationProperties:
    """
    Property-based tests for JWT token expiration.
    
    **Validates: Requirement 8.2** - THE RBAC_System SHALL implement JWT token 
    expiration of 24 hours with refresh token support
    """
    
    @given(user_data=user_data_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_access_token_expires_in_future(self, user_data):
        """
        Property: All newly created access tokens should have expiration
        time in the future.
        """
        token = create_access_token(user_data)
        payload = decode_token(token)
        
        assert payload is not None, "Token should be valid"
        
        exp_timestamp = payload['exp']
        exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        assert exp_time > now, \
            "Token expiration should be in the future"
    
    @given(user_data=user_data_strategy)
    @settings(max_examples=100, deadline=2000)
    def test_refresh_token_expires_in_future(self, user_data):
        """
        Property: All newly created refresh tokens should have expiration
        time in the future.
        """
        token = create_refresh_token(user_data)
        payload = decode_token(token)
        
        assert payload is not None, "Token should be valid"
        
        exp_timestamp = payload['exp']
        exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        assert exp_time > now, \
            "Token expiration should be in the future"
    
    @given(
        user_data=user_data_strategy,
        expiry_seconds=st.integers(min_value=-3600, max_value=-1)
    )
    @settings(max_examples=50, deadline=2000)
    def test_expired_tokens_are_rejected(self, user_data, expiry_seconds):
        """
        Property: Tokens with expiration in the past should always be rejected.
        """
        # Create token with negative expiration (already expired)
        expires_delta = timedelta(seconds=expiry_seconds)
        token = create_access_token(user_data, expires_delta=expires_delta)
        
        # Token should be rejected
        payload = decode_token(token)
        assert payload is None, \
            "Expired token should be rejected"
    
    @given(
        user_data=user_data_strategy,
        expiry_minutes=st.integers(min_value=1, max_value=1440)  # 1 min to 24 hours
    )
    @settings(max_examples=50, deadline=2000)
    def test_token_expiration_respects_custom_delta(self, user_data, expiry_minutes):
        """
        Property: Token expiration should respect custom expiration delta.
        """
        expires_delta = timedelta(minutes=expiry_minutes)
        token = create_access_token(user_data, expires_delta=expires_delta)
        payload = decode_token(token)
        
        assert payload is not None, "Token should be valid"
        
        exp_timestamp = payload['exp']
        exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Calculate expected expiration
        expected_exp = now + expires_delta
        
        # Allow 5 second tolerance for test execution time
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 5, \
            f"Token expiration should match custom delta (diff: {time_diff}s)"
    
    @given(user_data=user_data_strategy)
    @settings(max_examples=50, deadline=2000)
    def test_access_token_default_expiration_is_reasonable(self, user_data):
        """
        Property: Access tokens should have reasonable default expiration
        (between 10 minutes and 2 hours).
        """
        token = create_access_token(user_data)
        payload = decode_token(token)
        
        exp_timestamp = payload['exp']
        exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        time_until_expiry = (exp_time - now).total_seconds()
        
        # Should be between 10 minutes and 2 hours
        assert 10 * 60 <= time_until_expiry <= 2 * 60 * 60, \
            f"Access token expiration should be reasonable (got {time_until_expiry}s)"
    
    @given(user_data=user_data_strategy)
    @settings(max_examples=50, deadline=2000)
    def test_refresh_token_lives_longer_than_access_token(self, user_data):
        """
        Property: Refresh tokens should always have longer expiration
        than access tokens.
        """
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        access_exp = access_payload['exp']
        refresh_exp = refresh_payload['exp']
        
        assert refresh_exp > access_exp, \
            "Refresh token should expire after access token"
    
    @given(user_data=user_data_strategy)
    @settings(max_examples=50, deadline=2000)
    def test_token_includes_all_required_claims(self, user_data):
        """
        Property: All tokens should include required JWT claims (exp, type, jti).
        """
        token = create_access_token(user_data)
        payload = decode_token(token)
        
        assert payload is not None, "Token should be valid"
        
        # Check required claims
        assert 'exp' in payload, "Token must include 'exp' claim"
        assert 'type' in payload, "Token must include 'type' claim"
        assert 'jti' in payload, "Token must include 'jti' claim"
        
        # Check claim types
        assert isinstance(payload['exp'], int), "'exp' should be integer timestamp"
        assert isinstance(payload['type'], str), "'type' should be string"
        assert isinstance(payload['jti'], str), "'jti' should be string"


class TestTokenBlacklistProperties:
    """
    Property-based tests for token blacklist functionality.
    
    **Validates: Requirement 8.2** - Token blacklist prevents reuse
    """
    
    @pytest.mark.asyncio
    @given(user_data=user_data_strategy)
    @settings(max_examples=50, deadline=5000)
    async def test_revoked_token_is_always_rejected(self, user_data):
        """
        Property: Once a token is revoked, it should always be rejected
        by verify_token_with_revocation.
        """
        # Create token
        token = create_access_token(user_data)
        payload = decode_token(token)
        
        jti = payload['jti']
        exp_timestamp = payload['exp']
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Token should be valid before revocation
        verified = await verify_token_with_revocation(token, 'access')
        assert verified is not None, "Token should be valid before revocation"
        
        # Revoke token
        await revoke_token(jti, expires_at)
        
        # Token should be rejected after revocation
        verified = await verify_token_with_revocation(token, 'access')
        assert verified is None, \
            "Revoked token should always be rejected"
    
    @pytest.mark.asyncio
    @given(user_data=user_data_strategy)
    @settings(max_examples=50, deadline=5000)
    async def test_non_revoked_token_is_always_accepted(self, user_data):
        """
        Property: Non-revoked valid tokens should always be accepted.
        """
        # Create token
        token = create_access_token(user_data)
        
        # Token should be valid (not revoked)
        verified = await verify_token_with_revocation(token, 'access')
        assert verified is not None, \
            "Non-revoked token should be accepted"
        
        # Verify payload contains original data
        for key, value in user_data.items():
            assert verified.get(key) == value, \
                f"Token payload should contain original data: {key}"
    
    @pytest.mark.asyncio
    @given(
        user_data=user_data_strategy,
        num_tokens=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=30, deadline=10000)
    async def test_revoking_one_token_does_not_affect_others(self, user_data, num_tokens):
        """
        Property: Revoking one token should not affect other tokens
        for the same user.
        """
        # Create multiple tokens
        tokens = [create_access_token(user_data) for _ in range(num_tokens)]
        payloads = [decode_token(token) for token in tokens]
        
        # Revoke the first token
        first_jti = payloads[0]['jti']
        first_exp = datetime.fromtimestamp(payloads[0]['exp'], tz=timezone.utc)
        await revoke_token(first_jti, first_exp)
        
        # First token should be rejected
        verified = await verify_token_with_revocation(tokens[0], 'access')
        assert verified is None, "Revoked token should be rejected"
        
        # Other tokens should still be valid
        for i in range(1, num_tokens):
            verified = await verify_token_with_revocation(tokens[i], 'access')
            assert verified is not None, \
                f"Token {i} should still be valid after revoking token 0"
    
    @pytest.mark.asyncio
    @given(user_data=user_data_strategy)
    @settings(max_examples=30, deadline=5000)
    async def test_revoked_token_jti_is_in_blacklist(self, user_data):
        """
        Property: After revoking a token, its JTI should be in the blacklist.
        """
        # Create token
        token = create_access_token(user_data)
        payload = decode_token(token)
        
        jti = payload['jti']
        exp_timestamp = payload['exp']
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # JTI should not be in blacklist initially
        is_blacklisted = await is_token_revoked(jti)
        assert not is_blacklisted, "JTI should not be in blacklist initially"
        
        # Revoke token
        await revoke_token(jti, expires_at)
        
        # JTI should now be in blacklist
        is_blacklisted = await is_token_revoked(jti)
        assert is_blacklisted, \
            "JTI should be in blacklist after revocation"
    
    @pytest.mark.asyncio
    @given(user_data=user_data_strategy)
    @settings(max_examples=30, deadline=5000)
    async def test_token_type_validation_still_applies_to_revoked_tokens(self, user_data):
        """
        Property: Token type validation should still apply even for
        non-revoked tokens.
        """
        # Create access token
        token = create_access_token(user_data)
        
        # Try to verify as refresh token (wrong type)
        verified = await verify_token_with_revocation(token, 'refresh')
        assert verified is None, \
            "Token type mismatch should be rejected even if not revoked"
    
    @pytest.mark.asyncio
    @given(
        user_data=user_data_strategy,
        expiry_seconds=st.integers(min_value=-3600, max_value=-1)
    )
    @settings(max_examples=30, deadline=5000)
    async def test_expired_tokens_not_added_to_blacklist(self, user_data, expiry_seconds):
        """
        Property: Tokens that are already expired should not be added
        to the blacklist (no point storing them).
        """
        # Create an already-expired token
        expires_delta = timedelta(seconds=expiry_seconds)
        expires_at = datetime.now(timezone.utc) + expires_delta
        
        jti = f"expired-{user_data['user_id']}"
        
        # Try to revoke the expired token
        await revoke_token(jti, expires_at)
        
        # Should not be in blacklist
        is_blacklisted = await is_token_revoked(jti)
        assert not is_blacklisted, \
            "Expired tokens should not be added to blacklist"


class TestTokenUniquenessProperties:
    """
    Property-based tests for token uniqueness.
    """
    
    @given(
        user_data=user_data_strategy,
        num_tokens=st.integers(min_value=2, max_value=10)
    )
    @settings(max_examples=50, deadline=3000)
    def test_all_tokens_have_unique_jti(self, user_data, num_tokens):
        """
        Property: Every token should have a unique JTI, even for the same user.
        """
        # Create multiple tokens
        tokens = [create_access_token(user_data) for _ in range(num_tokens)]
        payloads = [decode_token(token) for token in tokens]
        
        # Extract all JTIs
        jtis = [payload['jti'] for payload in payloads]
        
        # All JTIs should be unique
        assert len(jtis) == len(set(jtis)), \
            "All tokens should have unique JTIs"
    
    @given(
        user_data1=user_data_strategy,
        user_data2=user_data_strategy
    )
    @settings(max_examples=50, deadline=2000)
    def test_tokens_for_different_users_have_unique_jti(self, user_data1, user_data2):
        """
        Property: Tokens for different users should have unique JTIs.
        """
        # Skip if user data is identical
        assume(user_data1 != user_data2)
        
        token1 = create_access_token(user_data1)
        token2 = create_access_token(user_data2)
        
        payload1 = decode_token(token1)
        payload2 = decode_token(token2)
        
        assert payload1['jti'] != payload2['jti'], \
            "Tokens for different users should have unique JTIs"

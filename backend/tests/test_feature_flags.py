"""
Tests for feature flag system.

Validates Requirement 14.7: Implement feature flags for gradual rollout
"""
import pytest
import os
from app.core.feature_flags import (
    FeatureFlagManager,
    FeatureFlagStrategy,
    is_feature_enabled,
    require_feature,
    FeatureFlagDisabledError
)


@pytest.fixture
def flag_manager():
    """Create a fresh feature flag manager for testing."""
    manager = FeatureFlagManager()
    # Clear default flags for clean testing
    manager.flags.clear()
    return manager


class TestBooleanFlags:
    """Test boolean feature flags."""
    
    def test_enabled_flag(self, flag_manager):
        """Test that enabled flag returns True."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.BOOLEAN
        )
        
        assert flag_manager.is_enabled("test_feature") is True
    
    def test_disabled_flag(self, flag_manager):
        """Test that disabled flag returns False."""
        flag_manager.register_flag(
            "test_feature",
            enabled=False,
            description="Test feature",
            strategy=FeatureFlagStrategy.BOOLEAN
        )
        
        assert flag_manager.is_enabled("test_feature") is False
    
    def test_unknown_flag_returns_default(self, flag_manager):
        """Test that unknown flag returns default value."""
        assert flag_manager.is_enabled("unknown_flag", default=True) is True
        assert flag_manager.is_enabled("unknown_flag", default=False) is False
    
    def test_enable_flag(self, flag_manager):
        """Test enabling a flag."""
        flag_manager.register_flag(
            "test_feature",
            enabled=False,
            description="Test feature"
        )
        
        assert flag_manager.is_enabled("test_feature") is False
        
        flag_manager.enable_flag("test_feature")
        assert flag_manager.is_enabled("test_feature") is True
    
    def test_disable_flag(self, flag_manager):
        """Test disabling a flag."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature"
        )
        
        assert flag_manager.is_enabled("test_feature") is True
        
        flag_manager.disable_flag("test_feature")
        assert flag_manager.is_enabled("test_feature") is False


class TestPercentageFlags:
    """Test percentage-based feature flags."""
    
    def test_percentage_0_always_disabled(self, flag_manager):
        """Test that 0% rollout disables for all users."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 0}
        )
        
        # Test multiple users
        for i in range(100):
            assert flag_manager.is_enabled("test_feature", user_id=f"user{i}") is False
    
    def test_percentage_100_always_enabled(self, flag_manager):
        """Test that 100% rollout enables for all users."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        # Test multiple users
        for i in range(100):
            assert flag_manager.is_enabled("test_feature", user_id=f"user{i}") is True
    
    def test_percentage_50_approximately_half(self, flag_manager):
        """Test that 50% rollout enables for approximately half of users."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 50}
        )
        
        # Test 1000 users
        enabled_count = sum(
            1 for i in range(1000)
            if flag_manager.is_enabled("test_feature", user_id=f"user{i}")
        )
        
        # Should be approximately 500 (allow 10% variance)
        assert 450 <= enabled_count <= 550
    
    def test_percentage_consistent_for_same_user(self, flag_manager):
        """Test that same user always gets same result."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 50}
        )
        
        # Check same user multiple times
        user_id = "test_user_123"
        first_result = flag_manager.is_enabled("test_feature", user_id=user_id)
        
        for _ in range(10):
            result = flag_manager.is_enabled("test_feature", user_id=user_id)
            assert result == first_result
    
    def test_set_percentage(self, flag_manager):
        """Test setting percentage dynamically."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 0}
        )
        
        # Initially 0%
        assert flag_manager.is_enabled("test_feature", user_id="user1") is False
        
        # Set to 100%
        flag_manager.set_percentage("test_feature", 100)
        assert flag_manager.is_enabled("test_feature", user_id="user1") is True
    
    def test_percentage_requires_user_id(self, flag_manager):
        """Test that percentage flag requires user_id."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        # Without user_id, should return False
        assert flag_manager.is_enabled("test_feature") is False


class TestUserListFlags:
    """Test user-list feature flags."""
    
    def test_user_in_list(self, flag_manager):
        """Test that user in list gets feature."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": ["user1", "user2", "user3"]}
        )
        
        assert flag_manager.is_enabled("test_feature", user_id="user1") is True
        assert flag_manager.is_enabled("test_feature", user_id="user2") is True
        assert flag_manager.is_enabled("test_feature", user_id="user3") is True
    
    def test_user_not_in_list(self, flag_manager):
        """Test that user not in list doesn't get feature."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": ["user1", "user2"]}
        )
        
        assert flag_manager.is_enabled("test_feature", user_id="user3") is False
        assert flag_manager.is_enabled("test_feature", user_id="user4") is False
    
    def test_add_user_to_flag(self, flag_manager):
        """Test adding user to flag."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": ["user1"]}
        )
        
        assert flag_manager.is_enabled("test_feature", user_id="user2") is False
        
        flag_manager.add_user_to_flag("test_feature", "user2")
        assert flag_manager.is_enabled("test_feature", user_id="user2") is True
    
    def test_remove_user_from_flag(self, flag_manager):
        """Test removing user from flag."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": ["user1", "user2"]}
        )
        
        assert flag_manager.is_enabled("test_feature", user_id="user1") is True
        
        flag_manager.remove_user_from_flag("test_feature", "user1")
        assert flag_manager.is_enabled("test_feature", user_id="user1") is False


class TestEnvironmentFlags:
    """Test environment-specific feature flags."""
    
    def test_environment_in_list(self, flag_manager):
        """Test that flag is enabled in specified environments."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.ENVIRONMENT,
            config={"environments": ["staging", "production"]}
        )
        
        assert flag_manager.is_enabled("test_feature", environment="staging") is True
        assert flag_manager.is_enabled("test_feature", environment="production") is True
    
    def test_environment_not_in_list(self, flag_manager):
        """Test that flag is disabled in other environments."""
        flag_manager.register_flag(
            "test_feature",
            enabled=True,
            description="Test feature",
            strategy=FeatureFlagStrategy.ENVIRONMENT,
            config={"environments": ["production"]}
        )
        
        assert flag_manager.is_enabled("test_feature", environment="development") is False
        assert flag_manager.is_enabled("test_feature", environment="staging") is False


class TestFlagManagement:
    """Test flag management operations."""
    
    def test_get_all_flags(self, flag_manager):
        """Test getting all flags."""
        flag_manager.register_flag("flag1", enabled=True, description="Flag 1")
        flag_manager.register_flag("flag2", enabled=False, description="Flag 2")
        
        all_flags = flag_manager.get_all_flags()
        
        assert "flag1" in all_flags
        assert "flag2" in all_flags
        assert all_flags["flag1"]["enabled"] is True
        assert all_flags["flag2"]["enabled"] is False
    
    def test_get_enabled_flags(self, flag_manager):
        """Test getting only enabled flags."""
        flag_manager.register_flag("flag1", enabled=True, description="Flag 1")
        flag_manager.register_flag("flag2", enabled=False, description="Flag 2")
        flag_manager.register_flag("flag3", enabled=True, description="Flag 3")
        
        enabled = flag_manager.get_enabled_flags()
        
        assert "flag1" in enabled
        assert "flag3" in enabled
        assert "flag2" not in enabled


class TestEnvironmentVariableOverride:
    """Test environment variable override."""
    
    def test_env_var_override_enable(self, flag_manager, monkeypatch):
        """Test enabling flag via environment variable."""
        flag_manager.register_flag("test_feature", enabled=False, description="Test")
        
        # Set environment variable
        monkeypatch.setenv("FEATURE_FLAG_TEST_FEATURE", "true")
        
        # Reload from environment
        flag_manager._load_from_environment()
        
        assert flag_manager.is_enabled("test_feature") is True
    
    def test_env_var_override_disable(self, flag_manager, monkeypatch):
        """Test disabling flag via environment variable."""
        flag_manager.register_flag("test_feature", enabled=True, description="Test")
        
        # Set environment variable
        monkeypatch.setenv("FEATURE_FLAG_TEST_FEATURE", "false")
        
        # Reload from environment
        flag_manager._load_from_environment()
        
        assert flag_manager.is_enabled("test_feature") is False


class TestDecorator:
    """Test require_feature decorator."""
    
    def test_decorator_with_enabled_flag(self, monkeypatch):
        """Test decorator allows function when flag is enabled."""
        # Register flag in global instance
        from app.core.feature_flags import get_feature_flags
        flags = get_feature_flags()
        flags.register_flag("test_feature", enabled=False, description="Test")
        
        # Use environment variable to enable flag
        monkeypatch.setenv("FEATURE_FLAG_TEST_FEATURE", "true")
        flags._load_from_environment()
        
        @require_feature("test_feature")
        def my_function():
            return "success"
        
        result = my_function()
        assert result == "success"
    
    def test_decorator_with_disabled_flag(self, monkeypatch):
        """Test decorator blocks function when flag is disabled."""
        # Register flag in global instance
        from app.core.feature_flags import get_feature_flags
        flags = get_feature_flags()
        flags.register_flag("test_feature_disabled", enabled=True, description="Test")
        
        # Use environment variable to disable flag
        monkeypatch.setenv("FEATURE_FLAG_TEST_FEATURE_DISABLED", "false")
        flags._load_from_environment()
        
        @require_feature("test_feature_disabled")
        def my_function():
            return "success"
        
        with pytest.raises(FeatureFlagDisabledError):
            my_function()


class TestConvenienceFunction:
    """Test is_feature_enabled convenience function."""
    
    def test_convenience_function(self):
        """Test that convenience function works."""
        # This uses the global instance
        result = is_feature_enabled("github_integration")
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

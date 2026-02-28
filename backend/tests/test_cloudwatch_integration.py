"""
Tests for CloudWatch Logs integration

Validates Requirements: 7.2, 7.10
"""
import logging
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
from botocore.exceptions import ClientError, NoCredentialsError

from app.core.cloudwatch_handler import (
    CloudWatchConfig,
    create_cloudwatch_handler,
    add_cloudwatch_handler_to_logger,
    get_cloudwatch_status,
    _ensure_log_group_exists
)


class TestCloudWatchConfig:
    """Test CloudWatch configuration"""
    
    def test_default_config(self):
        """Test default CloudWatch configuration"""
        config = CloudWatchConfig()
        
        assert config.log_group == "/aws/application/backend-api"
        assert config.log_stream == "development/local"
        assert config.region_name == "us-east-1"
        assert config.retention_days == 30  # Requirement 7.10
        assert config.enabled is True
    
    def test_custom_config(self):
        """Test custom CloudWatch configuration"""
        config = CloudWatchConfig(
            log_group="/custom/log-group",
            log_stream="custom-stream",
            region_name="us-west-2",
            retention_days=30,
            enabled=True
        )
        
        assert config.log_group == "/custom/log-group"
        assert config.log_stream == "custom-stream"
        assert config.region_name == "us-west-2"
        assert config.retention_days == 30
        assert config.enabled is True
    
    def test_config_from_environment(self, monkeypatch):
        """Test configuration from environment variables"""
        monkeypatch.setenv('SERVICE_NAME', 'test-service')
        monkeypatch.setenv('ENVIRONMENT', 'production')
        monkeypatch.setenv('INSTANCE_ID', 'i-12345')
        monkeypatch.setenv('AWS_REGION', 'eu-west-1')
        monkeypatch.setenv('CLOUDWATCH_ENABLED', 'true')
        
        config = CloudWatchConfig()
        
        assert config.service_name == 'test-service'
        assert config.environment == 'production'
        assert config.instance_id == 'i-12345'
        assert config.log_group == '/aws/application/test-service'
        assert config.log_stream == 'production/i-12345'
        assert config.region_name == 'eu-west-1'
        assert config.enabled is True
    
    def test_config_disabled_via_env(self, monkeypatch):
        """Test disabling CloudWatch via environment variable"""
        monkeypatch.setenv('CLOUDWATCH_ENABLED', 'false')
        
        config = CloudWatchConfig()
        
        assert config.enabled is False
    
    def test_config_repr(self):
        """Test configuration string representation"""
        config = CloudWatchConfig()
        repr_str = repr(config)
        
        assert 'CloudWatchConfig' in repr_str
        assert 'log_group' in repr_str
        assert 'retention_days=30' in repr_str


class TestCreateCloudWatchHandler:
    """Test CloudWatch handler creation"""
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_create_handler_success(self, mock_boto_client):
        """Test successful CloudWatch handler creation"""
        # Mock boto3 client
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        
        # Mock describe_log_groups response
        mock_logs_client.describe_log_groups.return_value = {
            'logGroups': []
        }
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config)
        
        # Verify handler was created
        assert handler is not None
        
        # Verify boto3 client was created with correct region
        mock_boto_client.assert_called_once_with(
            'logs',
            region_name='us-east-1'
        )
        
        # Verify log group creation was attempted
        mock_logs_client.create_log_group.assert_called_once()
        
        # Verify retention policy was set (Requirement 7.10)
        mock_logs_client.put_retention_policy.assert_called_once_with(
            logGroupName='/aws/application/backend-api',
            retentionInDays=30
        )
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_create_handler_disabled(self, mock_boto_client):
        """Test handler creation when CloudWatch is disabled"""
        config = CloudWatchConfig(enabled=False)
        handler = create_cloudwatch_handler(config)
        
        assert handler is None
        mock_boto_client.assert_not_called()
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_create_handler_no_credentials(self, mock_boto_client):
        """Test handler creation with missing AWS credentials"""
        mock_boto_client.side_effect = NoCredentialsError()
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config)
        
        # Should return None and log warning
        assert handler is None
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_create_handler_client_error(self, mock_boto_client):
        """Test handler creation with AWS client error"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        
        # Simulate AccessDeniedException
        error_response = {
            'Error': {
                'Code': 'AccessDeniedException',
                'Message': 'Access denied'
            }
        }
        mock_logs_client.describe_log_groups.side_effect = ClientError(
            error_response,
            'DescribeLogGroups'
        )
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config)
        
        # Should return None and log warning
        assert handler is None
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_create_handler_with_custom_log_level(self, mock_boto_client):
        """Test handler creation with custom log level"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {'logGroups': []}
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config, log_level=logging.WARNING)
        
        assert handler is not None
        assert handler.level == logging.WARNING


class TestEnsureLogGroupExists:
    """Test log group creation and retention configuration"""
    
    def test_create_new_log_group(self):
        """Test creating a new log group with retention"""
        mock_client = Mock()
        mock_client.describe_log_groups.return_value = {'logGroups': []}
        
        _ensure_log_group_exists(mock_client, '/test/log-group', 30)
        
        # Verify log group was created
        mock_client.create_log_group.assert_called_once_with(
            logGroupName='/test/log-group'
        )
        
        # Verify retention was set (Requirement 7.10)
        mock_client.put_retention_policy.assert_called_once_with(
            logGroupName='/test/log-group',
            retentionInDays=30
        )
    
    def test_update_existing_log_group_retention(self):
        """Test updating retention for existing log group"""
        mock_client = Mock()
        mock_client.describe_log_groups.return_value = {
            'logGroups': [
                {'logGroupName': '/test/log-group'}
            ]
        }
        
        _ensure_log_group_exists(mock_client, '/test/log-group', 30)
        
        # Should not create log group
        mock_client.create_log_group.assert_not_called()
        
        # Should update retention (Requirement 7.10)
        mock_client.put_retention_policy.assert_called_once_with(
            logGroupName='/test/log-group',
            retentionInDays=30
        )
    
    def test_handle_resource_already_exists(self):
        """Test handling ResourceAlreadyExistsException"""
        mock_client = Mock()
        mock_client.describe_log_groups.return_value = {'logGroups': []}
        
        # Simulate ResourceAlreadyExistsException on create
        error_response = {
            'Error': {
                'Code': 'ResourceAlreadyExistsException',
                'Message': 'Log group already exists'
            }
        }
        mock_client.create_log_group.side_effect = ClientError(
            error_response,
            'CreateLogGroup'
        )
        
        _ensure_log_group_exists(mock_client, '/test/log-group', 30)
        
        # Should still set retention
        mock_client.put_retention_policy.assert_called_once()


class TestAddCloudWatchHandlerToLogger:
    """Test adding CloudWatch handler to logger"""
    
    @patch('app.core.cloudwatch_handler.create_cloudwatch_handler')
    def test_add_handler_success(self, mock_create_handler):
        """Test successfully adding CloudWatch handler to logger"""
        mock_handler = Mock()
        mock_create_handler.return_value = mock_handler
        
        test_logger = logging.getLogger('test_logger')
        initial_handler_count = len(test_logger.handlers)
        
        result = add_cloudwatch_handler_to_logger(test_logger)
        
        assert result is True
        assert len(test_logger.handlers) == initial_handler_count + 1
        assert mock_handler in test_logger.handlers
    
    @patch('app.core.cloudwatch_handler.create_cloudwatch_handler')
    def test_add_handler_failure(self, mock_create_handler):
        """Test adding CloudWatch handler when creation fails"""
        mock_create_handler.return_value = None
        
        test_logger = logging.getLogger('test_logger_2')
        initial_handler_count = len(test_logger.handlers)
        
        result = add_cloudwatch_handler_to_logger(test_logger)
        
        assert result is False
        assert len(test_logger.handlers) == initial_handler_count


class TestGetCloudWatchStatus:
    """Test CloudWatch status checking"""
    
    def test_status_disabled(self):
        """Test status when CloudWatch is disabled"""
        config = CloudWatchConfig(enabled=False)
        status = get_cloudwatch_status(config)
        
        assert status['enabled'] is False
        assert status['connected'] is False
        assert 'disabled' in status['error']
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_status_connected(self, mock_boto_client):
        """Test status when CloudWatch is connected"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {'logGroups': []}
        
        config = CloudWatchConfig()
        status = get_cloudwatch_status(config)
        
        assert status['enabled'] is True
        assert status['connected'] is True
        assert status['error'] is None
        assert status['log_group'] == '/aws/application/backend-api'
        assert status['retention_days'] == 30  # Requirement 7.10
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_status_no_credentials(self, mock_boto_client):
        """Test status when AWS credentials are missing"""
        mock_boto_client.side_effect = NoCredentialsError()
        
        config = CloudWatchConfig()
        status = get_cloudwatch_status(config)
        
        assert status['enabled'] is True
        assert status['connected'] is False
        assert 'credentials not found' in status['error']
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_status_client_error(self, mock_boto_client):
        """Test status when AWS client error occurs"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        
        error_response = {
            'Error': {
                'Code': 'AccessDeniedException',
                'Message': 'Access denied'
            }
        }
        mock_logs_client.describe_log_groups.side_effect = ClientError(
            error_response,
            'DescribeLogGroups'
        )
        
        config = CloudWatchConfig()
        status = get_cloudwatch_status(config)
        
        assert status['enabled'] is True
        assert status['connected'] is False
        assert 'AccessDeniedException' in status['error']


class TestCloudWatchIntegration:
    """Integration tests for CloudWatch logging"""
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_log_retention_30_days(self, mock_boto_client):
        """Test that log retention is set to 30 days (Requirement 7.10)"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {'logGroups': []}
        
        config = CloudWatchConfig(retention_days=30)
        handler = create_cloudwatch_handler(config)
        
        # Verify retention was set to 30 days
        mock_logs_client.put_retention_policy.assert_called_once()
        call_args = mock_logs_client.put_retention_policy.call_args
        assert call_args[1]['retentionInDays'] == 30
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_centralized_logging(self, mock_boto_client):
        """Test centralized logging to CloudWatch (Requirement 7.2)"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {'logGroups': []}
        
        config = CloudWatchConfig(
            log_group='/aws/application/backend-api',
            log_stream='production/instance-1'
        )
        handler = create_cloudwatch_handler(config)
        
        assert handler is not None
        
        # Verify log group was created for centralized logging
        mock_logs_client.create_log_group.assert_called_once_with(
            logGroupName='/aws/application/backend-api'
        )
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_graceful_fallback_on_error(self, mock_boto_client):
        """Test graceful fallback when CloudWatch is unavailable"""
        mock_boto_client.side_effect = Exception("Network error")
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config)
        
        # Should return None instead of raising exception
        assert handler is None
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_multiple_environments(self, mock_boto_client):
        """Test CloudWatch configuration for multiple environments"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {'logGroups': []}
        
        # Test different environments
        environments = ['development', 'staging', 'production']
        
        for env in environments:
            config = CloudWatchConfig(
                log_stream=f'{env}/instance-1'
            )
            handler = create_cloudwatch_handler(config)
            
            assert handler is not None
            assert env in config.log_stream


class TestCloudWatchErrorHandling:
    """Test error handling for CloudWatch integration"""
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_handle_access_denied(self, mock_boto_client):
        """Test handling AccessDeniedException"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        
        error_response = {
            'Error': {
                'Code': 'AccessDeniedException',
                'Message': 'User is not authorized'
            }
        }
        mock_logs_client.describe_log_groups.side_effect = ClientError(
            error_response,
            'DescribeLogGroups'
        )
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config)
        
        # Should handle gracefully
        assert handler is None
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_handle_throttling(self, mock_boto_client):
        """Test handling ThrottlingException"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        
        error_response = {
            'Error': {
                'Code': 'ThrottlingException',
                'Message': 'Rate exceeded'
            }
        }
        mock_logs_client.describe_log_groups.side_effect = ClientError(
            error_response,
            'DescribeLogGroups'
        )
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config)
        
        # Should handle gracefully
        assert handler is None
    
    @patch('app.core.cloudwatch_handler.boto3.client')
    def test_handle_invalid_parameter(self, mock_boto_client):
        """Test handling InvalidParameterException"""
        mock_logs_client = Mock()
        mock_boto_client.return_value = mock_logs_client
        
        error_response = {
            'Error': {
                'Code': 'InvalidParameterException',
                'Message': 'Invalid log group name'
            }
        }
        mock_logs_client.describe_log_groups.side_effect = ClientError(
            error_response,
            'DescribeLogGroups'
        )
        
        config = CloudWatchConfig()
        handler = create_cloudwatch_handler(config)
        
        # Should handle gracefully
        assert handler is None

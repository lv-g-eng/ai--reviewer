"""
Tests for CloudWatch Notification Channels Configuration

Tests the notification channel configuration script and validates
email and Slack notification setup.

Run tests:
    pytest backend/tests/test_notification_channels.py -v
"""

from unittest.mock import MagicMock, patch

import pytest

# Import the script module
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from configure_notification_channels import NotificationChannelManager


@pytest.fixture
def mock_boto3_clients():
    """Mock boto3 clients"""
    with patch("configure_notification_channels.boto3") as mock_boto3:
        mock_sns = MagicMock()
        mock_cloudwatch = MagicMock()

        mock_boto3.client.side_effect = lambda service, **kwargs: (
            mock_sns if service == "sns" else mock_cloudwatch
        )

        yield {
            "boto3": mock_boto3,
            "sns": mock_sns,
            "cloudwatch": mock_cloudwatch,
        }


@pytest.fixture
def manager(mock_boto3_clients):
    """Create NotificationChannelManager instance with mocked clients"""
    return NotificationChannelManager(region="us-east-1")


class TestNotificationChannelManager:
    """Test NotificationChannelManager class"""

    def test_manager_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager.region == "us-east-1"
        assert manager.sns_client is not None
        assert manager.cloudwatch_client is not None

    def test_setup_email_subscription_new(self, manager, mock_boto3_clients):
        """Test setting up new email subscription"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        email = "test@example.com"

        # Mock no existing subscription
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": []
        }

        # Mock subscribe response
        mock_boto3_clients["sns"].subscribe.return_value = {
            "SubscriptionArn": "PendingConfirmation"
        }

        result = manager.setup_email_subscription(topic_arn, email)

        # Verify subscribe was called
        mock_boto3_clients["sns"].subscribe.assert_called_once_with(
            TopicArn=topic_arn, Protocol="email", Endpoint=email
        )

        # Verify result
        assert result["SubscriptionArn"] == "PendingConfirmation"
        assert result["Protocol"] == "email"
        assert result["Endpoint"] == email
        assert result["Status"] == "PendingConfirmation"

    def test_setup_email_subscription_existing(
        self, manager, mock_boto3_clients
    ):
        """Test setting up email subscription when already exists"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        email = "test@example.com"

        # Mock existing subscription
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:abc123",
                    "Protocol": "email",
                    "Endpoint": email,
                }
            ]
        }

        result = manager.setup_email_subscription(topic_arn, email)

        # Verify subscribe was NOT called
        mock_boto3_clients["sns"].subscribe.assert_not_called()

        # Verify result
        assert (
            result["SubscriptionArn"]
            == "arn:aws:sns:us-east-1:123456789012:test-alerts:abc123"
        )
        assert result["Protocol"] == "email"
        assert result["Endpoint"] == email

    def test_setup_email_subscription_pending(
        self, manager, mock_boto3_clients
    ):
        """Test email subscription pending confirmation"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        email = "test@example.com"

        # Mock pending subscription
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "PendingConfirmation",
                    "Protocol": "email",
                    "Endpoint": email,
                }
            ]
        }

        result = manager.setup_email_subscription(topic_arn, email)

        # Verify result shows pending
        assert result["SubscriptionArn"] == "PendingConfirmation"

    def test_setup_slack_subscription_new(self, manager, mock_boto3_clients):
        """Test setting up new Slack subscription"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        webhook_url = "https://hooks.slack.com/services/T00/B00/XXX"

        # Mock no existing subscription
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": []
        }

        # Mock subscribe response
        mock_boto3_clients["sns"].subscribe.return_value = {
            "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:def456"
        }

        result = manager.setup_slack_subscription(topic_arn, webhook_url)

        # Verify subscribe was called
        mock_boto3_clients["sns"].subscribe.assert_called_once_with(
            TopicArn=topic_arn, Protocol="https", Endpoint=webhook_url
        )

        # Verify result
        assert (
            result["SubscriptionArn"]
            == "arn:aws:sns:us-east-1:123456789012:test-alerts:def456"
        )
        assert result["Protocol"] == "https"
        assert result["Endpoint"] == webhook_url
        assert result["Status"] == "Active"

    def test_setup_slack_subscription_existing(
        self, manager, mock_boto3_clients
    ):
        """Test setting up Slack subscription when already exists"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        webhook_url = "https://hooks.slack.com/services/T00/B00/XXX"

        # Mock existing subscription
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:def456",
                    "Protocol": "https",
                    "Endpoint": webhook_url,
                }
            ]
        }

        result = manager.setup_slack_subscription(topic_arn, webhook_url)

        # Verify subscribe was NOT called
        mock_boto3_clients["sns"].subscribe.assert_not_called()

        # Verify result
        assert (
            result["SubscriptionArn"]
            == "arn:aws:sns:us-east-1:123456789012:test-alerts:def456"
        )

    def test_list_subscriptions_empty(self, manager, mock_boto3_clients):
        """Test listing subscriptions when none exist"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"

        # Mock empty subscriptions
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": []
        }

        result = manager.list_subscriptions(topic_arn)

        assert result == []

    def test_list_subscriptions_multiple(self, manager, mock_boto3_clients):
        """Test listing multiple subscriptions"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"

        # Mock multiple subscriptions
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:abc123",
                    "Protocol": "email",
                    "Endpoint": "test@example.com",
                },
                {
                    "SubscriptionArn": "PendingConfirmation",
                    "Protocol": "email",
                    "Endpoint": "pending@example.com",
                },
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:def456",
                    "Protocol": "https",
                    "Endpoint": "https://hooks.slack.com/services/T00/B00/XXX",
                },
            ]
        }

        result = manager.list_subscriptions(topic_arn)

        assert len(result) == 3
        assert result[0]["Protocol"] == "email"
        assert result[1]["SubscriptionArn"] == "PendingConfirmation"
        assert result[2]["Protocol"] == "https"

    def test_test_notification_default_message(
        self, manager, mock_boto3_clients
    ):
        """Test sending test notification with default message"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"

        # Mock publish response
        mock_boto3_clients["sns"].publish.return_value = {
            "MessageId": "test-message-id-123"
        }

        result = manager.test_notification(topic_arn)

        # Verify publish was called
        mock_boto3_clients["sns"].publish.assert_called_once()
        call_args = mock_boto3_clients["sns"].publish.call_args[1]

        assert call_args["TopicArn"] == topic_arn
        assert call_args["Subject"] == "TEST: CloudWatch Alarm Notification"
        assert "Test notification" in call_args["Message"]
        assert result is True

    def test_test_notification_custom_message(
        self, manager, mock_boto3_clients
    ):
        """Test sending test notification with custom message"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        custom_message = "Custom test message"

        # Mock publish response
        mock_boto3_clients["sns"].publish.return_value = {
            "MessageId": "test-message-id-456"
        }

        result = manager.test_notification(topic_arn, custom_message)

        # Verify publish was called with custom message
        call_args = mock_boto3_clients["sns"].publish.call_args[1]
        assert call_args["Message"] == custom_message
        assert result is True

    def test_verify_configuration_topic_not_found(
        self, manager, mock_boto3_clients
    ):
        """Test verification when topic doesn't exist"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:nonexistent"

        # Mock topic not found
        from botocore.exceptions import ClientError

        mock_boto3_clients["sns"].get_topic_attributes.side_effect = (
            ClientError(
                {"Error": {"Code": "NotFound", "Message": "Topic not found"}},
                "GetTopicAttributes",
            )
        )

        result = manager.verify_configuration(topic_arn)

        assert result["topic_exists"] is False
        assert "SNS topic not found" in result["issues"]

    def test_verify_configuration_no_subscriptions(
        self, manager, mock_boto3_clients
    ):
        """Test verification when no subscriptions configured"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"

        # Mock topic exists
        mock_boto3_clients["sns"].get_topic_attributes.return_value = {}

        # Mock no subscriptions
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": []
        }

        result = manager.verify_configuration(topic_arn)

        assert result["topic_exists"] is True
        assert result["total_subscriptions"] == 0
        assert "No subscriptions configured" in result["issues"]

    def test_verify_configuration_email_pending(
        self, manager, mock_boto3_clients
    ):
        """Test verification with pending email subscription"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"

        # Mock topic exists
        mock_boto3_clients["sns"].get_topic_attributes.return_value = {}

        # Mock pending email subscription
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "PendingConfirmation",
                    "Protocol": "email",
                    "Endpoint": "test@example.com",
                }
            ]
        }

        result = manager.verify_configuration(topic_arn)

        assert result["topic_exists"] is True
        assert result["email_configured"] is True
        assert result["email_confirmed"] is False
        assert "Email subscription pending confirmation" in result["issues"]

    def test_verify_configuration_all_active(
        self, manager, mock_boto3_clients
    ):
        """Test verification with all subscriptions active"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"

        # Mock topic exists
        mock_boto3_clients["sns"].get_topic_attributes.return_value = {}

        # Mock active subscriptions
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:abc123",
                    "Protocol": "email",
                    "Endpoint": "test@example.com",
                },
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:def456",
                    "Protocol": "https",
                    "Endpoint": "https://hooks.slack.com/services/T00/B00/XXX",
                },
            ]
        }

        result = manager.verify_configuration(topic_arn)

        assert result["topic_exists"] is True
        assert result["email_configured"] is True
        assert result["email_confirmed"] is True
        assert result["slack_configured"] is True
        assert result["total_subscriptions"] == 2
        assert len(result["issues"]) == 0

    def test_get_subscription_by_endpoint_found(
        self, manager, mock_boto3_clients
    ):
        """Test finding subscription by endpoint"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        endpoint = "test@example.com"

        # Mock subscriptions
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:abc123",
                    "Protocol": "email",
                    "Endpoint": endpoint,
                }
            ]
        }

        result = manager._get_subscription_by_endpoint(topic_arn, endpoint)

        assert result is not None
        assert result["Endpoint"] == endpoint

    def test_get_subscription_by_endpoint_not_found(
        self, manager, mock_boto3_clients
    ):
        """Test subscription not found by endpoint"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        endpoint = "notfound@example.com"

        # Mock subscriptions
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:abc123",
                    "Protocol": "email",
                    "Endpoint": "other@example.com",
                }
            ]
        }

        result = manager._get_subscription_by_endpoint(topic_arn, endpoint)

        assert result is None


class TestNotificationChannelIntegration:
    """Integration tests for notification channels"""

    def test_email_subscription_workflow(self, manager, mock_boto3_clients):
        """Test complete email subscription workflow"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        email = "workflow@example.com"

        # Step 1: No subscriptions initially
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": []
        }

        # Step 2: Create subscription
        mock_boto3_clients["sns"].subscribe.return_value = {
            "SubscriptionArn": "PendingConfirmation"
        }

        result = manager.setup_email_subscription(topic_arn, email)
        assert result["Status"] == "PendingConfirmation"

        # Step 3: Simulate confirmation (subscription now active)
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:confirmed",
                    "Protocol": "email",
                    "Endpoint": email,
                }
            ]
        }

        # Step 4: Verify configuration
        mock_boto3_clients["sns"].get_topic_attributes.return_value = {}
        verify_result = manager.verify_configuration(topic_arn)

        assert verify_result["email_configured"] is True
        assert verify_result["email_confirmed"] is True
        assert len(verify_result["issues"]) == 0

    def test_slack_subscription_workflow(self, manager, mock_boto3_clients):
        """Test complete Slack subscription workflow"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        webhook_url = "https://hooks.slack.com/services/T00/B00/XXX"

        # Step 1: No subscriptions initially
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": []
        }

        # Step 2: Create subscription (auto-confirmed for HTTPS)
        mock_boto3_clients["sns"].subscribe.return_value = {
            "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:slack123"
        }

        result = manager.setup_slack_subscription(topic_arn, webhook_url)
        assert result["Status"] == "Active"

        # Step 3: Verify configuration
        mock_boto3_clients["sns"].get_topic_attributes.return_value = {}
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:slack123",
                    "Protocol": "https",
                    "Endpoint": webhook_url,
                }
            ]
        }

        verify_result = manager.verify_configuration(topic_arn)

        assert verify_result["slack_configured"] is True
        assert len(verify_result["issues"]) == 0

    def test_multiple_channels_workflow(self, manager, mock_boto3_clients):
        """Test workflow with both email and Slack"""
        topic_arn = "arn:aws:sns:us-east-1:123456789012:test-alerts"
        email = "multi@example.com"
        webhook_url = "https://hooks.slack.com/services/T00/B00/XXX"

        # Set up both channels
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": []
        }

        mock_boto3_clients["sns"].subscribe.side_effect = [
            {"SubscriptionArn": "PendingConfirmation"},
            {
                "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:slack123"
            },
        ]

        email_result = manager.setup_email_subscription(topic_arn, email)
        slack_result = manager.setup_slack_subscription(topic_arn, webhook_url)

        assert email_result["Protocol"] == "email"
        assert slack_result["Protocol"] == "https"

        # Verify both configured
        mock_boto3_clients["sns"].get_topic_attributes.return_value = {}
        mock_boto3_clients["sns"].list_subscriptions_by_topic.return_value = {
            "Subscriptions": [
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:email123",
                    "Protocol": "email",
                    "Endpoint": email,
                },
                {
                    "SubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-alerts:slack123",
                    "Protocol": "https",
                    "Endpoint": webhook_url,
                },
            ]
        }

        verify_result = manager.verify_configuration(topic_arn)

        assert verify_result["email_configured"] is True
        assert verify_result["email_confirmed"] is True
        assert verify_result["slack_configured"] is True
        assert verify_result["total_subscriptions"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

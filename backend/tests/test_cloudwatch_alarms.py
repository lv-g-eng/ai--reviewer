"""
Tests for CloudWatch Alarms Management

This test suite validates the CloudWatch alarms management functionality,
including alarm creation, configuration, and notification setup.

Run with: pytest backend/tests/test_cloudwatch_alarms.py -v
"""

import json
from unittest.mock import MagicMock, patch
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.manage_cloudwatch_alarms import CloudWatchAlarmsManager


@pytest.fixture
def mock_boto3_clients():
    """Mock boto3 clients for CloudWatch and SNS."""
    with patch('scripts.manage_cloudwatch_alarms.boto3') as mock_boto3:
        mock_cloudwatch = MagicMock()
        mock_sns = MagicMock()

        def client_factory(service_name, **kwargs):
            if service_name == 'cloudwatch':
                return mock_cloudwatch
            elif service_name == 'sns':
                return mock_sns
            return MagicMock()

        mock_boto3.client.side_effect = client_factory

        yield {
            'boto3': mock_boto3,
            'cloudwatch': mock_cloudwatch,
            'sns': mock_sns
        }


@pytest.fixture
def alarms_manager(mock_boto3_clients):
    """Create CloudWatchAlarmsManager instance with mocked clients."""
    manager = CloudWatchAlarmsManager(
        region='us-east-1',
        environment='test',
        service_name='ai-reviewer'
    )
    return manager


class TestCloudWatchAlarmsManager:
    """Test suite for CloudWatchAlarmsManager."""

    def test_manager_initialization(self, alarms_manager):
        """Test manager initializes with correct configuration."""
        assert alarms_manager.region == 'us-east-1'
        assert alarms_manager.environment == 'test'
        assert alarms_manager.service_name == 'ai-reviewer'
        assert alarms_manager.cloudwatch is not None
        assert alarms_manager.sns is not None

    def test_create_sns_topic(self, alarms_manager, mock_boto3_clients):
        """Test SNS topic creation for alarm notifications."""
        mock_sns = mock_boto3_clients['sns']
        mock_sns.create_topic.return_value = {
            'TopicArn': 'arn:aws:sns:us-east-1:123456789012:test-ai-reviewer-alerts'
        }

        topic_arn = alarms_manager.create_sns_topic()

        # Verify topic creation
        mock_sns.create_topic.assert_called_once()
        call_args = mock_sns.create_topic.call_args
        assert call_args[1]['Name'] == 'test-ai-reviewer-alerts'
        assert any(tag['Key'] == 'Environment' and tag['Value'] == 'test'
                  for tag in call_args[1]['Tags'])

        assert topic_arn == 'arn:aws:sns:us-east-1:123456789012:test-ai-reviewer-alerts'

    def test_create_sns_topic_with_email(self, alarms_manager, mock_boto3_clients):
        """Test SNS topic creation with email subscription."""
        mock_sns = mock_boto3_clients['sns']
        mock_sns.create_topic.return_value = {
            'TopicArn': 'arn:aws:sns:us-east-1:123456789012:test-ai-reviewer-alerts'
        }

        email = 'ops@example.com'
        topic_arn = alarms_manager.create_sns_topic(email=email)

        # Verify email subscription
        mock_sns.subscribe.assert_called_once_with(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )

    def test_create_high_error_rate_alarm(self, alarms_manager, mock_boto3_clients):
        """Test creation of high error rate alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        alarm_name = alarms_manager.create_high_error_rate_alarm(sns_topic_arn, threshold=5.0)

        # Verify alarm creation
        mock_cloudwatch.put_metric_alarm.assert_called_once()
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]

        assert call_args['AlarmName'] == 'test-ai-reviewer-high-error-rate'
        assert call_args['ComparisonOperator'] == 'GreaterThanThreshold'
        assert call_args['EvaluationPeriods'] == 2
        assert call_args['Threshold'] == 5.0
        assert sns_topic_arn in call_args['AlarmActions']
        assert call_args['TreatMissingData'] == 'notBreaching'

        # Verify metrics configuration
        metrics = call_args['Metrics']
        assert len(metrics) == 3
        assert metrics[0]['Id'] == 'error_rate'
        assert metrics[0]['Expression'] == '100 * (errors / requests)'
        assert metrics[1]['Id'] == 'errors'
        assert metrics[2]['Id'] == 'requests'

        # Verify tags
        tags = call_args['Tags']
        assert any(tag['Key'] == 'Severity' and tag['Value'] == 'Critical' for tag in tags)

        assert alarm_name == 'test-ai-reviewer-high-error-rate'

    def test_create_high_response_time_alarm(self, alarms_manager, mock_boto3_clients):
        """Test creation of high response time alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        alarm_name = alarms_manager.create_high_response_time_alarm(sns_topic_arn, threshold=1.0)

        # Verify alarm creation
        mock_cloudwatch.put_metric_alarm.assert_called_once()
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]

        assert call_args['AlarmName'] == 'test-ai-reviewer-high-response-time'
        assert call_args['Threshold'] == 1.0
        assert sns_topic_arn in call_args['AlarmActions']

        # Verify metrics configuration
        metrics = call_args['Metrics']
        assert len(metrics) == 1
        assert metrics[0]['Id'] == 'response_time'
        assert metrics[0]['MetricStat']['Metric']['MetricName'] == 'http_request_duration_seconds'
        assert metrics[0]['MetricStat']['Stat'] == 'p95'
        assert metrics[0]['MetricStat']['Period'] == 300

        assert alarm_name == 'test-ai-reviewer-high-response-time'

    def test_create_high_cpu_alarm(self, alarms_manager, mock_boto3_clients):
        """Test creation of high CPU utilization alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        alarm_name = alarms_manager.create_high_cpu_alarm(
            sns_topic_arn,
            threshold=80.0,
            autoscaling_group='test-asg'
        )

        # Verify alarm creation
        mock_cloudwatch.put_metric_alarm.assert_called_once()
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]

        assert call_args['AlarmName'] == 'test-ai-reviewer-high-cpu-utilization'
        assert call_args['MetricName'] == 'CPUUtilization'
        assert call_args['Namespace'] == 'AWS/EC2'
        assert call_args['Threshold'] == 80.0
        assert call_args['Statistic'] == 'Average'
        assert call_args['Period'] == 300
        assert call_args['EvaluationPeriods'] == 2

        # Verify dimensions
        dimensions = call_args['Dimensions']
        assert len(dimensions) == 1
        assert dimensions[0]['Name'] == 'AutoScalingGroupName'
        assert dimensions[0]['Value'] == 'test-asg'

        assert alarm_name == 'test-ai-reviewer-high-cpu-utilization'

    def test_create_high_memory_alarm(self, alarms_manager, mock_boto3_clients):
        """Test creation of high memory utilization alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        alarm_name = alarms_manager.create_high_memory_alarm(sns_topic_arn, threshold=85.0)

        # Verify alarm creation
        mock_cloudwatch.put_metric_alarm.assert_called_once()
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]

        assert call_args['AlarmName'] == 'test-ai-reviewer-high-memory-utilization'
        assert call_args['MetricName'] == 'mem_used_percent'
        assert call_args['Namespace'] == 'CWAgent'
        assert call_args['Threshold'] == 85.0

        # Verify severity tag
        tags = call_args['Tags']
        assert any(tag['Key'] == 'Severity' and tag['Value'] == 'Warning' for tag in tags)

        assert alarm_name == 'test-ai-reviewer-high-memory-utilization'

    def test_create_high_disk_alarm(self, alarms_manager, mock_boto3_clients):
        """Test creation of high disk utilization alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        alarm_name = alarms_manager.create_high_disk_alarm(sns_topic_arn, threshold=90.0)

        # Verify alarm creation
        mock_cloudwatch.put_metric_alarm.assert_called_once()
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]

        assert call_args['AlarmName'] == 'test-ai-reviewer-high-disk-utilization'
        assert call_args['MetricName'] == 'disk_used_percent'
        assert call_args['Namespace'] == 'CWAgent'
        assert call_args['Threshold'] == 90.0
        assert call_args['EvaluationPeriods'] == 1

        assert alarm_name == 'test-ai-reviewer-high-disk-utilization'

    def test_create_all_alarms(self, alarms_manager, mock_boto3_clients):
        """Test creation of all alarms at once."""
        mock_sns = mock_boto3_clients['sns']
        mock_cloudwatch = mock_boto3_clients['cloudwatch']

        mock_sns.create_topic.return_value = {
            'TopicArn': 'arn:aws:sns:us-east-1:123456789012:test-alerts'
        }

        alarm_names = alarms_manager.create_all_alarms(
            email='ops@example.com',
            autoscaling_group='test-asg'
        )

        # Verify SNS topic creation
        mock_sns.create_topic.assert_called_once()
        mock_sns.subscribe.assert_called_once()

        # Verify all alarms created
        assert len(alarm_names) == 5
        assert mock_cloudwatch.put_metric_alarm.call_count == 5

        # Verify alarm names
        expected_alarms = [
            'test-ai-reviewer-high-error-rate',
            'test-ai-reviewer-high-response-time',
            'test-ai-reviewer-high-cpu-utilization',
            'test-ai-reviewer-high-memory-utilization',
            'test-ai-reviewer-high-disk-utilization'
        ]
        assert all(name in alarm_names for name in expected_alarms)

    def test_list_alarms(self, alarms_manager, mock_boto3_clients):
        """Test listing CloudWatch alarms."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        mock_cloudwatch.describe_alarms.return_value = {
            'MetricAlarms': [
                {
                    'AlarmName': 'test-alarm-1',
                    'StateValue': 'OK',
                    'AlarmDescription': 'Test alarm 1',
                    'Threshold': 5.0
                },
                {
                    'AlarmName': 'test-alarm-2',
                    'StateValue': 'ALARM',
                    'AlarmDescription': 'Test alarm 2',
                    'Threshold': 80.0
                }
            ]
        }

        alarms = alarms_manager.list_alarms()

        # Verify API call
        mock_cloudwatch.describe_alarms.assert_called_once_with(MaxRecords=100)

        # Verify results
        assert len(alarms) == 2
        assert alarms[0]['AlarmName'] == 'test-alarm-1'
        assert alarms[0]['StateValue'] == 'OK'
        assert alarms[1]['AlarmName'] == 'test-alarm-2'
        assert alarms[1]['StateValue'] == 'ALARM'

    def test_list_alarms_with_prefix(self, alarms_manager, mock_boto3_clients):
        """Test listing alarms with name prefix filter."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        mock_cloudwatch.describe_alarms.return_value = {
            'MetricAlarms': [
                {
                    'AlarmName': 'prod-ai-reviewer-high-error-rate',
                    'StateValue': 'OK',
                    'AlarmDescription': 'Error rate alarm',
                    'Threshold': 5.0
                }
            ]
        }

        alarms = alarms_manager.list_alarms(prefix='prod-ai-reviewer')

        # Verify API call with prefix
        mock_cloudwatch.describe_alarms.assert_called_once_with(
            AlarmNamePrefix='prod-ai-reviewer',
            MaxRecords=100
        )

        assert len(alarms) == 1
        assert 'prod-ai-reviewer' in alarms[0]['AlarmName']

    def test_describe_alarm(self, alarms_manager, mock_boto3_clients):
        """Test describing a specific alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        mock_cloudwatch.describe_alarms.return_value = {
            'MetricAlarms': [
                {
                    'AlarmName': 'test-alarm',
                    'StateValue': 'OK',
                    'AlarmDescription': 'Test alarm',
                    'Threshold': 5.0,
                    'ComparisonOperator': 'GreaterThanThreshold',
                    'EvaluationPeriods': 2
                }
            ]
        }

        alarm = alarms_manager.describe_alarm('test-alarm')

        # Verify API call
        mock_cloudwatch.describe_alarms.assert_called_once_with(
            AlarmNames=['test-alarm']
        )

        # Verify result
        assert alarm is not None
        assert alarm['AlarmName'] == 'test-alarm'
        assert alarm['StateValue'] == 'OK'
        assert alarm['Threshold'] == 5.0

    def test_describe_alarm_not_found(self, alarms_manager, mock_boto3_clients):
        """Test describing a non-existent alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        mock_cloudwatch.describe_alarms.return_value = {
            'MetricAlarms': []
        }

        alarm = alarms_manager.describe_alarm('non-existent-alarm')

        assert alarm is None

    def test_delete_alarm(self, alarms_manager, mock_boto3_clients):
        """Test deleting a CloudWatch alarm."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']

        result = alarms_manager.delete_alarm('test-alarm')

        # Verify API call
        mock_cloudwatch.delete_alarms.assert_called_once_with(
            AlarmNames=['test-alarm']
        )

        assert result is True

    def test_test_alarm(self, alarms_manager, mock_boto3_clients):
        """Test triggering an alarm for testing."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']

        result = alarms_manager.test_alarm('test-alarm')

        # Verify API call
        mock_cloudwatch.set_alarm_state.assert_called_once()
        call_args = mock_cloudwatch.set_alarm_state.call_args[1]

        assert call_args['AlarmName'] == 'test-alarm'
        assert call_args['StateValue'] == 'ALARM'
        assert call_args['StateReason'] == 'Testing alarm notification'

        # Verify state reason data is valid JSON
        state_data = json.loads(call_args['StateReasonData'])
        assert state_data['test'] is True

        assert result is True

    def test_alarm_configuration_thresholds(self, alarms_manager, mock_boto3_clients):
        """Test that alarm thresholds match requirements."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        # Test error rate threshold (5%)
        alarms_manager.create_high_error_rate_alarm(sns_topic_arn, threshold=5.0)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]
        assert call_args['Threshold'] == 5.0

        # Test response time threshold (1 second)
        alarms_manager.create_high_response_time_alarm(sns_topic_arn, threshold=1.0)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]
        assert call_args['Threshold'] == 1.0

        # Test CPU threshold (80%)
        alarms_manager.create_high_cpu_alarm(sns_topic_arn, threshold=80.0)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]
        assert call_args['Threshold'] == 80.0

    def test_alarm_evaluation_periods(self, alarms_manager, mock_boto3_clients):
        """Test that alarms have correct evaluation periods."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        # Error rate: 2 periods of 5 minutes = 10 minutes total
        alarms_manager.create_high_error_rate_alarm(sns_topic_arn)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]
        assert call_args['EvaluationPeriods'] == 2

        # Response time: 2 periods of 5 minutes = 10 minutes total
        alarms_manager.create_high_response_time_alarm(sns_topic_arn)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]
        assert call_args['EvaluationPeriods'] == 2

        # CPU: 2 periods of 5 minutes = 10 minutes total
        alarms_manager.create_high_cpu_alarm(sns_topic_arn)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]
        assert call_args['EvaluationPeriods'] == 2

    def test_alarm_actions_configuration(self, alarms_manager, mock_boto3_clients):
        """Test that alarms have correct actions configured."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        alarms_manager.create_high_error_rate_alarm(sns_topic_arn)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]

        # Verify alarm actions (triggered when alarm state)
        assert sns_topic_arn in call_args['AlarmActions']

        # Verify OK actions (triggered when returning to OK state)
        assert sns_topic_arn in call_args['OKActions']

    def test_alarm_tags(self, alarms_manager, mock_boto3_clients):
        """Test that alarms have proper tags."""
        mock_cloudwatch = mock_boto3_clients['cloudwatch']
        sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-alerts'

        alarms_manager.create_high_error_rate_alarm(sns_topic_arn)
        call_args = mock_cloudwatch.put_metric_alarm.call_args[1]

        tags = call_args['Tags']

        # Verify required tags
        tag_dict = {tag['Key']: tag['Value'] for tag in tags}
        assert 'Environment' in tag_dict
        assert tag_dict['Environment'] == 'test'
        assert 'Severity' in tag_dict
        assert 'Runbook' in tag_dict


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

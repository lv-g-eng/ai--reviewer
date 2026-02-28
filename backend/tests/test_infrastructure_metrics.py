"""
Unit tests for infrastructure metrics collection

Tests:
- System metrics collection (CPU, memory, disk, network)
- Connection pool metrics collection
- Cache metrics collection
- CloudWatch metrics sending
- Metrics collector initialization

Validates Requirements: 7.4, 7.10
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.infrastructure_metrics import (
    InfrastructureMetricsCollector,
    get_metrics_collector,
    collect_and_send_metrics
)


class TestInfrastructureMetricsCollector:
    """Test infrastructure metrics collector"""
    
    def test_collector_initialization(self):
        """Test metrics collector initializes with correct configuration"""
        collector = InfrastructureMetricsCollector(
            namespace="TestNamespace",
            region_name="us-west-2",
            enabled=True
        )
        
        assert collector.namespace == "TestNamespace"
        assert collector.region_name == "us-west-2"
        assert collector.enabled is True
    
    def test_collector_initialization_from_env(self, monkeypatch):
        """Test metrics collector reads configuration from environment"""
        monkeypatch.setenv('ENVIRONMENT', 'production')
        monkeypatch.setenv('SERVICE_NAME', 'test-service')
        monkeypatch.setenv('INSTANCE_ID', 'i-12345')
        monkeypatch.setenv('AWS_REGION', 'eu-west-1')
        
        collector = InfrastructureMetricsCollector()
        
        assert collector.environment == 'production'
        assert collector.service_name == 'test-service'
        assert collector.instance_id == 'i-12345'
        assert collector.region_name == 'eu-west-1'
        assert collector.namespace == 'AICodeReviewer/production'
    
    @patch('app.core.infrastructure_metrics.psutil')
    def test_collect_system_metrics(self, mock_psutil):
        """Test system metrics collection (Requirement 7.4)"""
        # Mock psutil functions
        mock_psutil.cpu_percent.return_value = 45.5
        mock_psutil.virtual_memory.return_value = Mock(
            percent=60.0,
            available=4 * 1024 * 1024 * 1024,  # 4GB
            used=6 * 1024 * 1024 * 1024  # 6GB
        )
        mock_psutil.disk_usage.return_value = Mock(
            percent=70.0,
            free=100 * 1024 * 1024 * 1024,  # 100GB
            used=200 * 1024 * 1024 * 1024  # 200GB
        )
        mock_psutil.net_io_counters.return_value = Mock(
            bytes_sent=1000000,
            bytes_recv=2000000,
            packets_sent=5000,
            packets_recv=10000,
            errin=10,
            errout=5,
            dropin=2,
            dropout=1
        )
        mock_psutil.pids.return_value = list(range(100))
        
        collector = InfrastructureMetricsCollector(enabled=False)
        metrics = collector.collect_system_metrics()
        
        # Verify CPU metrics
        assert metrics['cpu_usage_percent'] == 45.5
        
        # Verify memory metrics
        assert metrics['memory_used_percent'] == 60.0
        assert metrics['memory_available_mb'] == pytest.approx(4096, rel=0.1)
        assert metrics['memory_used_mb'] == pytest.approx(6144, rel=0.1)
        
        # Verify disk metrics
        assert metrics['disk_used_percent'] == 70.0
        assert metrics['disk_free_gb'] == pytest.approx(100, rel=0.1)
        assert metrics['disk_used_gb'] == pytest.approx(200, rel=0.1)
        
        # Verify network metrics
        assert metrics['network_bytes_sent'] == 1000000
        assert metrics['network_bytes_received'] == 2000000
        assert metrics['network_packets_sent'] == 5000
        assert metrics['network_packets_received'] == 10000
        assert metrics['network_errors_in'] == 10
        assert metrics['network_errors_out'] == 5
        assert metrics['network_drops_in'] == 2
        assert metrics['network_drops_out'] == 1
        
        # Verify process metrics
        assert metrics['processes_total'] == 100
    
    def test_collect_connection_pool_metrics(self):
        """Test connection pool metrics collection (Requirement 7.4)"""
        collector = InfrastructureMetricsCollector(enabled=False)
        
        metrics = collector.collect_connection_pool_metrics(
            pool_name='postgresql',
            size=20,
            checked_out=15,
            overflow=2,
            checked_in=5
        )
        
        assert metrics['postgresql_pool_size'] == 20
        assert metrics['postgresql_pool_checked_out'] == 15
        assert metrics['postgresql_pool_overflow'] == 2
        assert metrics['postgresql_pool_checked_in'] == 5
        assert metrics['postgresql_pool_utilization_percent'] == 75.0
    
    def test_collect_connection_pool_metrics_zero_size(self):
        """Test connection pool metrics with zero size"""
        collector = InfrastructureMetricsCollector(enabled=False)
        
        metrics = collector.collect_connection_pool_metrics(
            pool_name='test',
            size=0,
            checked_out=0,
            overflow=0,
            checked_in=0
        )
        
        assert metrics['test_pool_utilization_percent'] == 0
    
    def test_collect_cache_metrics(self):
        """Test cache metrics collection (Requirement 7.4)"""
        collector = InfrastructureMetricsCollector(enabled=False)
        
        metrics = collector.collect_cache_metrics(
            cache_name='redis',
            hits=800,
            misses=200,
            evictions=50,
            size=10000
        )
        
        assert metrics['redis_cache_hits'] == 800
        assert metrics['redis_cache_misses'] == 200
        assert metrics['redis_cache_hit_ratio_percent'] == 80.0
        assert metrics['redis_cache_miss_ratio_percent'] == 20.0
        assert metrics['redis_cache_evictions'] == 50
        assert metrics['redis_cache_size'] == 10000
    
    def test_collect_cache_metrics_zero_requests(self):
        """Test cache metrics with zero requests"""
        collector = InfrastructureMetricsCollector(enabled=False)
        
        metrics = collector.collect_cache_metrics(
            cache_name='test',
            hits=0,
            misses=0,
            evictions=0,
            size=0
        )
        
        assert metrics['test_cache_hit_ratio_percent'] == 0
        assert metrics['test_cache_miss_ratio_percent'] == 0
    
    @patch('app.core.infrastructure_metrics.boto3')
    def test_send_metrics_to_cloudwatch(self, mock_boto3):
        """Test sending metrics to CloudWatch (Requirement 7.4)"""
        # Mock CloudWatch client
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        collector = InfrastructureMetricsCollector(enabled=True)
        collector.cloudwatch_client = mock_client
        
        metrics = {
            'cpu_usage_percent': 45.5,
            'memory_used_percent': 60.0,
            'disk_used_percent': 70.0
        }
        
        success = collector.send_metrics_to_cloudwatch(metrics)
        
        assert success is True
        assert mock_client.put_metric_data.called
        
        # Verify call arguments
        call_args = mock_client.put_metric_data.call_args
        assert call_args[1]['Namespace'] == collector.namespace
        assert len(call_args[1]['MetricData']) == 3
    
    @patch('app.core.infrastructure_metrics.boto3')
    def test_send_metrics_with_custom_dimensions(self, mock_boto3):
        """Test sending metrics with custom dimensions"""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        collector = InfrastructureMetricsCollector(enabled=True)
        collector.cloudwatch_client = mock_client
        
        metrics = {'test_metric': 100}
        dimensions = {'CustomDimension': 'CustomValue'}
        
        success = collector.send_metrics_to_cloudwatch(metrics, dimensions)
        
        assert success is True
        
        # Verify dimensions are included
        call_args = mock_client.put_metric_data.call_args
        metric_data = call_args[1]['MetricData'][0]
        dimension_names = [d['Name'] for d in metric_data['Dimensions']]
        
        assert 'CustomDimension' in dimension_names
        assert 'Environment' in dimension_names
        assert 'ServiceName' in dimension_names
        assert 'InstanceId' in dimension_names
    
    def test_send_metrics_disabled(self):
        """Test metrics sending when disabled"""
        collector = InfrastructureMetricsCollector(enabled=False)
        
        metrics = {'test_metric': 100}
        success = collector.send_metrics_to_cloudwatch(metrics)
        
        assert success is False
    
    def test_send_metrics_empty(self):
        """Test sending empty metrics"""
        collector = InfrastructureMetricsCollector(enabled=True)
        
        metrics = {}
        success = collector.send_metrics_to_cloudwatch(metrics)
        
        assert success is False
    
    @patch('app.core.infrastructure_metrics.boto3')
    def test_send_metrics_batch_processing(self, mock_boto3):
        """Test metrics are sent in batches of 20 (CloudWatch limit)"""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        collector = InfrastructureMetricsCollector(enabled=True)
        collector.cloudwatch_client = mock_client
        
        # Create 45 metrics (should result in 3 batches: 20, 20, 5)
        metrics = {f'metric_{i}': i for i in range(45)}
        
        success = collector.send_metrics_to_cloudwatch(metrics)
        
        assert success is True
        assert mock_client.put_metric_data.call_count == 3
    
    def test_get_metric_unit(self):
        """Test metric unit detection"""
        collector = InfrastructureMetricsCollector(enabled=False)
        
        assert collector._get_metric_unit('cpu_usage_percent') == 'Percent'
        assert collector._get_metric_unit('memory_used_mb') == 'Megabytes'
        assert collector._get_metric_unit('disk_free_gb') == 'Gigabytes'
        assert collector._get_metric_unit('network_bytes_sent') == 'Bytes'
        assert collector._get_metric_unit('response_time_ms') == 'Milliseconds'
        assert collector._get_metric_unit('duration_seconds') == 'Seconds'
        assert collector._get_metric_unit('request_count') == 'Count'
    
    @patch('app.core.infrastructure_metrics.psutil')
    @patch('app.core.infrastructure_metrics.boto3')
    def test_collect_and_send_all_metrics(self, mock_boto3, mock_psutil):
        """Test collecting and sending all metrics"""
        # Mock psutil
        mock_psutil.cpu_percent.return_value = 45.5
        mock_psutil.virtual_memory.return_value = Mock(
            percent=60.0,
            available=4 * 1024 * 1024 * 1024,
            used=6 * 1024 * 1024 * 1024
        )
        mock_psutil.disk_usage.return_value = Mock(
            percent=70.0,
            free=100 * 1024 * 1024 * 1024,
            used=200 * 1024 * 1024 * 1024
        )
        mock_psutil.net_io_counters.return_value = Mock(
            bytes_sent=1000000,
            bytes_recv=2000000,
            packets_sent=5000,
            packets_recv=10000,
            errin=10,
            errout=5,
            dropin=2,
            dropout=1
        )
        mock_psutil.pids.return_value = list(range(100))
        
        # Mock CloudWatch client
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        collector = InfrastructureMetricsCollector(enabled=True)
        collector.cloudwatch_client = mock_client
        
        # Add additional metrics
        additional_metrics = {'custom_metric': 123}
        
        success = collector.collect_and_send_all_metrics(additional_metrics)
        
        assert success is True
        assert mock_client.put_metric_data.called
        
        # Verify system metrics and additional metrics were sent
        call_args = mock_client.put_metric_data.call_args
        metric_names = [m['MetricName'] for m in call_args[1]['MetricData']]
        
        assert 'cpu_usage_percent' in metric_names
        assert 'memory_used_percent' in metric_names
        assert 'custom_metric' in metric_names


class TestGlobalMetricsCollector:
    """Test global metrics collector functions"""
    
    def test_get_metrics_collector_singleton(self):
        """Test get_metrics_collector returns singleton instance"""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        
        assert collector1 is collector2
    
    @patch('app.core.infrastructure_metrics.InfrastructureMetricsCollector')
    def test_collect_and_send_metrics_convenience(self, mock_collector_class):
        """Test convenience function for collecting and sending metrics"""
        mock_instance = MagicMock()
        mock_instance.collect_and_send_all_metrics.return_value = True
        mock_collector_class.return_value = mock_instance
        
        # Reset global instance
        import app.core.infrastructure_metrics as metrics_module
        metrics_module._metrics_collector = None
        
        additional_metrics = {'test': 123}
        result = collect_and_send_metrics(additional_metrics)
        
        assert result is True
        mock_instance.collect_and_send_all_metrics.assert_called_once_with(additional_metrics)


class TestMetricsCollectorErrorHandling:
    """Test error handling in metrics collector"""
    
    @patch('app.core.infrastructure_metrics.psutil')
    def test_collect_system_metrics_error_handling(self, mock_psutil):
        """Test system metrics collection handles errors gracefully"""
        mock_psutil.cpu_percent.side_effect = Exception("CPU error")
        
        collector = InfrastructureMetricsCollector(enabled=False)
        metrics = collector.collect_system_metrics()
        
        # Should return empty dict on error
        assert metrics == {}
    
    @patch('app.core.infrastructure_metrics.boto3')
    def test_send_metrics_client_error(self, mock_boto3):
        """Test sending metrics handles ClientError"""
        from botocore.exceptions import ClientError
        
        mock_client = MagicMock()
        mock_client.put_metric_data.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied'}},
            'PutMetricData'
        )
        mock_boto3.client.return_value = mock_client
        
        collector = InfrastructureMetricsCollector(enabled=True)
        collector.cloudwatch_client = mock_client
        
        metrics = {'test_metric': 100}
        success = collector.send_metrics_to_cloudwatch(metrics)
        
        assert success is False
    
    @patch('app.core.infrastructure_metrics.boto3')
    def test_send_metrics_unexpected_error(self, mock_boto3):
        """Test sending metrics handles unexpected errors"""
        mock_client = MagicMock()
        mock_client.put_metric_data.side_effect = Exception("Unexpected error")
        mock_boto3.client.return_value = mock_client
        
        collector = InfrastructureMetricsCollector(enabled=True)
        collector.cloudwatch_client = mock_client
        
        metrics = {'test_metric': 100}
        success = collector.send_metrics_to_cloudwatch(metrics)
        
        assert success is False

"""
Tests for CloudWatch dashboard management.

Validates Requirements: 18.2
"""
import json
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from manage_cloudwatch_dashboards import CloudWatchDashboardManager
    SCRIPT_AVAILABLE = True
except ImportError:
    SCRIPT_AVAILABLE = False


@pytest.mark.skipif(not SCRIPT_AVAILABLE, reason="Dashboard management script not available")
class TestCloudWatchDashboardManager:
    """Test CloudWatch dashboard management."""
    
    @pytest.fixture
    def mock_cloudwatch_client(self):
        """Create mock CloudWatch client."""
        with patch('manage_cloudwatch_dashboards.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def manager(self, mock_cloudwatch_client):
        """Create dashboard manager instance."""
        return CloudWatchDashboardManager(
            region='us-east-1',
            environment='test',
            service_name='test-service'
        )
    
    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.region == 'us-east-1'
        assert manager.environment == 'test'
        assert manager.service_name == 'test-service'
    
    def test_initialization_with_env_vars(self, mock_cloudwatch_client):
        """Test initialization with environment variables."""
        with patch.dict(os.environ, {
            'AWS_REGION': 'eu-west-1',
            'ENVIRONMENT': 'prod',
            'SERVICE_NAME': 'my-service'
        }):
            manager = CloudWatchDashboardManager()
            assert manager.region == 'eu-west-1'
            assert manager.environment == 'prod'
            assert manager.service_name == 'my-service'
    
    def test_create_system_health_dashboard(self, manager, mock_cloudwatch_client):
        """Test creating system health dashboard."""
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        response = manager.create_system_health_dashboard()
        
        # Verify put_dashboard was called
        assert mock_cloudwatch_client.put_dashboard.called
        call_args = mock_cloudwatch_client.put_dashboard.call_args
        
        # Verify dashboard name
        assert call_args[1]['DashboardName'] == 'test-test-service-system-health'
        
        # Verify dashboard body is valid JSON
        dashboard_body = json.loads(call_args[1]['DashboardBody'])
        assert 'widgets' in dashboard_body
        assert len(dashboard_body['widgets']) > 0
        
        # Verify required widgets exist
        widget_titles = [w['properties']['title'] for w in dashboard_body['widgets']]
        assert any('Uptime' in title for title in widget_titles)
        assert any('Error' in title for title in widget_titles)
        assert any('Health Check' in title for title in widget_titles)
        assert any('Active User Sessions' in title for title in widget_titles)
    
    def test_create_performance_dashboard(self, manager, mock_cloudwatch_client):
        """Test creating performance dashboard."""
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        response = manager.create_performance_dashboard()
        
        # Verify put_dashboard was called
        assert mock_cloudwatch_client.put_dashboard.called
        call_args = mock_cloudwatch_client.put_dashboard.call_args
        
        # Verify dashboard name
        assert call_args[1]['DashboardName'] == 'test-test-service-performance'
        
        # Verify dashboard body
        dashboard_body = json.loads(call_args[1]['DashboardBody'])
        widget_titles = [w['properties']['title'] for w in dashboard_body['widgets']]
        assert any('Response Time' in title for title in widget_titles)
        assert any('Database' in title for title in widget_titles)
        assert any('Cache' in title for title in widget_titles)
    
    def test_create_business_metrics_dashboard(self, manager, mock_cloudwatch_client):
        """Test creating business metrics dashboard."""
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        response = manager.create_business_metrics_dashboard()
        
        # Verify put_dashboard was called
        assert mock_cloudwatch_client.put_dashboard.called
        call_args = mock_cloudwatch_client.put_dashboard.call_args
        
        # Verify dashboard name
        assert call_args[1]['DashboardName'] == 'test-test-service-business-metrics'
        
        # Verify dashboard body
        dashboard_body = json.loads(call_args[1]['DashboardBody'])
        widget_titles = [w['properties']['title'] for w in dashboard_body['widgets']]
        assert any('Analysis' in title for title in widget_titles)
        assert any('User Activity' in title for title in widget_titles)
    
    def test_list_dashboards(self, manager, mock_cloudwatch_client):
        """Test listing dashboards."""
        mock_cloudwatch_client.list_dashboards.return_value = {
            'DashboardEntries': [
                {'DashboardName': 'test-dashboard-1'},
                {'DashboardName': 'test-dashboard-2'}
            ]
        }
        
        dashboards = manager.list_dashboards()
        
        assert len(dashboards) == 2
        assert dashboards[0]['DashboardName'] == 'test-dashboard-1'
        assert dashboards[1]['DashboardName'] == 'test-dashboard-2'
    
    def test_get_dashboard(self, manager, mock_cloudwatch_client):
        """Test getting dashboard configuration."""
        dashboard_config = {
            'widgets': [
                {'type': 'metric', 'properties': {'title': 'Test Widget'}}
            ]
        }
        
        mock_cloudwatch_client.get_dashboard.return_value = {
            'DashboardBody': json.dumps(dashboard_config)
        }
        
        config = manager.get_dashboard('test-dashboard')
        
        assert config == dashboard_config
        assert config['widgets'][0]['properties']['title'] == 'Test Widget'
    
    def test_delete_dashboard(self, manager, mock_cloudwatch_client):
        """Test deleting dashboard."""
        mock_cloudwatch_client.delete_dashboards.return_value = {}
        
        response = manager.delete_dashboard('test-dashboard')
        
        mock_cloudwatch_client.delete_dashboards.assert_called_once_with(
            DashboardNames=['test-dashboard']
        )
    
    def test_create_all_dashboards(self, manager, mock_cloudwatch_client):
        """Test creating all dashboards."""
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        manager.create_all_dashboards()
        
        # Verify put_dashboard was called 3 times (one for each dashboard)
        assert mock_cloudwatch_client.put_dashboard.call_count == 3
        
        # Verify dashboard names
        call_args_list = mock_cloudwatch_client.put_dashboard.call_args_list
        dashboard_names = [call[1]['DashboardName'] for call in call_args_list]
        
        assert 'test-test-service-system-health' in dashboard_names
        assert 'test-test-service-performance' in dashboard_names
        assert 'test-test-service-business-metrics' in dashboard_names
    
    def test_dashboard_widget_structure(self, manager, mock_cloudwatch_client):
        """Test dashboard widget structure is valid."""
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        manager.create_system_health_dashboard()
        
        call_args = mock_cloudwatch_client.put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]['DashboardBody'])
        
        # Verify each widget has required fields
        for widget in dashboard_body['widgets']:
            assert 'type' in widget
            assert 'properties' in widget
            assert 'width' in widget
            assert 'height' in widget
            assert 'x' in widget
            assert 'y' in widget
            
            # Verify properties
            properties = widget['properties']
            assert 'metrics' in properties
            assert 'region' in properties
            assert 'title' in properties
    
    def test_dashboard_metrics_format(self, manager, mock_cloudwatch_client):
        """Test dashboard metrics are properly formatted."""
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        manager.create_system_health_dashboard()
        
        call_args = mock_cloudwatch_client.put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]['DashboardBody'])
        
        # Check first widget's metrics
        first_widget = dashboard_body['widgets'][0]
        metrics = first_widget['properties']['metrics']
        
        # Verify metrics is a list
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        
        # Verify each metric is properly formatted
        for metric in metrics:
            assert isinstance(metric, list)
            # Metric should have at least namespace and metric name
            assert len(metric) >= 2
    
    def test_error_handling_put_dashboard(self, manager, mock_cloudwatch_client):
        """Test error handling when creating dashboard fails."""
        from botocore.exceptions import ClientError
        
        mock_cloudwatch_client.put_dashboard.side_effect = ClientError(
            {'Error': {'Code': 'InvalidParameterValue', 'Message': 'Invalid dashboard'}},
            'PutDashboard'
        )
        
        with pytest.raises(ClientError):
            manager.create_system_health_dashboard()
    
    def test_error_handling_list_dashboards(self, manager, mock_cloudwatch_client):
        """Test error handling when listing dashboards fails."""
        from botocore.exceptions import ClientError
        
        mock_cloudwatch_client.list_dashboards.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'ListDashboards'
        )
        
        with pytest.raises(ClientError):
            manager.list_dashboards()
    
    def test_dashboard_annotations(self, manager, mock_cloudwatch_client):
        """Test dashboard widgets have proper annotations for thresholds."""
        mock_cloudwatch_client.put_dashboard.return_value = {
            'DashboardValidationMessages': []
        }
        
        manager.create_system_health_dashboard()
        
        call_args = mock_cloudwatch_client.put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]['DashboardBody'])
        
        # Find widgets with annotations
        widgets_with_annotations = [
            w for w in dashboard_body['widgets']
            if 'annotations' in w['properties']
        ]
        
        # Verify at least some widgets have annotations
        assert len(widgets_with_annotations) > 0
        
        # Verify annotation structure
        for widget in widgets_with_annotations:
            annotations = widget['properties']['annotations']
            assert 'horizontal' in annotations
            
            for annotation in annotations['horizontal']:
                assert 'value' in annotation
                assert 'label' in annotation
                assert 'fill' in annotation
                assert 'color' in annotation


@pytest.mark.skipif(not SCRIPT_AVAILABLE, reason="Dashboard management script not available")
class TestDashboardWidgetContent:
    """Test specific dashboard widget content."""
    
    @pytest.fixture
    def manager(self):
        """Create dashboard manager instance."""
        with patch('manage_cloudwatch_dashboards.boto3'):
            return CloudWatchDashboardManager(
                region='us-east-1',
                environment='test',
                service_name='test-service'
            )
    
    def test_uptime_widget_calculation(self, manager):
        """Test uptime percentage widget exists with correct title."""
        with patch.object(manager.cloudwatch, 'put_dashboard') as mock_put:
            mock_put.return_value = {'DashboardValidationMessages': []}
            
            manager.create_system_health_dashboard()
            
            call_args = mock_put.call_args
            dashboard_body = json.loads(call_args[1]['DashboardBody'])
            
            # Find uptime percentage widget
            uptime_widget = next(
                (w for w in dashboard_body['widgets']
                 if 'Uptime Percentage' in w['properties']['title']),
                None
            )
            
            assert uptime_widget is not None
            assert 'Target: 99.5%' in uptime_widget['properties']['title']
            
            # Verify it has metrics
            metrics = uptime_widget['properties']['metrics']
            assert len(metrics) > 0
    
    def test_error_rate_widget_calculation(self, manager):
        """Test error rate widget exists with correct title."""
        with patch.object(manager.cloudwatch, 'put_dashboard') as mock_put:
            mock_put.return_value = {'DashboardValidationMessages': []}
            
            manager.create_system_health_dashboard()
            
            call_args = mock_put.call_args
            dashboard_body = json.loads(call_args[1]['DashboardBody'])
            
            # Find error rate percentage widget
            error_rate_widget = next(
                (w for w in dashboard_body['widgets']
                 if 'Overall Error Rate' in w['properties']['title']),
                None
            )
            
            assert error_rate_widget is not None
            assert 'Target: < 5%' in error_rate_widget['properties']['title']
            
            # Verify it has metrics
            metrics = error_rate_widget['properties']['metrics']
            assert len(metrics) > 0
    
    def test_sla_target_annotation(self, manager):
        """Test SLA target annotation is set correctly."""
        with patch.object(manager.cloudwatch, 'put_dashboard') as mock_put:
            mock_put.return_value = {'DashboardValidationMessages': []}
            
            manager.create_system_health_dashboard()
            
            call_args = mock_put.call_args
            dashboard_body = json.loads(call_args[1]['DashboardBody'])
            
            # Find uptime percentage widget
            uptime_widget = next(
                w for w in dashboard_body['widgets']
                if 'Uptime Percentage' in w['properties']['title']
            )
            
            # Verify SLA target annotation
            annotations = uptime_widget['properties']['annotations']['horizontal']
            sla_annotation = next(a for a in annotations if 'SLA' in a['label'])
            
            assert sla_annotation['value'] == 99.5
            assert sla_annotation['fill'] == 'above'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

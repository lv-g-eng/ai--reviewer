"""
Unit tests for Celery configuration with Redis backend.

Tests verify:
- Celery app initialization
- Redis broker and result backend configuration
- Task routing and priority queues
- Task execution settings
- Retry configuration
- Rate limiting
- Periodic task scheduling

Validates Requirements: 10.7 (Asynchronous task processing using Celery)
"""
import pytest
from celery import Celery

from app.celery_config import celery_app, debug_task


class TestCeleryConfiguration:
    """Test Celery configuration settings."""
    
    def test_celery_app_initialization(self):
        """Test Celery app is properly initialized."""
        assert isinstance(celery_app, Celery)
        assert celery_app.main == "ai_code_review"
    
    def test_broker_configuration(self):
        """Test Redis broker is configured correctly."""
        # Broker URL should be set
        assert celery_app.conf.broker_url is not None
        assert 'redis://' in celery_app.conf.broker_url
        
        # Broker connection settings
        assert celery_app.conf.broker_connection_retry_on_startup is True
        assert celery_app.conf.broker_connection_retry is True
        assert celery_app.conf.broker_connection_max_retries == 10
    
    def test_result_backend_configuration(self):
        """Test Redis result backend is configured correctly."""
        # Result backend URL should be set
        assert celery_app.conf.result_backend is not None
        assert 'redis://' in celery_app.conf.result_backend
        
        # Result backend settings
        assert celery_app.conf.result_expires == 3600  # 1 hour
        assert celery_app.conf.result_persistent is True
        assert celery_app.conf.result_compression == 'gzip'
        assert celery_app.conf.result_extended is True
    
    def test_serialization_configuration(self):
        """Test task serialization is configured for security."""
        assert celery_app.conf.task_serializer == 'json'
        assert celery_app.conf.accept_content == ['json']
        assert celery_app.conf.result_serializer == 'json'
    
    def test_timezone_configuration(self):
        """Test timezone is set to UTC."""
        assert celery_app.conf.timezone == 'UTC'
        assert celery_app.conf.enable_utc is True
    
    def test_task_execution_settings(self):
        """Test task execution settings for reliability."""
        assert celery_app.conf.task_acks_late is True
        assert celery_app.conf.task_reject_on_worker_lost is True
        assert celery_app.conf.task_track_started is True
        assert celery_app.conf.task_time_limit == 3600  # 1 hour
        assert celery_app.conf.task_soft_time_limit == 3300  # 55 minutes
        assert celery_app.conf.task_ignore_result is False
        assert celery_app.conf.task_store_errors_even_if_ignored is True
    
    def test_task_queues_configuration(self):
        """Test priority queues are configured correctly."""
        queues = celery_app.conf.task_queues
        
        # Should have 3 queues
        assert len(queues) == 3
        
        # Extract queue names
        queue_names = {q.name for q in queues}
        
        # Verify all queues exist
        assert 'high_priority' in queue_names
        assert 'default' in queue_names
        assert 'low_priority' in queue_names
        
        # Verify queue arguments for priority
        for queue in queues:
            assert 'x-max-priority' in queue.queue_arguments
            assert queue.queue_arguments['x-max-priority'] == 10
    
    def test_task_routing_configuration(self):
        """Test task routing to appropriate queues."""
        routes = celery_app.conf.task_routes
        
        # High priority tasks
        pr_analysis_route = routes.get('app.tasks.pull_request_analysis.analyze_pull_request')
        assert pr_analysis_route is not None
        assert pr_analysis_route['queue'] == 'high_priority'
        assert pr_analysis_route['priority'] == 10
        
        # Low priority tasks
        drift_route = routes.get('app.tasks.architectural_drift.detect_architectural_drift')
        assert drift_route is not None
        assert drift_route['queue'] == 'low_priority'
        assert drift_route['priority'] == 2
    
    def test_worker_configuration(self):
        """Test worker settings."""
        assert celery_app.conf.worker_prefetch_multiplier == 1
        assert celery_app.conf.worker_max_tasks_per_child == 1000
        assert celery_app.conf.worker_disable_rate_limits is False
        assert celery_app.conf.worker_send_task_events is True
    
    def test_retry_configuration(self):
        """Test retry settings for failed tasks."""
        assert celery_app.conf.task_default_retry_delay == 60  # 1 minute
        assert celery_app.conf.task_max_retries == 3
        assert celery_app.conf.task_autoretry_for == (Exception,)
        assert celery_app.conf.task_retry_backoff is True
        assert celery_app.conf.task_retry_backoff_max == 600  # 10 minutes
        assert celery_app.conf.task_retry_jitter is True
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting settings."""
        assert celery_app.conf.task_default_rate_limit == '10/m'
        
        # Task-specific rate limits
        annotations = celery_app.conf.task_annotations
        assert annotations['app.tasks.pull_request_analysis.analyze_pull_request']['rate_limit'] == '5/m'
        assert annotations['app.tasks.llm_analysis.*']['rate_limit'] == '10/m'
        assert annotations['app.tasks.architectural_drift.*']['rate_limit'] == '2/m'
    
    def test_monitoring_configuration(self):
        """Test monitoring and event settings."""
        assert celery_app.conf.task_send_sent_event is True
        assert celery_app.conf.worker_send_task_events is True
        assert celery_app.conf.task_track_started is True
    
    def test_beat_schedule_configuration(self):
        """Test periodic task scheduling."""
        schedule = celery_app.conf.beat_schedule
        
        # Weekly drift detection
        assert 'detect-drift-weekly' in schedule
        drift_task = schedule['detect-drift-weekly']
        assert drift_task['task'] == 'app.tasks.architectural_drift.detect_architectural_drift'
        assert drift_task['options']['queue'] == 'low_priority'
        
        # Daily cycle detection
        assert 'detect-cycles-daily' in schedule
        cycle_task = schedule['detect-cycles-daily']
        assert cycle_task['task'] == 'app.tasks.architectural_drift.detect_cyclic_dependencies'
        assert cycle_task['options']['queue'] == 'low_priority'
        
        # Health check
        assert 'celery-health-check' in schedule
        health_task = schedule['celery-health-check']
        assert health_task['task'] == 'app.tasks.debug_task'
        assert health_task['options']['queue'] == 'default'
    
    def test_default_queue_configuration(self):
        """Test default queue settings."""
        assert celery_app.conf.task_default_queue == 'default'
        assert celery_app.conf.task_default_exchange == 'default'
        assert celery_app.conf.task_default_routing_key == 'default'


class TestDebugTask:
    """Test debug task for health monitoring."""
    
    def test_debug_task_execution(self):
        """Test debug task returns health status."""
        # Execute task directly (not through Celery)
        # In a real scenario, this would be called by Celery workers
        result = debug_task()
        
        # Verify result structure
        assert 'status' in result
        assert result['status'] == 'ok'
        assert 'worker_pid' in result
    
    def test_debug_task_is_registered(self):
        """Test debug task is registered with Celery."""
        # Task should be registered
        assert 'app.celery_config.debug_task' in celery_app.tasks or 'debug_task' in celery_app.tasks


class TestTaskRouting:
    """Test task routing to correct queues."""
    
    def test_high_priority_task_routing(self):
        """Test high priority tasks route to high_priority queue."""
        routes = celery_app.conf.task_routes
        
        # PR analysis tasks
        pr_analysis = routes.get('app.tasks.pull_request_analysis.analyze_pull_request')
        assert pr_analysis['queue'] == 'high_priority'
        assert pr_analysis['routing_key'] == 'high_priority'
        assert pr_analysis['priority'] == 10
        
        # Parse PR files
        parse_files = routes.get('app.tasks.pull_request_analysis.parse_pull_request_files')
        assert parse_files['queue'] == 'high_priority'
        assert parse_files['priority'] == 9
        
        # Post review comments
        post_comments = routes.get('app.tasks.pull_request_analysis.post_review_comments')
        assert post_comments['queue'] == 'high_priority'
        assert post_comments['priority'] == 8
    
    def test_default_priority_task_routing(self):
        """Test default priority tasks route to default queue."""
        routes = celery_app.conf.task_routes
        
        # AST parsing tasks
        ast_parsing = routes.get('app.tasks.ast_parsing.*')
        assert ast_parsing['queue'] == 'default'
        assert ast_parsing['routing_key'] == 'default'
        assert ast_parsing['priority'] == 5
        
        # Graph building tasks
        graph_building = routes.get('app.tasks.graph_building.*')
        assert graph_building['queue'] == 'default'
        assert graph_building['priority'] == 5
        
        # LLM analysis tasks
        llm_analysis = routes.get('app.tasks.llm_analysis.*')
        assert llm_analysis['queue'] == 'default'
        assert llm_analysis['priority'] == 5
    
    def test_low_priority_task_routing(self):
        """Test low priority tasks route to low_priority queue."""
        routes = celery_app.conf.task_routes
        
        # Architectural drift
        drift = routes.get('app.tasks.architectural_drift.detect_architectural_drift')
        assert drift['queue'] == 'low_priority'
        assert drift['routing_key'] == 'low_priority'
        assert drift['priority'] == 2
        
        # Circular dependencies
        cycles = routes.get('app.tasks.architectural_drift.detect_cyclic_dependencies')
        assert cycles['queue'] == 'low_priority'
        assert cycles['priority'] == 2
        
        # Cleanup tasks
        cleanup = routes.get('app.tasks.cleanup.*')
        assert cleanup['queue'] == 'low_priority'
        assert cleanup['priority'] == 1


class TestResultBackendSettings:
    """Test result backend configuration details."""
    
    def test_result_backend_transport_options(self):
        """Test result backend transport options for reliability."""
        transport_options = celery_app.conf.result_backend_transport_options
        
        assert transport_options['retry_on_timeout'] is True
        assert transport_options['socket_keepalive'] is True
        assert 'socket_keepalive_options' in transport_options
        
        # Socket keepalive options
        keepalive = transport_options['socket_keepalive_options']
        assert keepalive[1] == 1  # TCP_KEEPIDLE
        assert keepalive[2] == 1  # TCP_KEEPINTVL
        assert keepalive[3] == 5  # TCP_KEEPCNT
    
    def test_result_expiration(self):
        """Test results expire after configured time."""
        assert celery_app.conf.result_expires == 3600  # 1 hour
    
    def test_result_compression(self):
        """Test results are compressed to save memory."""
        assert celery_app.conf.result_compression == 'gzip'
    
    def test_result_persistence(self):
        """Test results are persisted to disk."""
        assert celery_app.conf.result_persistent is True
    
    def test_result_extended_metadata(self):
        """Test extended metadata is stored with results."""
        assert celery_app.conf.result_extended is True


class TestPeriodicTasks:
    """Test periodic task scheduling configuration."""
    
    def test_drift_detection_schedule(self):
        """Test weekly drift detection is scheduled correctly."""
        schedule = celery_app.conf.beat_schedule
        drift_task = schedule['detect-drift-weekly']
        
        assert drift_task['task'] == 'app.tasks.architectural_drift.detect_architectural_drift'
        assert drift_task['args'] == ('*',)
        assert drift_task['kwargs'] == {'baseline_version': 'latest'}
        assert drift_task['options']['queue'] == 'low_priority'
        assert drift_task['options']['expires'] == 86400  # 24 hours
    
    def test_cycle_detection_schedule(self):
        """Test daily cycle detection is scheduled correctly."""
        schedule = celery_app.conf.beat_schedule
        cycle_task = schedule['detect-cycles-daily']
        
        assert cycle_task['task'] == 'app.tasks.architectural_drift.detect_cyclic_dependencies'
        assert cycle_task['args'] == ('*',)
        assert cycle_task['options']['queue'] == 'low_priority'
        assert cycle_task['options']['expires'] == 86400
    
    def test_layer_violation_schedule(self):
        """Test twice-weekly layer violation check is scheduled correctly."""
        schedule = celery_app.conf.beat_schedule
        violation_task = schedule['detect-violations-twice-weekly']
        
        assert violation_task['task'] == 'app.tasks.architectural_drift.detect_layer_violations'
        assert violation_task['args'] == ('*',)
        assert violation_task['options']['queue'] == 'low_priority'
        assert violation_task['options']['expires'] == 86400
    
    def test_cleanup_schedule(self):
        """Test daily cleanup is scheduled correctly."""
        schedule = celery_app.conf.beat_schedule
        cleanup_task = schedule['cleanup-old-data']
        
        assert cleanup_task['task'] == 'app.tasks.cleanup.cleanup_old_analysis_results'
        assert cleanup_task['options']['queue'] == 'low_priority'
        assert cleanup_task['options']['expires'] == 86400
    
    def test_health_check_schedule(self):
        """Test health check runs every 5 minutes."""
        schedule = celery_app.conf.beat_schedule
        health_task = schedule['celery-health-check']
        
        assert health_task['task'] == 'app.tasks.debug_task'
        assert health_task['options']['queue'] == 'default'
        assert health_task['options']['expires'] == 300  # 5 minutes


class TestRetryBehavior:
    """Test retry configuration and behavior."""
    
    def test_retry_delay(self):
        """Test initial retry delay is 1 minute."""
        assert celery_app.conf.task_default_retry_delay == 60
    
    def test_max_retries(self):
        """Test maximum 3 retry attempts."""
        assert celery_app.conf.task_max_retries == 3
    
    def test_autoretry_exceptions(self):
        """Test tasks auto-retry on any exception."""
        assert celery_app.conf.task_autoretry_for == (Exception,)
    
    def test_exponential_backoff(self):
        """Test exponential backoff is enabled."""
        assert celery_app.conf.task_retry_backoff is True
        assert celery_app.conf.task_retry_backoff_max == 600  # 10 minutes
    
    def test_retry_jitter(self):
        """Test jitter is added to prevent thundering herd."""
        assert celery_app.conf.task_retry_jitter is True


class TestRateLimiting:
    """Test rate limiting configuration."""
    
    def test_default_rate_limit(self):
        """Test default rate limit is 10 tasks per minute."""
        assert celery_app.conf.task_default_rate_limit == '10/m'
    
    def test_pr_analysis_rate_limit(self):
        """Test PR analysis is limited to 5 per minute."""
        annotations = celery_app.conf.task_annotations
        assert annotations['app.tasks.pull_request_analysis.analyze_pull_request']['rate_limit'] == '5/m'
    
    def test_llm_analysis_rate_limit(self):
        """Test LLM analysis is limited to 10 per minute."""
        annotations = celery_app.conf.task_annotations
        assert annotations['app.tasks.llm_analysis.*']['rate_limit'] == '10/m'
    
    def test_drift_detection_rate_limit(self):
        """Test drift detection is limited to 2 per minute."""
        annotations = celery_app.conf.task_annotations
        assert annotations['app.tasks.architectural_drift.*']['rate_limit'] == '2/m'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

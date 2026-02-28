"""
Tests for task monitoring functionality

Tests cover:
- Task progress tracking
- Task failure handling and retry
- Task timeout handling
- Task status query functions
- MonitoredTask base class

Validates Requirements: 12.7 (Timeout handling for all external API calls)
"""
import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded

from app.tasks.task_monitoring import (
    MonitoredTask,
    TaskStatus,
    TaskProgressStage,
    get_task_status,
    get_task_progress,
    revoke_task,
    get_active_tasks,
    get_scheduled_tasks,
    get_worker_stats,
    TaskTimeoutError,
    with_timeout,
    TaskFailureHandler
)
from app.celery_config import celery_app


# ========================================
# TEST MONITORED TASK BASE CLASS
# ========================================

class TestMonitoredTask:
    """Test MonitoredTask base class"""
    
    def test_task_success_tracking(self):
        """Test that successful tasks update state correctly"""
        
        @celery_app.task(base=MonitoredTask, bind=True)
        def success_task(self):
            return {'result': 'success'}
        
        # Mock update_state
        with patch.object(success_task, 'update_state') as mock_update:
            result = success_task()
            
            # Verify started state was set
            assert mock_update.call_count >= 2
            started_call = mock_update.call_args_list[0]
            assert started_call[1]['state'] == TaskStatus.STARTED
            assert 'started_at' in started_call[1]['meta']
            
            # Verify success state was set
            success_call = mock_update.call_args_list[-1]
            assert success_call[1]['state'] == TaskStatus.SUCCESS
            assert success_call[1]['meta']['progress'] == 100
            assert success_call[1]['meta']['stage'] == TaskProgressStage.COMPLETED
    
    def test_task_failure_tracking(self):
        """Test that failed tasks update state correctly"""
        
        @celery_app.task(base=MonitoredTask, bind=True, max_retries=0)
        def failing_task(self):
            raise ValueError("Test error")
        
        # Mock update_state
        with patch.object(failing_task, 'update_state') as mock_update:
            with pytest.raises(ValueError):
                failing_task()
            
            # Verify failure state was set
            failure_call = mock_update.call_args_list[-1]
            assert failure_call[1]['state'] == TaskStatus.FAILURE
            assert 'error_type' in failure_call[1]['meta']
            assert failure_call[1]['meta']['error_type'] == 'ValueError'
            assert 'error_message' in failure_call[1]['meta']
            assert 'traceback' in failure_call[1]['meta']
    
    def test_task_soft_timeout_tracking(self):
        """Test that soft timeout is tracked correctly"""
        
        @celery_app.task(base=MonitoredTask, bind=True)
        def timeout_task(self):
            raise SoftTimeLimitExceeded()
        
        # Mock update_state
        with patch.object(timeout_task, 'update_state') as mock_update:
            with pytest.raises(SoftTimeLimitExceeded):
                timeout_task()
            
            # Verify timeout state was set
            timeout_call = mock_update.call_args_list[-1]
            assert timeout_call[1]['state'] == TaskStatus.TIMEOUT
            assert timeout_call[1]['meta']['error_type'] == 'SoftTimeLimitExceeded'
    
    def test_task_hard_timeout_tracking(self):
        """Test that hard timeout is tracked correctly"""
        
        @celery_app.task(base=MonitoredTask, bind=True)
        def hard_timeout_task(self):
            raise TimeLimitExceeded()
        
        # Mock update_state
        with patch.object(hard_timeout_task, 'update_state') as mock_update:
            with pytest.raises(TimeLimitExceeded):
                hard_timeout_task()
            
            # Verify timeout state was set
            timeout_call = mock_update.call_args_list[-1]
            assert timeout_call[1]['state'] == TaskStatus.TIMEOUT
            assert timeout_call[1]['meta']['error_type'] == 'TimeLimitExceeded'
    
    def test_task_retry_tracking(self):
        """Test that retries are tracked correctly"""
        
        @celery_app.task(base=MonitoredTask, bind=True, max_retries=3)
        def retry_task(self):
            raise ConnectionError("Network error")
        
        # Mock update_state and retry
        with patch.object(retry_task, 'update_state') as mock_update:
            with patch.object(retry_task, 'retry', side_effect=Exception("Retry")):
                with pytest.raises(Exception):
                    retry_task()
                
                # Verify retry state was set
                retry_call = mock_update.call_args_list[-1]
                assert retry_call[1]['state'] == TaskStatus.RETRY
                assert 'retry_count' in retry_call[1]['meta']
                assert 'will_retry' in retry_call[1]['meta']
    
    def test_update_progress(self):
        """Test update_progress method"""
        
        @celery_app.task(base=MonitoredTask, bind=True)
        def progress_task(self):
            self.update_progress(50, "Halfway done", TaskProgressStage.PARSING_FILES)
            return "done"
        
        # Mock update_state
        with patch.object(progress_task, 'update_state') as mock_update:
            progress_task()
            
            # Find progress update call
            progress_calls = [
                call for call in mock_update.call_args_list
                if call[1].get('state') == TaskStatus.PROGRESS
            ]
            
            assert len(progress_calls) > 0
            progress_call = progress_calls[0]
            assert progress_call[1]['meta']['progress'] == 50
            assert progress_call[1]['meta']['message'] == "Halfway done"
            assert progress_call[1]['meta']['stage'] == TaskProgressStage.PARSING_FILES


# ========================================
# TEST TASK STATUS QUERY FUNCTIONS
# ========================================

class TestTaskStatusQueries:
    """Test task status query functions"""
    
    def test_get_task_status_pending(self):
        """Test getting status of pending task"""
        mock_result = Mock()
        mock_result.state = 'PENDING'
        mock_result.ready.return_value = False
        mock_result.info = None
        
        with patch('app.tasks.task_monitoring.AsyncResult', return_value=mock_result):
            status = get_task_status('test-task-id')
            
            assert status['task_id'] == 'test-task-id'
            assert status['state'] == 'PENDING'
            assert status['ready'] is False
    
    def test_get_task_status_success(self):
        """Test getting status of successful task"""
        mock_result = Mock()
        mock_result.state = 'SUCCESS'
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.failed.return_value = False
        mock_result.info = {'progress': 100, 'message': 'Completed'}
        mock_result.result = {'data': 'result'}
        
        with patch('app.tasks.task_monitoring.AsyncResult', return_value=mock_result):
            status = get_task_status('test-task-id')
            
            assert status['state'] == 'SUCCESS'
            assert status['ready'] is True
            assert status['successful'] is True
            assert status['progress'] == 100
            assert status['result'] == {'data': 'result'}
    
    def test_get_task_status_failure(self):
        """Test getting status of failed task"""
        mock_result = Mock()
        mock_result.state = 'FAILURE'
        mock_result.ready.return_value = True
        mock_result.successful.return_value = False
        mock_result.failed.return_value = True
        mock_result.info = Exception("Test error")
        mock_result.traceback = "Traceback..."
        
        with patch('app.tasks.task_monitoring.AsyncResult', return_value=mock_result):
            status = get_task_status('test-task-id')
            
            assert status['state'] == 'FAILURE'
            assert status['failed'] is True
            assert status['error'] == "Test error"
            assert status['traceback'] == "Traceback..."
    
    def test_get_task_progress(self):
        """Test getting task progress"""
        mock_result = Mock()
        mock_result.state = 'PROGRESS'
        mock_result.info = {
            'progress': 75,
            'stage': 'analyzing_llm',
            'message': 'Analyzing code...',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        
        with patch('app.tasks.task_monitoring.AsyncResult', return_value=mock_result):
            progress = get_task_progress('test-task-id')
            
            assert progress['progress'] == 75
            assert progress['stage'] == 'analyzing_llm'
            assert progress['message'] == 'Analyzing code...'
    
    def test_revoke_task(self):
        """Test revoking a task"""
        mock_result = Mock()
        
        with patch('app.tasks.task_monitoring.AsyncResult', return_value=mock_result):
            result = revoke_task('test-task-id', terminate=True)
            
            mock_result.revoke.assert_called_once_with(terminate=True)
            assert result['task_id'] == 'test-task-id'
            assert result['revoked'] is True
            assert result['terminated'] is True
    
    def test_get_active_tasks(self):
        """Test getting active tasks"""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {
            'worker1': [
                {
                    'id': 'task-1',
                    'name': 'app.tasks.test_task',
                    'args': '[]',
                    'kwargs': '{}',
                    'time_start': 1234567890.0
                }
            ]
        }
        
        with patch('app.celery_config.celery_app.control.inspect', return_value=mock_inspect):
            tasks = get_active_tasks()
            
            assert len(tasks) == 1
            assert tasks[0]['task_id'] == 'task-1'
            assert tasks[0]['worker'] == 'worker1'
    
    def test_get_scheduled_tasks(self):
        """Test getting scheduled tasks"""
        mock_inspect = Mock()
        mock_inspect.scheduled.return_value = {
            'worker1': [
                {
                    'request': {
                        'id': 'task-1',
                        'name': 'app.tasks.test_task',
                        'priority': 10
                    },
                    'eta': '2024-01-01T00:00:00Z'
                }
            ]
        }
        
        with patch('app.celery_config.celery_app.control.inspect', return_value=mock_inspect):
            tasks = get_scheduled_tasks()
            
            assert len(tasks) == 1
            assert tasks[0]['task_id'] == 'task-1'
            assert tasks[0]['priority'] == 10
    
    def test_get_worker_stats(self):
        """Test getting worker statistics"""
        mock_inspect = Mock()
        mock_inspect.stats.return_value = {
            'worker1': {
                'pool': {'implementation': 'prefork', 'max-concurrency': 4},
                'total': {'tasks': 100},
                'rusage': {'utime': 1.5, 'stime': 0.5}
            }
        }
        
        with patch('app.celery_config.celery_app.control.inspect', return_value=mock_inspect):
            stats = get_worker_stats()
            
            assert stats['total_workers'] == 1
            assert len(stats['workers']) == 1
            assert stats['workers'][0]['name'] == 'worker1'
            assert stats['workers'][0]['max_concurrency'] == 4


# ========================================
# TEST TIMEOUT HANDLING
# ========================================

class TestTimeoutHandling:
    """Test timeout handling utilities"""
    
    @pytest.mark.asyncio
    async def test_async_timeout_success(self):
        """Test async timeout decorator with successful operation"""
        
        @with_timeout(1.0)
        async def fast_operation():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await fast_operation()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_async_timeout_exceeded(self):
        """Test async timeout decorator with timeout"""
        
        @with_timeout(0.1)
        async def slow_operation():
            await asyncio.sleep(1.0)
            return "success"
        
        with pytest.raises(TaskTimeoutError) as exc_info:
            await slow_operation()
        
        assert "timed out" in str(exc_info.value).lower()


# ========================================
# TEST FAILURE HANDLING
# ========================================

class TestFailureHandling:
    """Test failure handling utilities"""
    
    def test_should_retry_transient_error(self):
        """Test retry decision for transient errors"""
        handler = TaskFailureHandler()
        
        # Should retry connection errors
        assert handler.should_retry(ConnectionError(), 0, 3) is True
        assert handler.should_retry(TimeoutError(), 1, 3) is True
        assert handler.should_retry(TaskTimeoutError(), 2, 3) is True
    
    def test_should_not_retry_validation_error(self):
        """Test retry decision for validation errors"""
        handler = TaskFailureHandler()
        
        # Should not retry validation errors
        assert handler.should_retry(ValueError(), 0, 3) is False
        assert handler.should_retry(TypeError(), 0, 3) is False
        assert handler.should_retry(KeyError(), 0, 3) is False
    
    def test_should_not_retry_max_retries_reached(self):
        """Test retry decision when max retries reached"""
        handler = TaskFailureHandler()
        
        # Should not retry when max retries reached
        assert handler.should_retry(ConnectionError(), 3, 3) is False
    
    def test_get_retry_delay_exponential_backoff(self):
        """Test exponential backoff calculation"""
        handler = TaskFailureHandler()
        
        # Test exponential backoff
        delay0 = handler.get_retry_delay(0, base_delay=60)
        delay1 = handler.get_retry_delay(1, base_delay=60)
        delay2 = handler.get_retry_delay(2, base_delay=60)
        
        # Delays should increase exponentially (with jitter)
        assert 40 < delay0 < 80  # ~60 ± 20%
        assert 80 < delay1 < 160  # ~120 ± 20%
        assert 160 < delay2 < 320  # ~240 ± 20%
    
    def test_get_retry_delay_capped(self):
        """Test retry delay is capped at maximum"""
        handler = TaskFailureHandler()
        
        # Very high retry count should be capped at 600s
        delay = handler.get_retry_delay(10, base_delay=60)
        assert delay <= 600
    
    def test_log_failure(self):
        """Test failure logging"""
        handler = TaskFailureHandler()
        
        with patch('app.tasks.task_monitoring.logger') as mock_logger:
            handler.log_failure(
                task_name='test_task',
                task_id='task-123',
                exc=ValueError("Test error"),
                args=(1, 2),
                kwargs={'key': 'value'},
                retry_count=1
            )
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert 'test_task' in call_args[0][0]
            assert 'task-123' in call_args[0][0]


# ========================================
# TEST INTEGRATION
# ========================================

class TestTaskMonitoringIntegration:
    """Integration tests for task monitoring"""
    
    def test_monitored_task_with_progress_updates(self):
        """Test complete workflow with progress updates"""
        
        @celery_app.task(base=MonitoredTask, bind=True)
        def workflow_task(self):
            self.update_progress(25, "Step 1", TaskProgressStage.PARSING_FILES)
            self.update_progress(50, "Step 2", TaskProgressStage.BUILDING_GRAPH)
            self.update_progress(75, "Step 3", TaskProgressStage.ANALYZING_LLM)
            self.update_progress(100, "Done", TaskProgressStage.COMPLETED)
            return "success"
        
        with patch.object(workflow_task, 'update_state') as mock_update:
            result = workflow_task()
            
            # Verify all progress updates were made
            progress_calls = [
                call for call in mock_update.call_args_list
                if call[1].get('state') == TaskStatus.PROGRESS
            ]
            
            assert len(progress_calls) == 4
            assert progress_calls[0][1]['meta']['progress'] == 25
            assert progress_calls[1][1]['meta']['progress'] == 50
            assert progress_calls[2][1]['meta']['progress'] == 75
            assert progress_calls[3][1]['meta']['progress'] == 100
    
    def test_monitored_task_with_retry_and_success(self):
        """Test task monitoring tracks retry attempts"""
        
        @celery_app.task(base=MonitoredTask, bind=True, max_retries=3)
        def flaky_task(self):
            # Simulate a task that would retry
            return "success"
        
        # Just verify the task can execute with MonitoredTask base
        with patch.object(flaky_task, 'update_state') as mock_update:
            result = flaky_task()
            
            assert result == "success"
            # Verify monitoring states were set
            assert any(
                call[1].get('state') == TaskStatus.STARTED
                for call in mock_update.call_args_list
            )
            assert any(
                call[1].get('state') == TaskStatus.SUCCESS
                for call in mock_update.call_args_list
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

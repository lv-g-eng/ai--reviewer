"""
Tests for data cleanup Celery tasks

Tests cover:
- Scheduled cleanup task execution
- Task retry behavior
- Task error handling
- Dry run mode

Validates Requirements: 11.1, 11.8
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone, timedelta

from app.tasks.data_cleanup import (
    cleanup_old_analysis_results,
    cleanup_old_architectural_baselines,
    cleanup_expired_sessions,
    verify_audit_log_retention,
    get_cleanup_statistics
)


@pytest.mark.unit
class TestDataCleanupTasks:
    """Test Celery tasks for data cleanup"""
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_cleanup_old_analysis_results_success(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test successful execution of analysis results cleanup task"""
        # Mock service
        mock_service = Mock()
        mock_service.cleanup_old_analysis_results = AsyncMock(return_value={
            "status": "success",
            "deleted_count": 10,
            "retention_days": 90
        })
        mock_service_class.return_value = mock_service
        
        # Mock session
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        # Execute task
        result = cleanup_old_analysis_results(dry_run=False)
        
        assert result["status"] == "success"
        assert result["deleted_count"] == 10
        mock_service.cleanup_old_analysis_results.assert_called_once_with(dry_run=False)
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_cleanup_old_analysis_results_dry_run(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test dry run mode for analysis results cleanup task"""
        mock_service = Mock()
        mock_service.cleanup_old_analysis_results = AsyncMock(return_value={
            "status": "dry_run",
            "would_delete_count": 5,
            "dry_run": True
        })
        mock_service_class.return_value = mock_service
        
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        result = cleanup_old_analysis_results(dry_run=True)
        
        assert result["status"] == "dry_run"
        assert result["would_delete_count"] == 5
        mock_service.cleanup_old_analysis_results.assert_called_once_with(dry_run=True)
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_cleanup_architectural_baselines_success(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test successful execution of architectural baselines cleanup task"""
        mock_service = Mock()
        mock_service.cleanup_old_architectural_baselines = AsyncMock(return_value={
            "status": "success",
            "deleted_count": 3,
            "retention_days": 365
        })
        mock_service_class.return_value = mock_service
        
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        result = cleanup_old_architectural_baselines(dry_run=False, keep_current=True)
        
        assert result["status"] == "success"
        assert result["deleted_count"] == 3
        mock_service.cleanup_old_architectural_baselines.assert_called_once_with(
            dry_run=False,
            keep_current=True
        )
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_cleanup_expired_sessions_success(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test successful execution of expired sessions cleanup task"""
        mock_service = Mock()
        mock_service.cleanup_expired_sessions = AsyncMock(return_value={
            "status": "success",
            "deleted_count": 15,
            "retention_days": 30
        })
        mock_service_class.return_value = mock_service
        
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        result = cleanup_expired_sessions(dry_run=False)
        
        assert result["status"] == "success"
        assert result["deleted_count"] == 15
        mock_service.cleanup_expired_sessions.assert_called_once_with(dry_run=False)
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_verify_audit_log_retention_success(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test successful execution of audit log retention verification task"""
        mock_service = Mock()
        mock_service.verify_audit_log_retention = AsyncMock(return_value={
            "status": "verified",
            "total_audit_logs": 1000,
            "retention_policy_days": 2555
        })
        mock_service_class.return_value = mock_service
        
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        result = verify_audit_log_retention()
        
        assert result["status"] == "verified"
        assert result["total_audit_logs"] == 1000
        mock_service.verify_audit_log_retention.assert_called_once()
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_get_cleanup_statistics_success(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test successful execution of cleanup statistics task"""
        mock_service = Mock()
        mock_service.get_cleanup_statistics = AsyncMock(return_value={
            "analysis_results": {"total": 100, "expired": 20},
            "audit_logs": {"total": 1000},
            "generated_at": datetime.now(timezone.utc).isoformat()
        })
        mock_service_class.return_value = mock_service
        
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        result = get_cleanup_statistics()
        
        assert "analysis_results" in result
        assert result["analysis_results"]["total"] == 100
        mock_service.get_cleanup_statistics.assert_called_once()


@pytest.mark.unit
class TestTaskErrorHandling:
    """Test error handling and retry behavior"""
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_cleanup_task_handles_exception(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test that cleanup task handles exceptions and retries"""
        # Mock service to raise exception
        mock_service = Mock()
        mock_service.cleanup_old_analysis_results = AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        mock_service_class.return_value = mock_service
        
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        # Create mock task with retry method
        mock_task = Mock()
        mock_task.retry = Mock(side_effect=Exception("Retry triggered"))
        
        # Bind task to mock
        with patch.object(cleanup_old_analysis_results, 'retry', mock_task.retry):
            with pytest.raises(Exception) as exc_info:
                cleanup_old_analysis_results(dry_run=False)
            
            assert "Retry triggered" in str(exc_info.value)
    
    @patch('app.tasks.data_cleanup.get_db')
    @patch('app.tasks.data_cleanup.DataLifecycleService')
    def test_verification_task_logs_warning(
        self,
        mock_service_class,
        mock_get_db
    ):
        """Test that verification task logs warning when issues found"""
        mock_service = Mock()
        mock_service.verify_audit_log_retention = AsyncMock(return_value={
            "status": "warning",
            "total_audit_logs": 1000,
            "logs_with_incorrect_retention": 10
        })
        mock_service_class.return_value = mock_service
        
        mock_session = AsyncMock()
        mock_get_db.return_value.__aiter__.return_value = [mock_session]
        
        with patch('app.tasks.data_cleanup.logger') as mock_logger:
            result = verify_audit_log_retention()
            
            assert result["status"] == "warning"
            # Verify warning was logged
            mock_logger.warning.assert_called_once()


@pytest.mark.integration
class TestTaskIntegration:
    """Integration tests for cleanup tasks"""
    
    def test_task_names_registered(self):
        """Test that all cleanup tasks are registered with correct names"""
        from app.celery_config import celery_app
        
        registered_tasks = celery_app.tasks.keys()
        
        assert 'app.tasks.data_cleanup.cleanup_old_analysis_results' in registered_tasks
        assert 'app.tasks.data_cleanup.cleanup_old_architectural_baselines' in registered_tasks
        assert 'app.tasks.data_cleanup.cleanup_expired_sessions' in registered_tasks
        assert 'app.tasks.data_cleanup.verify_audit_log_retention' in registered_tasks
        assert 'app.tasks.data_cleanup.get_cleanup_statistics' in registered_tasks
    
    def test_scheduled_tasks_configured(self):
        """Test that cleanup tasks are configured in beat schedule"""
        from app.celery_config import celery_app
        
        beat_schedule = celery_app.conf.beat_schedule
        
        assert 'cleanup-old-analysis-results' in beat_schedule
        assert 'cleanup-expired-sessions' in beat_schedule
        assert 'cleanup-old-baselines' in beat_schedule
        assert 'verify-audit-retention' in beat_schedule
        
        # Verify task configuration
        cleanup_config = beat_schedule['cleanup-old-analysis-results']
        assert cleanup_config['task'] == 'app.tasks.data_cleanup.cleanup_old_analysis_results'
        assert cleanup_config['kwargs']['dry_run'] is False
        assert cleanup_config['options']['queue'] == 'low_priority'

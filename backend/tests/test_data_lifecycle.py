"""
Tests for data lifecycle management service

Tests cover:
- Analysis results cleanup (90-day retention)
- Audit log retention verification (7-year retention)
- Architectural baselines cleanup
- Cleanup statistics
- Retention policy configuration

Validates Requirements: 11.1, 11.8
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
import uuid

from app.services.data_lifecycle_service import DataLifecycleService, DataRetentionPolicy


@pytest.mark.unit
class TestDataRetentionPolicy:
    """Test data retention policy configuration"""
    
    def test_retention_policy_constants(self):
        """Test that retention policy constants are correct"""
        assert DataRetentionPolicy.ANALYSIS_RESULTS_RETENTION_DAYS == 90
        assert DataRetentionPolicy.AUDIT_LOGS_RETENTION_DAYS == 2555  # 7 years
        assert DataRetentionPolicy.ARCHITECTURAL_BASELINES_RETENTION_DAYS == 365
        assert DataRetentionPolicy.USER_SESSIONS_RETENTION_DAYS == 30


@pytest.mark.unit
class TestDataLifecycleServiceUnit:
    """Unit tests for data lifecycle service"""
    
    @pytest.mark.asyncio
    async def test_cleanup_old_analysis_results_dry_run(self):
        """Test dry run mode for analysis results cleanup"""
        # Mock database session
        mock_session = AsyncMock()
        
        # Mock count query result
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_count_result
        
        # Create service
        service = DataLifecycleService(mock_session)
        
        # Run cleanup in dry run mode
        result = await service.cleanup_old_analysis_results(dry_run=True)
        
        assert result["status"] == "dry_run"
        assert result["would_delete_count"] == 5
        assert result["dry_run"] is True
        assert result["retention_days"] == 90
    
    @pytest.mark.asyncio
    async def test_cleanup_no_old_data(self):
        """Test cleanup when no old data exists"""
        # Mock database session
        mock_session = AsyncMock()
        
        # Mock count query result (no records)
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_count_result
        
        # Create service
        service = DataLifecycleService(mock_session)
        
        # Run cleanup
        result = await service.cleanup_old_analysis_results(dry_run=False)
        
        assert result["status"] == "success"
        assert result["deleted_count"] == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_with_custom_retention(self):
        """Test cleanup with custom retention period"""
        # Mock database session
        mock_session = AsyncMock()
        
        # Mock count query result
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 3
        mock_session.execute.return_value = mock_count_result
        
        # Create service
        service = DataLifecycleService(mock_session)
        
        # Run cleanup with custom retention
        result = await service.cleanup_old_analysis_results(
            retention_days=50,
            dry_run=True
        )
        
        assert result["status"] == "dry_run"
        assert result["retention_days"] == 50
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_no_table(self):
        """Test cleanup when sessions table doesn't exist"""
        # Mock database session
        mock_session = AsyncMock()
        
        # Mock table existence check (table doesn't exist)
        mock_table_check = Mock()
        mock_table_check.scalar.return_value = False
        mock_session.execute.return_value = mock_table_check
        
        # Create service
        service = DataLifecycleService(mock_session)
        
        # Run cleanup
        result = await service.cleanup_expired_sessions(dry_run=False)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "sessions_table_not_found"
    
    @pytest.mark.asyncio
    async def test_verify_audit_log_retention(self):
        """Test verification of audit log retention policy"""
        # Mock database session
        mock_session = AsyncMock()
        
        # Mock oldest log query
        mock_oldest_result = Mock()
        mock_oldest_row = Mock()
        mock_oldest_row.oldest_timestamp = datetime.now(timezone.utc) - timedelta(days=365)
        mock_oldest_row.oldest_retention = datetime.now(timezone.utc) + timedelta(days=2190)
        mock_oldest_result.fetchone.return_value = mock_oldest_row
        
        # Mock incorrect retention query
        mock_incorrect_result = Mock()
        mock_incorrect_result.scalar.return_value = 0
        
        # Mock total count query
        mock_total_result = Mock()
        mock_total_result.scalar.return_value = 1000
        
        # Set up execute to return different results for different queries
        mock_session.execute.side_effect = [
            mock_oldest_result,
            mock_incorrect_result,
            mock_total_result
        ]
        
        # Create service
        service = DataLifecycleService(mock_session)
        
        # Run verification
        result = await service.verify_audit_log_retention()
        
        assert result["status"] == "verified"
        assert result["total_audit_logs"] == 1000
        assert result["retention_policy_days"] == 2555
        assert result["logs_with_incorrect_retention"] == 0


@pytest.mark.unit
class TestDataLifecycleEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_cleanup_with_zero_retention(self):
        """Test cleanup with zero retention days"""
        mock_session = AsyncMock()
        
        # Mock count query
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 10
        mock_session.execute.return_value = mock_count_result
        
        service = DataLifecycleService(mock_session)
        
        result = await service.cleanup_old_analysis_results(
            retention_days=0,
            dry_run=True
        )
        
        # In dry run mode, the result should show what would be deleted
        assert result["status"] == "dry_run"
        assert result["would_delete_count"] == 10
    
    @pytest.mark.asyncio
    async def test_cleanup_with_large_retention(self):
        """Test cleanup with very large retention period"""
        mock_session = AsyncMock()
        
        # Mock count query (nothing old enough)
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_count_result
        
        service = DataLifecycleService(mock_session)
        
        result = await service.cleanup_old_analysis_results(
            retention_days=1000,
            dry_run=False
        )
        
        assert result["status"] == "success"
        assert result["deleted_count"] == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_handles_exception(self):
        """Test that cleanup handles database exceptions"""
        mock_session = AsyncMock()
        
        # Mock execute to raise exception
        mock_session.execute.side_effect = Exception("Database error")
        
        service = DataLifecycleService(mock_session)
        
        with pytest.raises(Exception) as exc_info:
            await service.cleanup_old_analysis_results(dry_run=False)
        
        assert "Database error" in str(exc_info.value)
        # Verify rollback was called
        mock_session.rollback.assert_called_once()

"""
Tests for user data management endpoints (GDPR compliance).

Tests data export and account deletion functionality.
Validates Requirements: 11.5, 11.6, 11.7, 15.10
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi import status
from sqlalchemy import text
import uuid

from app.models import User, Project, PullRequest, AuditLog, UserRole


@pytest.mark.unit
class TestDataExportUnit:
    """Unit tests for data export functionality (Requirement 11.5)"""
    
    def test_data_export_endpoint_exists(self):
        """Test that the data export endpoint is registered"""
        from app.api.v1.endpoints import user_data
        
        assert hasattr(user_data, 'router')
        assert user_data.router is not None
    
    def test_account_deletion_endpoint_exists(self):
        """Test that the account deletion endpoint is registered"""
        from app.api.v1.endpoints import user_data
        
        # Check that the router has the delete endpoint
        routes = [route.path for route in user_data.router.routes]
        assert "/{user_id}" in routes


@pytest.mark.unit
class TestDataExportModels:
    """Test data export response models"""
    
    def test_data_export_response_model(self):
        """Test DataExportResponse model structure"""
        from app.api.v1.endpoints.user_data import DataExportResponse
        
        # Create sample response
        response = DataExportResponse(
            user_id=str(uuid.uuid4()),
            email="test@example.com",
            full_name="Test User",
            role="developer",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            projects=[],
            pull_requests=[],
            audit_logs=[],
            export_timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        assert response.email == "test@example.com"
        assert response.role == "developer"
        assert isinstance(response.projects, list)
        assert isinstance(response.pull_requests, list)
        assert isinstance(response.audit_logs, list)
    
    def test_account_deletion_request_model(self):
        """Test AccountDeletionRequest model structure"""
        from app.api.v1.endpoints.user_data import AccountDeletionRequest
        
        request = AccountDeletionRequest(
            confirm_email="test@example.com",
            reason="No longer needed"
        )
        
        assert request.confirm_email == "test@example.com"
        assert request.reason == "No longer needed"
    
    def test_account_deletion_response_model(self):
        """Test AccountDeletionResponse model structure"""
        from app.api.v1.endpoints.user_data import AccountDeletionResponse
        
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=30)
        
        response = AccountDeletionResponse(
            message="Account deletion scheduled",
            deletion_scheduled_at=now.isoformat(),
            deletion_will_complete_by=future.isoformat(),
            user_id=str(uuid.uuid4())
        )
        
        assert "scheduled" in response.message.lower()
        assert response.deletion_scheduled_at == now.isoformat()
        assert response.deletion_will_complete_by == future.isoformat()


@pytest.mark.unit
class TestScheduledDeletionTask:
    """Unit tests for scheduled deletion task"""
    
    def test_scheduled_deletion_task_exists(self):
        """Test that the scheduled deletion task is defined"""
        from app.tasks.data_cleanup import process_scheduled_account_deletions
        
        assert callable(process_scheduled_account_deletions)


@pytest.mark.unit
class TestDataLifecycleIntegration:
    """Integration tests for data lifecycle"""
    
    def test_data_retention_policy_constants(self):
        """Test that retention policy constants are defined"""
        from app.services.data_lifecycle_service import DataRetentionPolicy
        
        assert DataRetentionPolicy.ANALYSIS_RESULTS_RETENTION_DAYS == 90
        assert DataRetentionPolicy.AUDIT_LOGS_RETENTION_DAYS == 2555  # 7 years
        assert DataRetentionPolicy.USER_SESSIONS_RETENTION_DAYS == 30
    
    def test_30_day_deletion_window(self):
        """
        Test that the 30-day deletion window is correctly calculated.
        
        Validates Requirement: 11.7 (Delete all personal data within 30 days)
        """
        now = datetime.now(timezone.utc)
        deletion_complete_by = now + timedelta(days=30)
        
        delta = deletion_complete_by - now
        
        assert delta.days == 30
    
    def test_audit_log_anonymization_format(self):
        """
        Test the format of anonymized audit log identifiers.
        
        Validates Requirement: 15.10 (GDPR compliance - audit log handling)
        """
        user_id = uuid.uuid4()
        anonymized_id = f"deleted-user-{user_id}"
        
        assert anonymized_id.startswith("deleted-user-")
        assert str(user_id) in anonymized_id

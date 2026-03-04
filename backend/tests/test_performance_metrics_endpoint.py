"""
Performance Metrics Endpoint Integration Tests

Tests the performance metrics API endpoint.
Validates Requirements 2.4, 3.7

**Validates: Requirements 2.4, 3.7**
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models import User, Project, PullRequest, ReviewStatus
from app.utils.password import hash_password


class TestPerformanceMetricsEndpoint:
    """Integration tests for performance metrics endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_success(self, db_session):
        """
        Test successful retrieval of performance metrics
        
        **Validates: Requirements 2.4, 3.7**
        """
        from app.database.postgresql import get_db
        from app.auth import get_current_user
        from app.models.code_review import TokenPayload
        
        async def override_get_db():
            yield db_session
        
        # Create test user and project
        user = User(
            email="metrics@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Metrics Test User"
        )
        db_session.add(user)
        await db_session.flush()
        
        project = Project(
            name="Test Project",
            github_url="https://github.com/test/repo",
            owner_id=user.id
        )
        db_session.add(project)
        await db_session.flush()
        
        # Create test PRs
        now = datetime.utcnow()
        for i in range(5):
            pr = PullRequest(
                project_id=str(project.id),
                github_pr_number=i + 1,
                title=f"Test PR {i + 1}",
                status=ReviewStatus.COMPLETED if i < 4 else ReviewStatus.FAILED,
                files_changed=5 + i,
                lines_added=100 + (i * 10),
                lines_deleted=50 + (i * 5),
                risk_score=30.0 + (i * 5),
                created_at=now - timedelta(days=i),
                analyzed_at=now - timedelta(days=i) + timedelta(hours=1)
            )
            db_session.add(pr)
        
        await db_session.commit()
        
        # Mock authentication
        mock_user = TokenPayload(
            sub=str(user.id),
            email=user.email,
            exp=int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        )
        
        async def override_get_current_user():
            return mock_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Test endpoint with default time range
                response = await client.get(
                    f"/api/v1/project-analytics/{project.id}/metrics",
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify response structure
                assert "api_version" in data
                assert data["api_version"] == "1.0.0"
                assert "project_id" in data
                assert data["project_id"] == str(project.id)
                assert "time_range" in data
                assert "start" in data["time_range"]
                assert "end" in data["time_range"]
                assert "metrics" in data
                assert "aggregations" in data
                
                # Verify metrics structure
                metrics = data["metrics"]
                assert "response_time" in metrics
                assert "throughput" in metrics
                assert "error_rate" in metrics
                assert "cpu_usage" in metrics
                assert "memory_usage" in metrics
                
                # Verify aggregations structure
                agg = data["aggregations"]
                assert "avg_response_time" in agg
                assert "p95_response_time" in agg
                assert "p99_response_time" in agg
                assert "total_requests" in agg
                assert "total_errors" in agg
                
                # Verify numeric ranges
                assert 0 <= agg["avg_response_time"] <= 10000
                assert 0 <= agg["p95_response_time"] <= 10000
                assert 0 <= agg["p99_response_time"] <= 10000
                assert agg["total_requests"] >= 0
                assert agg["total_errors"] >= 0
                
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_with_time_range(self, db_session):
        """
        Test performance metrics with custom time range
        
        **Validates: Requirements 2.4, 3.7**
        """
        from app.database.postgresql import get_db
        from app.auth import get_current_user
        from app.models.code_review import TokenPayload
        
        async def override_get_db():
            yield db_session
        
        # Create test user and project
        user = User(
            email="metrics2@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Metrics Test User 2"
        )
        db_session.add(user)
        await db_session.flush()
        
        project = Project(
            name="Test Project 2",
            github_url="https://github.com/test/repo2",
            owner_id=user.id
        )
        db_session.add(project)
        await db_session.commit()
        
        # Mock authentication
        mock_user = TokenPayload(
            sub=str(user.id),
            email=user.email,
            exp=int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        )
        
        async def override_get_current_user():
            return mock_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Test with custom time range
                start_time = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
                end_time = datetime.utcnow().isoformat() + 'Z'
                
                response = await client.get(
                    f"/api/v1/project-analytics/{project.id}/metrics",
                    params={"start_time": start_time, "end_time": end_time},
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify time range matches request
                assert data["time_range"]["start"] == start_time
                assert data["time_range"]["end"] == end_time
                
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_invalid_time_range(self, db_session):
        """
        Test performance metrics with invalid time range
        
        **Validates: Requirements 3.7**
        """
        from app.database.postgresql import get_db
        from app.auth import get_current_user
        from app.models.code_review import TokenPayload
        
        async def override_get_db():
            yield db_session
        
        # Create test user and project
        user = User(
            email="metrics3@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Metrics Test User 3"
        )
        db_session.add(user)
        await db_session.flush()
        
        project = Project(
            name="Test Project 3",
            github_url="https://github.com/test/repo3",
            owner_id=user.id
        )
        db_session.add(project)
        await db_session.commit()
        
        # Mock authentication
        mock_user = TokenPayload(
            sub=str(user.id),
            email=user.email,
            exp=int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        )
        
        async def override_get_current_user():
            return mock_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Test with start_time after end_time
                start_time = datetime.utcnow().isoformat() + 'Z'
                end_time = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
                
                response = await client.get(
                    f"/api/v1/project-analytics/{project.id}/metrics",
                    params={"start_time": start_time, "end_time": end_time},
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 400
                assert "start_time must be before end_time" in response.json()["detail"]
                
                # Test with time range > 90 days
                start_time = (datetime.utcnow() - timedelta(days=100)).isoformat() + 'Z'
                end_time = datetime.utcnow().isoformat() + 'Z'
                
                response = await client.get(
                    f"/api/v1/project-analytics/{project.id}/metrics",
                    params={"start_time": start_time, "end_time": end_time},
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 400
                assert "Time range cannot exceed 90 days" in response.json()["detail"]
                
        finally:
            app.dependency_overrides.clear()

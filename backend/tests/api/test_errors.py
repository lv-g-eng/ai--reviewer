"""
Tests for Client Error Reporting Endpoint

Tests the /errors/client endpoint that receives error reports from frontend clients.
Requirement 7.4: Client-side error reporting
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


class TestClientErrorReporting:
    """Test client error reporting endpoint"""

    def test_report_client_error_success(self, client: TestClient):
        """Test successful error report submission"""
        error_report = {
            "type": "NETWORK_ERROR",
            "message": "Failed to fetch data",
            "statusCode": None,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "url": "/api/v1/architecture/123",
                "method": "GET"
            },
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "url": "https://example.com/dashboard"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Error report received"
        assert "error_id" in data
        assert data["error_id"].startswith("client-")

    def test_report_timeout_error(self, client: TestClient):
        """Test reporting timeout error"""
        error_report = {
            "type": "TIMEOUT_ERROR",
            "message": "Request timeout",
            "statusCode": None,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "timeout": 30000,
                "url": "/api/v1/projects"
            },
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com/projects"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_report_auth_error(self, client: TestClient):
        """Test reporting authentication error"""
        error_report = {
            "type": "AUTH_ERROR",
            "message": "Session expired",
            "statusCode": 401,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "response": {"detail": "Invalid token"}
            },
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com/dashboard"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_report_server_error(self, client: TestClient):
        """Test reporting server error"""
        error_report = {
            "type": "SERVER_ERROR",
            "message": "Internal server error",
            "statusCode": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "response": {"detail": "Database connection failed"}
            },
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com/api/data"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_report_validation_error(self, client: TestClient):
        """Test reporting validation error"""
        error_report = {
            "type": "VALIDATION_ERROR",
            "message": "Invalid data format",
            "statusCode": 422,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "field": "email",
                "error": "Invalid email format"
            },
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com/settings"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_report_error_missing_required_fields(self, client: TestClient):
        """Test error report with missing required fields"""
        error_report = {
            "type": "NETWORK_ERROR",
            # Missing required fields: message, timestamp, userAgent, url
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 422  # Validation error

    def test_report_error_invalid_timestamp(self, client: TestClient):
        """Test error report with invalid timestamp format"""
        error_report = {
            "type": "NETWORK_ERROR",
            "message": "Test error",
            "timestamp": "invalid-timestamp",
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        # Should still accept it as it's just a string field
        assert response.status_code == 201

    def test_report_error_with_complex_details(self, client: TestClient):
        """Test error report with complex nested details"""
        error_report = {
            "type": "NETWORK_ERROR",
            "message": "Complex error",
            "statusCode": None,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "nested": {
                    "level1": {
                        "level2": {
                            "data": "value"
                        }
                    }
                },
                "array": [1, 2, 3],
                "boolean": True
            },
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_report_error_with_null_details(self, client: TestClient):
        """Test error report with null details"""
        error_report = {
            "type": "NETWORK_ERROR",
            "message": "Error without details",
            "statusCode": None,
            "timestamp": datetime.utcnow().isoformat(),
            "details": None,
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_error_reporting_health_check(self, client: TestClient):
        """Test error reporting service health check"""
        response = client.get("/api/v1/errors/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "error-reporting"

    def test_multiple_error_reports(self, client: TestClient):
        """Test submitting multiple error reports"""
        error_reports = [
            {
                "type": "NETWORK_ERROR",
                "message": f"Error {i}",
                "timestamp": datetime.utcnow().isoformat(),
                "userAgent": "Mozilla/5.0",
                "url": f"https://example.com/page{i}"
            }
            for i in range(5)
        ]

        for error_report in error_reports:
            response = client.post("/api/v1/errors/client", json=error_report)
            assert response.status_code == 201
            assert response.json()["status"] == "success"

    def test_error_report_with_special_characters(self, client: TestClient):
        """Test error report with special characters in message"""
        error_report = {
            "type": "VALIDATION_ERROR",
            "message": "Error with special chars: <>&\"'",
            "timestamp": datetime.utcnow().isoformat(),
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_error_report_with_long_message(self, client: TestClient):
        """Test error report with very long message"""
        long_message = "A" * 10000  # 10KB message

        error_report = {
            "type": "SERVER_ERROR",
            "message": long_message,
            "timestamp": datetime.utcnow().isoformat(),
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_error_report_with_unicode(self, client: TestClient):
        """Test error report with unicode characters"""
        error_report = {
            "type": "VALIDATION_ERROR",
            "message": "错误信息 🚨 エラー",
            "timestamp": datetime.utcnow().isoformat(),
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com/页面"
        }

        response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        assert response.json()["status"] == "success"


class TestErrorReportingIntegration:
    """Integration tests for error reporting"""

    def test_error_report_logged_correctly(self, client: TestClient, caplog):
        """Test that error reports are logged with correct structure"""
        error_report = {
            "type": "NETWORK_ERROR",
            "message": "Test error for logging",
            "timestamp": datetime.utcnow().isoformat(),
            "userAgent": "Mozilla/5.0",
            "url": "https://example.com"
        }

        with caplog.at_level("ERROR"):
            response = client.post("/api/v1/errors/client", json=error_report)

        assert response.status_code == 201
        
        # Check that error was logged
        assert len(caplog.records) > 0
        log_record = caplog.records[0]
        assert "Client error reported" in log_record.message
        assert "NETWORK_ERROR" in log_record.message

    def test_concurrent_error_reports(self, client: TestClient):
        """Test handling concurrent error reports"""
        import concurrent.futures

        def submit_error_report(index: int):
            error_report = {
                "type": "NETWORK_ERROR",
                "message": f"Concurrent error {index}",
                "timestamp": datetime.utcnow().isoformat(),
                "userAgent": "Mozilla/5.0",
                "url": f"https://example.com/page{index}"
            }
            return client.post("/api/v1/errors/client", json=error_report)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(submit_error_report, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(r.status_code == 201 for r in results)
        assert all(r.json()["status"] == "success" for r in results)

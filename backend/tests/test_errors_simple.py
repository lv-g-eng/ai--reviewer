"""
Simple integration test for error reporting endpoint
Tests without complex fixtures
"""

from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

client = TestClient(app)


def test_error_reporting_endpoint_exists():
    """Test that the error reporting endpoint is accessible"""
    # Test health check first
    response = client.get("/api/v1/errors/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "error-reporting"


def test_submit_client_error():
    """Test submitting a client error report"""
    error_report = {
        "type": "NETWORK_ERROR",
        "message": "Test network error",
        "statusCode": None,
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"test": "data"},
        "userAgent": "Mozilla/5.0 Test",
        "url": "https://test.example.com"
    }
    
    response = client.post("/api/v1/errors/client", json=error_report)
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "error_id" in data


def test_submit_error_with_status_code():
    """Test submitting an error with HTTP status code"""
    error_report = {
        "type": "SERVER_ERROR",
        "message": "Internal server error",
        "statusCode": 500,
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"response": {"detail": "Database error"}},
        "userAgent": "Mozilla/5.0 Test",
        "url": "https://test.example.com/api"
    }
    
    response = client.post("/api/v1/errors/client", json=error_report)
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"


def test_missing_required_fields():
    """Test that missing required fields returns validation error"""
    error_report = {
        "type": "NETWORK_ERROR",
        # Missing required fields
    }
    
    response = client.post("/api/v1/errors/client", json=error_report)
    
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    print("Running simple error reporting tests...")
    test_error_reporting_endpoint_exists()
    print("✓ Health check test passed")
    
    test_submit_client_error()
    print("✓ Submit client error test passed")
    
    test_submit_error_with_status_code()
    print("✓ Submit error with status code test passed")
    
    test_missing_required_fields()
    print("✓ Missing required fields test passed")
    
    print("\nAll tests passed!")

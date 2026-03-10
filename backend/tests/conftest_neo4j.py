"""
Pytest configuration for Neo4j integration tests

This module provides fixtures and configuration for Neo4j integration tests.
It handles both testcontainer-based tests (when Docker is available) and
mock-based tests (when Docker is not available).
"""
import pytest
import subprocess


def is_docker_available() -> bool:
    """Check if Docker is available and running"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "requires_docker: mark test as requiring Docker to run"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests that require Docker if Docker is not available"""
    if not is_docker_available():
        skip_docker = pytest.mark.skip(reason="Docker is not available")
        for item in items:
            if "requires_docker" in item.keywords:
                item.add_marker(skip_docker)


@pytest.fixture(scope="session")
def docker_available():
    """Fixture that provides Docker availability status"""
    return is_docker_available()

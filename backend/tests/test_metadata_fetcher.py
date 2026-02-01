"""
Unit tests for metadata fetcher service
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from app.services.library_management.metadata_fetcher import (
    MetadataFetcher,
    NPMRegistryClient,
    PyPIRegistryClient,
    AsyncCircuitBreaker,
    NetworkError,
    PackageNotFoundError,
    InvalidResponseError,
    MetadataFetchError
)
from app.schemas.library import LibraryMetadata, Dependency
from app.models.library import RegistryType


class TestAsyncCircuitBreaker:
    """Test async circuit breaker functionality"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state_success(self):
        """Test circuit breaker allows calls in CLOSED state"""
        breaker = AsyncCircuitBreaker(failure_threshold=2)
        
        async def mock_func():
            return "success"
        
        result = await breaker.call(mock_func)
        assert result == "success"
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_failure_tracking(self):
        """Test circuit breaker tracks failures"""
        breaker = AsyncCircuitBreaker(failure_threshold=2, expected_exception=ValueError)
        
        async def mock_func():
            raise ValueError("test error")
        
        # First failure
        with pytest.raises(ValueError):
            await breaker.call(mock_func)
        
        assert breaker.failure_count == 1
        assert breaker.state == "CLOSED"
        
        # Second failure should open circuit
        with pytest.raises(ValueError):
            await breaker.call(mock_func)
        
        assert breaker.failure_count == 2
        assert breaker.state == "OPEN"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_open_state_rejects_calls(self):
        """Test circuit breaker rejects calls in OPEN state"""
        breaker = AsyncCircuitBreaker(failure_threshold=1, expected_exception=ValueError)
        
        async def failing_func():
            raise ValueError("test error")
        
        # Trigger circuit breaker
        with pytest.raises(ValueError):
            await breaker.call(failing_func)
        
        assert breaker.state == "OPEN"
        
        # Should reject subsequent calls
        async def success_func():
            return "success"
        
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await breaker.call(success_func)


class TestNPMRegistryClient:
    """Test npm registry client"""
    
    @pytest.fixture
    def mock_http_client(self):
        return AsyncMock(spec=httpx.AsyncClient)
    
    @pytest.fixture
    def mock_circuit_breaker(self):
        breaker = AsyncMock(spec=AsyncCircuitBreaker)
        breaker.call = AsyncMock()
        return breaker
    
    @pytest.fixture
    def npm_client(self, mock_http_client, mock_circuit_breaker):
        return NPMRegistryClient(mock_http_client, mock_circuit_breaker)
    
    @pytest.mark.asyncio
    async def test_get_package_info_success(self, npm_client, mock_circuit_breaker):
        """Test successful package info retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "test-package"}
        
        mock_circuit_breaker.call.return_value = mock_response
        
        result = await npm_client.get_package_info("test-package")
        
        assert result == {"name": "test-package"}
        mock_circuit_breaker.call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_package_info_not_found(self, npm_client, mock_circuit_breaker):
        """Test package not found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        
        mock_circuit_breaker.call.return_value = mock_response
        
        with pytest.raises(PackageNotFoundError, match="not found in npm registry"):
            await npm_client.get_package_info("nonexistent-package")
    
    @pytest.mark.asyncio
    async def test_get_package_info_network_error(self, npm_client, mock_circuit_breaker):
        """Test network error handling"""
        mock_circuit_breaker.call.side_effect = httpx.RequestError("Connection failed")
        
        with pytest.raises(NetworkError, match="Network error accessing npm registry"):
            await npm_client.get_package_info("test-package")
    
    def test_extract_metadata_success(self, npm_client):
        """Test successful metadata extraction"""
        package_data = {
            "name": "test-package",
            "dist-tags": {"latest": "1.0.0"},
            "versions": {
                "1.0.0": {
                    "description": "A test package",
                    "license": "MIT",
                    "dependencies": {
                        "lodash": "^4.17.21"
                    },
                    "homepage": "https://example.com",
                    "repository": {
                        "url": "https://github.com/test/test-package"
                    }
                }
            }
        }
        
        metadata = npm_client.extract_metadata(package_data)
        
        assert metadata.name == "test-package"
        assert metadata.version == "1.0.0"
        assert metadata.description == "A test package"
        assert metadata.license == "MIT"
        assert metadata.registry_type == RegistryType.NPM
        assert len(metadata.dependencies) == 1
        assert metadata.dependencies[0].name == "lodash"
        assert metadata.dependencies[0].version == "^4.17.21"
        assert metadata.homepage == "https://example.com"
        assert metadata.repository == "https://github.com/test/test-package"
    
    def test_extract_metadata_specific_version(self, npm_client):
        """Test metadata extraction for specific version"""
        package_data = {
            "name": "test-package",
            "versions": {
                "1.0.0": {
                    "description": "Version 1.0.0",
                    "license": "MIT",
                    "dependencies": {}
                },
                "2.0.0": {
                    "description": "Version 2.0.0",
                    "license": "Apache-2.0",
                    "dependencies": {}
                }
            }
        }
        
        metadata = npm_client.extract_metadata(package_data, version="2.0.0")
        
        assert metadata.version == "2.0.0"
        assert metadata.description == "Version 2.0.0"
        assert metadata.license == "Apache-2.0"
    
    def test_extract_metadata_missing_version(self, npm_client):
        """Test error when version not found"""
        package_data = {
            "name": "test-package",
            "versions": {
                "1.0.0": {
                    "description": "Version 1.0.0",
                    "license": "MIT",
                    "dependencies": {}
                }
            }
        }
        
        with pytest.raises(InvalidResponseError, match="Version 2.0.0 not found"):
            npm_client.extract_metadata(package_data, version="2.0.0")
    
    def test_extract_metadata_license_object(self, npm_client):
        """Test license extraction when license is an object"""
        package_data = {
            "name": "test-package",
            "dist-tags": {"latest": "1.0.0"},
            "versions": {
                "1.0.0": {
                    "description": "A test package",
                    "license": {"type": "BSD-3-Clause"},
                    "dependencies": {}
                }
            }
        }
        
        metadata = npm_client.extract_metadata(package_data)
        assert metadata.license == "BSD-3-Clause"


class TestPyPIRegistryClient:
    """Test PyPI registry client"""
    
    @pytest.fixture
    def mock_http_client(self):
        return AsyncMock(spec=httpx.AsyncClient)
    
    @pytest.fixture
    def mock_circuit_breaker(self):
        breaker = AsyncMock(spec=AsyncCircuitBreaker)
        breaker.call = AsyncMock()
        return breaker
    
    @pytest.fixture
    def pypi_client(self, mock_http_client, mock_circuit_breaker):
        return PyPIRegistryClient(mock_http_client, mock_circuit_breaker)
    
    @pytest.mark.asyncio
    async def test_get_package_info_success(self, pypi_client, mock_circuit_breaker):
        """Test successful package info retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"name": "test-package"}}
        
        mock_circuit_breaker.call.return_value = mock_response
        
        result = await pypi_client.get_package_info("test-package")
        
        assert result == {"info": {"name": "test-package"}}
        mock_circuit_breaker.call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_package_info_not_found(self, pypi_client, mock_circuit_breaker):
        """Test package not found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        
        mock_circuit_breaker.call.return_value = mock_response
        
        with pytest.raises(PackageNotFoundError, match="not found in PyPI"):
            await pypi_client.get_package_info("nonexistent-package")
    
    def test_extract_metadata_success(self, pypi_client):
        """Test successful metadata extraction"""
        package_data = {
            "info": {
                "name": "test-package",
                "version": "1.0.0",
                "summary": "A test package for PyPI",
                "license": "MIT",
                "home_page": "https://example.com",
                "project_urls": {
                    "Repository": "https://github.com/test/test-package",
                    "Documentation": "https://docs.example.com"
                }
            }
        }
        
        metadata = pypi_client.extract_metadata(package_data)
        
        assert metadata.name == "test-package"
        assert metadata.version == "1.0.0"
        assert metadata.description == "A test package for PyPI"
        assert metadata.license == "MIT"
        assert metadata.registry_type == RegistryType.PYPI
        assert metadata.homepage == "https://example.com"
        assert metadata.repository == "https://github.com/test/test-package"
        # PyPI doesn't provide dependencies in JSON API
        assert len(metadata.dependencies) == 0
    
    def test_extract_metadata_repository_from_homepage(self, pypi_client):
        """Test repository extraction from homepage when it's a GitHub URL"""
        package_data = {
            "info": {
                "name": "test-package",
                "version": "1.0.0",
                "summary": "A test package",
                "license": "MIT",
                "home_page": "https://github.com/test/test-package",
                "project_urls": {}
            }
        }
        
        metadata = pypi_client.extract_metadata(package_data)
        
        assert metadata.homepage == "https://github.com/test/test-package"
        assert metadata.repository == "https://github.com/test/test-package"


class TestMetadataFetcher:
    """Test metadata fetcher orchestrator"""
    
    @pytest.fixture
    def mock_http_client(self):
        return AsyncMock(spec=httpx.AsyncClient)
    
    @pytest.fixture
    def metadata_fetcher(self, mock_http_client):
        return MetadataFetcher(http_client=mock_http_client)
    
    @pytest.mark.asyncio
    async def test_fetch_metadata_npm_success(self, metadata_fetcher):
        """Test successful npm metadata fetching"""
        # Mock the npm client
        mock_npm_client = AsyncMock()
        mock_npm_client.get_package_info.return_value = {
            "name": "react",
            "dist-tags": {"latest": "18.2.0"},
            "versions": {
                "18.2.0": {
                    "description": "React is a JavaScript library for building user interfaces.",
                    "license": "MIT",
                    "dependencies": {}
                }
            }
        }
        
        expected_metadata = LibraryMetadata(
            name="react",
            version="18.2.0",
            description="React is a JavaScript library for building user interfaces.",
            license="MIT",
            registry_type=RegistryType.NPM,
            dependencies=[]
        )
        
        # Mock extract_metadata as a regular method, not async
        mock_npm_client.extract_metadata = Mock(return_value=expected_metadata)
        metadata_fetcher.registries[RegistryType.NPM] = mock_npm_client
        
        result = await metadata_fetcher.fetch_metadata(RegistryType.NPM, "react")
        
        assert result == expected_metadata
        mock_npm_client.get_package_info.assert_called_once_with("react")
        mock_npm_client.extract_metadata.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_metadata_pypi_success(self, metadata_fetcher):
        """Test successful PyPI metadata fetching"""
        # Mock the PyPI client
        mock_pypi_client = AsyncMock()
        mock_pypi_client.get_package_info.return_value = {
            "info": {
                "name": "django",
                "version": "4.2.0",
                "summary": "A high-level Python Web framework.",
                "license": "BSD"
            }
        }
        
        expected_metadata = LibraryMetadata(
            name="django",
            version="4.2.0",
            description="A high-level Python Web framework.",
            license="BSD",
            registry_type=RegistryType.PYPI,
            dependencies=[]
        )
        
        # Mock extract_metadata as a regular method, not async
        mock_pypi_client.extract_metadata = Mock(return_value=expected_metadata)
        metadata_fetcher.registries[RegistryType.PYPI] = mock_pypi_client
        
        result = await metadata_fetcher.fetch_metadata(RegistryType.PYPI, "django")
        
        assert result == expected_metadata
        mock_pypi_client.get_package_info.assert_called_once_with("django")
        mock_pypi_client.extract_metadata.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_metadata_unsupported_registry(self, metadata_fetcher):
        """Test error for unsupported registry type"""
        with pytest.raises(ValueError, match="Unsupported registry type"):
            await metadata_fetcher.fetch_metadata(RegistryType.MAVEN, "test-package")
    
    @pytest.mark.asyncio
    async def test_fetch_metadata_network_error(self, metadata_fetcher):
        """Test network error handling"""
        mock_npm_client = AsyncMock()
        mock_npm_client.get_package_info.side_effect = NetworkError("Connection failed")
        metadata_fetcher.registries[RegistryType.NPM] = mock_npm_client
        
        with pytest.raises(NetworkError, match="Connection failed"):
            await metadata_fetcher.fetch_metadata(RegistryType.NPM, "test-package")
    
    @pytest.mark.asyncio
    async def test_fetch_metadata_package_not_found(self, metadata_fetcher):
        """Test package not found error handling"""
        mock_npm_client = AsyncMock()
        mock_npm_client.get_package_info.side_effect = PackageNotFoundError("Package not found")
        metadata_fetcher.registries[RegistryType.NPM] = mock_npm_client
        
        with pytest.raises(PackageNotFoundError, match="Package not found"):
            await metadata_fetcher.fetch_metadata(RegistryType.NPM, "nonexistent-package")
    
    @pytest.mark.asyncio
    async def test_fetch_metadata_unexpected_error(self, metadata_fetcher):
        """Test unexpected error handling"""
        mock_npm_client = AsyncMock()
        mock_npm_client.get_package_info.side_effect = Exception("Unexpected error")
        metadata_fetcher.registries[RegistryType.NPM] = mock_npm_client
        
        with pytest.raises(MetadataFetchError, match="Unexpected error"):
            await metadata_fetcher.fetch_metadata(RegistryType.NPM, "test-package")
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality"""
        async with MetadataFetcher() as fetcher:
            assert fetcher is not None
            assert fetcher.http_client is not None
        
        # Client should be closed after exiting context
        # Note: We can't easily test this without mocking, but the structure is correct
    
    @pytest.mark.asyncio
    async def test_close_method(self, metadata_fetcher):
        """Test close method"""
        # Should not raise any errors
        await metadata_fetcher.close()
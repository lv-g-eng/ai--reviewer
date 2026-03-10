"""
Unit tests for Search Service
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

import httpx

from app.services.library_management.search_service import (
    SearchService,
    NPMSearchClient,
    PyPISearchClient,
    AsyncCircuitBreaker,
    NetworkSearchError,
    InvalidSearchQueryError
)
from app.schemas.library import LibrarySearchResult
from app.models.library import RegistryType


class TestAsyncCircuitBreaker:
    """Test AsyncCircuitBreaker functionality"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in CLOSED state allows calls"""
        breaker = AsyncCircuitBreaker(failure_threshold=2, recovery_timeout=1.0)
        
        async def success_func():
            return "success"
        
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        breaker = AsyncCircuitBreaker(failure_threshold=2, recovery_timeout=1.0)
        
        async def failing_func():
            raise Exception("Test failure")
        
        # First failure
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 1
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        assert breaker.state == "OPEN"
        assert breaker.failure_count == 2
        
        # Third call should be rejected
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout"""
        breaker = AsyncCircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        
        async def failing_func():
            raise Exception("Test failure")
        
        async def success_func():
            return "success"
        
        # Trigger failure to open circuit
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        assert breaker.state == "OPEN"
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Should enter HALF_OPEN and allow call
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == "CLOSED"


class TestNPMSearchClient:
    """Test NPMSearchClient functionality"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        return AsyncMock(spec=httpx.AsyncClient)
    
    @pytest.fixture
    def mock_circuit_breaker(self):
        """Create mock circuit breaker"""
        async def mock_call(func, *args, **kwargs):
            return await func(*args, **kwargs)
        
        breaker = AsyncMock(spec=AsyncCircuitBreaker)
        breaker.call = AsyncMock(side_effect=mock_call)
        return breaker
    
    @pytest.fixture
    def npm_client(self, mock_http_client, mock_circuit_breaker):
        """Create NPMSearchClient with mocks"""
        return NPMSearchClient(mock_http_client, mock_circuit_breaker)
    
    @pytest.mark.asyncio
    async def test_npm_search_success(self, npm_client, mock_http_client):
        """Test successful npm search"""
        # Mock response data
        mock_response_data = {
            "objects": [
                {
                    "package": {
                        "name": "react",
                        "description": "A JavaScript library for building user interfaces",
                        "version": "18.2.0"
                    },
                    "score": {
                        "detail": {
                            "popularity": 0.95
                        }
                    }
                },
                {
                    "package": {
                        "name": "react-dom",
                        "description": "React package for working with the DOM",
                        "version": "18.2.0"
                    },
                    "score": {
                        "detail": {
                            "popularity": 0.85
                        }
                    }
                }
            ]
        }
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_http_client.get.return_value = mock_response
        
        # Perform search
        results = await npm_client.search("react", limit=10)
        
        # Verify results
        assert len(results) == 2
        assert results[0].name == "react"
        assert results[0].description == "A JavaScript library for building user interfaces"
        assert results[0].version == "18.2.0"
        assert results[0].registry_type == RegistryType.NPM
        assert results[0].uri == "npm:react@18.2.0"
        assert results[0].downloads == 950000  # Approximate from popularity
        
        assert results[1].name == "react-dom"
        assert results[1].registry_type == RegistryType.NPM
        
        # Verify HTTP call
        mock_http_client.get.assert_called_once()
        call_args = mock_http_client.get.call_args
        assert "/-/v1/search" in call_args[0][0]
        assert call_args[1]["params"]["text"] == "react"
        assert call_args[1]["params"]["size"] == 10
    
    @pytest.mark.asyncio
    async def test_npm_search_empty_query(self, npm_client):
        """Test npm search with empty query"""
        with pytest.raises(InvalidSearchQueryError, match="Search query cannot be empty"):
            await npm_client.search("")
        
        with pytest.raises(InvalidSearchQueryError, match="Search query cannot be empty"):
            await npm_client.search("   ")
    
    @pytest.mark.asyncio
    async def test_npm_search_network_error(self, npm_client, mock_http_client):
        """Test npm search with network error"""
        mock_http_client.get.side_effect = httpx.RequestError("Connection failed")
        
        with pytest.raises(NetworkSearchError, match="Network error accessing npm search API"):
            await npm_client.search("react")
    
    @pytest.mark.asyncio
    async def test_npm_search_api_error(self, npm_client, mock_http_client):
        """Test npm search with API error response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_http_client.get.return_value = mock_response
        
        with pytest.raises(NetworkSearchError, match="npm search API returned status 500"):
            await npm_client.search("react")
    
    @pytest.mark.asyncio
    async def test_npm_search_invalid_json(self, npm_client, mock_http_client):
        """Test npm search with invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_http_client.get.return_value = mock_response
        
        with pytest.raises(NetworkSearchError, match="Invalid JSON response"):
            await npm_client.search("react")
    
    @pytest.mark.asyncio
    async def test_npm_search_empty_results(self, npm_client, mock_http_client):
        """Test npm search with empty results"""
        mock_response_data = {"objects": []}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_http_client.get.return_value = mock_response
        
        results = await npm_client.search("nonexistent-package")
        assert len(results) == 0
    
    def test_npm_parse_results_missing_fields(self, npm_client):
        """Test npm result parsing with missing fields"""
        data = {
            "objects": [
                {
                    "package": {
                        "name": "test-package"
                        # Missing description and version
                    }
                },
                {
                    "package": {
                        # Missing name
                        "description": "Test description",
                        "version": "1.0.0"
                    }
                }
            ]
        }
        
        results = npm_client._parse_search_results(data, 10)
        
        # Should only include the first package (has name)
        assert len(results) == 1
        assert results[0].name == "test-package"
        assert results[0].description == ""
        assert results[0].version == ""


class TestPyPISearchClient:
    """Test PyPISearchClient functionality"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        return AsyncMock(spec=httpx.AsyncClient)
    
    @pytest.fixture
    def mock_circuit_breaker(self):
        """Create mock circuit breaker"""
        async def mock_call(func, *args, **kwargs):
            return await func(*args, **kwargs)
        
        breaker = AsyncMock(spec=AsyncCircuitBreaker)
        breaker.call = AsyncMock(side_effect=mock_call)
        return breaker
    
    @pytest.fixture
    def pypi_client(self, mock_http_client, mock_circuit_breaker):
        """Create PyPISearchClient with mocks"""
        return PyPISearchClient(mock_http_client, mock_circuit_breaker)
    
    @pytest.mark.asyncio
    async def test_pypi_search_success(self, pypi_client, mock_http_client):
        """Test successful PyPI search"""
        # Mock response data for exact match
        mock_response_data = {
            "info": {
                "name": "django",
                "summary": "A high-level Python Web framework",
                "version": "4.2.0"
            }
        }
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_http_client.get.return_value = mock_response
        
        # Perform search
        results = await pypi_client.search("django", limit=10)
        
        # Verify results
        assert len(results) == 1
        assert results[0].name == "django"
        assert results[0].description == "A high-level Python Web framework"
        assert results[0].version == "4.2.0"
        assert results[0].registry_type == RegistryType.PYPI
        assert results[0].uri == "pypi:django==4.2.0"
        assert results[0].downloads is None  # PyPI doesn't provide download counts
        
        # Verify HTTP call
        mock_http_client.get.assert_called()
        call_args = mock_http_client.get.call_args_list[0]
        assert "/pypi/django/json" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_pypi_search_empty_query(self, pypi_client):
        """Test PyPI search with empty query"""
        with pytest.raises(InvalidSearchQueryError, match="Search query cannot be empty"):
            await pypi_client.search("")
        
        with pytest.raises(InvalidSearchQueryError, match="Search query cannot be empty"):
            await pypi_client.search("   ")
    
    @pytest.mark.asyncio
    async def test_pypi_search_not_found(self, pypi_client, mock_http_client):
        """Test PyPI search with package not found"""
        # Mock 404 response for exact match and variations
        mock_response = Mock()
        mock_response.status_code = 404
        mock_http_client.get.return_value = mock_response
        
        results = await pypi_client.search("nonexistent-package")
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_pypi_search_network_error(self, pypi_client, mock_http_client):
        """Test PyPI search with network error"""
        mock_http_client.get.side_effect = httpx.RequestError("Connection failed")
        
        # Should return empty results, not raise exception
        results = await pypi_client.search("django")
        assert len(results) == 0
    
    def test_pypi_generate_name_variations(self, pypi_client):
        """Test PyPI name variation generation"""
        variations = pypi_client._generate_name_variations("test-package")
        
        expected_variations = [
            "test_package",      # hyphens to underscores
            "python-test-package",  # python- prefix
            "py-test-package",   # py- prefix
            "test-package-python",  # -python suffix
            "test-package2",     # version suffix
            "test-package3",     # version suffix
        ]
        
        for expected in expected_variations:
            assert expected in variations
        
        # Original query should not be in variations
        assert "test-package" not in variations
    
    @pytest.mark.asyncio
    async def test_pypi_try_package_name_success(self, pypi_client, mock_http_client):
        """Test successful package name lookup"""
        mock_response_data = {
            "info": {
                "name": "requests",
                "summary": "Python HTTP for Humans",
                "version": "2.28.0"
            }
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_http_client.get.return_value = mock_response
        
        result = await pypi_client._try_package_name("requests")
        
        assert result is not None
        assert result.name == "requests"
        assert result.description == "Python HTTP for Humans"
        assert result.version == "2.28.0"
    
    @pytest.mark.asyncio
    async def test_pypi_try_package_name_not_found(self, pypi_client, mock_http_client):
        """Test package name lookup with 404"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_http_client.get.return_value = mock_response
        
        result = await pypi_client._try_package_name("nonexistent")
        assert result is None
    
    def test_pypi_parse_package_info_missing_fields(self, pypi_client):
        """Test PyPI package info parsing with missing fields"""
        # Missing name
        data = {"info": {"summary": "Test description", "version": "1.0.0"}}
        result = pypi_client._parse_package_info(data)
        assert result is None
        
        # Valid data
        data = {"info": {"name": "test", "summary": "Test", "version": "1.0.0"}}
        result = pypi_client._parse_package_info(data)
        assert result is not None
        assert result.name == "test"


class TestSearchService:
    """Test SearchService functionality"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        return AsyncMock(spec=httpx.AsyncClient)
    
    @pytest.fixture
    def search_service(self, mock_http_client):
        """Create SearchService with mock HTTP client"""
        return SearchService(mock_http_client)
    
    @pytest.mark.asyncio
    async def test_search_service_npm_only(self, search_service):
        """Test search service with npm registry only"""
        # Mock npm search results
        npm_results = [
            LibrarySearchResult(
                name="react",
                description="JavaScript library",
                version="18.2.0",
                downloads=1000000,
                uri="npm:react@18.2.0",
                registry_type=RegistryType.NPM
            )
        ]
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results) as mock_npm_search:
            
            results = await search_service.search("react", registry_type=RegistryType.NPM)
            
            assert len(results) == 1
            assert results[0].name == "react"
            assert results[0].registry_type == RegistryType.NPM
            
            mock_npm_search.assert_called_once_with("react", 20)
    
    @pytest.mark.asyncio
    async def test_search_service_all_registries(self, search_service):
        """Test search service across all registries"""
        # Mock npm search results
        npm_results = [
            LibrarySearchResult(
                name="react",
                description="JavaScript library",
                version="18.2.0",
                downloads=1000000,
                uri="npm:react@18.2.0",
                registry_type=RegistryType.NPM
            )
        ]
        
        # Mock PyPI search results
        pypi_results = [
            LibrarySearchResult(
                name="django",
                description="Python web framework",
                version="4.2.0",
                downloads=None,
                uri="pypi:django==4.2.0",
                registry_type=RegistryType.PYPI
            )
        ]
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results) as mock_npm_search, \
             patch.object(search_service.search_clients[RegistryType.PYPI], 'search', 
                         return_value=pypi_results) as mock_pypi_search:
            
            results = await search_service.search("test")
            
            assert len(results) == 2
            registry_types = {r.registry_type for r in results}
            assert RegistryType.NPM in registry_types
            assert RegistryType.PYPI in registry_types
            
            mock_npm_search.assert_called_once()
            mock_pypi_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_service_empty_query(self, search_service):
        """Test search service with empty query"""
        with pytest.raises(InvalidSearchQueryError, match="Search query cannot be empty"):
            await search_service.search("")
        
        with pytest.raises(InvalidSearchQueryError, match="Search query cannot be empty"):
            await search_service.search("   ")
    
    @pytest.mark.asyncio
    async def test_search_service_invalid_limit(self, search_service):
        """Test search service with invalid limit"""
        with pytest.raises(InvalidSearchQueryError, match="Limit must be greater than 0"):
            await search_service.search("react", limit=0)
        
        with pytest.raises(InvalidSearchQueryError, match="Limit must be greater than 0"):
            await search_service.search("react", limit=-1)
    
    @pytest.mark.asyncio
    async def test_search_service_unsupported_registry(self, search_service):
        """Test search service with unsupported registry"""
        with pytest.raises(InvalidSearchQueryError, match="Unsupported registry type"):
            await search_service.search("react", registry_type=RegistryType.MAVEN)
    
    @pytest.mark.asyncio
    async def test_search_service_limit_capping(self, search_service):
        """Test search service caps limit at 100"""
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=[]) as mock_npm_search:
            
            await search_service.search("react", registry_type=RegistryType.NPM, limit=200)
            
            # Should be capped at 100
            mock_npm_search.assert_called_once_with("react", 100)
    
    @pytest.mark.asyncio
    async def test_search_service_result_sorting(self, search_service):
        """Test search service sorts results correctly"""
        # Mock results with exact match and partial matches
        npm_results = [
            LibrarySearchResult(
                name="react-dom",
                description="React DOM",
                version="18.2.0",
                downloads=500000,
                uri="npm:react-dom@18.2.0",
                registry_type=RegistryType.NPM
            ),
            LibrarySearchResult(
                name="react",  # Exact match
                description="React library",
                version="18.2.0",
                downloads=1000000,
                uri="npm:react@18.2.0",
                registry_type=RegistryType.NPM
            )
        ]
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results):
            
            results = await search_service.search("react", registry_type=RegistryType.NPM)
            
            # Exact match should be first
            assert results[0].name == "react"
            assert results[1].name == "react-dom"
    
    @pytest.mark.asyncio
    async def test_search_service_registry_failure_handling(self, search_service):
        """Test search service handles registry failures gracefully"""
        # Mock npm to succeed, PyPI to fail
        npm_results = [
            LibrarySearchResult(
                name="react",
                description="JavaScript library",
                version="18.2.0",
                downloads=1000000,
                uri="npm:react@18.2.0",
                registry_type=RegistryType.NPM
            )
        ]
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results), \
             patch.object(search_service.search_clients[RegistryType.PYPI], 'search', 
                         side_effect=NetworkSearchError("PyPI unavailable")):
            
            results = await search_service.search("react")
            
            # Should still return npm results despite PyPI failure
            assert len(results) == 1
            assert results[0].registry_type == RegistryType.NPM
    
    @pytest.mark.asyncio
    async def test_search_service_close(self, search_service, mock_http_client):
        """Test search service close method"""
        # Service owns the client, should close it
        search_service._own_client = True
        
        await search_service.close()
        
        mock_http_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_service_context_manager(self, mock_http_client):
        """Test search service as async context manager"""
        async with SearchService(mock_http_client) as service:
            assert service is not None
        
        # Should not close client if not owned
        mock_http_client.aclose.assert_not_called()


# Integration-style tests
class TestSearchServiceIntegration:
    """Integration tests for SearchService"""
    
    @pytest.mark.asyncio
    async def test_search_service_end_to_end_mock(self):
        """Test complete search workflow with mocked HTTP responses"""
        # Create real SearchService with mocked HTTP client
        mock_http_client = AsyncMock(spec=httpx.AsyncClient)
        
        # Mock npm search response
        npm_response = Mock()
        npm_response.status_code = 200
        npm_response.json.return_value = {
            "objects": [
                {
                    "package": {
                        "name": "lodash",
                        "description": "A modern JavaScript utility library",
                        "version": "4.17.21"
                    },
                    "score": {
                        "detail": {
                            "popularity": 0.99
                        }
                    }
                }
            ]
        }
        
        # Mock PyPI response (404 for exact match)
        pypi_response = Mock()
        pypi_response.status_code = 404
        
        # Configure mock to return different responses for different URLs
        def mock_get(url, **kwargs):
            if "/-/v1/search" in url:
                return npm_response
            elif "/pypi/" in url:
                return pypi_response
            else:
                raise ValueError(f"Unexpected URL: {url}")
        
        mock_http_client.get.side_effect = mock_get
        
        # Perform search
        async with SearchService(mock_http_client) as service:
            results = await service.search("lodash")
        
        # Verify results
        assert len(results) == 1
        assert results[0].name == "lodash"
        assert results[0].description == "A modern JavaScript utility library"
        assert results[0].version == "4.17.21"
        assert results[0].registry_type == RegistryType.NPM
        assert results[0].uri == "npm:lodash@4.17.21"
        
        # Verify HTTP calls were made
        assert mock_http_client.get.call_count >= 1
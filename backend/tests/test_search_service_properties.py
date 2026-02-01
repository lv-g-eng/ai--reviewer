"""
Property-based tests for Search Service

These tests verify universal properties that should hold across all valid inputs
for the search functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List

from hypothesis import given, strategies as st, assume, settings
from hypothesis import HealthCheck

from app.services.library_management.search_service import (
    SearchService,
    NPMSearchClient,
    PyPISearchClient,
    InvalidSearchQueryError,
    NetworkSearchError
)
from app.schemas.library import LibrarySearchResult
from app.models.library import RegistryType


# Test data generators
@st.composite
def valid_search_queries(draw):
    """Generate valid search query strings"""
    # Generate non-empty strings with reasonable characters
    query = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd')),
        min_size=1,
        max_size=50
    ).filter(lambda s: s.strip()))
    
    assume(len(query.strip()) > 0)
    return query.strip()


@st.composite
def invalid_search_queries(draw):
    """Generate invalid search query strings"""
    return draw(st.one_of(
        st.just(""),           # Empty string
        st.just("   "),        # Whitespace only
        st.just("\t\n"),       # Tabs and newlines
    ))


@st.composite
def search_limits(draw):
    """Generate valid search limits"""
    return draw(st.integers(min_value=1, max_value=100))


@st.composite
def invalid_search_limits(draw):
    """Generate invalid search limits"""
    return draw(st.integers(max_value=0))


@st.composite
def mock_npm_search_results(draw):
    """Generate mock npm search results"""
    num_results = draw(st.integers(min_value=0, max_value=20))
    results = []
    
    for i in range(num_results):
        name = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd')),
            min_size=1,
            max_size=30
        ).filter(lambda s: s.strip()))
        
        assume(len(name.strip()) > 0)
        name = name.strip().lower()
        
        result = LibrarySearchResult(
            name=name,
            description=f"Description for {name}",
            version=f"{draw(st.integers(min_value=1, max_value=10))}.0.0",
            downloads=draw(st.integers(min_value=0, max_value=1000000)),
            uri=f"npm:{name}@1.0.0",
            registry_type=RegistryType.NPM
        )
        results.append(result)
    
    return results


@st.composite
def mock_pypi_search_results(draw):
    """Generate mock PyPI search results"""
    num_results = draw(st.integers(min_value=0, max_value=20))
    results = []
    
    for i in range(num_results):
        name = draw(st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd', 'Pc')),
            min_size=1,
            max_size=30
        ).filter(lambda s: s.strip()))
        
        assume(len(name.strip()) > 0)
        name = name.strip().lower().replace('-', '_')  # PyPI naming convention
        
        result = LibrarySearchResult(
            name=name,
            description=f"Description for {name}",
            version=f"{draw(st.integers(min_value=1, max_value=10))}.0.0",
            downloads=None,  # PyPI doesn't provide download counts
            uri=f"pypi:{name}==1.0.0",
            registry_type=RegistryType.PYPI
        )
        results.append(result)
    
    return results


class TestSearchServiceProperties:
    """Property-based tests for SearchService"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        return AsyncMock()
    
    @pytest.fixture
    def search_service(self, mock_http_client):
        """Create SearchService with mock HTTP client"""
        return SearchService(mock_http_client)
    
    # Feature: library-management, Property 17: Search Query Routing
    @given(
        query=valid_search_queries(),
        registry_type=st.sampled_from([RegistryType.NPM, RegistryType.PYPI, None])
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_search_query_routing_correctness(self, search_service, query, registry_type):
        """
        Property 17: For any search query, the system should query the appropriate 
        Package Registry APIs based on the specified registry type filter 
        (or all registries if no filter is specified).
        
        **Validates: Requirements 9.2**
        """
        # Mock search client methods
        npm_results = [
            LibrarySearchResult(
                name="test-npm",
                description="Test npm package",
                version="1.0.0",
                downloads=1000,
                uri="npm:test-npm@1.0.0",
                registry_type=RegistryType.NPM
            )
        ]
        
        pypi_results = [
            LibrarySearchResult(
                name="test_pypi",
                description="Test PyPI package",
                version="1.0.0",
                downloads=None,
                uri="pypi:test_pypi==1.0.0",
                registry_type=RegistryType.PYPI
            )
        ]
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results) as mock_npm_search, \
             patch.object(search_service.search_clients[RegistryType.PYPI], 'search', 
                         return_value=pypi_results) as mock_pypi_search:
            
            results = await search_service.search(query, registry_type=registry_type)
            
            # Verify correct APIs were called based on registry filter
            if registry_type == RegistryType.NPM:
                mock_npm_search.assert_called_once()
                mock_pypi_search.assert_not_called()
                # All results should be from npm
                for result in results:
                    assert result.registry_type == RegistryType.NPM
                    
            elif registry_type == RegistryType.PYPI:
                mock_pypi_search.assert_called_once()
                mock_npm_search.assert_not_called()
                # All results should be from PyPI
                for result in results:
                    assert result.registry_type == RegistryType.PYPI
                    
            else:  # registry_type is None - should search all
                mock_npm_search.assert_called_once()
                mock_pypi_search.assert_called_once()
                # Results can be from any registry
                registry_types = {result.registry_type for result in results}
                assert registry_types.issubset({RegistryType.NPM, RegistryType.PYPI})
    
    # Feature: library-management, Property 18: Search Result Completeness
    @given(
        query=valid_search_queries(),
        npm_results=mock_npm_search_results(),
        pypi_results=mock_pypi_search_results()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_search_result_completeness(self, search_service, query, npm_results, pypi_results):
        """
        Property 18: For any search result, the displayed information should include 
        the library name, description, and version at minimum.
        
        **Validates: Requirements 9.3**
        """
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results), \
             patch.object(search_service.search_clients[RegistryType.PYPI], 'search', 
                         return_value=pypi_results):
            
            results = await search_service.search(query)
            
            # Verify all results have required fields
            for result in results:
                assert result.name is not None
                assert len(result.name) > 0
                assert result.description is not None  # Can be empty string
                assert result.version is not None
                assert len(result.version) > 0
                assert result.registry_type in [RegistryType.NPM, RegistryType.PYPI]
                assert result.uri is not None
                assert len(result.uri) > 0
    
    # Feature: library-management, Property 19: Search Result Filtering
    @given(
        query=valid_search_queries(),
        registry_filter=st.sampled_from([RegistryType.NPM, RegistryType.PYPI])
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_search_result_filtering_correctness(self, search_service, query, registry_filter):
        """
        Property 19: For any search results and registry type filter, the filtered 
        results should contain only libraries from the specified registry type.
        
        **Validates: Requirements 9.5**
        """
        # Create mixed results
        npm_results = [
            LibrarySearchResult(
                name="npm-package",
                description="NPM package",
                version="1.0.0",
                downloads=1000,
                uri="npm:npm-package@1.0.0",
                registry_type=RegistryType.NPM
            )
        ]
        
        pypi_results = [
            LibrarySearchResult(
                name="pypi_package",
                description="PyPI package",
                version="1.0.0",
                downloads=None,
                uri="pypi:pypi_package==1.0.0",
                registry_type=RegistryType.PYPI
            )
        ]
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results), \
             patch.object(search_service.search_clients[RegistryType.PYPI], 'search', 
                         return_value=pypi_results):
            
            results = await search_service.search(query, registry_type=registry_filter)
            
            # All results should be from the specified registry
            for result in results:
                assert result.registry_type == registry_filter
    
    # Feature: library-management, Property: Invalid Query Rejection
    @given(invalid_query=invalid_search_queries())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_invalid_search_query_rejection(self, search_service, invalid_query):
        """
        Property: For any invalid search query (empty or whitespace-only), 
        the search service should reject it with a descriptive error message.
        
        **Validates: Input validation requirements**
        """
        with pytest.raises(InvalidSearchQueryError) as exc_info:
            await search_service.search(invalid_query)
        
        # Error message should be descriptive
        error_message = str(exc_info.value)
        assert len(error_message) > 0
        assert "empty" in error_message.lower() or "whitespace" in error_message.lower()
    
    # Feature: library-management, Property: Limit Enforcement
    @given(
        query=valid_search_queries(),
        limit=search_limits()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_search_limit_enforcement(self, search_service, query, limit):
        """
        Property: For any valid search query and limit, the number of returned 
        results should not exceed the specified limit.
        
        **Validates: Requirements 9.5 (pagination/limits)**
        """
        # Create more results than the limit
        large_npm_results = []
        for i in range(limit + 10):  # Create more than limit
            result = LibrarySearchResult(
                name=f"package-{i}",
                description=f"Package {i}",
                version="1.0.0",
                downloads=1000,
                uri=f"npm:package-{i}@1.0.0",
                registry_type=RegistryType.NPM
            )
            large_npm_results.append(result)
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=large_npm_results), \
             patch.object(search_service.search_clients[RegistryType.PYPI], 'search', 
                         return_value=[]):
            
            results = await search_service.search(query, limit=limit)
            
            # Results should not exceed limit
            assert len(results) <= limit
    
    # Feature: library-management, Property: Invalid Limit Rejection
    @given(
        query=valid_search_queries(),
        invalid_limit=invalid_search_limits()
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_invalid_limit_rejection(self, search_service, query, invalid_limit):
        """
        Property: For any search query with an invalid limit (≤ 0), 
        the search service should reject it with a descriptive error message.
        
        **Validates: Input validation requirements**
        """
        with pytest.raises(InvalidSearchQueryError) as exc_info:
            await search_service.search(query, limit=invalid_limit)
        
        # Error message should mention limit validation
        error_message = str(exc_info.value)
        assert len(error_message) > 0
        assert "limit" in error_message.lower()
    
    # Feature: library-management, Property: Result Consistency
    @given(
        query=valid_search_queries(),
        registry_type=st.sampled_from([RegistryType.NPM, RegistryType.PYPI, None])
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_search_result_consistency(self, search_service, query, registry_type):
        """
        Property: For any search query, multiple calls with the same parameters 
        should return consistent results (assuming no external changes).
        
        **Validates: Search consistency requirements**
        """
        # Mock consistent results
        npm_results = [
            LibrarySearchResult(
                name="consistent-package",
                description="Consistent package",
                version="1.0.0",
                downloads=1000,
                uri="npm:consistent-package@1.0.0",
                registry_type=RegistryType.NPM
            )
        ]
        
        pypi_results = [
            LibrarySearchResult(
                name="consistent_package",
                description="Consistent PyPI package",
                version="1.0.0",
                downloads=None,
                uri="pypi:consistent_package==1.0.0",
                registry_type=RegistryType.PYPI
            )
        ]
        
        with patch.object(search_service.search_clients[RegistryType.NPM], 'search', 
                         return_value=npm_results), \
             patch.object(search_service.search_clients[RegistryType.PYPI], 'search', 
                         return_value=pypi_results):
            
            # Perform search twice
            results1 = await search_service.search(query, registry_type=registry_type)
            results2 = await search_service.search(query, registry_type=registry_type)
            
            # Results should be identical
            assert len(results1) == len(results2)
            
            for r1, r2 in zip(results1, results2):
                assert r1.name == r2.name
                assert r1.description == r2.description
                assert r1.version == r2.version
                assert r1.registry_type == r2.registry_type
                assert r1.uri == r2.uri
                assert r1.downloads == r2.downloads


class TestNPMSearchClientProperties:
    """Property-based tests for NPMSearchClient"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_circuit_breaker(self):
        """Create mock circuit breaker"""
        async def mock_call(func, *args, **kwargs):
            return await func(*args, **kwargs)
        
        breaker = AsyncMock()
        breaker.call = AsyncMock(side_effect=mock_call)
        return breaker
    
    @pytest.fixture
    def npm_client(self, mock_http_client, mock_circuit_breaker):
        """Create NPMSearchClient with mocks"""
        return NPMSearchClient(mock_http_client, mock_circuit_breaker)
    
    # Feature: library-management, Property: NPM API Parameter Validation
    @given(
        query=valid_search_queries(),
        limit=search_limits()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_npm_api_parameter_correctness(self, npm_client, mock_http_client, query, limit):
        """
        Property: For any valid query and limit, NPM search should call the API 
        with correct parameters.
        
        **Validates: NPM API integration correctness**
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"objects": []}
        mock_http_client.get.return_value = mock_response
        
        await npm_client.search(query, limit)
        
        # Verify API call parameters
        assert mock_http_client.get.call_count >= 1
        
        # Check the last call (or any call) for correct parameters
        call_args = mock_http_client.get.call_args_list[-1]
        
        # Check URL
        assert "/-/v1/search" in call_args[0][0]
        
        # Check parameters
        params = call_args[1]["params"]
        assert params["text"] == query
        assert params["size"] == min(limit, 250)  # npm API max
        assert "quality" in params
        assert "popularity" in params
        assert "maintenance" in params


class TestPyPISearchClientProperties:
    """Property-based tests for PyPISearchClient"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_circuit_breaker(self):
        """Create mock circuit breaker"""
        async def mock_call(func, *args, **kwargs):
            return await func(*args, **kwargs)
        
        breaker = AsyncMock()
        breaker.call = AsyncMock(side_effect=mock_call)
        return breaker
    
    @pytest.fixture
    def pypi_client(self, mock_http_client, mock_circuit_breaker):
        """Create PyPISearchClient with mocks"""
        return PyPISearchClient(mock_http_client, mock_circuit_breaker)
    
    # Feature: library-management, Property: PyPI Name Variation Generation
    @given(query=valid_search_queries())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_pypi_name_variation_properties(self, pypi_client, query):
        """
        Property: For any valid query, PyPI name variation generation should 
        produce valid package name variations and not include the original query.
        
        **Validates: PyPI search strategy correctness**
        """
        variations = pypi_client._generate_name_variations(query)
        
        # Original query should not be in variations
        assert query not in variations
        
        # All variations should be non-empty strings
        for variation in variations:
            assert isinstance(variation, str)
            assert len(variation) > 0
        
        # Should include common patterns
        expected_patterns = [
            query.replace("-", "_"),
            query.replace("_", "-"),
            f"python-{query}",
            f"py-{query}",
            f"{query}-python"
        ]
        
        # At least some expected patterns should be present (if they differ from original)
        found_patterns = 0
        for pattern in expected_patterns:
            if pattern != query and pattern in variations:
                found_patterns += 1
        
        # Should find at least one valid pattern
        assert found_patterns > 0
"""
Property-Based Tests for URI Parser Service

Tests universal properties that should hold across all valid inputs.
Uses hypothesis for property-based testing with minimum 100 iterations.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.services.library_management.uri_parser import URIParser
from app.models.library import RegistryType


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

# Strategy for generating valid npm package names
npm_package_names = st.one_of(
    # Simple package names: lowercase letters, numbers, hyphens
    st.from_regex(r'^[a-z0-9][a-z0-9-]{0,50}$', fullmatch=True),
    # Scoped package names: @scope/package
    st.from_regex(r'^@[a-z0-9][a-z0-9-]{0,20}/[a-z0-9][a-z0-9-]{0,20}$', fullmatch=True)
)

# Strategy for generating valid PyPI package names
pypi_package_names = st.from_regex(
    r'^[a-z0-9][a-z0-9-_.]{0,50}$',
    fullmatch=True
)

# Strategy for generating valid Maven coordinates
maven_group_ids = st.from_regex(r'^[a-z0-9][a-z0-9.-]{0,30}$', fullmatch=True)
maven_artifact_ids = st.from_regex(r'^[a-z0-9][a-z0-9-]{0,30}$', fullmatch=True)

# Strategy for generating semantic versions
semantic_versions = st.one_of(
    # Standard versions: 1.2.3
    st.from_regex(r'^[0-9]+\.[0-9]+\.[0-9]+$', fullmatch=True),
    # Versions with prerelease: 1.2.3-alpha.1
    st.from_regex(r'^[0-9]+\.[0-9]+\.[0-9]+-[a-z0-9.]+$', fullmatch=True),
    # Versions with build metadata: 1.2.3+build.123
    st.from_regex(r'^[0-9]+\.[0-9]+\.[0-9]+\+[a-z0-9.]+$', fullmatch=True),
)

# Strategy for generating npm URIs
npm_uris = st.one_of(
    # npm:package format
    st.builds(
        lambda pkg: f"npm:{pkg}",
        npm_package_names
    ),
    # npm:package@version format
    st.builds(
        lambda pkg, ver: f"npm:{pkg}@{ver}",
        npm_package_names,
        semantic_versions
    ),
    # https://npmjs.com/package/name format
    st.builds(
        lambda pkg: f"https://npmjs.com/package/{pkg}",
        npm_package_names.filter(lambda x: '@' not in x)  # URLs don't support scoped packages well
    ),
)

# Strategy for generating PyPI URIs
pypi_uris = st.one_of(
    # pypi:package format
    st.builds(
        lambda pkg: f"pypi:{pkg}",
        pypi_package_names
    ),
    # pypi:package==version format
    st.builds(
        lambda pkg, ver: f"pypi:{pkg}=={ver}",
        pypi_package_names,
        semantic_versions
    ),
    # https://pypi.org/project/name format
    st.builds(
        lambda pkg: f"https://pypi.org/project/{pkg}",
        pypi_package_names
    ),
)

# Strategy for generating Maven URIs
maven_uris = st.one_of(
    # maven:group:artifact format
    st.builds(
        lambda grp, art: f"maven:{grp}:{art}",
        maven_group_ids,
        maven_artifact_ids
    ),
    # maven:group:artifact:version format
    st.builds(
        lambda grp, art, ver: f"maven:{grp}:{art}:{ver}",
        maven_group_ids,
        maven_artifact_ids,
        semantic_versions
    ),
)

# Strategy for generating any valid URI
valid_uris = st.one_of(npm_uris, pypi_uris, maven_uris)

# Strategy for generating invalid URIs
invalid_uris = st.one_of(
    # Empty or whitespace
    st.just(""),
    st.just("   "),
    # Invalid prefixes
    st.from_regex(r'^(invalid|wrong|bad):[a-z0-9-]+$', fullmatch=True),
    # Malformed URIs
    st.just("npm:"),
    st.just("pypi:"),
    st.just("maven:"),
    st.just("maven:group"),  # Maven needs at least group:artifact
    # Invalid URLs
    st.from_regex(r'^https?://example\.com/[a-z0-9-]+$', fullmatch=True),
    # npm with underscores (not allowed) - must have at least 2 chars with underscore
    st.from_regex(r'^npm:[a-z0-9]+_[a-z0-9_]+$', fullmatch=True),
)


# ============================================================================
# Property Tests
# ============================================================================

# Feature: library-management, Property 1: URI Parsing Correctness
@given(valid_uris)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_1_uri_parsing_correctness(uri: str):
    """
    Property 1: URI Parsing Correctness
    
    **Validates: Requirements 1.1, 1.2, 1.3**
    
    For any valid library URI (npm, PyPI, or Maven format), parsing the URI
    should correctly identify the registry type, extract the package name,
    and extract the version specifier (if present).
    
    This property ensures that all valid URIs can be parsed without errors
    and that the parsed components are non-empty and of the correct type.
    """
    parser = URIParser()
    
    # Should not raise an exception
    result = parser.parse(uri)
    
    # Registry type should be one of the valid types
    assert result.registry_type in [RegistryType.NPM, RegistryType.PYPI, RegistryType.MAVEN]
    
    # Package name should be non-empty
    assert result.package_name is not None
    assert len(result.package_name) > 0
    
    # Version can be None or non-empty string
    if result.version is not None:
        assert len(result.version) > 0
    
    # Raw URI should match input
    assert result.raw_uri == uri


# Feature: library-management, Property 2: Invalid URI Rejection
@given(invalid_uris)
@settings(max_examples=100)
def test_property_2_invalid_uri_rejection(invalid_uri: str):
    """
    Property 2: Invalid URI Rejection
    
    **Validates: Requirements 1.4**
    
    For any malformed or unrecognized library URI, the parser should reject it
    and return a descriptive error message indicating the specific validation failure.
    
    This property ensures that invalid URIs are consistently rejected and that
    error messages are always provided to help users understand what went wrong.
    """
    parser = URIParser()
    
    # validate_format should return False with an error message
    valid, error = parser.validate_format(invalid_uri)
    
    assert valid is False
    assert error is not None
    assert len(error) > 0
    assert isinstance(error, str)
    
    # parse should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        parser.parse(invalid_uri)
    
    # Error message should be descriptive
    error_message = str(exc_info.value)
    assert len(error_message) > 0


# Feature: library-management, Property 3: Parse-Validate Consistency
@given(st.text(min_size=1, max_size=200))
@settings(max_examples=100)
def test_property_3_parse_validate_consistency(uri: str):
    """
    Property 3: Parse-Validate Consistency
    
    **Validates: Requirements 1.1, 1.2, 1.4**
    
    For any URI string, the validate_format method should return True if and only if
    the parse method succeeds without raising an exception.
    
    This property ensures consistency between the two validation approaches.
    """
    parser = URIParser()
    
    valid, error = parser.validate_format(uri)
    
    if valid:
        # If validate_format says it's valid, parse should succeed
        try:
            result = parser.parse(uri)
            assert result is not None
            assert error is None
        except ValueError:
            # This should not happen - inconsistency detected
            pytest.fail(f"validate_format returned True but parse raised ValueError for URI: {uri}")
    else:
        # If validate_format says it's invalid, parse should raise ValueError
        assert error is not None
        with pytest.raises(ValueError):
            parser.parse(uri)


# Feature: library-management, Property 4: Registry Type Consistency
@given(valid_uris)
@settings(max_examples=100)
def test_property_4_registry_type_consistency(uri: str):
    """
    Property 4: Registry Type Consistency
    
    **Validates: Requirements 1.1, 1.5, 1.6, 1.7**
    
    For any valid URI, the registry type identified by parse() should match
    the registry type returned by get_registry_type(), and should be consistent
    with the URI prefix or domain.
    
    This property ensures that registry type detection is consistent across
    different methods and matches the URI format.
    """
    parser = URIParser()
    
    parsed = parser.parse(uri)
    registry_type = parser.get_registry_type(uri)
    
    # Registry types should match
    assert parsed.registry_type == registry_type
    
    # Registry type should match URI prefix/domain
    uri_lower = uri.lower()
    if uri_lower.startswith('npm:') or 'npmjs.com' in uri_lower:
        assert parsed.registry_type == RegistryType.NPM
    elif uri_lower.startswith('pypi:') or 'pypi.org' in uri_lower:
        assert parsed.registry_type == RegistryType.PYPI
    elif uri_lower.startswith('maven:'):
        assert parsed.registry_type == RegistryType.MAVEN


# Feature: library-management, Property 5: Whitespace Normalization
@given(valid_uris, st.text(min_size=0, max_size=5).filter(lambda s: s.isspace() or s == ""))
@settings(max_examples=100)
def test_property_5_whitespace_normalization(uri: str, whitespace: str):
    """
    Property 5: Whitespace Normalization
    
    **Validates: Requirements 1.1, 1.2**
    
    For any valid URI with leading or trailing whitespace, the parser should
    normalize the whitespace and parse the URI correctly, producing the same
    result as parsing the URI without whitespace.
    
    This property ensures that whitespace handling is consistent and user-friendly.
    """
    parser = URIParser()
    
    # Parse original URI
    original_result = parser.parse(uri)
    
    # Parse URI with leading whitespace
    if whitespace:
        uri_with_leading = whitespace + uri
        leading_result = parser.parse(uri_with_leading)
        assert leading_result.registry_type == original_result.registry_type
        assert leading_result.package_name == original_result.package_name
        assert leading_result.version == original_result.version
        
        # Parse URI with trailing whitespace
        uri_with_trailing = uri + whitespace
        trailing_result = parser.parse(uri_with_trailing)
        assert trailing_result.registry_type == original_result.registry_type
        assert trailing_result.package_name == original_result.package_name
        assert trailing_result.version == original_result.version
        
        # Parse URI with both leading and trailing whitespace
        uri_with_both = whitespace + uri + whitespace
        both_result = parser.parse(uri_with_both)
        assert both_result.registry_type == original_result.registry_type
        assert both_result.package_name == original_result.package_name
        assert both_result.version == original_result.version


# Feature: library-management, Property 6: Version Extraction Correctness
@given(
    st.one_of(
        st.builds(lambda pkg, ver: (f"npm:{pkg}@{ver}", ver), npm_package_names, semantic_versions),
        st.builds(lambda pkg, ver: (f"pypi:{pkg}=={ver}", ver), pypi_package_names, semantic_versions),
        st.builds(lambda grp, art, ver: (f"maven:{grp}:{art}:{ver}", ver), 
                  maven_group_ids, maven_artifact_ids, semantic_versions),
    )
)
@settings(max_examples=100)
def test_property_6_version_extraction_correctness(uri_and_version: tuple):
    """
    Property 6: Version Extraction Correctness
    
    **Validates: Requirements 1.3**
    
    For any URI with a version specifier, the parser should extract the exact
    version string that was included in the URI.
    
    This property ensures that version information is preserved accurately
    during parsing.
    """
    uri, expected_version = uri_and_version
    parser = URIParser()
    
    result = parser.parse(uri)
    
    # Version should match exactly
    assert result.version == expected_version


# Feature: library-management, Property 7: Package Name Extraction
@given(
    st.one_of(
        st.builds(lambda pkg: (f"npm:{pkg}", pkg), npm_package_names),
        st.builds(lambda pkg: (f"pypi:{pkg}", pkg), pypi_package_names),
        st.builds(lambda grp, art: (f"maven:{grp}:{art}", f"{grp}:{art}"), 
                  maven_group_ids, maven_artifact_ids),
    )
)
@settings(max_examples=100)
def test_property_7_package_name_extraction(uri_and_name: tuple):
    """
    Property 7: Package Name Extraction
    
    **Validates: Requirements 1.1, 1.2**
    
    For any URI, the parser should extract the package name correctly,
    preserving the exact format from the URI (including scopes for npm,
    and group:artifact format for Maven).
    
    This property ensures that package names are extracted accurately.
    """
    uri, expected_name = uri_and_name
    parser = URIParser()
    
    result = parser.parse(uri)
    
    # Package name should match exactly
    assert result.package_name == expected_name


# Feature: library-management, Property 8: Idempotent Parsing
@given(valid_uris)
@settings(max_examples=100)
def test_property_8_idempotent_parsing(uri: str):
    """
    Property 8: Idempotent Parsing
    
    **Validates: Requirements 1.1, 1.2, 1.3**
    
    For any valid URI, parsing it multiple times should always produce
    the same result.
    
    This property ensures that parsing is deterministic and consistent.
    """
    parser = URIParser()
    
    # Parse the URI multiple times
    result1 = parser.parse(uri)
    result2 = parser.parse(uri)
    result3 = parser.parse(uri)
    
    # All results should be identical
    assert result1.registry_type == result2.registry_type == result3.registry_type
    assert result1.package_name == result2.package_name == result3.package_name
    assert result1.version == result2.version == result3.version
    assert result1.raw_uri == result2.raw_uri == result3.raw_uri


# Feature: library-management, Property 9: Error Message Non-Empty
@given(invalid_uris)
@settings(max_examples=100)
def test_property_9_error_message_non_empty(invalid_uri: str):
    """
    Property 9: Error Message Non-Empty
    
    **Validates: Requirements 1.4**
    
    For any invalid URI, the error message returned should be non-empty
    and contain useful information about why the URI is invalid.
    
    This property ensures that error messages are always helpful.
    """
    parser = URIParser()
    
    valid, error = parser.validate_format(invalid_uri)
    
    if not valid:
        assert error is not None
        assert len(error) > 0
        # Error message should contain some indication of the problem
        assert any(keyword in error.lower() for keyword in 
                   ['invalid', 'format', 'empty', 'expected', 'cannot'])

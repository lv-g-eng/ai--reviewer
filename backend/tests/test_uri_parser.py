"""
Unit tests for URI Parser Service

Tests specific URI format examples, edge cases, and error conditions.
"""

import pytest
from app.services.library_management.uri_parser import URIParser
from app.models.library import RegistryType
from app.schemas.library import ParsedURI


class TestNPMURIParsing:
    """Test npm URI format parsing"""
    
    def test_npm_simple_package(self):
        """Test parsing simple npm package without version"""
        parser = URIParser()
        result = parser.parse("npm:react")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version is None
        assert result.raw_uri == "npm:react"
    
    def test_npm_package_with_version(self):
        """Test parsing npm package with version"""
        parser = URIParser()
        result = parser.parse("npm:react@18.0.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version == "18.0.0"
        assert result.raw_uri == "npm:react@18.0.0"
    
    def test_npm_scoped_package(self):
        """Test parsing npm scoped package"""
        parser = URIParser()
        result = parser.parse("npm:@types/node@18.0.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "@types/node"
        assert result.version == "18.0.0"
    
    def test_npm_scoped_package_without_version(self):
        """Test parsing npm scoped package without version"""
        parser = URIParser()
        result = parser.parse("npm:@babel/core")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "@babel/core"
        assert result.version is None
    
    def test_npm_url_format(self):
        """Test parsing npm URL format"""
        parser = URIParser()
        result = parser.parse("https://npmjs.com/package/react")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version is None
    
    def test_npm_url_with_version(self):
        """Test parsing npm URL with version"""
        parser = URIParser()
        result = parser.parse("https://npmjs.com/package/react/v/18.0.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version == "18.0.0"
    
    def test_npm_url_with_www(self):
        """Test parsing npm URL with www prefix"""
        parser = URIParser()
        result = parser.parse("https://www.npmjs.com/package/lodash")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "lodash"
        assert result.version is None
    
    def test_npm_package_with_hyphens(self):
        """Test parsing npm package with hyphens"""
        parser = URIParser()
        result = parser.parse("npm:react-dom@18.0.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react-dom"
        assert result.version == "18.0.0"
    
    def test_npm_semantic_version_caret(self):
        """Test parsing npm package with caret version"""
        parser = URIParser()
        result = parser.parse("npm:express@^4.18.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "express"
        assert result.version == "^4.18.0"
    
    def test_npm_semantic_version_tilde(self):
        """Test parsing npm package with tilde version"""
        parser = URIParser()
        result = parser.parse("npm:lodash@~4.17.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "lodash"
        assert result.version == "~4.17.0"


class TestPyPIURIParsing:
    """Test PyPI URI format parsing"""
    
    def test_pypi_simple_package(self):
        """Test parsing simple PyPI package without version"""
        parser = URIParser()
        result = parser.parse("pypi:django")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "django"
        assert result.version is None
        assert result.raw_uri == "pypi:django"
    
    def test_pypi_package_with_version(self):
        """Test parsing PyPI package with version"""
        parser = URIParser()
        result = parser.parse("pypi:django==4.2.0")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "django"
        assert result.version == "4.2.0"
    
    def test_pypi_package_with_hyphens(self):
        """Test parsing PyPI package with hyphens"""
        parser = URIParser()
        result = parser.parse("pypi:scikit-learn==1.3.0")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "scikit-learn"
        assert result.version == "1.3.0"
    
    def test_pypi_package_with_underscores(self):
        """Test parsing PyPI package with underscores"""
        parser = URIParser()
        result = parser.parse("pypi:python_dateutil==2.8.2")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "python_dateutil"
        assert result.version == "2.8.2"
    
    def test_pypi_package_with_dots(self):
        """Test parsing PyPI package with dots"""
        parser = URIParser()
        result = parser.parse("pypi:zope.interface==5.4.0")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "zope.interface"
        assert result.version == "5.4.0"
    
    def test_pypi_url_format(self):
        """Test parsing PyPI URL format"""
        parser = URIParser()
        result = parser.parse("https://pypi.org/project/django")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "django"
        assert result.version is None
    
    def test_pypi_url_with_version(self):
        """Test parsing PyPI URL with version"""
        parser = URIParser()
        result = parser.parse("https://pypi.org/project/django/4.2.0")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "django"
        assert result.version == "4.2.0"
    
    def test_pypi_http_url(self):
        """Test parsing PyPI HTTP URL (not HTTPS)"""
        parser = URIParser()
        result = parser.parse("http://pypi.org/project/requests")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "requests"
        assert result.version is None


class TestMavenURIParsing:
    """Test Maven URI format parsing"""
    
    def test_maven_simple_coordinates(self):
        """Test parsing Maven coordinates without version"""
        parser = URIParser()
        result = parser.parse("maven:org.springframework:spring-core")
        
        assert result.registry_type == RegistryType.MAVEN
        assert result.package_name == "org.springframework:spring-core"
        assert result.version is None
    
    def test_maven_coordinates_with_version(self):
        """Test parsing Maven coordinates with version"""
        parser = URIParser()
        result = parser.parse("maven:org.springframework:spring-core:5.3.0")
        
        assert result.registry_type == RegistryType.MAVEN
        assert result.package_name == "org.springframework:spring-core"
        assert result.version == "5.3.0"
    
    def test_maven_simple_group(self):
        """Test parsing Maven with simple group ID"""
        parser = URIParser()
        result = parser.parse("maven:junit:junit:4.13.2")
        
        assert result.registry_type == RegistryType.MAVEN
        assert result.package_name == "junit:junit"
        assert result.version == "4.13.2"
    
    def test_maven_complex_group(self):
        """Test parsing Maven with complex group ID"""
        parser = URIParser()
        result = parser.parse("maven:com.google.guava:guava:31.0-jre")
        
        assert result.registry_type == RegistryType.MAVEN
        assert result.package_name == "com.google.guava:guava"
        assert result.version == "31.0-jre"


class TestInvalidURIs:
    """Test invalid URI handling"""
    
    def test_empty_uri(self):
        """Test that empty URI raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="URI cannot be empty"):
            parser.parse("")
    
    def test_whitespace_uri(self):
        """Test that whitespace-only URI raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="URI cannot be empty"):
            parser.parse("   ")
    
    def test_invalid_prefix(self):
        """Test that invalid prefix raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="Invalid URI format"):
            parser.parse("invalid:package-name")
    
    def test_malformed_npm_uri(self):
        """Test that malformed npm URI raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="Invalid URI format"):
            parser.parse("npm:")
    
    def test_malformed_pypi_uri(self):
        """Test that malformed PyPI URI raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="Invalid URI format"):
            parser.parse("pypi:")
    
    def test_malformed_maven_uri(self):
        """Test that malformed Maven URI raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="Invalid URI format"):
            parser.parse("maven:group")
    
    def test_invalid_url(self):
        """Test that invalid URL raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="Invalid URI format"):
            parser.parse("https://example.com/package")
    
    def test_npm_with_invalid_characters(self):
        """Test that npm package with invalid characters raises ValueError"""
        parser = URIParser()
        with pytest.raises(ValueError, match="Invalid URI format"):
            parser.parse("npm:package_name")  # npm doesn't allow underscores


class TestValidateFormat:
    """Test validate_format method"""
    
    def test_valid_npm_uri(self):
        """Test that valid npm URI returns True"""
        parser = URIParser()
        valid, error = parser.validate_format("npm:react@18.0.0")
        
        assert valid is True
        assert error is None
    
    def test_valid_pypi_uri(self):
        """Test that valid PyPI URI returns True"""
        parser = URIParser()
        valid, error = parser.validate_format("pypi:django==4.2.0")
        
        assert valid is True
        assert error is None
    
    def test_invalid_uri_returns_error(self):
        """Test that invalid URI returns False with error message"""
        parser = URIParser()
        valid, error = parser.validate_format("invalid:format")
        
        assert valid is False
        assert error is not None
        assert "Invalid URI format" in error
    
    def test_empty_uri_returns_error(self):
        """Test that empty URI returns False with error message"""
        parser = URIParser()
        valid, error = parser.validate_format("")
        
        assert valid is False
        assert error is not None
        assert "cannot be empty" in error


class TestGetRegistryType:
    """Test get_registry_type convenience method"""
    
    def test_npm_registry_type(self):
        """Test getting registry type for npm URI"""
        parser = URIParser()
        registry_type = parser.get_registry_type("npm:react")
        
        assert registry_type == RegistryType.NPM
    
    def test_pypi_registry_type(self):
        """Test getting registry type for PyPI URI"""
        parser = URIParser()
        registry_type = parser.get_registry_type("pypi:django")
        
        assert registry_type == RegistryType.PYPI
    
    def test_maven_registry_type(self):
        """Test getting registry type for Maven URI"""
        parser = URIParser()
        registry_type = parser.get_registry_type("maven:junit:junit:4.13.2")
        
        assert registry_type == RegistryType.MAVEN
    
    def test_invalid_uri_returns_none(self):
        """Test that invalid URI returns None"""
        parser = URIParser()
        registry_type = parser.get_registry_type("invalid:format")
        
        assert registry_type is None


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_uri_with_leading_whitespace(self):
        """Test that URI with leading whitespace is handled"""
        parser = URIParser()
        result = parser.parse("  npm:react@18.0.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version == "18.0.0"
    
    def test_uri_with_trailing_whitespace(self):
        """Test that URI with trailing whitespace is handled"""
        parser = URIParser()
        result = parser.parse("npm:react@18.0.0  ")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version == "18.0.0"
    
    def test_case_insensitive_npm_prefix(self):
        """Test that npm prefix is case-insensitive"""
        parser = URIParser()
        result = parser.parse("NPM:react")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
    
    def test_case_insensitive_pypi_prefix(self):
        """Test that pypi prefix is case-insensitive"""
        parser = URIParser()
        result = parser.parse("PYPI:django")
        
        assert result.registry_type == RegistryType.PYPI
        assert result.package_name == "django"
    
    def test_version_with_prerelease(self):
        """Test parsing version with prerelease tag"""
        parser = URIParser()
        result = parser.parse("npm:react@18.0.0-rc.1")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version == "18.0.0-rc.1"
    
    def test_version_with_build_metadata(self):
        """Test parsing version with build metadata"""
        parser = URIParser()
        result = parser.parse("npm:react@18.0.0+build.123")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "react"
        assert result.version == "18.0.0+build.123"
    
    def test_very_long_package_name(self):
        """Test parsing very long package name"""
        parser = URIParser()
        long_name = "a" * 100
        result = parser.parse(f"npm:{long_name}")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == long_name
    
    def test_numeric_package_name(self):
        """Test parsing package name with numbers"""
        parser = URIParser()
        result = parser.parse("npm:vue3@3.0.0")
        
        assert result.registry_type == RegistryType.NPM
        assert result.package_name == "vue3"
        assert result.version == "3.0.0"

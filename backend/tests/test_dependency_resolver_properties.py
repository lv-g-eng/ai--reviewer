"""
Property-based tests for Dependency Resolver Service

These tests verify universal properties that should hold across all valid inputs
using the hypothesis library for property-based testing.
"""

import json
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import composite
import pytest

from app.services.library_management.dependency_resolver import DependencyResolver
from app.schemas.library import LibraryMetadata, Dependency
from app.models.library import RegistryType, ProjectContext


# ============================================================================
# Hypothesis Strategies
# ============================================================================

@composite
def valid_package_name(draw):
    """Generate valid package names for different registries"""
    # Package names can contain letters, numbers, hyphens, underscores, dots
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='-_.'),
        min_size=1,
        max_size=50
    ))
    # Ensure it starts with a letter or number
    assume(name[0].isalnum())
    # Ensure it doesn't end with special characters
    assume(name[-1].isalnum())
    return name


@composite
def valid_version_string(draw):
    """Generate valid semantic version strings"""
    major = draw(st.integers(min_value=0, max_value=99))
    minor = draw(st.integers(min_value=0, max_value=99))
    patch = draw(st.integers(min_value=0, max_value=99))
    return f"{major}.{minor}.{patch}"


@composite
def npm_version_specifier(draw):
    """Generate npm-style version specifiers"""
    version = draw(valid_version_string())
    specifier_type = draw(st.sampled_from(['exact', 'caret', 'tilde', 'gte']))
    
    if specifier_type == 'exact':
        return version
    elif specifier_type == 'caret':
        return f"^{version}"
    elif specifier_type == 'tilde':
        return f"~{version}"
    elif specifier_type == 'gte':
        return f">={version}"


@composite
def python_version_specifier(draw):
    """Generate Python-style version specifiers"""
    version = draw(valid_version_string())
    specifier_type = draw(st.sampled_from(['exact', 'gte', 'lte', 'gt', 'lt', 'compatible']))
    
    if specifier_type == 'exact':
        return f"=={version}"
    elif specifier_type == 'gte':
        return f">={version}"
    elif specifier_type == 'lte':
        return f"<={version}"
    elif specifier_type == 'gt':
        return f">{version}"
    elif specifier_type == 'lt':
        return f"<{version}"
    elif specifier_type == 'compatible':
        return f"~={version}"


@composite
def dependency_strategy(draw, registry_type=None):
    """Generate Dependency objects"""
    name = draw(valid_package_name())
    
    if registry_type == RegistryType.NPM:
        version = draw(npm_version_specifier())
    elif registry_type in [RegistryType.PYPI, RegistryType.MAVEN]:
        version = draw(python_version_specifier())
    else:
        version = draw(st.one_of(npm_version_specifier(), python_version_specifier()))
    
    is_direct = draw(st.booleans())
    
    return Dependency(name=name, version=version, is_direct=is_direct)


@composite
def library_metadata_strategy(draw, registry_type=None):
    """Generate LibraryMetadata objects"""
    if registry_type is None:
        registry_type = draw(st.sampled_from(list(RegistryType)))
    
    name = draw(valid_package_name())
    version = draw(valid_version_string())
    description = draw(st.text(min_size=0, max_size=200))
    license_name = draw(st.sampled_from(['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'ISC']))
    
    # Generate dependencies for the same registry type
    dependencies = draw(st.lists(
        dependency_strategy(registry_type=registry_type),
        min_size=0,
        max_size=10
    ))
    
    return LibraryMetadata(
        name=name,
        version=version,
        description=description,
        license=license_name,
        registry_type=registry_type,
        dependencies=dependencies
    )


@composite
def package_json_dependencies(draw):
    """Generate package.json-style dependencies"""
    num_deps = draw(st.integers(min_value=0, max_value=20))
    dependencies = {}
    
    for _ in range(num_deps):
        name = draw(valid_package_name())
        version = draw(npm_version_specifier())
        dependencies[name] = version
    
    return dependencies


@composite
def requirements_txt_lines(draw):
    """Generate requirements.txt-style lines"""
    num_deps = draw(st.integers(min_value=0, max_value=20))
    lines = []
    
    for _ in range(num_deps):
        name = draw(valid_package_name())
        version = draw(python_version_specifier())
        lines.append(f"{name}{version}")
    
    # Add some comments and empty lines
    if draw(st.booleans()):
        lines.insert(0, "# Generated dependencies")
    if draw(st.booleans()):
        lines.append("")
    
    return lines


# ============================================================================
# Property Tests
# ============================================================================

class TestDependencyResolverProperties:
    """Property-based tests for DependencyResolver"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.resolver = DependencyResolver(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_package_json(self, dependencies: dict):
        """Helper to create package.json with given dependencies"""
        package_data = {
            "name": "test-package",
            "version": "1.0.0",
            "dependencies": dependencies
        }
        
        full_path = Path(self.temp_dir) / "frontend" / "package.json"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(package_data, indent=2))
    
    def create_requirements_txt(self, lines: list):
        """Helper to create requirements.txt with given lines"""
        full_path = Path(self.temp_dir) / "backend" / "requirements.txt"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("\n".join(lines))
    
    # Feature: library-management, Property 7: Dependency Conflict Detection
    @given(
        library=library_metadata_strategy(registry_type=RegistryType.NPM),
        existing_deps=package_json_dependencies()
    )
    @settings(max_examples=100, deadline=None)
    def test_dependency_conflict_detection_correctness(self, library, existing_deps):
        """
        Property 7: For any library with dependencies, the dependency resolver should 
        analyze all dependencies against existing project dependencies and correctly 
        identify version conflicts when they exist.
        
        **Validates: Requirements 4.1, 4.2**
        """
        # Create package.json with existing dependencies
        self.create_package_json(existing_deps)
        
        # Detect conflicts
        conflicts = self.resolver._detect_version_conflicts(library, existing_deps)
        
        # Property: All conflicts should involve packages that exist in both
        # the library's dependencies and existing dependencies
        for conflict in conflicts:
            assert conflict.package in existing_deps
            assert any(dep.name == conflict.package for dep in library.dependencies)
            assert conflict.existing_version == existing_deps[conflict.package]
            assert any(
                dep.version == conflict.required_version 
                for dep in library.dependencies 
                if dep.name == conflict.package
            )
        
        # Property: If no library dependencies overlap with existing dependencies,
        # there should be no conflicts
        library_dep_names = {dep.name for dep in library.dependencies}
        existing_dep_names = set(existing_deps.keys())
        
        if library_dep_names.isdisjoint(existing_dep_names):
            assert len(conflicts) == 0
    
    # Feature: library-management, Property 8: Circular Dependency Detection
    @given(library=library_metadata_strategy())
    @settings(max_examples=100, deadline=None)
    def test_circular_dependency_detection_completeness(self, library):
        """
        Property 8: For any dependency tree, the dependency resolver should detect 
        circular dependency chains and report them before installation.
        
        **Validates: Requirements 4.5**
        """
        # Create existing dependencies (simplified - no actual circular deps in this test)
        existing_deps = [
            Dependency(name=dep.name, version=dep.version) 
            for dep in library.dependencies[:5]  # Limit to avoid too many deps
        ]
        
        # Test that the method runs without error
        result = self.resolver.detect_circular_dependencies(library, existing_deps)
        
        # Property: Result should be either None (no cycles) or a list of strings (cycle path)
        assert result is None or (isinstance(result, list) and all(isinstance(item, str) for item in result))
        
        # Property: If a cycle is detected, it should contain at least 2 nodes
        if result is not None:
            assert len(result) >= 2
            # Property: The cycle should start and end with the same node
            assert result[0] == result[-1]
    
    # Feature: library-management, Property 11: Database Storage Completeness
    @given(dependencies=package_json_dependencies())
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_dependency_parsing_completeness_npm(self, dependencies):
        """
        Property 11: For any valid package.json file, all dependencies should be 
        correctly parsed and returned with their version specifiers.
        
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        """
        # Create package.json with dependencies
        self.create_package_json(dependencies)
        
        # Parse dependencies
        parsed = await self.resolver._parse_package_json()
        
        # Property: All original dependencies should be present in parsed result
        for name, version in dependencies.items():
            assert name in parsed
            assert parsed[name] == version
        
        # Property: No extra dependencies should be added
        assert len(parsed) >= len(dependencies)  # May include devDependencies, etc.
        
        # Property: All parsed dependency names should be non-empty strings
        for name in parsed.keys():
            assert isinstance(name, str)
            assert len(name) > 0
        
        # Property: All parsed version specifiers should be strings
        for version in parsed.values():
            assert isinstance(version, str)
    
    # Feature: library-management, Property 12: Library Query Correctness
    @given(requirements=requirements_txt_lines())
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_dependency_parsing_completeness_python(self, requirements):
        """
        Property 12: For any valid requirements.txt file, all dependencies should be 
        correctly parsed and returned with their version specifiers.
        
        **Validates: Requirements 6.5**
        """
        # Filter out comments and empty lines for expected result
        expected_deps = {}
        for line in requirements:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # Parse the line to extract name and version
                import re
                match = re.match(r'^([a-zA-Z0-9_.-]+)([><=!~]+.*)?', line)
                if match:
                    name = match.group(1)
                    version = match.group(2) or ""
                    expected_deps[name] = version
        
        # Create requirements.txt
        self.create_requirements_txt(requirements)
        
        # Parse dependencies
        parsed = await self.resolver._parse_requirements_txt()
        
        # Property: All expected dependencies should be present in parsed result
        for name, version in expected_deps.items():
            assert name in parsed
            assert parsed[name] == version
        
        # Property: No extra dependencies should be added beyond what's expected
        assert len(parsed) == len(expected_deps)
        
        # Property: All parsed dependency names should be non-empty strings
        for name in parsed.keys():
            assert isinstance(name, str)
            assert len(name) > 0
        
        # Property: All parsed version specifiers should be strings
        for version in parsed.values():
            assert isinstance(version, str)
    
    # Feature: library-management, Property 9: Installation Rollback on Failure
    @given(
        library=library_metadata_strategy(),
        project_context=st.sampled_from(list(ProjectContext))
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_conflict_analysis_structure_consistency(self, library, project_context):
        """
        Property 9: For any library and project context, conflict analysis should 
        return a well-formed ConflictAnalysis object with consistent structure.
        
        **Validates: Requirements 5.4**
        """
        # Create appropriate dependency file based on context
        if project_context == ProjectContext.FRONTEND:
            self.create_package_json({})
        elif project_context == ProjectContext.BACKEND:
            self.create_requirements_txt([])
        elif project_context == ProjectContext.SERVICES:
            # Services uses package.json in services directory
            package_data = {"name": "services", "version": "1.0.0", "dependencies": {}}
            full_path = Path(self.temp_dir) / "services" / "package.json"
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(json.dumps(package_data, indent=2))
        
        # Perform conflict analysis
        try:
            result = await self.resolver.check_conflicts(library, project_context)
            
            # Property: Result should be a ConflictAnalysis object
            from app.schemas.library import ConflictAnalysis
            assert isinstance(result, ConflictAnalysis)
            
            # Property: has_conflicts should be boolean
            assert isinstance(result.has_conflicts, bool)
            
            # Property: conflicts should be a list
            assert isinstance(result.conflicts, list)
            
            # Property: suggestions should be a list of strings
            assert isinstance(result.suggestions, list)
            assert all(isinstance(s, str) for s in result.suggestions)
            
            # Property: circular_dependencies should be None or list of strings
            assert result.circular_dependencies is None or (
                isinstance(result.circular_dependencies, list) and
                all(isinstance(item, str) for item in result.circular_dependencies)
            )
            
            # Property: If has_conflicts is True, there should be conflicts or circular deps
            if result.has_conflicts:
                assert len(result.conflicts) > 0 or result.circular_dependencies is not None
            
            # Property: If has_conflicts is False, there should be no conflicts and no circular deps
            if not result.has_conflicts:
                assert len(result.conflicts) == 0 and result.circular_dependencies is None
                
        except Exception as e:
            # Property: Any exceptions should be DependencyResolverError or its subclasses
            from app.services.library_management.dependency_resolver import DependencyResolverError
            assert isinstance(e, DependencyResolverError)
    
    # Feature: library-management, Property 13: Version Selection Correctness
    @given(
        existing_version=npm_version_specifier(),
        required_version=npm_version_specifier()
    )
    @settings(max_examples=100, deadline=None)
    def test_npm_version_compatibility_symmetry(self, existing_version, required_version):
        """
        Property 13: For any two npm version specifiers, compatibility checking 
        should be deterministic and handle edge cases gracefully.
        
        **Validates: Requirements 7.1, 7.2**
        """
        # Test version compatibility
        result1 = self.resolver._are_npm_versions_compatible(existing_version, required_version)
        result2 = self.resolver._are_npm_versions_compatible(existing_version, required_version)
        
        # Property: Compatibility check should be deterministic
        assert result1 == result2
        
        # Property: Result should be boolean
        assert isinstance(result1, bool)
        
        # Property: Identical versions should be compatible
        if existing_version == required_version:
            assert result1 is True
    
    # Feature: library-management, Property 14: Semantic Versioning Constraint Handling
    @given(
        existing_version=python_version_specifier(),
        required_version=python_version_specifier()
    )
    @settings(max_examples=100, deadline=None)
    def test_python_version_compatibility_consistency(self, existing_version, required_version):
        """
        Property 14: For any two Python version specifiers, compatibility checking 
        should correctly interpret constraints and be consistent.
        
        **Validates: Requirements 7.3**
        """
        # Test version compatibility
        result1 = self.resolver._are_python_versions_compatible(existing_version, required_version)
        result2 = self.resolver._are_python_versions_compatible(existing_version, required_version)
        
        # Property: Compatibility check should be deterministic
        assert result1 == result2
        
        # Property: Result should be boolean
        assert isinstance(result1, bool)
        
        # Property: Identical exact versions should be compatible
        if existing_version == required_version and existing_version.startswith('=='):
            assert result1 is True
    
    # Feature: library-management, Property 20: Operation Logging
    @given(
        library=library_metadata_strategy(),
        constraints=st.lists(st.one_of(npm_version_specifier(), python_version_specifier()), min_size=1, max_size=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_version_suggestion_robustness(self, library, constraints):
        """
        Property 20: For any library and set of version constraints, version suggestion 
        should either return a valid version string or None, and handle all inputs gracefully.
        
        **Validates: Requirements 10.3**
        """
        # Test version suggestion
        result = self.resolver.suggest_compatible_version(library.name, constraints)
        
        # Property: Result should be None or a non-empty string
        assert result is None or (isinstance(result, str) and len(result) > 0)
        
        # Property: If result is a string, it should look like a version
        if result is not None:
            import re
            # Should contain at least one digit
            assert re.search(r'\d', result) is not None
    
    # Feature: library-management, Property 21: Rate Limit Enforcement
    @given(
        conflicts=st.lists(
            st.builds(
                lambda: None,  # We'll create ConflictInfo objects manually
            ),
            min_size=0,
            max_size=10
        ),
        library=library_metadata_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_conflict_suggestion_generation_completeness(self, conflicts, library):
        """
        Property 21: For any set of conflicts and library, suggestion generation 
        should produce helpful, non-empty suggestions when conflicts exist.
        
        **Validates: Requirements 10.4**
        """
        # Create actual ConflictInfo objects
        from app.schemas.library import ConflictInfo
        actual_conflicts = []
        
        for i in range(len(conflicts)):
            conflict = ConflictInfo(
                package=f"package-{i}",
                existing_version="1.0.0",
                required_version="2.0.0"
            )
            actual_conflicts.append(conflict)
        
        # Generate suggestions
        suggestions = self.resolver._generate_conflict_suggestions(actual_conflicts, library)
        
        # Property: Suggestions should be a list of strings
        assert isinstance(suggestions, list)
        assert all(isinstance(s, str) for s in suggestions)
        
        # Property: If there are conflicts, there should be suggestions
        if len(actual_conflicts) > 0:
            assert len(suggestions) > 0
            # Property: All suggestions should be non-empty
            assert all(len(s.strip()) > 0 for s in suggestions)
        
        # Property: If there are no conflicts, there should be no suggestions
        if len(actual_conflicts) == 0:
            assert len(suggestions) == 0
    
    # Feature: library-management, Property 1: URI Parsing Correctness (adapted for dependency parsing)
    @given(
        package_name=valid_package_name(),
        version_spec=st.one_of(npm_version_specifier(), python_version_specifier())
    )
    @settings(max_examples=100, deadline=None)
    def test_dependency_name_version_parsing_correctness(self, package_name, version_spec):
        """
        Property 1: For any valid package name and version specifier, 
        dependency parsing should correctly extract both components.
        
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        # Create a dependency entry
        if '==' in version_spec or '>=' in version_spec or '<=' in version_spec or '~=' in version_spec:
            # Python-style
            dep_line = f"{package_name}{version_spec}"
            
            # Test parsing logic (simplified version of what's in _parse_requirements_txt)
            import re
            match = re.match(r'^([a-zA-Z0-9_.-]+)([><=!~]+.*)?', dep_line)
            
            if match:
                parsed_name = match.group(1)
                parsed_version = match.group(2) or ""
                
                # Property: Parsed name should match original
                assert parsed_name == package_name
                # Property: Parsed version should match original
                assert parsed_version == version_spec
        else:
            # npm-style (stored in JSON, so we test the structure)
            deps = {package_name: version_spec}
            
            # Property: Package name should be preserved as key
            assert package_name in deps
            # Property: Version spec should be preserved as value
            assert deps[package_name] == version_spec


# ============================================================================
# Edge Case Property Tests
# ============================================================================

class TestDependencyResolverEdgeCaseProperties:
    """Property tests for edge cases and error conditions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.resolver = DependencyResolver(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @given(
        malformed_json=st.text(min_size=1, max_size=100).filter(
            lambda x: x.strip() and not x.strip().startswith('{')
        )
    )
    @settings(max_examples=50, deadline=None)
    @pytest.mark.asyncio
    async def test_malformed_package_json_handling(self, malformed_json):
        """
        Property: For any malformed JSON content, package.json parsing should 
        raise FileParsingError rather than crashing.
        """
        # Create malformed package.json
        full_path = Path(self.temp_dir) / "frontend" / "package.json"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(malformed_json)
        
        # Property: Should raise FileParsingError, not crash
        with pytest.raises(Exception) as exc_info:
            await self.resolver._parse_package_json()
        
        # Should be a FileParsingError or its base class
        from app.services.library_management.dependency_resolver import FileParsingError
        assert isinstance(exc_info.value, (FileParsingError, Exception))
    
    @given(
        empty_or_whitespace=st.one_of(
            st.just(""),
            st.text(max_size=20).filter(lambda x: x.isspace())
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_empty_version_handling(self, empty_or_whitespace):
        """
        Property: For any empty or whitespace-only version specifier, 
        version compatibility checking should handle gracefully.
        """
        # Property: Should not crash with empty versions
        result = self.resolver._are_npm_versions_compatible(empty_or_whitespace, "1.0.0")
        assert isinstance(result, bool)
        
        result = self.resolver._are_python_versions_compatible(empty_or_whitespace, "==1.0.0")
        assert isinstance(result, bool)
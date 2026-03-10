"""
Unit tests for Context Detector Service
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from app.services.library_management.context_detector import (
    ContextDetector
)
from app.models.library import RegistryType, ProjectContext


class TestContextDetector:
    """Test cases for ContextDetector class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.detector = ContextDetector(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_config_file(self, relative_path: str, content: str = "{}"):
        """Helper method to create configuration files"""
        full_path = Path(self.temp_dir) / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return full_path
    
    # ========================================================================
    # Test detect_context method
    # ========================================================================
    
    def test_detect_context_npm_returns_frontend(self):
        """Test that npm registry type maps to frontend context"""
        context = self.detector.detect_context(RegistryType.NPM)
        assert context == ProjectContext.FRONTEND
    
    def test_detect_context_pypi_returns_backend(self):
        """Test that pypi registry type maps to backend context"""
        context = self.detector.detect_context(RegistryType.PYPI)
        assert context == ProjectContext.BACKEND
    
    def test_detect_context_maven_returns_backend(self):
        """Test that maven registry type maps to backend context"""
        context = self.detector.detect_context(RegistryType.MAVEN)
        assert context == ProjectContext.BACKEND
    
    def test_detect_context_unsupported_registry_raises_error(self):
        """Test that unsupported registry type raises ValueError"""
        # Create a mock registry type that's not in the map
        with patch('app.models.library.RegistryType') as mock_registry:
            mock_registry.UNSUPPORTED = "unsupported"
            
            with pytest.raises(ValueError, match="Unsupported registry type"):
                self.detector.detect_context("unsupported")
    
    # ========================================================================
    # Test validate_context method
    # ========================================================================
    
    def test_validate_context_frontend_with_existing_package_json(self):
        """Test frontend context validation with existing package.json"""
        # Create frontend/package.json
        self.create_config_file("frontend/package.json", '{"name": "test-frontend"}')
        
        is_valid, error = self.detector.validate_context(ProjectContext.FRONTEND)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_context_frontend_without_package_json(self):
        """Test frontend context validation without package.json"""
        is_valid, error = self.detector.validate_context(ProjectContext.FRONTEND)
        
        assert is_valid is False
        assert error == "Configuration file not found: frontend/package.json"
    
    def test_validate_context_backend_with_existing_requirements_txt(self):
        """Test backend context validation with existing requirements.txt"""
        # Create backend/requirements.txt
        self.create_config_file("backend/requirements.txt", "django==4.2.0\npsycopg2==2.9.0")
        
        is_valid, error = self.detector.validate_context(ProjectContext.BACKEND)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_context_backend_without_requirements_txt(self):
        """Test backend context validation without requirements.txt"""
        is_valid, error = self.detector.validate_context(ProjectContext.BACKEND)
        
        assert is_valid is False
        assert error == "Configuration file not found: backend/requirements.txt"
    
    def test_validate_context_services_with_existing_package_json(self):
        """Test services context validation with existing package.json"""
        # Create services/package.json
        self.create_config_file("services/package.json", '{"name": "test-services"}')
        
        is_valid, error = self.detector.validate_context(ProjectContext.SERVICES)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_context_services_without_package_json(self):
        """Test services context validation without package.json"""
        is_valid, error = self.detector.validate_context(ProjectContext.SERVICES)
        
        assert is_valid is False
        assert error == "Configuration file not found: services/package.json"
    
    def test_validate_context_with_directory_instead_of_file(self):
        """Test validation fails when config path is a directory"""
        # Create frontend directory but not the package.json file
        frontend_dir = Path(self.temp_dir) / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a directory with the same name as the expected file
        package_json_dir = frontend_dir / "package.json"
        package_json_dir.mkdir()
        
        is_valid, error = self.detector.validate_context(ProjectContext.FRONTEND)
        
        assert is_valid is False
        assert "Configuration path exists but is not a file" in error
    
    # ========================================================================
    # Test get_config_file_path method
    # ========================================================================
    
    def test_get_config_file_path_frontend(self):
        """Test getting config file path for frontend context"""
        path = self.detector.get_config_file_path(ProjectContext.FRONTEND)
        assert path == "frontend/package.json"
    
    def test_get_config_file_path_backend(self):
        """Test getting config file path for backend context"""
        path = self.detector.get_config_file_path(ProjectContext.BACKEND)
        assert path == "backend/requirements.txt"
    
    def test_get_config_file_path_services(self):
        """Test getting config file path for services context"""
        path = self.detector.get_config_file_path(ProjectContext.SERVICES)
        assert path == "services/package.json"
    
    # ========================================================================
    # Test get_absolute_config_path method
    # ========================================================================
    
    def test_get_absolute_config_path_frontend(self):
        """Test getting absolute config file path for frontend context"""
        abs_path = self.detector.get_absolute_config_path(ProjectContext.FRONTEND)
        expected_path = Path(self.temp_dir) / "frontend" / "package.json"
        assert abs_path == expected_path
    
    def test_get_absolute_config_path_backend(self):
        """Test getting absolute config file path for backend context"""
        abs_path = self.detector.get_absolute_config_path(ProjectContext.BACKEND)
        expected_path = Path(self.temp_dir) / "backend" / "requirements.txt"
        assert abs_path == expected_path
    
    # ========================================================================
    # Test detect_and_validate_context method
    # ========================================================================
    
    def test_detect_and_validate_context_npm_with_valid_frontend(self):
        """Test detect and validate for npm with valid frontend setup"""
        # Create frontend/package.json
        self.create_config_file("frontend/package.json", '{"name": "test-frontend"}')
        
        context, is_valid, error = self.detector.detect_and_validate_context(RegistryType.NPM)
        
        assert context == ProjectContext.FRONTEND
        assert is_valid is True
        assert error is None
    
    def test_detect_and_validate_context_npm_without_frontend(self):
        """Test detect and validate for npm without frontend setup"""
        context, is_valid, error = self.detector.detect_and_validate_context(RegistryType.NPM)
        
        assert context == ProjectContext.FRONTEND
        assert is_valid is False
        assert error == "Configuration file not found: frontend/package.json"
    
    def test_detect_and_validate_context_pypi_with_valid_backend(self):
        """Test detect and validate for pypi with valid backend setup"""
        # Create backend/requirements.txt
        self.create_config_file("backend/requirements.txt", "django==4.2.0")
        
        context, is_valid, error = self.detector.detect_and_validate_context(RegistryType.PYPI)
        
        assert context == ProjectContext.BACKEND
        assert is_valid is True
        assert error is None
    
    def test_detect_and_validate_context_pypi_without_backend(self):
        """Test detect and validate for pypi without backend setup"""
        context, is_valid, error = self.detector.detect_and_validate_context(RegistryType.PYPI)
        
        assert context == ProjectContext.BACKEND
        assert is_valid is False
        assert error == "Configuration file not found: backend/requirements.txt"
    
    # ========================================================================
    # Test list_available_contexts method
    # ========================================================================
    
    def test_list_available_contexts_all_valid(self):
        """Test listing contexts when all are valid"""
        # Create all config files
        self.create_config_file("frontend/package.json", '{"name": "frontend"}')
        self.create_config_file("backend/requirements.txt", "django==4.2.0")
        self.create_config_file("services/package.json", '{"name": "services"}')
        
        contexts = self.detector.list_available_contexts()
        
        assert len(contexts) == 3
        assert contexts["frontend"]["valid"] is True
        assert contexts["backend"]["valid"] is True
        assert contexts["services"]["valid"] is True
        assert "error" not in contexts["frontend"]
        assert "error" not in contexts["backend"]
        assert "error" not in contexts["services"]
    
    def test_list_available_contexts_none_valid(self):
        """Test listing contexts when none are valid"""
        contexts = self.detector.list_available_contexts()
        
        assert len(contexts) == 3
        assert contexts["frontend"]["valid"] is False
        assert contexts["backend"]["valid"] is False
        assert contexts["services"]["valid"] is False
        assert "error" in contexts["frontend"]
        assert "error" in contexts["backend"]
        assert "error" in contexts["services"]
    
    def test_list_available_contexts_mixed_validity(self):
        """Test listing contexts with mixed validity"""
        # Only create frontend config
        self.create_config_file("frontend/package.json", '{"name": "frontend"}')
        
        contexts = self.detector.list_available_contexts()
        
        assert contexts["frontend"]["valid"] is True
        assert contexts["backend"]["valid"] is False
        assert contexts["services"]["valid"] is False
        assert "error" not in contexts["frontend"]
        assert "error" in contexts["backend"]
        assert "error" in contexts["services"]
    
    # ========================================================================
    # Test suggest_alternative_contexts method
    # ========================================================================
    
    def test_suggest_alternative_contexts_npm_with_backend_available(self):
        """Test suggesting alternatives for npm when backend is available"""
        # Create backend config but not frontend
        self.create_config_file("backend/requirements.txt", "django==4.2.0")
        
        alternatives = self.detector.suggest_alternative_contexts(RegistryType.NPM)
        
        assert ProjectContext.BACKEND in alternatives
        assert ProjectContext.FRONTEND not in alternatives  # Primary context excluded
    
    def test_suggest_alternative_contexts_npm_with_services_available(self):
        """Test suggesting alternatives for npm when services is available"""
        # Create services config but not frontend
        self.create_config_file("services/package.json", '{"name": "services"}')
        
        alternatives = self.detector.suggest_alternative_contexts(RegistryType.NPM)
        
        assert ProjectContext.SERVICES in alternatives
        assert ProjectContext.FRONTEND not in alternatives  # Primary context excluded
    
    def test_suggest_alternative_contexts_no_alternatives(self):
        """Test suggesting alternatives when no valid contexts exist"""
        alternatives = self.detector.suggest_alternative_contexts(RegistryType.NPM)
        
        assert len(alternatives) == 0
    
    def test_suggest_alternative_contexts_pypi_with_frontend_available(self):
        """Test suggesting alternatives for pypi when frontend is available"""
        # Create frontend config but not backend
        self.create_config_file("frontend/package.json", '{"name": "frontend"}')
        
        alternatives = self.detector.suggest_alternative_contexts(RegistryType.PYPI)
        
        assert ProjectContext.FRONTEND in alternatives
        assert ProjectContext.BACKEND not in alternatives  # Primary context excluded
    
    # ========================================================================
    # Test initialization and edge cases
    # ========================================================================
    
    def test_initialization_with_default_project_root(self):
        """Test initialization with default project root"""
        with patch('os.getcwd', return_value='/test/path'):
            detector = ContextDetector()
            assert detector.project_root == Path('/test/path')
    
    def test_initialization_with_custom_project_root(self):
        """Test initialization with custom project root"""
        custom_root = "/custom/path"
        detector = ContextDetector(project_root=custom_root)
        assert detector.project_root == Path(custom_root)
    
    def test_registry_context_mapping_completeness(self):
        """Test that all registry types have context mappings"""
        # Verify all registry types are mapped
        for registry_type in RegistryType:
            context = self.detector.detect_context(registry_type)
            assert isinstance(context, ProjectContext)
    
    def test_context_config_files_completeness(self):
        """Test that all project contexts have config file mappings"""
        # Verify all project contexts have config files defined
        for context in ProjectContext:
            config_file = self.detector.get_config_file_path(context)
            assert isinstance(config_file, str)
            assert len(config_file) > 0
    
    # ========================================================================
    # Test error handling and logging
    # ========================================================================
    
    @patch('app.services.library_management.context_detector.logger')
    def test_logging_on_successful_detection(self, mock_logger):
        """Test that successful context detection is logged"""
        self.detector.detect_context(RegistryType.NPM)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Detected context frontend for registry type npm" in call_args
    
    @patch('app.services.library_management.context_detector.logger')
    def test_logging_on_successful_validation(self, mock_logger):
        """Test that successful context validation is logged"""
        # Create frontend/package.json
        self.create_config_file("frontend/package.json", '{"name": "test"}')
        
        self.detector.validate_context(ProjectContext.FRONTEND)
        
        # Check that success was logged
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Context frontend validated successfully" in call_args
    
    @patch('app.services.library_management.context_detector.logger')
    def test_logging_on_validation_failure(self, mock_logger):
        """Test that validation failure is logged"""
        self.detector.validate_context(ProjectContext.FRONTEND)
        
        # Check that warning was logged
        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Context validation failed" in call_args
    
    # ========================================================================
    # Test edge cases and error conditions
    # ========================================================================
    
    def test_empty_config_file_is_valid(self):
        """Test that empty config files are considered valid"""
        # Create empty frontend/package.json
        self.create_config_file("frontend/package.json", "")
        
        is_valid, error = self.detector.validate_context(ProjectContext.FRONTEND)
        
        assert is_valid is True
        assert error is None
    
    def test_config_file_with_invalid_json_is_still_valid(self):
        """Test that config files with invalid JSON are still considered valid for existence check"""
        # Create frontend/package.json with invalid JSON
        self.create_config_file("frontend/package.json", "invalid json content")
        
        is_valid, error = self.detector.validate_context(ProjectContext.FRONTEND)
        
        # The detector only checks for file existence, not content validity
        assert is_valid is True
        assert error is None
    
    def test_symlink_config_file_is_valid(self):
        """Test that symlinked config files are considered valid"""
        # Create actual file
        actual_file = self.create_config_file("actual_package.json", '{"name": "test"}')
        
        # Create frontend directory
        frontend_dir = Path(self.temp_dir) / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        
        # Create symlink
        symlink_path = frontend_dir / "package.json"
        try:
            symlink_path.symlink_to(actual_file)
            
            is_valid, error = self.detector.validate_context(ProjectContext.FRONTEND)
            
            assert is_valid is True
            assert error is None
        except OSError:
            # Skip test if symlinks are not supported (e.g., Windows without admin rights)
            pytest.skip("Symlinks not supported on this system")


# ============================================================================
# Integration-style tests
# ============================================================================

class TestContextDetectorIntegration:
    """Integration tests for ContextDetector with realistic scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = ContextDetector(project_root=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_realistic_project_structure(self):
        """Create a realistic project structure"""
        # Frontend package.json
        frontend_package = {
            "name": "ai-code-review-frontend",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "next": "^14.0.0"
            }
        }
        
        # Backend requirements.txt
        backend_requirements = """
django==4.2.0
psycopg2==2.9.0
celery==5.3.0
redis==4.5.0
        """.strip()
        
        # Services package.json
        services_package = {
            "name": "ai-code-review-services",
            "version": "1.0.0",
            "dependencies": {
                "express": "^4.18.0",
                "socket.io": "^4.7.0"
            }
        }
        
        # Create files
        self._create_json_file("frontend/package.json", frontend_package)
        self._create_text_file("backend/requirements.txt", backend_requirements)
        self._create_json_file("services/package.json", services_package)
    
    def _create_json_file(self, relative_path: str, content: dict):
        """Helper to create JSON files"""
        import json
        full_path = Path(self.temp_dir) / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(content, indent=2))
    
    def _create_text_file(self, relative_path: str, content: str):
        """Helper to create text files"""
        full_path = Path(self.temp_dir) / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    def test_full_project_npm_library_workflow(self):
        """Test complete workflow for adding npm library"""
        self.create_realistic_project_structure()
        
        # Detect context for npm library
        context = self.detector.detect_context(RegistryType.NPM)
        assert context == ProjectContext.FRONTEND
        
        # Validate the detected context
        is_valid, error = self.detector.validate_context(context)
        assert is_valid is True
        assert error is None
        
        # Combined operation
        context, is_valid, error = self.detector.detect_and_validate_context(RegistryType.NPM)
        assert context == ProjectContext.FRONTEND
        assert is_valid is True
        assert error is None
    
    def test_full_project_pypi_library_workflow(self):
        """Test complete workflow for adding pypi library"""
        self.create_realistic_project_structure()
        
        # Detect context for pypi library
        context = self.detector.detect_context(RegistryType.PYPI)
        assert context == ProjectContext.BACKEND
        
        # Validate the detected context
        is_valid, error = self.detector.validate_context(context)
        assert is_valid is True
        assert error is None
        
        # Combined operation
        context, is_valid, error = self.detector.detect_and_validate_context(RegistryType.PYPI)
        assert context == ProjectContext.BACKEND
        assert is_valid is True
        assert error is None
    
    def test_project_with_missing_frontend_suggests_alternatives(self):
        """Test that missing frontend context suggests valid alternatives"""
        # Create only backend and services
        self._create_text_file("backend/requirements.txt", "django==4.2.0")
        self._create_json_file("services/package.json", {"name": "services"})
        
        # Try to use npm (which defaults to frontend)
        context, is_valid, error = self.detector.detect_and_validate_context(RegistryType.NPM)
        assert context == ProjectContext.FRONTEND
        assert is_valid is False
        
        # Get alternatives
        alternatives = self.detector.suggest_alternative_contexts(RegistryType.NPM)
        assert ProjectContext.BACKEND in alternatives
        assert ProjectContext.SERVICES in alternatives
        assert ProjectContext.FRONTEND not in alternatives
    
    def test_list_contexts_in_realistic_project(self):
        """Test listing contexts in a realistic project setup"""
        self.create_realistic_project_structure()
        
        contexts = self.detector.list_available_contexts()
        
        # All contexts should be valid
        assert contexts["frontend"]["valid"] is True
        assert contexts["backend"]["valid"] is True
        assert contexts["services"]["valid"] is True
        
        # Check config file paths
        assert contexts["frontend"]["config_file"] == "frontend/package.json"
        assert contexts["backend"]["config_file"] == "backend/requirements.txt"
        assert contexts["services"]["config_file"] == "services/package.json"
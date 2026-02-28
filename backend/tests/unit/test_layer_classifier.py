"""
Unit tests for layer_classifier service
"""
import pytest
from app.services.layer_classifier import LayerClassifier


class TestLayerClassifier:
    """Test suite for LayerClassifier"""
    
    @pytest.fixture
    def classifier(self):
        """Create LayerClassifier instance"""
        return LayerClassifier()
    
    def test_classify_controller_layer(self, classifier):
        """Test classifying controller/API layer files"""
        file_path = "app/api/v1/endpoints/users.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['controller', 'api', 'presentation']
    
    def test_classify_service_layer(self, classifier):
        """Test classifying service layer files"""
        file_path = "app/services/user_service.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer == 'service' or layer == 'business'
    
    def test_classify_model_layer(self, classifier):
        """Test classifying model/data layer files"""
        file_path = "app/models/user.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['model', 'data', 'entity']
    
    def test_classify_database_layer(self, classifier):
        """Test classifying database layer files"""
        file_path = "app/database/connection.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['database', 'data', 'persistence']
    
    def test_classify_utility_layer(self, classifier):
        """Test classifying utility files"""
        file_path = "app/utils/helpers.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['utility', 'helper', 'common']
    
    def test_classify_middleware_layer(self, classifier):
        """Test classifying middleware files"""
        file_path = "app/middleware/auth_middleware.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer == 'middleware'
    
    def test_classify_config_layer(self, classifier):
        """Test classifying configuration files"""
        file_path = "app/core/config.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['config', 'configuration', 'core']
    
    def test_classify_test_layer(self, classifier):
        """Test classifying test files"""
        file_path = "tests/test_user_service.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer == 'test'
    
    def test_classify_schema_layer(self, classifier):
        """Test classifying schema files"""
        file_path = "app/schemas/user_schema.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['schema', 'dto', 'model']
    
    def test_classify_repository_layer(self, classifier):
        """Test classifying repository files"""
        file_path = "app/repositories/user_repository.py"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['repository', 'data']
    
    def test_classify_by_content_controller(self, classifier):
        """Test classifying by file content - controller"""
        content = """
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/users")
async def get_users():
    return []
"""
        
        layer = classifier.classify_by_content(content)
        
        assert layer in ['controller', 'api']
    
    def test_classify_by_content_service(self, classifier):
        """Test classifying by file content - service"""
        content = """
class UserService:
    def __init__(self, db):
        self.db = db
    
    async def create_user(self, data):
        # Business logic here
        return user
"""
        
        layer = classifier.classify_by_content(content)
        
        assert layer in ['service', 'business']
    
    def test_classify_by_content_model(self, classifier):
        """Test classifying by file content - model"""
        content = """
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
"""
        
        layer = classifier.classify_by_content(content)
        
        assert layer in ['model', 'entity', 'data']
    
    def test_classify_unknown_file(self, classifier):
        """Test classifying unknown file type"""
        file_path = "random/unknown/file.xyz"
        
        layer = classifier.classify_file(file_path)
        
        assert layer in ['unknown', 'other', None]
    
    def test_get_layer_dependencies(self, classifier):
        """Test getting typical dependencies for a layer"""
        dependencies = classifier.get_layer_dependencies('service')
        
        assert isinstance(dependencies, list)
        assert 'repository' in dependencies or 'data' in dependencies
    
    def test_validate_layer_architecture(self, classifier):
        """Test validating layer architecture rules"""
        # Service layer should not depend on controller layer
        is_valid = classifier.validate_dependency('service', 'controller')
        
        assert is_valid is False
    
    def test_validate_allowed_dependency(self, classifier):
        """Test validating allowed dependency"""
        # Controller can depend on service
        is_valid = classifier.validate_dependency('controller', 'service')
        
        assert is_valid is True

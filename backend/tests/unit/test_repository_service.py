"""
Unit tests for repository_service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.services.repository_service import RepositoryService


class TestRepositoryService:
    """Test suite for RepositoryService"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_db):
        """Create RepositoryService instance"""
        return RepositoryService(db=mock_db, github_token="test_token")
    
    def test_parse_repository_url_https(self, service):
        """Test parsing HTTPS GitHub URL"""
        url = "https://github.com/owner/repo"
        result = service.parse_repository_url(url)
        
        assert result.owner == "owner"
        assert result.name == "repo"
        assert result.full_name == "owner/repo"
    
    def test_parse_repository_url_https_with_git(self, service):
        """Test parsing HTTPS GitHub URL with .git extension"""
        url = "https://github.com/owner/repo.git"
        result = service.parse_repository_url(url)
        
        assert result.owner == "owner"
        assert result.name == "repo"
    
    def test_parse_repository_url_ssh(self, service):
        """Test parsing SSH GitHub URL"""
        url = "git@github.com:owner/repo.git"
        result = service.parse_repository_url(url)
        
        assert result.owner == "owner"
        assert result.name == "repo"
    
    def test_parse_repository_url_invalid(self, service):
        """Test parsing invalid URL raises error"""
        with pytest.raises(ValueError, match="Invalid GitHub repository URL"):
            service.parse_repository_url("not-a-valid-url")
    
    def test_parse_repository_url_non_github(self, service):
        """Test parsing non-GitHub URL raises error"""
        with pytest.raises(ValueError, match="Only GitHub repositories are supported"):
            service.parse_repository_url("https://gitlab.com/owner/repo")
    
    @pytest.mark.asyncio
    async def test_validate_repository_success(self, service):
        """Test successful repository validation"""
        with patch.object(service, '_check_repository_exists', return_value=True):
            with patch.object(service, '_check_repository_accessible', return_value=True):
                result = await service.validate_repository("https://github.com/owner/repo")
                
                assert result['valid'] is True
                assert result['exists'] is True
                assert result['accessible'] is True
    
    @pytest.mark.asyncio
    async def test_validate_repository_not_exists(self, service):
        """Test validation when repository doesn't exist"""
        with patch.object(service, '_check_repository_exists', return_value=False):
            result = await service.validate_repository("https://github.com/owner/repo")
            
            assert result['valid'] is False
            assert result['exists'] is False
    
    @pytest.mark.asyncio
    async def test_validate_repository_not_accessible(self, service):
        """Test validation when repository is not accessible"""
        with patch.object(service, '_check_repository_exists', return_value=True):
            with patch.object(service, '_check_repository_accessible', return_value=False):
                result = await service.validate_repository("https://github.com/owner/repo")
                
                assert result['valid'] is False
                assert result['accessible'] is False
    
    @pytest.mark.asyncio
    async def test_fetch_dependencies_success(self, service):
        """Test successful dependency fetching"""
        mock_dependencies = [
            {'name': 'requests', 'version': '2.28.0'},
            {'name': 'pytest', 'version': '7.2.0'}
        ]
        
        with patch.object(service, '_parse_requirements_file', return_value=mock_dependencies):
            result = await service.fetch_dependencies("https://github.com/owner/repo")
            
            assert len(result) == 2
            assert result[0]['name'] == 'requests'
            assert result[1]['name'] == 'pytest'
    
    @pytest.mark.asyncio
    async def test_fetch_dependencies_no_file(self, service):
        """Test fetching dependencies when no requirements file exists"""
        with patch.object(service, '_parse_requirements_file', return_value=[]):
            result = await service.fetch_dependencies("https://github.com/owner/repo")
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_add_repository_success(self, service, mock_db):
        """Test successfully adding a repository"""
        repo_url = "https://github.com/owner/repo"
        
        with patch.object(service, 'validate_repository', return_value={'valid': True, 'exists': True, 'accessible': True}):
            with patch.object(service, 'fetch_dependencies', return_value=[]):
                mock_db.add = Mock()
                mock_db.commit = AsyncMock()
                mock_db.refresh = AsyncMock()
                
                result = await service.add_repository(repo_url, user_id=1)
                
                assert result is not None
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_repository_invalid(self, service):
        """Test adding invalid repository raises error"""
        with patch.object(service, 'validate_repository', return_value={'valid': False, 'exists': False}):
            with pytest.raises(ValueError, match="Repository validation failed"):
                await service.add_repository("https://github.com/owner/repo", user_id=1)
    
    def test_parse_repository_url_with_trailing_slash(self, service):
        """Test parsing URL with trailing slash"""
        url = "https://github.com/owner/repo/"
        result = service.parse_repository_url(url)
        
        assert result.owner == "owner"
        assert result.name == "repo"
    
    def test_parse_repository_url_with_subdirectory(self, service):
        """Test parsing URL with subdirectory path"""
        url = "https://github.com/owner/repo/tree/main/src"
        result = service.parse_repository_url(url)
        
        assert result.owner == "owner"
        assert result.name == "repo"
    
    @pytest.mark.asyncio
    async def test_validate_repository_handles_exception(self, service):
        """Test validation handles exceptions gracefully"""
        with patch.object(service, '_check_repository_exists', side_effect=Exception("API Error")):
            result = await service.validate_repository("https://github.com/owner/repo")
            
            assert result['valid'] is False
            assert 'error' in result

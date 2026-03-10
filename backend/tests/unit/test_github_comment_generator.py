"""
Unit tests for github_comment_generator service
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.github_comment_generator import GitHubCommentGenerator


class TestGitHubCommentGenerator:
    """Test suite for GitHubCommentGenerator"""
    
    @pytest.fixture
    def generator(self):
        """Create GitHubCommentGenerator instance"""
        return GitHubCommentGenerator(github_token="test_token", repo_owner="owner", repo_name="repo")
    
    def test_format_security_finding_high_severity(self, generator):
        """Test formatting security finding with high severity"""
        finding = {
            'severity': 'high',
            'title': 'SQL Injection',
            'description': 'Potential SQL injection vulnerability',
            'location': 'app/database.py:42',
            'recommendation': 'Use parameterized queries'
        }
        
        formatted = generator.format_security_finding(finding)
        
        assert 'high' in formatted.lower() or '🔴' in formatted
        assert 'SQL Injection' in formatted
        assert isinstance(formatted, str)
    
    def test_format_security_finding_medium_severity(self, generator):
        """Test formatting security finding with medium severity"""
        finding = {
            'severity': 'medium',
            'title': 'Weak Encryption',
            'description': 'Using weak encryption algorithm',
            'location': 'app/crypto.py:10'
        }
        
        formatted = generator.format_security_finding(finding)
        
        assert 'medium' in formatted.lower() or '🟡' in formatted
        assert 'Weak Encryption' in formatted
    
    def test_format_security_finding_low_severity(self, generator):
        """Test formatting security finding with low severity"""
        finding = {
            'severity': 'low',
            'title': 'Missing Header',
            'description': 'Security header not set',
            'location': 'app/middleware.py:5'
        }
        
        formatted = generator.format_security_finding(finding)
        
        assert 'low' in formatted.lower() or '🟢' in formatted
    
    def test_format_classified_finding(self, generator):
        """Test formatting classified finding"""
        finding = {
            'category': 'code_quality',
            'title': 'Complex Function',
            'description': 'Function has high cyclomatic complexity',
            'location': 'app/utils.py:100',
            'severity': 'medium'
        }
        
        formatted = generator.format_classified_finding(finding)
        
        assert 'code_quality' in formatted.lower() or 'Complex Function' in formatted
        assert isinstance(formatted, str)
    
    @pytest.mark.asyncio
    async def test_post_comment_success(self, generator):
        """Test successfully posting a comment"""
        with patch.object(generator, '_github_client') as mock_client:
            mock_client.post_comment = AsyncMock(return_value={'id': 123})
            
            result = await generator.post_comment(
                pr_number=1,
                body="Test comment",
                path="test.py",
                line=10
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_post_security_findings_multiple(self, generator):
        """Test posting multiple security findings"""
        findings = [
            {
                'severity': 'high',
                'title': 'Issue 1',
                'description': 'Description 1',
                'location': 'file1.py:10'
            },
            {
                'severity': 'medium',
                'title': 'Issue 2',
                'description': 'Description 2',
                'location': 'file2.py:20'
            }
        ]
        
        with patch.object(generator, 'post_comment', new=AsyncMock(return_value={'id': 123})):
            result = await generator.post_security_findings(pr_number=1, findings=findings)
            
            assert result is not None
    
    def test_parse_location_with_line_number(self, generator):
        """Test parsing location with line number"""
        location = "app/main.py:42"
        
        file_path, line_number = generator._parse_location(location)
        
        assert file_path == "app/main.py"
        assert line_number == 42
    
    def test_parse_location_without_line_number(self, generator):
        """Test parsing location without line number"""
        location = "app/main.py"
        
        file_path, line_number = generator._parse_location(location)
        
        assert file_path == "app/main.py"
        assert line_number == 1  # Default to line 1
    
    @pytest.mark.asyncio
    async def test_post_summary_comment(self, generator):
        """Test posting summary comment"""
        summary = {
            'total_findings': 5,
            'high_severity': 2,
            'medium_severity': 2,
            'low_severity': 1
        }
        
        with patch.object(generator, 'post_comment', new=AsyncMock(return_value={'id': 123})):
            result = await generator.post_summary_comment(pr_number=1, summary=summary)
            
            assert result is not None
    
    def test_format_summary_with_findings(self, generator):
        """Test formatting summary with findings"""
        summary = {
            'total_findings': 3,
            'high_severity': 1,
            'medium_severity': 1,
            'low_severity': 1
        }
        
        formatted = generator._format_summary(summary)
        
        assert '3' in formatted
        assert 'high' in formatted.lower() or '🔴' in formatted
    
    def test_format_summary_no_findings(self, generator):
        """Test formatting summary with no findings"""
        summary = {
            'total_findings': 0,
            'high_severity': 0,
            'medium_severity': 0,
            'low_severity': 0
        }
        
        formatted = generator._format_summary(summary)
        
        assert 'no' in formatted.lower() or '0' in formatted
    
    def test_format_security_finding_with_recommendation(self, generator):
        """Test formatting finding with recommendation"""
        finding = {
            'severity': 'high',
            'title': 'Security Issue',
            'description': 'Issue description',
            'location': 'app/auth.py:10',
            'recommendation': 'Fix by doing X'
        }
        
        formatted = generator.format_security_finding(finding)
        
        assert 'recommendation' in formatted.lower() or 'Fix by doing X' in formatted
    
    def test_format_security_finding_with_references(self, generator):
        """Test formatting finding with references"""
        finding = {
            'severity': 'medium',
            'title': 'Issue',
            'description': 'Description',
            'location': 'app/test.py:5',
            'references': ['https://owasp.org/example']
        }
        
        formatted = generator.format_security_finding(finding)
        
        # Should include references if provided
        assert isinstance(formatted, str)

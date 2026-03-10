"""
Unit tests for Code Reviewer integration with Agentic AI Service

Tests the integration between Code Review Service and Agentic AI Service
for complex code pattern analysis.

Validates Requirements: 1.2
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.code_reviewer import CodeReviewer
from app.services.agentic_ai_service import (
    AgenticAIService,
    CleanCodeViolation,
    CleanCodePrinciple,
    NaturalLanguageExplanation
)
from app.schemas.code_review import ReviewComment, ReviewSeverity, ReviewCategory


@pytest.fixture
def mock_agentic_ai_service():
    """Create a mock Agentic AI Service"""
    service = Mock(spec=AgenticAIService)
    service.analyze_clean_code_violations = AsyncMock()
    service.analyze_with_graph_context = AsyncMock()
    service.generate_natural_language_explanation = AsyncMock()
    return service


@pytest.fixture
def code_reviewer_with_ai(mock_agentic_ai_service):
    """Create a Code Reviewer with Agentic AI Service integration"""
    with patch('app.services.code_reviewer.get_llm_client'):
        with patch('app.services.code_reviewer.get_standards_classifier'):
            reviewer = CodeReviewer(agentic_ai_service=mock_agentic_ai_service)
            return reviewer


class TestAgenticAIIntegration:
    """Test suite for Agentic AI Service integration"""
    
    @pytest.mark.asyncio
    async def test_query_agentic_ai_for_clean_code_violations(
        self,
        code_reviewer_with_ai,
        mock_agentic_ai_service
    ):
        """Test querying Agentic AI for Clean Code violations"""
        # Arrange
        file_path = "test.py"
        code_content = "def f(x):\n    return x + 1"
        repository = "test-repo"
        existing_comments = []
        
        # Mock Clean Code violations
        mock_violations = [
            CleanCodeViolation(
                principle=CleanCodePrinciple.MEANINGFUL_NAMES,
                severity="high",
                location="test.py:1",
                description="Function name 'f' is not meaningful",
                suggestion="Use a descriptive name like 'increment_value'",
                example_fix="def increment_value(x):\n    return x + 1"
            ),
            CleanCodeViolation(
                principle=CleanCodePrinciple.SMALL_FUNCTIONS,
                severity="medium",
                location="test.py:1",
                description="Function could be more focused",
                suggestion="Consider breaking into smaller functions"
            )
        ]
        mock_agentic_ai_service.analyze_clean_code_violations.return_value = mock_violations
        
        # Mock architectural analysis
        mock_agentic_ai_service.analyze_with_graph_context.return_value = {
            'recommendations': []
        }
        
        # Act
        ai_comments = await code_reviewer_with_ai._query_agentic_ai_for_complex_analysis(
            file_path=file_path,
            code_content=code_content,
            repository=repository,
            existing_comments=existing_comments
        )
        
        # Assert
        assert len(ai_comments) == 2
        assert ai_comments[0].category == ReviewCategory.MAINTAINABILITY
        assert 'meaningful_names' in ai_comments[0].message.lower()
        assert ai_comments[0].severity == ReviewSeverity.HIGH
        assert 'increment_value' in ai_comments[0].suggested_fix
        
        # Verify Agentic AI Service was called
        mock_agentic_ai_service.analyze_clean_code_violations.assert_called_once_with(
            code=code_content,
            file_path=file_path,
            language='python'
        )
    
    @pytest.mark.asyncio
    async def test_query_agentic_ai_for_architectural_analysis(
        self,
        code_reviewer_with_ai,
        mock_agentic_ai_service
    ):
        """Test querying Agentic AI for architectural context analysis"""
        # Arrange
        file_path = "service.py"
        code_content = "class Service:\n    pass"
        repository = "test-repo"
        existing_comments = []
        
        # Mock Clean Code violations (empty)
        mock_agentic_ai_service.analyze_clean_code_violations.return_value = []
        
        # Mock architectural analysis with recommendations
        mock_agentic_ai_service.analyze_with_graph_context.return_value = {
            'recommendations': [
                {
                    'line': 1,
                    'message': 'This class introduces tight coupling with database layer',
                    'severity': 'high',
                    'suggestion': 'Consider using dependency injection'
                },
                {
                    'line': 5,
                    'message': 'Missing error handling for external API calls',
                    'severity': 'medium',
                    'suggestion': 'Add try-except blocks with proper error handling'
                }
            ]
        }
        
        # Act
        ai_comments = await code_reviewer_with_ai._query_agentic_ai_for_complex_analysis(
            file_path=file_path,
            code_content=code_content,
            repository=repository,
            existing_comments=existing_comments
        )
        
        # Assert
        assert len(ai_comments) == 2
        assert ai_comments[0].category == ReviewCategory.ARCHITECTURE
        assert 'tight coupling' in ai_comments[0].message.lower()
        assert ai_comments[0].severity == ReviewSeverity.HIGH
        assert 'dependency injection' in ai_comments[0].suggested_fix
        
        # Verify Agentic AI Service was called
        mock_agentic_ai_service.analyze_with_graph_context.assert_called_once_with(
            code=code_content,
            file_path=file_path,
            repository=repository
        )
    
    @pytest.mark.asyncio
    async def test_query_agentic_ai_for_natural_language_explanations(
        self,
        code_reviewer_with_ai,
        mock_agentic_ai_service
    ):
        """Test generating natural language explanations for complex findings"""
        # Arrange
        file_path = "auth.py"
        code_content = "password = input()"
        repository = "test-repo"
        
        # Create existing complex findings
        existing_comments = [
            ReviewComment(
                file_path=file_path,
                line=1,
                message="SQL injection vulnerability detected",
                severity=ReviewSeverity.CRITICAL,
                category=ReviewCategory.SECURITY
            ),
            ReviewComment(
                file_path=file_path,
                line=2,
                message="Architectural violation: direct database access",
                severity=ReviewSeverity.HIGH,
                category=ReviewCategory.ARCHITECTURE
            )
        ]
        
        # Mock Clean Code violations (empty)
        mock_agentic_ai_service.analyze_clean_code_violations.return_value = []
        
        # Mock architectural analysis (empty)
        mock_agentic_ai_service.analyze_with_graph_context.return_value = {
            'recommendations': []
        }
        
        # Mock natural language explanations
        mock_explanation = NaturalLanguageExplanation(
            technical_finding="SQL injection vulnerability detected",
            developer_explanation="Your code is vulnerable to SQL injection attacks, which could allow attackers to access or modify your database.",
            why_it_matters="This is a critical security issue that could lead to data breaches and compromise user data.",
            how_to_fix="Use parameterized queries or an ORM to safely handle user input.",
            code_example="""
# Example of SQL injection vulnerability (for educational purposes):
# BAD: query = f'SELECT * FROM users WHERE id = {user_id}'
# cursor.execute(query)

# SECURE: Use parameterized queries
query = 'SELECT * FROM users WHERE id = ?'
cursor.execute(query, (user_id,))
"""
        )
        mock_agentic_ai_service.generate_natural_language_explanation.return_value = mock_explanation
        
        # Act
        ai_comments = await code_reviewer_with_ai._query_agentic_ai_for_complex_analysis(
            file_path=file_path,
            code_content=code_content,
            repository=repository,
            existing_comments=existing_comments
        )
        
        # Assert
        # Should have explanations for complex findings
        explained_comments = [c for c in ai_comments if c.category == ReviewCategory.OTHER and '[AI Explanation]' in c.message]
        assert len(explained_comments) > 0
        
        # Check that explanation was generated
        assert any('SQL injection' in c.message for c in ai_comments)
        assert any('parameterized queries' in (c.suggested_fix or '') for c in ai_comments)
        
        # Verify Agentic AI Service was called for explanations
        assert mock_agentic_ai_service.generate_natural_language_explanation.called
    
    @pytest.mark.asyncio
    async def test_agentic_ai_integration_handles_errors_gracefully(
        self,
        code_reviewer_with_ai,
        mock_agentic_ai_service
    ):
        """Test that errors in Agentic AI Service don't break code review"""
        # Arrange
        file_path = "test.py"
        code_content = "def test(): pass"
        repository = "test-repo"
        existing_comments = []
        
        # Mock Agentic AI Service to raise an exception
        mock_agentic_ai_service.analyze_clean_code_violations.side_effect = Exception(
            "AI service unavailable"
        )
        
        # Act - should not raise exception
        ai_comments = await code_reviewer_with_ai._query_agentic_ai_for_complex_analysis(
            file_path=file_path,
            code_content=code_content,
            repository=repository,
            existing_comments=existing_comments
        )
        
        # Assert - should return empty list on error
        assert isinstance(ai_comments, list)
        # May be empty or contain partial results
    
    @pytest.mark.asyncio
    async def test_agentic_ai_integration_limits_explanation_generation(
        self,
        code_reviewer_with_ai,
        mock_agentic_ai_service
    ):
        """Test that explanation generation is limited to avoid excessive API calls"""
        # Arrange
        file_path = "test.py"
        code_content = "code"
        repository = "test-repo"
        
        # Create many complex findings
        existing_comments = [
            ReviewComment(
                file_path=file_path,
                line=i,
                message=f"Critical issue {i}",
                severity=ReviewSeverity.CRITICAL,
                category=ReviewCategory.SECURITY
            )
            for i in range(10)  # 10 critical findings
        ]
        
        # Mock services
        mock_agentic_ai_service.analyze_clean_code_violations.return_value = []
        mock_agentic_ai_service.analyze_with_graph_context.return_value = {
            'recommendations': []
        }
        mock_agentic_ai_service.generate_natural_language_explanation.return_value = NaturalLanguageExplanation(
            technical_finding="test",
            developer_explanation="test",
            why_it_matters="test",
            how_to_fix="test"
        )
        
        # Act
        ai_comments = await code_reviewer_with_ai._query_agentic_ai_for_complex_analysis(
            file_path=file_path,
            code_content=code_content,
            repository=repository,
            existing_comments=existing_comments
        )
        
        # Assert - should limit to 3 explanations
        explanation_calls = mock_agentic_ai_service.generate_natural_language_explanation.call_count
        assert explanation_calls <= 3, "Should limit explanation generation to avoid excessive API calls"
    
    def test_detect_language(self, code_reviewer_with_ai):
        """Test language detection from file extension"""
        assert code_reviewer_with_ai._detect_language("test.py") == "python"
        assert code_reviewer_with_ai._detect_language("test.js") == "javascript"
        assert code_reviewer_with_ai._detect_language("test.ts") == "typescript"
        assert code_reviewer_with_ai._detect_language("test.java") == "java"
        assert code_reviewer_with_ai._detect_language("test.cpp") == "cpp"
        assert code_reviewer_with_ai._detect_language("test.unknown") == "unknown"
    
    def test_extract_line_number(self, code_reviewer_with_ai):
        """Test extracting line number from location string"""
        assert code_reviewer_with_ai._extract_line_number("file.py:42") == 42
        assert code_reviewer_with_ai._extract_line_number("file.py:1") == 1
        assert code_reviewer_with_ai._extract_line_number("file.py") == 0
        assert code_reviewer_with_ai._extract_line_number("invalid") == 0
    
    def test_map_severity(self, code_reviewer_with_ai):
        """Test mapping severity strings to ReviewSeverity enum"""
        assert code_reviewer_with_ai._map_severity("critical") == ReviewSeverity.CRITICAL
        assert code_reviewer_with_ai._map_severity("high") == ReviewSeverity.HIGH
        assert code_reviewer_with_ai._map_severity("medium") == ReviewSeverity.MEDIUM
        assert code_reviewer_with_ai._map_severity("low") == ReviewSeverity.LOW
        assert code_reviewer_with_ai._map_severity("info") == ReviewSeverity.LOW
        assert code_reviewer_with_ai._map_severity("unknown") == ReviewSeverity.MEDIUM


class TestCodeReviewerWithoutAI:
    """Test that Code Reviewer works without Agentic AI Service"""
    
    def test_code_reviewer_initializes_without_ai_service(self):
        """Test that Code Reviewer can be initialized without Agentic AI Service"""
        with patch('app.services.code_reviewer.get_llm_client'):
            with patch('app.services.code_reviewer.get_standards_classifier'):
                reviewer = CodeReviewer()
                assert reviewer.agentic_ai_service is None
    
    @pytest.mark.asyncio
    async def test_code_review_works_without_ai_service(self):
        """Test that code review works without Agentic AI Service integration"""
        with patch('app.services.code_reviewer.get_llm_client'):
            with patch('app.services.code_reviewer.get_standards_classifier'):
                reviewer = CodeReviewer()
                
                # Mock the necessary methods
                reviewer._parse_diff = Mock(return_value=[])
                reviewer._perform_architectural_analysis = AsyncMock()
                
                # Act - should not raise exception
                result = await reviewer.review_pull_request(
                    pr_data={'id': '123', 'head_sha': 'abc'},
                    project_id='test-project',
                    diff_content='diff content'
                )
                
                # Assert
                assert result is not None
                assert result.pr_id == '123'

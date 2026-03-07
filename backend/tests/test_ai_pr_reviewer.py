"""
Test cases for AI PR Reviewer

This module contains comprehensive test cases for the AI PR reviewer functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_pr_reviewer import AIPRReviewer, ReviewResult, ComplianceStatus
from app.services.ai_pr_reviewer_service import AIReviewService, ReviewRequest, ReviewResponse
from app.services.llm_client import LLMClient, LLMProvider
from app.services.agentic_ai_service import AgenticAIService, ReasoningResult
from app.services.architectural_drift_detector import ArchitecturalDriftDetector
from app.services.security_compliance_service import SecurityComplianceService


class TestAIPRReviewer:
    """Test cases for AIPRReviewer class."""
    
    @pytest.fixture
    def mock_agentic_service(self):
        """Create a mock Agentic AI service."""
        mock_service = Mock(spec=AgenticAIService)
        mock_service.perform_complex_reasoning = AsyncMock()
        return mock_service
    
    @pytest.fixture
    def reviewer(self, mock_agentic_service):
        """Create an AIPRReviewer instance with mocked dependencies."""
        reviewer = AIPRReviewer(mock_agentic_service)
        return reviewer
    
    @pytest.fixture
    def sample_diff(self):
        """Sample git diff content for testing."""
        return """
        diff --git a/frontend/src/components/UserProfile.tsx b/frontend/src/components/UserProfile.tsx
        new file mode 100644
        index 0000000..1234567
        --- /dev/null
        +++ b/frontend/src/components/UserProfile.tsx
        @@ -0,0 +1,20 @@
        +import React from 'react';
        +import { getUserData } from '../services/api';
        +
        +const UserProfile: React.FC = () => {
        +  const [user, setUser] = React.useState(null);
        +
        +  React.useEffect(() => {
        +    // Direct API call from UI component - architectural violation
        +    getUserData().then(setUser);
        +  }, []);
        +
        +  return (
        +    <div>
        +      <h1>User Profile</h1>
        +      {user && <p>Name: {user.name}</p>}
        +    </div>
        +  );
        +};
        +
        +export default UserProfile;
        """
    
    @pytest.fixture
    def sample_standards(self):
        """Sample design standards for testing."""
        return {
            "layer_separation": {
                "ui_components": ["components/", "pages/", "views/"],
                "business_logic": ["services/", "use_cases/", "domain/"],
                "data_access": ["repositories/", "models/", "dao/"],
                "forbidden_connections": [
                    {"from": "ui_components", "to": "data_access"}
                ]
            },
            "security_standards": {
                "input_validation": True,
                "sql_injection_prevention": True,
                "xss_prevention": True,
                "authentication_required": True
            }
        }
    
    @pytest.fixture
    def mock_ai_response(self):
        """Mock AI response for testing."""
        return {
            "content": '{"code_quality_issues": ["Missing error handling"], "architecture_violations": ["UI component calling API directly"], "security_concerns": ["No input validation"], "best_practices": ["Add error boundaries", "Use proper state management"], "complexity_assessment": {"cyclomatic_complexity": "low", "maintainability": "medium", "readability": "high"}}'
        }
    
    def test_init(self, mock_agentic_service):
        """Test AIPRReviewer initialization."""
        reviewer = AIPRReviewer(mock_agentic_service)
        
        assert reviewer.agentic_service == mock_agentic_service
        assert reviewer.logger is not None
    
    @pytest.mark.asyncio
    async def test_analyze_pr_success(self, reviewer, mock_agentic_service, sample_diff, sample_standards, mock_ai_response):
        """Test successful pull request analysis."""
        # Setup mock reasoning result
        mock_reasoning_result = ReasoningResult(
            task_type="pr_review",
            suggestions=[],
            confidence=0.9,
            reasoning_chain=[json.dumps({
                "suggestions": ["Add error boundaries"],
                "architectural_issues": ["UI component calling API directly"],
                "security_issues": ["No input validation"],
                "code_quality_issues": ["Missing error handling"]
            })],
            knowledge_references=[]
        )
        mock_agentic_service.perform_complex_reasoning.return_value = mock_reasoning_result
        
        # Perform analysis
        result = await reviewer.analyze_pr(sample_diff, "Design standards text")
        
        # Verify results
        assert isinstance(result, ReviewResult)
        assert result.safety_score > 0
        assert result.safety_score <= 100
        assert result.compliance_status in [ComplianceStatus.COMPLIANT, ComplianceStatus.WARNING, ComplianceStatus.VIOLATION]
        assert len(result.architectural_issues) > 0
        assert len(result.security_issues) > 0
        assert len(result.refactoring_suggestions) > 0
        assert len(result.code_quality_issues) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_pr_with_agentic_service_unavailable(self, reviewer, mock_agentic_service, sample_diff):
        """Test analysis when agentic service is unavailable."""
        # Setup reviewer with NO agentic service
        reviewer.agentic_service = None
        
        # Perform analysis
        result = await reviewer.analyze_pr(sample_diff, "standards")
        
        # Verify results
        assert isinstance(result, ReviewResult)
        assert result.safety_score == 100.0  # Default score
        assert result.compliance_status == ComplianceStatus.COMPLIANT
    
    def test_calculate_safety_score(self, reviewer):
        """Test safety score calculation."""
        analysis_data = {
            "architectural_issues": ["Layer violation"],
            "security_issues": ["SQL injection risk"],
            "code_quality_issues": ["Missing error handling"]
        }
        
        score = reviewer._calculate_safety_score(
            analysis_data,
            "git diff content"
        )
        
        # 100 - (1*15) - (1*25) - (1*5) = 100 - 45 = 55
        expected_score = 55
        assert score == expected_score
    
    def test_determine_compliance_status(self, reviewer):
        """Test compliance status determination."""
        # High score
        status = reviewer._determine_compliance_status(90)
        assert status == ComplianceStatus.COMPLIANT
        
        # Medium score
        status = reviewer._determine_compliance_status(70)
        assert status == ComplianceStatus.WARNING
        
        # Low score
        status = reviewer._determine_compliance_status(50)
        assert status == ComplianceStatus.VIOLATION
    
    def test_parse_analysis_result_json(self, reviewer):
        """Test JSON result parsing."""
        analysis_text = '```json\n{"suggestions": ["Test suggestion"]}\n```'
        result = reviewer._parse_analysis_result(analysis_text)
        assert result["suggestions"] == ["Test suggestion"]
    
    def test_parse_text_analysis(self, reviewer):
        """Test text analysis parsing."""
        analysis_text = """Architectural issues
- Issue 1
Security issues
- Issue 2
Suggestions
- Suggestion 1"""
        result = reviewer._parse_text_analysis(analysis_text)
        assert "Issue 1" in result["architectural_issues"]
        assert "Issue 2" in result["security_issues"]
        assert "Suggestion 1" in result["suggestions"]
    
    def test_generate_markdown_report(self, reviewer):
        """Test report generation."""
        result = ReviewResult(
            safety_score=75,
            compliance_status=ComplianceStatus.WARNING,
            refactoring_suggestions=["Add error handling"],
            architectural_issues=["Layer violation"],
            security_issues=["Missing validation"],
            code_quality_issues=["Long method"]
        )
        
        report = reviewer.generate_markdown_report(result)
        
        assert "# AI PR Review Report" in report
        assert "Safety Score**: 75/100" in report
        assert "Compliance Status**: WARNING" in report
        assert "Layer violation" in report
        assert "Missing validation" in report
        assert "Long method" in report
    

class TestAIReviewService:
    """Test cases for AIReviewService class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def review_service(self, mock_db_session):
        """Create an AIReviewService instance."""
        return AIReviewService(db=mock_db_session, user_id="test-user")
    
    @pytest.fixture
    def sample_review_request(self):
        """Sample review request for testing."""
        from app.services.ai_pr_reviewer_service import ReviewRequest, ReviewResponse
        
        return ReviewRequest(
            diff_content="sample diff content",
            design_standards={"layer_separation": {}, "security_standards": {}},
            project_id="test-project",
            pr_id="pr-123",
            reviewer_id="test-reviewer"
        )
    
    @pytest.mark.asyncio
    async def test_review_pull_request(self, review_service, sample_review_request):
        """Test pull request review."""
        # Mock the LLM provider and generation
        mock_llm_provider = AsyncMock()
        mock_llm_response = Mock()
        mock_llm_response.content = "Analysis result"
        mock_llm_response.tokens = {"total": 100}
        mock_llm_response.cost = 0.01
        mock_llm_provider.generate.return_value = mock_llm_response
        mock_llm_provider.get_provider_type = Mock(return_value=Mock(value="openai"))
        mock_llm_provider.model = "gpt-4"
        
        with patch.object(review_service, '_get_llm_provider', return_value=mock_llm_provider):
            # Perform review
            response = await review_service.review_pull_request(sample_review_request)
            
            # Verify response
            assert response.review_id is not None
            assert response.review_result.safety_score == 85  # Default in current parser
            assert response.metadata["project_id"] == "test-project"
            assert response.metadata["pr_id"] == "pr-123"
    
    @pytest.mark.asyncio
    async def test_batch_review(self, review_service, sample_review_request):
        """Test batch review of multiple requests."""
        requests = [sample_review_request, sample_review_request]
        
        # Mock the LLM provider and generation
        mock_llm_provider = AsyncMock()
        mock_llm_response = Mock()
        mock_llm_response.content = "Analysis result"
        mock_llm_response.tokens = {"total": 100}
        mock_llm_response.cost = 0.01
        mock_llm_provider.generate.return_value = mock_llm_response
        mock_llm_provider.get_provider_type = Mock(return_value=Mock(value="openai"))
        mock_llm_provider.model = "gpt-4"
        
        with patch.object(review_service, '_get_llm_provider', return_value=mock_llm_provider):
            responses = await review_service.batch_review(requests)
            
            # Verify response
            assert len(responses) == 2
            assert responses[0].review_id is not None
            assert responses[1].review_id is not None
    
    def test_get_review_summary(self, review_service):
        """Test review summary generation."""
        from datetime import datetime
        
        responses = [
            ReviewResponse(
                review_id="review-1",
                timestamp=datetime.now(),
                review_result=ReviewResult(80, ComplianceStatus.COMPLIANT, [], [], [], []),
                report={"summary": {"total_issues": 0, "safety_score": 80, "compliance_status": "COMPLIANT"}},
                metadata={}
            ),
            ReviewResponse(
                review_id="review-2",
                timestamp=datetime.now(),
                review_result=ReviewResult(60, ComplianceStatus.WARNING, [], [], [], []),
                report={"summary": {"total_issues": 2, "safety_score": 60, "compliance_status": "WARNING"}},
                metadata={}
            )
        ]
        
        summary = review_service.get_review_summary(responses)
        
        assert summary["summary"]["total_reviews"] == 2
        assert summary["summary"]["compliant_reviews"] == 1
        assert summary["summary"]["warning_reviews"] == 1
        assert summary["summary"]["non_compliant_reviews"] == 0
        assert summary["summary"]["average_safety_score"] == 70.0
        assert summary["summary"]["total_issues"] == 2
    
    def test_export_review_report(self, review_service):
        """Test report export functionality."""
        from datetime import datetime
        
        response = ReviewResponse(
            review_id="test-review",
            timestamp=datetime.now(),
            review_result=ReviewResult(80, ComplianceStatus.COMPLIANT, [], [], [], []),
            report={
                "summary": {"safety_score": 80, "compliance_status": "COMPLIANT", "total_issues": 0},
                "markdown_report": "# AI PR Review Report\nSafety Score: 80/100",
                "architectural_analysis": {"issues": []},
                "security_analysis": {"issues": []},
                "refactoring_suggestions": []
            },
            metadata={}
        )
        
        # Test JSON export
        json_content = review_service.export_review_report(response, "json")
        assert "test-review" in json_content
        
        # Test markdown export
        markdown_content = review_service.export_review_report(response, "markdown")
        assert "# AI PR Review Report" in markdown_content
    
    def test_validate_design_standards(self, review_service):
        """Test design standards validation."""
        # Valid standards
        valid_standards = {
            "layer_separation": {
                "ui_components": [],
                "business_logic": [],
                "data_access": []
            },
            "security_standards": {
                "input_validation": True,
                "sql_injection_prevention": True,
                "xss_prevention": True
            }
        }
        
        errors = review_service.validate_design_standards(valid_standards)
        assert len(errors) == 0
        
        # Invalid standards
        invalid_standards = {
            "layer_separation": {
                "ui_components": []
                # Missing business_logic and data_access
            }
            # Missing security_standards
        }
        
        errors = review_service.validate_design_standards(invalid_standards)
        assert len(errors) > 0
        assert "Missing required section: security_standards" in errors
        assert "Missing required layer: business_logic" in errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

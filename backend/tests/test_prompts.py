"""
Unit Tests for Code Analysis Prompts

Tests the prompt manager and code analysis prompt generation.

Validates Requirements: 1.4
"""
import logging
logger = logging.getLogger(__name__)


import pytest
from app.services.llm.prompts import (
    AnalysisType,
    PromptTemplate,
    CodeAnalysisPrompts,
    PromptManager,
    get_prompt_manager
)


class TestPromptTemplate:
    """Test PromptTemplate class"""
    
    def test_template_creation(self):
        """Test creating a prompt template"""
        template = PromptTemplate(
            system_prompt="You are a code reviewer",
            user_prompt_template="Review this code: {code}",
            analysis_type=AnalysisType.CODE_QUALITY
        )
        
        assert template.system_prompt == "You are a code reviewer"
        assert template.user_prompt_template == "Review this code: {code}"
        assert template.analysis_type == AnalysisType.CODE_QUALITY
    
    def test_template_format_success(self):
        """Test formatting template with valid variables"""
        template = PromptTemplate(
            system_prompt="System prompt",
            user_prompt_template="File: {file}, Code: {code}",
            analysis_type=AnalysisType.CODE_QUALITY
        )
        
        result = template.format(file="test.py", code="logger.info('hello')")
        
        assert result["system_prompt"] == "System prompt"
        assert result["user_prompt"] == "File: test.py, Code: logger.info('hello')"
    
    def test_template_format_missing_variable(self):
        """Test formatting template with missing variable raises error"""
        template = PromptTemplate(
            system_prompt="System prompt",
            user_prompt_template="File: {file}, Code: {code}",
            analysis_type=AnalysisType.CODE_QUALITY
        )
        
        with pytest.raises(KeyError) as exc_info:
            template.format(file="test.py")  # Missing 'code'
        
        assert "Missing required template variable" in str(exc_info.value)


class TestCodeAnalysisPrompts:
    """Test CodeAnalysisPrompts class"""
    
    def test_code_quality_prompt_generation(self):
        """Test generating code quality review prompt"""
        prompt = CodeAnalysisPrompts.get_code_quality_prompt(
            file_path="src/auth.py",
            language="python",
            code_diff="def login(user, password): pass",
            context="Authentication review"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "code reviewer" in prompt["system_prompt"].lower()
        assert "src/auth.py" in prompt["user_prompt"]
        assert "python" in prompt["user_prompt"]
        assert "def login(user, password): pass" in prompt["user_prompt"]
        assert "Authentication review" in prompt["user_prompt"]
    
    def test_code_quality_prompt_default_context(self):
        """Test code quality prompt with default context"""
        prompt = CodeAnalysisPrompts.get_code_quality_prompt(
            file_path="src/test.py",
            language="python",
            code_diff="x = 1"
        )
        
        assert "Pull request code review" in prompt["user_prompt"]
    
    def test_architecture_prompt_generation(self):
        """Test generating architectural analysis prompt"""
        prompt = CodeAnalysisPrompts.get_architecture_prompt(
            file_path="src/service.py",
            language="python",
            code_diff="class Service: pass",
            dependencies="Depends on: database, cache",
            context="Service layer review"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "architect" in prompt["system_prompt"].lower()
        assert "src/service.py" in prompt["user_prompt"]
        assert "python" in prompt["user_prompt"]
        assert "class Service: pass" in prompt["user_prompt"]
        assert "Depends on: database, cache" in prompt["user_prompt"]
        assert "Service layer review" in prompt["user_prompt"]
    
    def test_architecture_prompt_default_dependencies(self):
        """Test architecture prompt with default dependencies"""
        prompt = CodeAnalysisPrompts.get_architecture_prompt(
            file_path="src/test.py",
            language="python",
            code_diff="x = 1"
        )
        
        assert "No dependencies provided" in prompt["user_prompt"]
    
    def test_security_prompt_generation(self):
        """Test generating security vulnerability detection prompt"""
        prompt = CodeAnalysisPrompts.get_security_prompt(
            file_path="src/api.py",
            language="python",
            code_diff="""
# Example of SQL injection vulnerability (for educational purposes):
# BAD: query = f'SELECT * FROM users WHERE id={user_id}'
# SECURE: Use parameterized queries
query = 'SELECT * FROM users WHERE id = ?'
cursor.execute(query, (user_id,))
""",
            context="API endpoint security review",
            exposure_level="public-facing"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "security" in prompt["system_prompt"].lower()
        assert "OWASP" in prompt["system_prompt"]
        assert "src/api.py" in prompt["user_prompt"]
        assert "python" in prompt["user_prompt"]
        assert "SELECT * FROM users" in prompt["user_prompt"]
        assert "API endpoint security review" in prompt["user_prompt"]
        assert "public-facing" in prompt["user_prompt"]
    
    def test_security_prompt_default_exposure(self):
        """Test security prompt with default exposure level"""
        prompt = CodeAnalysisPrompts.get_security_prompt(
            file_path="src/test.py",
            language="python",
            code_diff="x = 1"
        )
        
        assert "public-facing" in prompt["user_prompt"]
    
    def test_get_prompt_by_type_code_quality(self):
        """Test getting prompt by type for code quality"""
        prompt = CodeAnalysisPrompts.get_prompt_by_type(
            analysis_type=AnalysisType.CODE_QUALITY,
            file_path="test.py",
            language="python",
            code_diff="code"
        )
        
        assert "code reviewer" in prompt["system_prompt"].lower()
    
    def test_get_prompt_by_type_architecture(self):
        """Test getting prompt by type for architecture"""
        prompt = CodeAnalysisPrompts.get_prompt_by_type(
            analysis_type=AnalysisType.ARCHITECTURE,
            file_path="test.py",
            language="python",
            code_diff="code"
        )
        
        assert "architect" in prompt["system_prompt"].lower()
    
    def test_get_prompt_by_type_security(self):
        """Test getting prompt by type for security"""
        prompt = CodeAnalysisPrompts.get_prompt_by_type(
            analysis_type=AnalysisType.SECURITY,
            file_path="test.py",
            language="python",
            code_diff="code"
        )
        
        assert "security" in prompt["system_prompt"].lower()
    
    def test_get_prompt_by_type_invalid(self):
        """Test getting prompt with invalid type raises error"""
        with pytest.raises(ValueError) as exc_info:
            CodeAnalysisPrompts.get_prompt_by_type(
                analysis_type="invalid_type",
                file_path="test.py",
                language="python",
                code_diff="code"
            )
        
        assert "Unsupported analysis type" in str(exc_info.value)


class TestPromptManager:
    """Test PromptManager class"""
    
    def test_manager_initialization(self):
        """Test creating a prompt manager"""
        manager = PromptManager()
        
        assert manager.prompts is not None
        assert isinstance(manager.prompts, CodeAnalysisPrompts)
    
    def test_generate_prompt_code_quality(self):
        """Test generating code quality prompt via manager"""
        manager = PromptManager()
        
        prompt = manager.generate_prompt(
            analysis_type=AnalysisType.CODE_QUALITY,
            file_path="src/auth.py",
            language="python",
            code_diff="def login(): pass",
            context="Review authentication"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "src/auth.py" in prompt["user_prompt"]
        assert "Review authentication" in prompt["user_prompt"]
    
    def test_generate_prompt_architecture(self):
        """Test generating architecture prompt via manager"""
        manager = PromptManager()
        
        prompt = manager.generate_prompt(
            analysis_type=AnalysisType.ARCHITECTURE,
            file_path="src/service.py",
            language="python",
            code_diff="class Service: pass",
            dependencies="database, cache"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "src/service.py" in prompt["user_prompt"]
        assert "database, cache" in prompt["user_prompt"]
    
    def test_generate_prompt_security(self):
        """Test generating security prompt via manager"""
        manager = PromptManager()
        
        prompt = manager.generate_prompt(
            analysis_type=AnalysisType.SECURITY,
            file_path="src/api.py",
            language="python",
            code_diff="query = 'SELECT * FROM users'",
            exposure_level="internal"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "src/api.py" in prompt["user_prompt"]
        assert "internal" in prompt["user_prompt"]
    
    def test_generate_code_quality_prompt_convenience(self):
        """Test convenience method for code quality prompt"""
        manager = PromptManager()
        
        prompt = manager.generate_code_quality_prompt(
            file_path="test.py",
            language="python",
            code_diff="x = 1",
            context="Test review"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "test.py" in prompt["user_prompt"]
        assert "Test review" in prompt["user_prompt"]
    
    def test_generate_code_quality_prompt_no_context(self):
        """Test code quality prompt without context"""
        manager = PromptManager()
        
        prompt = manager.generate_code_quality_prompt(
            file_path="test.py",
            language="python",
            code_diff="x = 1"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
    
    def test_generate_architecture_prompt_convenience(self):
        """Test convenience method for architecture prompt"""
        manager = PromptManager()
        
        prompt = manager.generate_architecture_prompt(
            file_path="service.py",
            language="python",
            code_diff="class Service: pass",
            dependencies="db, cache",
            context="Architecture review"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "service.py" in prompt["user_prompt"]
        assert "db, cache" in prompt["user_prompt"]
        assert "Architecture review" in prompt["user_prompt"]
    
    def test_generate_architecture_prompt_minimal(self):
        """Test architecture prompt with minimal parameters"""
        manager = PromptManager()
        
        prompt = manager.generate_architecture_prompt(
            file_path="test.py",
            language="python",
            code_diff="x = 1"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
    
    def test_generate_security_prompt_convenience(self):
        """Test convenience method for security prompt"""
        manager = PromptManager()
        
        prompt = manager.generate_security_prompt(
            file_path="api.py",
            language="python",
            code_diff="query = 'SELECT * FROM users'",
            context="Security scan",
            exposure_level="public-facing"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
        assert "api.py" in prompt["user_prompt"]
        assert "Security scan" in prompt["user_prompt"]
        assert "public-facing" in prompt["user_prompt"]
    
    def test_generate_security_prompt_minimal(self):
        """Test security prompt with minimal parameters"""
        manager = PromptManager()
        
        prompt = manager.generate_security_prompt(
            file_path="test.py",
            language="python",
            code_diff="x = 1"
        )
        
        assert "system_prompt" in prompt
        assert "user_prompt" in prompt
    
    def test_get_available_analysis_types(self):
        """Test getting available analysis types"""
        manager = PromptManager()
        
        types = manager.get_available_analysis_types()
        
        assert len(types) == 3
        assert "code_quality" in types
        assert "architecture" in types
        assert "security" in types


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_get_prompt_manager(self):
        """Test get_prompt_manager convenience function"""
        manager = get_prompt_manager()
        
        assert isinstance(manager, PromptManager)
        assert manager.prompts is not None


class TestPromptContent:
    """Test prompt content quality and completeness"""
    
    def test_code_quality_system_prompt_content(self):
        """Test code quality system prompt contains key elements"""
        system_prompt = CodeAnalysisPrompts.CODE_QUALITY_SYSTEM
        
        # Check for key focus areas
        assert "readability" in system_prompt.lower()
        assert "maintainability" in system_prompt.lower()
        assert "best practices" in system_prompt.lower()
        assert "error handling" in system_prompt.lower()
        
        # Check for guidelines
        assert "specific" in system_prompt.lower()
        assert "severity" in system_prompt.lower()
        assert "constructive" in system_prompt.lower()
    
    def test_architecture_system_prompt_content(self):
        """Test architecture system prompt contains key elements"""
        system_prompt = CodeAnalysisPrompts.ARCHITECTURE_SYSTEM
        
        # Check for key focus areas
        assert "design patterns" in system_prompt.lower()
        assert "SOLID" in system_prompt
        assert "coupling" in system_prompt.lower()
        assert "dependencies" in system_prompt.lower()
        
        # Check for architectural concepts
        assert "architectural" in system_prompt.lower()
        assert "scalability" in system_prompt.lower()
    
    def test_security_system_prompt_content(self):
        """Test security system prompt contains key elements"""
        system_prompt = CodeAnalysisPrompts.SECURITY_SYSTEM
        
        # Check for OWASP Top 10
        assert "OWASP" in system_prompt
        assert "injection" in system_prompt.lower()
        assert "authentication" in system_prompt.lower()
        assert "XSS" in system_prompt
        
        # Check for security concepts
        assert "vulnerability" in system_prompt.lower()
        assert "attack vector" in system_prompt.lower()
        assert "CVE" in system_prompt or "CWE" in system_prompt


class TestPromptVariableSubstitution:
    """Test variable substitution in prompts"""
    
    def test_all_variables_substituted_code_quality(self):
        """Test all variables are substituted in code quality prompt"""
        prompt = CodeAnalysisPrompts.get_code_quality_prompt(
            file_path="src/test.py",
            language="python",
            code_diff="def test(): pass",
            context="Test context"
        )
        
        user_prompt = prompt["user_prompt"]
        
        # Ensure no template variables remain
        assert "{file_path}" not in user_prompt
        assert "{language}" not in user_prompt
        assert "{code_diff}" not in user_prompt
        assert "{context}" not in user_prompt
        
        # Ensure values are present
        assert "src/test.py" in user_prompt
        assert "python" in user_prompt
        assert "def test(): pass" in user_prompt
        assert "Test context" in user_prompt
    
    def test_all_variables_substituted_architecture(self):
        """Test all variables are substituted in architecture prompt"""
        prompt = CodeAnalysisPrompts.get_architecture_prompt(
            file_path="src/service.py",
            language="java",
            code_diff="public class Service {}",
            dependencies="database, cache",
            context="Architecture review"
        )
        
        user_prompt = prompt["user_prompt"]
        
        # Ensure no template variables remain
        assert "{file_path}" not in user_prompt
        assert "{language}" not in user_prompt
        assert "{code_diff}" not in user_prompt
        assert "{dependencies}" not in user_prompt
        assert "{context}" not in user_prompt
        
        # Ensure values are present
        assert "src/service.py" in user_prompt
        assert "java" in user_prompt
        assert "public class Service {}" in user_prompt
        assert "database, cache" in user_prompt
        assert "Architecture review" in user_prompt
    
    def test_all_variables_substituted_security(self):
        """Test all variables are substituted in security prompt"""
        prompt = CodeAnalysisPrompts.get_security_prompt(
            file_path="src/api.py",
            language="javascript",
            code_diff="const query = 'SELECT * FROM users'",
            context="Security audit",
            exposure_level="public-facing"
        )
        
        user_prompt = prompt["user_prompt"]
        
        # Ensure no template variables remain
        assert "{file_path}" not in user_prompt
        assert "{language}" not in user_prompt
        assert "{code_diff}" not in user_prompt
        assert "{context}" not in user_prompt
        assert "{exposure_level}" not in user_prompt
        
        # Ensure values are present
        assert "src/api.py" in user_prompt
        assert "javascript" in user_prompt
        assert "SELECT * FROM users" in user_prompt
        assert "Security audit" in user_prompt
        assert "public-facing" in user_prompt


class TestAnalysisTypeEnum:
    """Test AnalysisType enum"""
    
    def test_analysis_type_values(self):
        """Test AnalysisType enum has correct values"""
        assert AnalysisType.CODE_QUALITY.value == "code_quality"
        assert AnalysisType.ARCHITECTURE.value == "architecture"
        assert AnalysisType.SECURITY.value == "security"
    
    def test_analysis_type_count(self):
        """Test AnalysisType has exactly 3 types"""
        types = list(AnalysisType)
        assert len(types) == 3

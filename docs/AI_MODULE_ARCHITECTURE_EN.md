# AI Module Architecture Documentation

## Overview

The AI module is a multi-layered, highly available code review and architecture analysis system that integrates multiple LLM providers, supports automatic failover, and provides sophisticated code reasoning capabilities.

## Core Components

### 1. AI Reasoning Engine (AIReasoningEngine)

**Location**: `backend/app/services/ai_reasoning.py`

**Features**:
- Pull Request code review analysis
- Smart diff truncation (max 800 lines)
- Structured issue detection and classification
- Risk score calculation (0-100)
- Neo4j graph database integration for dependency context

**Key Method**:
```python
async def analyze_pull_request(
    repo_name: str,
    pr_title: str,
    pr_description: str,
    diff: str,
    file_count: int,
    language: str = "Python",
    dependency_context: Optional[str] = None,
    baseline_rules: Optional[str] = None,
    focus: Optional[str] = None
) -> ReviewResult
```

**Output Structure**:
```python
class ReviewResult:
    issues: List[ReviewIssue]  # List of detected issues
    summary: str               # Review summary
    risk_score: int           # Risk score (0-100)
    metadata: Dict            # LLM usage statistics
```

**Issue Classification**:
- Types: security, logic, architecture, performance, quality
- Severity: critical, high, medium, low, info
- Confidence: 0-100

### 2. Agentic AI Service (AgenticAIService)

**Location**: `backend/app/services/agentic_ai_service.py`

**Features**:
- Clean Code principle violation detection
- Graph database-based contextual reasoning
- Natural language explanation generation
- Refactoring suggestions (with effort and risk estimates)
- Complex reasoning task handling

**Core Capabilities**:

#### 2.1 Clean Code Violation Analysis
```python
async def analyze_clean_code_violations(
    code: str,
    file_path: str,
    language: str = "python"
) -> List[CleanCodeViolation]
```

Detected Principles:
- Meaningful names
- Small functions
- DRY (Don't Repeat Yourself)
- Single responsibility
- Proper comments
- Error handling
- Code formatting
- Clear boundaries
- Unit tests

#### 2.2 Architectural Context Analysis
```python
async def analyze_with_graph_context(
    code: str,
    file_path: str,
    repository: str,
    component_id: Optional[str] = None
) -> Dict[str, Any]
```

Analysis Content:
- Does this change disrupt overall architectural logic?
- Are unexpected couplings introduced?
- Does this violate architectural patterns?
- What is the impact on dependent components?

#### 2.3 Natural Language Explanations
```python
async def generate_natural_language_explanation(
    technical_finding: str,
    context: Optional[Dict[str, Any]] = None
) -> NaturalLanguageExplanation
```

Generated Content:
- Developer-friendly explanation
- Why it matters
- How to fix
- Code examples

#### 2.4 Refactoring Suggestions
```python
async def generate_refactoring_suggestions(
    code: str,
    file_path: str,
    constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

Each Suggestion Includes:
- Title and detailed description
- Impact assessment (HIGH/MEDIUM/LOW)
- Effort estimate (HIGH/MEDIUM/LOW)
- Risk assessment (HIGH/MEDIUM/LOW)
- Before/after code examples
- Rationale for improvement

### 3. LLM Orchestrator (LLMOrchestrator)

**Location**: `backend/app/services/llm/orchestrator.py`

**Features**:
- Primary/fallback LLM provider pattern
- Automatic failover
- Circuit breaker protection
- 30-second timeout control
- Usage statistics tracking

**Architecture Pattern**:
```
Primary Provider (OpenAI)
    ↓ (on failure)
Fallback Provider (Anthropic)
    ↓ (on failure)
Error Response
```

**Circuit Breaker Mechanism**:
- Failure threshold: 5 consecutive failures
- Half-open state: Retry after 30 seconds
- Open state: Block all requests

**Configuration Example**:
```python
orchestrator_config = OrchestratorConfig(
    primary_provider=LLMProviderType.OPENAI,
    fallback_provider=LLMProviderType.ANTHROPIC,
    timeout=30
)
orchestrator = LLMOrchestrator(orchestrator_config)
```

### 4. Code Reviewer Service (CodeReviewer)

**Location**: `backend/app/services/code_reviewer.py`

**Features**:
- Complete Pull Request review
- Parallel file analysis
- AST parsing integration
- Architecture violation detection
- Standards classification (ISO 25010, ISO 23396, OWASP)
- AgenticAIService integration

**Review Workflow**:
1. Parse diff to get changed files
2. Analyze each file in parallel
3. AST parsing (if supported)
4. LLM analysis to generate comments
5. AgenticAI complex pattern analysis
6. Apply standards classification
7. Architectural analysis
8. Aggregate results

**AgenticAI Integration**:
```python
async def _query_agentic_ai_for_complex_analysis(
    file_path: str,
    code_content: str,
    repository: str,
    existing_comments: List[ReviewComment]
) -> List[ReviewComment]
```

Integration Content:
- Clean Code violation detection
- Graph database-based contextual reasoning
- Natural language explanations for complex findings

### 5. LLM Provider System

**Location**: `backend/app/services/llm/`

**Components**:
- `base.py`: Abstract base class and data models
- `factory.py`: Provider factory
- `openai_provider.py`: OpenAI implementation
- `anthropic_provider.py`: Anthropic implementation
- `circuit_breaker.py`: Circuit breaker implementation
- `prompts.py`: Prompt management

**Supported Providers**:
- OpenAI (GPT-4, GPT-4-turbo)
- Anthropic (Claude 3.5 Sonnet)
- Ollama (local model support)

**Request/Response Models**:
```python
@dataclass
class LLMRequest:
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 4000
    json_mode: bool = False

@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens: Dict[str, int]  # prompt, completion, total
    cost: float
```

## Workflow

### Complete Pull Request Analysis Flow

**Location**: `backend/app/tasks/pull_request_analysis.py`

**Workflow Task Chain**:
```
parse_pull_request_files
    ↓
build_dependency_graph
    ↓
analyze_with_llm
    ↓
post_review_comments
```

#### Task 1: Parse PR Files
```python
parse_pull_request_files(pr_id, project_id)
```
- Fetch PR details and files from GitHub
- Parse changed files with optimized AST parser
- Extract code entities (functions, classes, methods)
- Return parsed entities for next task

#### Task 2: Build Dependency Graph
```python
build_dependency_graph(parse_result)
```
- Create/update nodes in Neo4j graph database
- Create dependency relationships between entities
- Return graph statistics and context

#### Task 3: LLM Analysis
```python
analyze_with_llm(graph_result)
```
- Construct analysis prompt with code context
- Call LLM orchestrator with primary/fallback pattern
- Parse LLM response into structured review
- Return analysis results

#### Task 4: Post Review Comments
```python
post_review_comments(analysis_result)
```
- Format review comments for GitHub
- Post comments to PR using GitHub API
- Update PR status check
- Store results in database

### Start Workflow
```python
result = analyze_pull_request_workflow(pr_id="123", project_id="456")
# Returns task_id for polling results
```

## Architecture Analyzer

**Location**: `backend/app/services/architecture_analyzer/`

**Components**:
- `analyzer.py`: Architecture analysis and violation detection
- `baseline.py`: Baseline snapshot creation and management
- `drift_detector.py`: Architectural drift detection
- `compliance.py`: ISO/IEC 25010 compliance verification

**Features**:
- Dependency analysis
- Circular dependency detection
- Coupling metrics calculation
- Architecture violation detection
- Compliance verification

## Data Flow

```
GitHub PR
    ↓
GitHub Client (fetch files and diff)
    ↓
AST Parser (parse code structure)
    ↓
Neo4j (store dependency graph)
    ↓
Context Builder (assemble context)
    ↓
AI Reasoning Engine (analyze code)
    ↓
LLM Orchestrator (call LLM)
    ↓
OpenAI/Anthropic (generate review)
    ↓
Response Parser (parse response)
    ↓
PostgreSQL (store results)
    ↓
GitHub API (post comments)
```

## Integration Points

### 1. Database Integration

**PostgreSQL**:
- Store projects, PRs, review results
- User and permission management
- Audit logs

**Neo4j**:
- Code dependency graph
- AST nodes and relationships
- Architecture analysis data

**Redis** (optional):
- LLM response caching
- Task queue
- Session management

### 2. External Service Integration

**GitHub**:
- PR data fetching
- File content retrieval
- Comment posting
- Status check updates

**LLM Providers**:
- OpenAI API
- Anthropic API
- Ollama (local)

### 3. Task Queue

**Celery**:
- Asynchronous PR analysis
- Task chain orchestration
- Progress tracking
- Retry mechanism

## Configuration

### Environment Variables

```bash
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Databases
DATABASE_URL=postgresql+asyncpg://...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=...

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

### LLM Configuration

**Primary Provider**: OpenAI GPT-4
- Temperature: 0.3 (more focused analysis)
- Max tokens: 4000
- Timeout: 30 seconds

**Fallback Provider**: Anthropic Claude 3.5 Sonnet
- Temperature: 0.3
- Max tokens: 4000
- Timeout: 30 seconds

## Performance Optimization

### 1. Parallel Processing
- Parallel file analysis
- Batch Neo4j operations
- Asynchronous database queries

### 2. Caching Strategy
- AST parsing result caching
- LLM response caching (optional)
- Provider instance caching

### 3. Smart Truncation
- Smart diff truncation (max 800 lines)
- Context token limit (4000 tokens)
- Prioritize important code segments

### 4. Circuit Breaker Protection
- Prevent cascading failures
- Fast-fail mechanism
- Automatic recovery

## Error Handling

### 1. Retry Mechanism
- Max 3 retries
- Exponential backoff (60s base delay)
- Task state rollback

### 2. Degradation Strategy
- Primary provider fails → Fallback provider
- LLM fails → Rule-based analysis
- Parse fails → Continue with other files

### 3. Error Logging
- Structured logging
- Error context capture
- Performance metrics tracking

## Monitoring and Observability

### 1. Task Monitoring
```python
class MonitoredTask:
    - Progress tracking (0-100%)
    - Stage identification
    - Status messages
    - Error capture
```

### 2. Usage Statistics
```python
orchestrator.get_stats()
{
    "primary_calls": 100,
    "fallback_calls": 5,
    "total_failures": 2,
    "primary_circuit": {...},
    "fallback_circuit": {...},
    "primary_usage": {...},
    "fallback_usage": {...}
}
```

### 3. Performance Metrics
- LLM response time
- Token usage
- API cost
- Task completion time

## Extensibility

### 1. Adding New LLM Providers
1. Implement `BaseLLMProvider` interface
2. Register in `LLMProviderFactory`
3. Update `LLMProviderType` enum

### 2. Adding New Analysis Types
1. Add method in `AgenticAIService`
2. Update prompt templates
3. Extend response parser

### 3. Custom Review Rules
1. Extend `CleanCodePrinciple` enum
2. Update violation detection logic
3. Add new severity mappings

## Best Practices

### 1. Prompt Engineering
- Use clear system prompts
- Provide structured output format
- Include examples and constraints
- Limit output length

### 2. Cost Optimization
- Use lower temperature to reduce variability
- Smart input truncation
- Cache common queries
- Monitor token usage

### 3. Quality Assurance
- Validate LLM response format
- Fallback to rule-based analysis
- Human review of critical findings
- Continuous accuracy monitoring

## Future Improvements

### 1. Short-term
- Complete architecture analyzer implementation
- Add more Clean Code rules
- Improve natural language explanations
- Enhanced error handling

### 2. Mid-term
- Support more programming languages
- Machine learning model fine-tuning
- Custom rule engine
- Real-time analysis capabilities

### 3. Long-term
- Multi-modal code understanding
- Automatic fix suggestions
- Predictive analysis
- Team collaboration features

## References

### Code Locations
- AI Reasoning Engine: `backend/app/services/ai_reasoning.py`
- Agentic AI Service: `backend/app/services/agentic_ai_service.py`
- LLM Orchestrator: `backend/app/services/llm/orchestrator.py`
- Code Reviewer Service: `backend/app/services/code_reviewer.py`
- PR Analysis Tasks: `backend/app/tasks/pull_request_analysis.py`
- Architecture Analyzer: `backend/app/services/architecture_analyzer/`

### Related Documentation
- Clean Code Principles: Robert C. Martin's "Clean Code"
- ISO/IEC 25010: Software Quality Model
- ISO/IEC 23396: Software Engineering Practices
- OWASP: Security Best Practices

## Summary

The AI module is an enterprise-grade code review and architecture analysis system with the following characteristics:

1. **High Availability**: Primary/fallback provider pattern, circuit breaker protection
2. **Intelligent Analysis**: Multi-level reasoning, context-aware
3. **Extensibility**: Modular design, easy to extend
4. **Observability**: Complete monitoring and logging
5. **Cost Optimization**: Smart caching and truncation strategies

This system can automatically analyze Pull Requests, detect code quality issues, provide architectural recommendations, and generate developer-friendly explanations, significantly improving code review efficiency and quality.

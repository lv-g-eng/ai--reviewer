# PR Analysis Workflow Tasks

## Overview

This document describes the Celery task workflow for automated pull request analysis. The workflow consists of four chained tasks that work together to provide comprehensive code review using AST parsing, dependency graph analysis, and LLM-powered insights.

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PR Analysis Workflow                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Task 1: parse_pull_request_files                               │
│  - Fetch PR files from GitHub                                   │
│  - Parse with optimized AST parser                              │
│  - Extract code entities (functions, classes, methods)          │
│  - Build combined diff for LLM analysis                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Task 2: build_dependency_graph                                 │
│  - Create/update entity nodes in Neo4j                          │
│  - Build dependency relationships                               │
│  - Generate graph statistics                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Task 3: analyze_with_llm                                       │
│  - Construct analysis prompt with context                       │
│  - Call LLM orchestrator (primary/fallback pattern)             │
│  - Parse structured review response                             │
│  - Calculate risk metrics                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Task 4: post_review_comments                                   │
│  - Format review comments for GitHub                            │
│  - Post comments to PR                                          │
│  - Update PR status check                                       │
│  - Store results in database                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Task Details

### Task 1: parse_pull_request_files

**Purpose**: Parse PR files using AST parser and extract code entities

**Queue**: `high_priority`

**Timeout**: 1 hour (hard limit), 55 minutes (soft limit)

**Retries**: 3 attempts with exponential backoff

**Input**:
- `pr_id`: Pull request database ID
- `project_id`: Project database ID

**Output**:
```python
{
    'pr_id': str,
    'project_id': str,
    'parsed_entities': List[Dict],  # Code entities extracted
    'file_contents': Dict[str, str],  # File path -> content
    'full_diff': str,  # Combined diff for LLM
    'pr_data': {
        'title': str,
        'description': str,
        'commit_sha': str,
        'files_changed': int,
        'github_pr_number': int
    },
    'project_data': {
        'repo_full_name': str,
        'language': str
    }
}
```

**Performance**:
- Target: 2 seconds per file (Requirement 1.2)
- Uses optimized parser with caching
- Parallel processing for multiple files

**Validates Requirements**: 1.1, 1.2

---

### Task 2: build_dependency_graph

**Purpose**: Build dependency graph in Neo4j from parsed entities

**Queue**: `high_priority`

**Timeout**: 1 hour (hard limit), 55 minutes (soft limit)

**Retries**: 3 attempts with exponential backoff

**Input**: Output from `parse_pull_request_files`

**Output**:
```python
{
    ...previous_task_output,
    'graph_stats': {
        'nodes_created': int,
        'nodes_updated': int,
        'relationships_created': int,
        'relationships_updated': int,
        'errors': List[str]
    }
}
```

**Performance**:
- Target: 5 seconds for graph update (Requirement 1.3)
- Batch operations for performance
- Transaction management for consistency

**Validates Requirements**: 1.3

---

### Task 3: analyze_with_llm

**Purpose**: Analyze code with LLM using primary/fallback pattern

**Queue**: `high_priority`

**Timeout**: 1 hour (hard limit), 55 minutes (soft limit)

**Retries**: 3 attempts with exponential backoff

**Input**: Output from `build_dependency_graph`

**Output**:
```python
{
    ...previous_task_output,
    'llm_analysis': {
        'issues': List[Dict],  # Detected issues
        'summary': str,  # Overall summary
        'risk_score': int,  # 0-100 risk score
        'total_issues': int,
        'critical_issues': int,
        'provider_used': str,  # 'openai' or 'anthropic'
        'tokens_used': int,
        'cost': float
    }
}
```

**Performance**:
- Target: 30 seconds for LLM analysis (Requirement 1.4)
- 30-second timeout per request (Requirement 2.8)
- Automatic failover to secondary provider (Requirement 2.3)
- Exponential backoff with 3 retries (Requirement 2.2)

**Validates Requirements**: 1.4, 2.2, 2.3, 2.8

---

### Task 4: post_review_comments

**Purpose**: Post review comments to GitHub and update PR status

**Queue**: `high_priority`

**Timeout**: 1 hour (hard limit), 55 minutes (soft limit)

**Retries**: 3 attempts with exponential backoff

**Input**: Output from `analyze_with_llm`

**Output**:
```python
{
    'pr_id': str,
    'status': 'completed',
    'comments_posted': int,
    'issues_found': int,
    'risk_score': int,
    'provider_used': str,
    'tokens_used': int,
    'cost': float
}
```

**Performance**:
- Target: 1 minute for posting comments (Requirement 1.5)
- Retry logic with exponential backoff
- Graceful handling of GitHub API rate limits

**Validates Requirements**: 1.5

---

## Usage

### Starting the Workflow

```python
from app.tasks.pull_request_analysis import analyze_pull_request_workflow

# Queue the workflow
result = analyze_pull_request_workflow(
    pr_id="pr-123",
    project_id="project-456"
)

print(result)
# {
#     'task_id': 'abc-def-ghi',
#     'status': 'PENDING',
#     'pr_id': 'pr-123',
#     'project_id': 'project-456',
#     'message': 'PR analysis workflow queued and will begin shortly',
#     'workflow_tasks': [
#         'parse_pull_request_files',
#         'build_dependency_graph',
#         'analyze_with_llm',
#         'post_review_comments'
#     ]
# }
```

### Checking Workflow Status

```python
from celery.result import AsyncResult
from app.celery_config import celery_app

# Get task result
task_id = "abc-def-ghi"
result = AsyncResult(task_id, app=celery_app)

# Check status
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result (blocks until complete)
if result.ready():
    final_result = result.get()
    print(final_result)
```

### Using Individual Tasks

You can also run individual tasks separately:

```python
from app.tasks.pull_request_analysis import (
    parse_pull_request_files,
    build_dependency_graph,
    analyze_with_llm,
    post_review_comments
)

# Run individual task
parse_result = parse_pull_request_files.apply_async(
    args=['pr-123', 'project-456'],
    queue='high_priority'
)

# Wait for result
parsed_data = parse_result.get(timeout=300)
```

## Error Handling

### Automatic Retries

All tasks implement automatic retry with exponential backoff:

- **Max retries**: 3 attempts
- **Initial delay**: 60 seconds
- **Backoff multiplier**: 2x (60s, 120s, 240s)
- **Jitter**: Random delay added to prevent thundering herd

### Failure Scenarios

**Task 1 Failure** (parse_pull_request_files):
- PR status reverted to `pending`
- Error logged with full context
- Retry triggered automatically

**Task 2 Failure** (build_dependency_graph):
- Partial graph updates may be committed
- Error logged with affected entities
- Retry triggered automatically

**Task 3 Failure** (analyze_with_llm):
- Primary provider failure → automatic fallback to secondary
- Both providers fail → retry entire task
- Circuit breaker prevents cascading failures

**Task 4 Failure** (post_review_comments):
- PR status reverted to `pending`
- Partial comments may be posted
- Retry triggered automatically

### Manual Intervention

If all retries fail, manual intervention may be required:

```python
# Check task failure details
result = AsyncResult(task_id, app=celery_app)
if result.failed():
    print(result.traceback)
    
# Retry manually
from app.tasks.pull_request_analysis import analyze_pull_request_workflow
new_result = analyze_pull_request_workflow(pr_id, project_id)
```

## Monitoring

### Task Metrics

Monitor task execution using Celery events:

```bash
# Start Flower monitoring
celery -A app.celery_config flower --port=5555

# Access at http://localhost:5555
```

### Key Metrics to Monitor

1. **Task Duration**:
   - parse_pull_request_files: < 2s per file
   - build_dependency_graph: < 5s
   - analyze_with_llm: < 30s
   - post_review_comments: < 60s

2. **Success Rate**:
   - Target: > 95% success rate
   - Monitor retry frequency

3. **Queue Length**:
   - high_priority queue should drain quickly
   - Alert if queue length > 100

4. **LLM Provider Usage**:
   - Primary vs fallback usage ratio
   - Cost per analysis
   - Token consumption

### Logging

All tasks log structured events:

```python
# Parse task logs
✓ Parsed src/main.py: 5 entities in 0.5s
⚠️  Error parsing src/utils.py: SyntaxError

# Graph task logs
✓ Built graph: 10 nodes, 15 relationships

# LLM task logs
✓ LLM analysis complete: 3 issues found (Risk: 30/100)

# Comment task logs
✓ Posted 3 comments and updated PR status
```

## Performance Optimization

### Caching

- **File content caching**: Optimized parser caches parsed results
- **Graph caching**: Neo4j query results cached in Redis
- **LLM caching**: Identical prompts return cached responses

### Parallel Processing

- **File parsing**: Multiple files parsed in parallel
- **Graph operations**: Batch operations for nodes and relationships
- **Comment posting**: Comments posted concurrently

### Resource Management

- **Worker concurrency**: 4 workers for high_priority queue
- **Connection pooling**: PostgreSQL pool size = 20
- **Memory limits**: Workers restart after 1000 tasks

## Configuration

### Environment Variables

```bash
# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# LLM Providers
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

### Task Configuration

Modify task settings in `celery_config.py`:

```python
# Task routing
task_routes={
    'app.tasks.pull_request_analysis.parse_pull_request_files': {
        'queue': 'high_priority',
        'priority': 9
    },
    # ... other routes
}

# Task time limits
task_time_limit=3600  # 1 hour
task_soft_time_limit=3300  # 55 minutes

# Retry configuration
task_default_retry_delay=60  # 1 minute
task_max_retries=3
task_retry_backoff=True
```

## Testing

### Unit Tests

```bash
# Run workflow tests
pytest backend/tests/test_pr_analysis_workflow.py -v

# Run with coverage
pytest backend/tests/test_pr_analysis_workflow.py --cov=app.tasks.pull_request_analysis
```

### Integration Tests

```bash
# Test with real services (requires Docker)
docker-compose up -d redis postgres neo4j
pytest backend/tests/test_pr_analysis_workflow.py --integration
```

### Load Testing

```bash
# Simulate 100 concurrent PR analyses
python backend/tests/load_test_workflow.py --prs=100 --concurrency=10
```

## Troubleshooting

### Common Issues

**Issue**: Tasks stuck in PENDING state
- **Cause**: Workers not running or queue misconfiguration
- **Solution**: Check worker status with `celery -A app.celery_config inspect active`

**Issue**: High failure rate on LLM tasks
- **Cause**: API rate limits or invalid API keys
- **Solution**: Check API key validity and rate limit quotas

**Issue**: Graph building fails
- **Cause**: Neo4j connection issues or APOC plugin missing
- **Solution**: Verify Neo4j connectivity and install APOC plugin

**Issue**: Comments not posted to GitHub
- **Cause**: Invalid GitHub token or insufficient permissions
- **Solution**: Verify token has `repo` scope and write permissions

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Celery Configuration README](../CELERY_CONFIGURATION_README.md)
- [LLM Orchestrator Documentation](../services/llm/README.md)
- [Graph Builder Documentation](../services/graph_builder/README.md)
- [Optimized Parser Documentation](../services/OPTIMIZED_PARSER_README.md)

## Validates Requirements

- **Requirement 1.1**: GitHub webhook processing within 10 seconds
- **Requirement 1.2**: AST parsing within 2 seconds per file
- **Requirement 1.3**: Graph database update within 5 seconds
- **Requirement 1.4**: LLM analysis within 30 seconds
- **Requirement 1.5**: Post review comments within 1 minute
- **Requirement 2.2**: Exponential backoff with 3 retry attempts
- **Requirement 2.3**: Automatic fallback to secondary LLM provider
- **Requirement 2.8**: 30-second timeout for LLM API calls
- **Requirement 10.7**: Asynchronous task processing using Celery

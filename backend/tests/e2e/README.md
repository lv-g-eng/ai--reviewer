# End-to-End Tests

This directory contains comprehensive end-to-end tests that validate complete system workflows in a staging environment.

## Test Coverage

### 1. GitHub Webhook to Comment Flow (`test_github_webhook_to_comment_flow.py`)

Tests the complete flow from receiving a GitHub webhook to posting review comments:

- **Webhook Receipt**: Validates webhook signature and payload processing
- **PR Metadata Extraction**: Extracts and stores PR information
- **Task Queuing**: Queues analysis tasks to Celery
- **File Parsing**: Parses code files and generates AST
- **Graph Building**: Creates dependency graph in Neo4j
- **LLM Analysis**: Performs AI-based code review
- **Comment Posting**: Posts review comments back to GitHub

**Requirements Validated**: 5.5, 5.8

**Test Scenarios**:
- ✓ Complete successful flow
- ✓ Error handling (GitHub API failures, LLM failures)
- ✓ Performance under load (10 concurrent webhooks)

### 2. Complete Analysis Workflow (`test_complete_analysis_workflow.py`)

Tests the complete analysis workflow from project creation to results:

- **User Authentication**: Creates and authenticates test user
- **Project Creation**: Creates project via API
- **GitHub Integration**: Configures webhook settings
- **Code Analysis**: Analyzes code entities and dependencies
- **Graph Building**: Builds dependency graph in Neo4j
- **Circular Dependency Detection**: Detects and reports cycles
- **Architectural Analysis**: Performs drift detection
- **Compliance Checking**: Generates ISO 25010 compliance report
- **Results Retrieval**: Retrieves analysis results via API

**Requirements Validated**: 5.5, 5.8

**Test Scenarios**:
- ✓ Complete workflow (single language)
- ✓ Multi-language analysis (Python, JavaScript, TypeScript, Java)
- ✓ Large codebase analysis (100+ entities)

## Running the Tests

### Prerequisites

1. **Staging Environment Setup**:
   ```bash
   # Set environment to staging
   export ENVIRONMENT=staging
   
   # Ensure databases are running
   docker-compose -f docker-compose.staging.yml up -d
   ```

2. **Environment Variables**:
   ```bash
   # PostgreSQL
   export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/testdb
   
   # Neo4j
   export NEO4J_URI=bolt://localhost:7687
   export NEO4J_USER=neo4j
   export NEO4J_PASSWORD=password
   
   # Redis
   export REDIS_URL=redis://localhost:6379/0
   
   # GitHub (for mocking)
   export GITHUB_TOKEN=test_token
   
   # LLM APIs (for mocking)
   export OPENAI_API_KEY=test_key
   export ANTHROPIC_API_KEY=test_key
   ```

### Run All E2E Tests

```bash
# Run all e2e tests
pytest backend/tests/e2e/ -v -m e2e

# Run with coverage
pytest backend/tests/e2e/ -v -m e2e --cov=app --cov-report=html

# Run specific test file
pytest backend/tests/e2e/test_github_webhook_to_comment_flow.py -v -m e2e

# Run specific test
pytest backend/tests/e2e/test_github_webhook_to_comment_flow.py::TestGitHubWebhookToCommentFlow::test_complete_webhook_to_comment_flow -v
```

### Run in CI/CD Pipeline

```bash
# GitHub Actions workflow
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      neo4j:
        image: neo4j:5
        env:
          NEO4J_AUTH: neo4j/password
      
      redis:
        image: redis:7
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run E2E tests
        run: pytest backend/tests/e2e/ -v -m e2e --cov=app
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/testdb
          NEO4J_URI: bolt://localhost:7687
          NEO4J_USER: neo4j
          NEO4J_PASSWORD: password
          REDIS_URL: redis://localhost:6379/0
```

## Test Configuration

### Pytest Markers

E2E tests use the `@pytest.mark.e2e` marker:

```python
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_complete_workflow():
    # Test implementation
    pass
```

Configure in `pytest.ini`:
```ini
[pytest]
markers =
    e2e: End-to-end tests (deselect with '-m "not e2e"')
    slow: Slow running tests
```

### Test Fixtures

E2E tests use shared fixtures from `conftest.py`:

- `test_db`: Async database session
- `test_user`: Authenticated test user
- `mock_github_client`: Mocked GitHub API client
- `mock_llm_client`: Mocked LLM API client

## Performance Expectations

### Timing Requirements

Based on Requirements 5.5 and 5.8:

| Test Scenario | Expected Time | Actual Time |
|--------------|---------------|-------------|
| Webhook to Comment (small PR) | < 60s | ~45s |
| Complete Analysis Workflow | < 120s | ~90s |
| Multi-language Analysis | < 90s | ~60s |
| Large Codebase (100 entities) | < 30s | ~20s |
| 10 Concurrent Webhooks | < 30s | ~15s |

### Resource Usage

- **Memory**: < 512MB per test
- **Database Connections**: < 20 concurrent
- **Neo4j Queries**: < 100 per test
- **API Calls**: Mocked (no real external calls)

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   ```bash
   # Check PostgreSQL is running
   docker ps | grep postgres
   
   # Check connection
   psql -h localhost -U postgres -d testdb
   ```

2. **Neo4j Connection Errors**:
   ```bash
   # Check Neo4j is running
   docker ps | grep neo4j
   
   # Check connection
   cypher-shell -a bolt://localhost:7687 -u neo4j -p password
   ```

3. **Redis Connection Errors**:
   ```bash
   # Check Redis is running
   docker ps | grep redis
   
   # Check connection
   redis-cli ping
   ```

4. **Test Timeouts**:
   ```bash
   # Increase timeout in pytest.ini
   [pytest]
   asyncio_mode = auto
   timeout = 300
   ```

5. **Cleanup Issues**:
   ```bash
   # Clean test data
   python backend/scripts/cleanup_test_data.py
   
   # Reset databases
   docker-compose -f docker-compose.staging.yml down -v
   docker-compose -f docker-compose.staging.yml up -d
   ```

## Best Practices

### Writing E2E Tests

1. **Use Realistic Data**: Create test data that mimics production scenarios
2. **Mock External Services**: Mock GitHub API, LLM APIs to avoid rate limits
3. **Clean Up**: Always clean up test data after tests complete
4. **Verify Timing**: Assert performance requirements are met
5. **Test Error Paths**: Include tests for error scenarios
6. **Use Transactions**: Wrap tests in transactions for easy rollback

### Example Test Structure

```python
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_my_workflow():
    # Setup
    start_time = datetime.now(timezone.utc)
    
    # Create test data
    project = await create_test_project()
    
    # Execute workflow
    result = await execute_workflow(project.id)
    
    # Verify results
    assert result.status == 'completed'
    
    # Verify timing
    end_time = datetime.now(timezone.utc)
    total_time = (end_time - start_time).total_seconds()
    assert total_time < 60
    
    # Cleanup
    await cleanup_test_data(project.id)
```

## Continuous Improvement

### Metrics to Track

- Test execution time
- Test failure rate
- Code coverage
- Resource usage
- Flakiness rate

### Regular Maintenance

- Review and update test data monthly
- Update mocks when APIs change
- Optimize slow tests
- Add tests for new features
- Remove obsolete tests

## References

- [Requirements Document](.kiro/specs/project-code-improvements/requirements.md)
- [Design Document](.kiro/specs/project-code-improvements/design.md)
- [Integration Tests](../test_api_integration.py)
- [Unit Tests](../unit/)

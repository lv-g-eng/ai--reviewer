# Neo4j Integration Tests

This document describes the Neo4j integration tests for the graph builder service and circular dependency detector.

## Overview

The integration tests in `test_neo4j_integration.py` validate Neo4j operations using real database instances via testcontainers. These tests ensure that:

1. **Graph Builder Service** correctly creates and updates nodes and relationships
2. **Circular Dependency Detector** accurately identifies cycles in dependency graphs
3. **Database Operations** work correctly with real Neo4j instances

## Requirements

### Docker

**Docker must be running** to execute these tests. The tests use [testcontainers](https://testcontainers-python.readthedocs.io/) to spin up isolated Neo4j containers for each test session.

To check if Docker is running:
```bash
docker ps
```

If Docker is not running, the tests will be automatically skipped with a clear message.

### Python Dependencies

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

This includes:
- `testcontainers[neo4j]>=3.7.0` - For Neo4j container management
- `pytest>=7.0.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support

## Running the Tests

### Run All Neo4j Integration Tests
```bash
pytest backend/tests/test_neo4j_integration.py -v
```

### Run Specific Test Class
```bash
# Test graph builder operations
pytest backend/tests/test_neo4j_integration.py::TestGraphBuilderIntegration -v

# Test circular dependency detection
pytest backend/tests/test_neo4j_integration.py::TestCircularDependencyDetectorIntegration -v

# Test graph update operations
pytest backend/tests/test_neo4j_integration.py::TestGraphUpdateOperations -v
```

### Run Specific Test
```bash
pytest backend/tests/test_neo4j_integration.py::TestGraphBuilderIntegration::test_create_single_entity_node -v
```

### Run with Detailed Output
```bash
pytest backend/tests/test_neo4j_integration.py -v -s
```

### Run with Coverage
```bash
pytest backend/tests/test_neo4j_integration.py --cov=app.services.graph_builder --cov-report=html
```

## Test Structure

### TestGraphBuilderIntegration

Tests for the `GraphBuilderService` class:

- **test_create_single_entity_node**: Verify single node creation
- **test_update_existing_entity_node**: Verify node updates
- **test_batch_create_entities**: Test batch node creation
- **test_create_dependency_relationship**: Test relationship creation
- **test_batch_create_relationships**: Test batch relationship creation
- **test_build_complete_dependency_graph**: Test complete graph building
- **test_update_entity_metrics**: Test metric updates
- **test_delete_entities_by_file**: Test entity deletion
- **test_get_entity_dependencies**: Test dependency retrieval

### TestCircularDependencyDetectorIntegration

Tests for the `CircularDependencyDetector` class:

- **test_detect_no_cycles**: Verify no false positives
- **test_detect_simple_cycle**: Test 2-node cycle detection
- **test_detect_complex_cycle**: Test multi-node cycle detection
- **test_detect_multiple_cycles**: Test multiple independent cycles
- **test_detect_critical_severity_cycle**: Test severity calculation
- **test_detect_cycles_with_severity_filter**: Test severity filtering
- **test_detect_cycles_for_specific_entity**: Test entity-specific detection
- **test_get_cycle_visualization_data**: Test visualization data generation
- **test_cycle_detection_with_project_filter**: Test project filtering
- **test_severity_breakdown_statistics**: Test statistics calculation

### TestGraphUpdateOperations

Tests for concurrent and large-scale operations:

- **test_concurrent_entity_updates**: Test concurrent updates
- **test_large_batch_operations**: Test large batch processing (2500+ entities)
- **test_relationship_type_mapping**: Test different relationship types

## Test Fixtures

### neo4j_container (module scope)
Starts a Neo4j 5.13.0 container for the test session. The container is automatically stopped after all tests complete.

### neo4j_test_config (module scope)
Configures Neo4j settings to use the test container and initializes the connection.

### clean_database (function scope)
Cleans the database before each test to ensure isolation.

### graph_builder (function scope)
Provides a `GraphBuilderService` instance.

### cycle_detector (function scope)
Provides a `CircularDependencyDetector` instance.

### sample_entities (function scope)
Provides sample `CodeEntity` objects for testing.

## Troubleshooting

### Docker Not Running

**Error:**
```
SKIPPED [1] conftest_neo4j.py:38: Docker is not available
```

**Solution:**
Start Docker Desktop or Docker daemon:
```bash
# Windows
Start Docker Desktop

# Linux
sudo systemctl start docker

# Verify
docker ps
```

### Container Startup Timeout

**Error:**
```
TimeoutError: Container did not start in time
```

**Solution:**
- Ensure Docker has sufficient resources (CPU, memory)
- Check Docker logs: `docker logs <container_id>`
- Increase timeout in test configuration

### Connection Refused

**Error:**
```
ServiceUnavailable: Failed to establish connection
```

**Solution:**
- Wait for Neo4j container to fully start (can take 10-30 seconds)
- Check container health: `docker ps`
- Verify Neo4j logs: `docker logs <container_id>`

### Port Already in Use

**Error:**
```
Port 7687 is already allocated
```

**Solution:**
- Stop existing Neo4j instances
- Use different port in test configuration
- Clean up Docker containers: `docker ps -a`

## Performance Considerations

### Test Execution Time

Integration tests with testcontainers are slower than unit tests:
- Container startup: 10-30 seconds
- Each test: 0.1-2 seconds
- Total suite: 1-3 minutes

### Optimization Tips

1. **Use module-scoped fixtures** for container setup (already implemented)
2. **Run tests in parallel** (requires careful isolation):
   ```bash
   pytest backend/tests/test_neo4j_integration.py -n auto
   ```
3. **Skip in CI if needed** (for faster feedback):
   ```bash
   pytest -m "not requires_docker"
   ```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Neo4j Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements-test.txt
      
      - name: Run Neo4j integration tests
        run: |
          pytest backend/tests/test_neo4j_integration.py -v
```

### Docker Compose Alternative

For local development, you can use Docker Compose instead of testcontainers:

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  neo4j-test:
    image: neo4j:5.13.0
    environment:
      NEO4J_AUTH: neo4j/testpassword
    ports:
      - "7687:7687"
      - "7474:7474"
```

Run tests:
```bash
docker-compose -f docker-compose.test.yml up -d
pytest backend/tests/test_neo4j_integration.py -v
docker-compose -f docker-compose.test.yml down
```

## Coverage Goals

Target coverage for Neo4j integration:
- **Graph Builder Service**: 80%+ coverage
- **Circular Dependency Detector**: 80%+ coverage
- **Critical paths**: 100% coverage

Check coverage:
```bash
pytest backend/tests/test_neo4j_integration.py \
  --cov=app.services.graph_builder \
  --cov-report=term-missing \
  --cov-report=html
```

## Related Documentation

- [Graph Builder Service README](../app/services/graph_builder/README.md)
- [Circular Dependency Detector README](../app/services/graph_builder/CIRCULAR_DEPENDENCY_DETECTOR_README.md)
- [Neo4j Database Configuration](../app/database/neo4j_db.py)
- [Testcontainers Documentation](https://testcontainers-python.readthedocs.io/)

## Maintenance

### Updating Neo4j Version

To update the Neo4j version used in tests:

1. Update the version in `test_neo4j_integration.py`:
   ```python
   container = Neo4jContainer("neo4j:5.14.0")  # Update version
   ```

2. Test compatibility:
   ```bash
   pytest backend/tests/test_neo4j_integration.py -v
   ```

3. Update documentation if needed

### Adding New Tests

When adding new tests:

1. Follow existing test structure and naming conventions
2. Use appropriate fixtures for setup/teardown
3. Ensure tests are isolated (use `clean_database` fixture)
4. Add docstrings explaining what is being tested
5. Update this README with new test descriptions

## Support

For issues or questions:
- Check existing tests for examples
- Review Neo4j driver documentation
- Check testcontainers documentation
- Open an issue in the project repository

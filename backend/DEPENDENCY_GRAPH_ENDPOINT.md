# Dependency Graph API Endpoint

## Overview

This document describes the newly implemented dependency graph API endpoint that provides dependency relationship data for projects.

## Endpoint Details

### GET `/api/v1/architecture/dependencies/{project_id}`

Retrieves the dependency graph data for a specified project.

#### Parameters

- **project_id** (path, required): Project UUID in format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **branch_id** (query, optional): Branch identifier to filter results by specific branch

#### Authentication

Requires authentication token with `VIEW_PROJECT` permission for the specified project.

#### Response Model

```json
{
  "id": "string (UUID)",
  "project_id": "string (UUID)",
  "branch_id": "string (optional)",
  "status": "string (pending|processing|completed|failed)",
  "nodes": [
    {
      "id": "string",
      "name": "string",
      "type": "string (module|class|function|package)",
      "file_path": "string (optional)",
      "lines_of_code": "integer (optional)",
      "complexity": "integer (optional)",
      "properties": "object (optional)"
    }
  ],
  "edges": [
    {
      "id": "string",
      "source": "string (node id)",
      "target": "string (node id)",
      "type": "string (import|call|inheritance)",
      "weight": "float",
      "is_circular": "boolean",
      "properties": "object (optional)"
    }
  ],
  "metrics": {
    "total_nodes": "integer",
    "total_edges": "integer",
    "circular_dependencies": "integer",
    "max_depth": "integer (optional)",
    "avg_dependencies_per_node": "float (optional)"
  },
  "circular_dependency_chains": "array of arrays (optional)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)",
  "api_version": "string (e.g., '1.0.0')"
}
```

#### Status Codes

- **200 OK**: Successfully retrieved dependency graph data
- **404 Not Found**: Project not found or no dependency data available
- **422 Unprocessable Entity**: Invalid UUID format
- **403 Forbidden**: User does not have permission to access the project

#### Example Request

```bash
curl -X GET "https://api.example.com/api/v1/architecture/dependencies/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "branch_id": "main",
  "status": "completed",
  "nodes": [
    {
      "id": "1",
      "name": "UserService",
      "type": "class",
      "file_path": "src/services/user_service.py",
      "lines_of_code": 150,
      "complexity": 8
    },
    {
      "id": "2",
      "name": "AuthService",
      "type": "class",
      "file_path": "src/services/auth_service.py",
      "lines_of_code": 200,
      "complexity": 12
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "1",
      "target": "2",
      "type": "import",
      "weight": 1.0,
      "is_circular": false
    }
  ],
  "metrics": {
    "total_nodes": 2,
    "total_edges": 1,
    "circular_dependencies": 0,
    "max_depth": 3,
    "avg_dependencies_per_node": 0.5
  },
  "circular_dependency_chains": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "api_version": "1.0.0"
}
```

## Implementation Details

### Requirements Satisfied

This endpoint satisfies the following production environment requirements:

- **Requirement 2.4**: Provides production API endpoint for dependency graph data fetching
- **Requirement 3.4**: Includes API version information in responses for backward compatibility
- **Requirement 3.6**: Implements input validation for request data (UUID format validation)

### Input Validation

The endpoint validates:
1. **UUID Format**: Ensures `project_id` is a valid UUID format
2. **Authentication**: Verifies user has `VIEW_PROJECT` permission
3. **Data Existence**: Checks if project and dependency data exist

### Data Sources

The endpoint retrieves dependency data from:
1. **Primary Source**: `ArchitectureAnalysis.summary` JSON field containing components and dependencies
2. **Fallback Source**: `ArchitectureViolation` records when summary data is not available

### Error Handling

The endpoint provides specific error messages for:
- Invalid UUID format (422)
- Missing project or dependency data (404)
- Permission denied (403)

## Integration

The endpoint is automatically registered in the API router at:
- **Router**: `backend/app/api/v1/router.py`
- **Prefix**: `/architecture`
- **Full Path**: `/api/v1/architecture/dependencies/{project_id}`
- **Tag**: "Architecture Visualization"

## Testing

To test the endpoint:

1. Ensure you have a valid project UUID
2. Obtain an authentication token with appropriate permissions
3. Make a GET request to the endpoint
4. Verify the response contains nodes, edges, and metrics

## Future Enhancements

Potential improvements:
- Add filtering by dependency type
- Support pagination for large dependency graphs
- Add graph visualization recommendations
- Include performance metrics for dependency resolution

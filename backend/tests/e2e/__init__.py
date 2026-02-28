"""
End-to-End Tests

This package contains end-to-end tests that validate complete system workflows
in a staging environment.

Tests in this package:
- test_github_webhook_to_comment_flow.py: Complete GitHub webhook to comment flow
- test_complete_analysis_workflow.py: Complete analysis workflow from start to finish

These tests require:
- Running PostgreSQL database
- Running Neo4j database
- Running Redis instance
- Staging environment configuration

Run with: pytest -m e2e
"""

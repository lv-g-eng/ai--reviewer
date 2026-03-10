#!/usr/bin/env python3
"""
API Endpoint Smoke Tests - Phase 2 Validation

Tests core API endpoints without requiring external services.
Uses mocking to isolate endpoint logic from database/external services.

Usage:
    pytest backend/tests/smoke_test_endpoints.py -v
"""

import os
import sys
import pytest

# Set test environment variables BEFORE importing app modules
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET"] = "test-jwt-secret-for-smoke-testing-min-32-chars"
os.environ["SECRET_KEY"] = "test-app-secret-for-smoke-testing-min-32-chars"
os.environ["POSTGRES_PASSWORD"] = "test_postgres_password"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_DB"] = "ai_code_review_test"
os.environ["NEO4J_PASSWORD"] = "test_neo4j_password"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["REDIS_PASSWORD"] = "test_redis_password"
os.environ["REDIS_HOST"] = "localhost"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestHealthEndpoints:
    """Smoke tests for Health endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint_imports(self):
        """Verify health endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import health
            assert hasattr(health, 'router'), "Health module should have router"
            print("✅ Health endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"Health endpoint import failed: {e}")

    @pytest.mark.asyncio
    async def test_health_endpoint_structure(self):
        """Verify health endpoint has required routes"""
        from app.api.v1.endpoints import health

        routes = [route.path for route in health.router.routes]
        assert "/" in routes, "Health endpoint should have root route"
        assert any("ready" in str(r) for r in routes), "Health endpoint should have ready route"
        assert any("live" in str(r) for r in routes), "Health endpoint should have live route"
        print("✅ Health endpoint: Structure OK")


class TestAuthEndpoints:
    """Smoke tests for Auth endpoints"""

    @pytest.mark.asyncio
    async def test_auth_endpoint_imports(self):
        """Verify auth endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import auth
            assert hasattr(auth, 'router'), "Auth module should have router"
            print("✅ Auth endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"Auth endpoint import failed: {e}")

    @pytest.mark.asyncio
    async def test_auth_endpoint_structure(self):
        """Verify auth endpoint has required routes"""
        from app.api.v1.endpoints import auth

        routes = [route.path for route in auth.router.routes]
        assert any("register" in str(r) for r in routes), "Auth should have register route"
        assert any("login" in str(r) for r in routes), "Auth should have login route"
        assert any("logout" in str(r) for r in routes), "Auth should have logout route"
        print("✅ Auth endpoint: Structure OK")


class TestGitHubEndpoints:
    """Smoke tests for GitHub integration endpoints"""

    @pytest.mark.asyncio
    async def test_github_endpoint_imports(self):
        """Verify GitHub endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import github
            assert hasattr(github, 'router'), "GitHub module should have router"
            print("✅ GitHub endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"GitHub endpoint import failed: {e}")

    @pytest.mark.asyncio
    async def test_github_endpoint_structure(self):
        """Verify GitHub endpoint has required routes"""
        from app.api.v1.endpoints import github

        routes = [route.path for route in github.router.routes]
        assert any("webhook" in str(r) for r in routes), "GitHub should have webhook route"
        assert any("status" in str(r) for r in routes), "GitHub should have status route"
        print("✅ GitHub endpoint: Structure OK")


class TestCodeReviewEndpoints:
    """Smoke tests for Code Review endpoints"""

    @pytest.mark.asyncio
    async def test_code_review_endpoint_imports(self):
        """Verify Code Review endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import code_review
            assert hasattr(code_review, 'router'), "CodeReview module should have router"
            print("✅ Code Review endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"Code Review endpoint import failed: {e}")

    @pytest.mark.asyncio
    async def test_code_review_endpoint_structure(self):
        """Verify Code Review endpoint has required routes"""
        from app.api.v1.endpoints import code_review

        routes = [route.path for route in code_review.router.routes]
        assert any("trigger" in str(r) for r in routes), "CodeReview should have trigger route"
        print("✅ Code Review endpoint: Structure OK")


class TestPullRequestEndpoints:
    """Smoke tests for Pull Request endpoints"""

    @pytest.mark.asyncio
    async def test_pull_request_endpoint_imports(self):
        """Verify Pull Request endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import pull_request
            assert hasattr(pull_request, 'router'), "PullRequest module should have router"
            print("✅ Pull Request endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"Pull Request endpoint import failed: {e}")

    @pytest.mark.asyncio
    async def test_pull_request_endpoint_structure(self):
        """Verify Pull Request endpoint has required routes"""
        from app.api.v1.endpoints import pull_request

        routes = [route.path for route in pull_request.router.routes]
        assert any("analyze" in str(r) for r in routes), "PullRequest should have analyze route"
        assert any("status" in str(r) for r in routes), "PullRequest should have status route"
        print("✅ Pull Request endpoint: Structure OK")




class TestArchitectureEndpoints:
    """Smoke tests for Architecture endpoints"""

    @pytest.mark.asyncio
    async def test_architecture_endpoint_imports(self):
        """Verify Architecture endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import architecture
            assert hasattr(architecture, 'router'), "Architecture module should have router"
            print("✅ Architecture endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"Architecture endpoint import failed: {e}")

    @pytest.mark.asyncio
    async def test_architecture_endpoint_structure(self):
        """Verify Architecture endpoint has required routes"""
        from app.api.v1.endpoints import architecture

        routes = [route.path for route in architecture.router.routes]
        assert any("branch" in str(r) for r in routes), "Architecture should have branch route"
        print("✅ Architecture endpoint: Structure OK")


class TestLLMEndpoints:
    """Smoke tests for LLM endpoints"""

    @pytest.mark.asyncio
    async def test_llm_endpoint_imports(self):
        """Verify LLM endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import llm
            assert hasattr(llm, 'router'), "LLM module should have router"
            print("✅ LLM endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"LLM endpoint import failed: {e}")


class TestMetricsEndpoints:
    """Smoke tests for Metrics endpoints"""

    @pytest.mark.asyncio
    async def test_metrics_endpoint_imports(self):
        """Verify Metrics endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import metrics
            assert hasattr(metrics, 'router'), "Metrics module should have router"
            print("✅ Metrics endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"Metrics endpoint import failed: {e}")


class TestDatabaseEndpoints:
    """Smoke tests for Database test endpoints"""

    @pytest.mark.asyncio
    async def test_database_endpoint_imports(self):
        """Verify Database endpoint module can be imported"""
        try:
            from app.api.v1.endpoints import database
            assert hasattr(database, 'router'), "Database module should have router"
            print("✅ Database endpoint: Import OK")
        except Exception as e:
            pytest.fail(f"Database endpoint import failed: {e}")


class TestMainApp:
    """Smoke tests for main application"""

    @pytest.mark.asyncio
    async def test_main_app_imports(self):
        """Verify main app module can be imported"""
        try:
            from app.main import app
            assert app is not None, "Main app should not be None"
            print("✅ Main app: Import OK")
        except Exception as e:
            pytest.fail(f"Main app import failed: {e}")

    @pytest.mark.asyncio
    async def test_main_app_routes(self):
        """Verify main app has API routes registered"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("/api/v1" in str(r) for r in routes), "App should have API v1 routes"
        assert any("/health" in str(r) for r in routes), "App should have health routes"
        print("✅ Main app: Routes OK")


class TestServiceModules:
    """Smoke tests for core service modules"""

    @pytest.mark.asyncio
    async def test_error_reporter_imports(self):
        """Verify error reporter module can be imported"""
        try:
            from app.core.error_reporter import ErrorReporter
            assert ErrorReporter is not None
            print("✅ ErrorReporter: Import OK")
        except Exception as e:
            pytest.fail(f"ErrorReporter import failed: {e}")

    @pytest.mark.asyncio
    async def test_config_imports(self):
        """Verify config module can be imported"""
        try:
            from app.core.config import settings
            assert settings is not None
            print("✅ Settings: Import OK")
        except Exception as e:
            pytest.fail(f"Settings import failed: {e}")


# Run as script for quick verification
if __name__ == "__main__":
    import asyncio

    async def run_all_tests():
        """Run all smoke tests"""
        print("\n" + "="*60)
        print("API Endpoint Smoke Tests - Phase 2 Validation")
        print("="*60 + "\n")

        test_classes = [
            TestHealthEndpoints(),
            TestAuthEndpoints(),
            TestGitHubEndpoints(),
            TestCodeReviewEndpoints(),
            TestPullRequestEndpoints(),
            TestRBACEndpoints(),
            TestArchitectureEndpoints(),
            TestLLMEndpoints(),
            TestMetricsEndpoints(),
            TestDatabaseEndpoints(),
            TestMainApp(),
            TestServiceModules(),
        ]

        passed = 0
        failed = 0
        total = 0

        for test_class in test_classes:
            class_name = test_class.__class__.__name__
            for method_name in dir(test_class):
                if method_name.startswith('test_'):
                    total += 1
                    method = getattr(test_class, method_name)
                    try:
                        if asyncio.iscoroutinefunction(method):
                            await method()
                        else:
                            method()
                        passed += 1
                    except Exception as e:
                        failed += 1
                        print(f"  ❌ {class_name}.{method_name}: {str(e)[:100]}")

        print("\n" + "="*60)
        print(f"SUMMARY: {passed}/{total} passed, {failed} failed")
        print("="*60)

        return failed == 0

    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

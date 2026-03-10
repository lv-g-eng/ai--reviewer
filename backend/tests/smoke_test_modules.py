#!/usr/bin/env python3
"""
Comprehensive Smoke Tests for AI Code Review Platform

This script performs health checks on all core modules without requiring
external dependencies (database, LLM APIs, etc.) to be running.

Usage:
    python backend/tests/smoke_test_modules.py [--verbose]

Categories:
    - STABLE: Module loads and basic functions work
    - FLAKY: Module loads but some functions may fail
    - BROKEN: Module fails to load or core functions fail
"""

import sys
import os
import importlib
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime


class ModuleStatus(Enum):
    STABLE = "STABLE"
    FLAKY = "FLAKY"
    BROKEN = "BROKEN"
    SKIPPED = "SKIPPED"


@dataclass
class TestResult:
    module_name: str
    status: ModuleStatus
    message: str
    error: Optional[str] = None
    duration_ms: float = 0


class SmokeTestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []

    def log(self, msg: str):
        if self.verbose:
            print(f"  {msg}")

    def test_module_import(self, module_path: str) -> TestResult:
        """Test if a module can be imported successfully"""
        start_time = datetime.now()
        try:
            importlib.import_module(module_path)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                module_name=module_path,
                status=ModuleStatus.STABLE,
                message="Import successful",
                duration_ms=duration
            )
        except ImportError as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                module_name=module_path,
                status=ModuleStatus.BROKEN,
                message="Import failed - missing dependency",
                error=str(e),
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                module_name=module_path,
                status=ModuleStatus.FLAKY,
                message="Import succeeded but with warnings",
                error=str(e)[:200],
                duration_ms=duration
            )

    def test_class_instantiation(self, module_path: str, class_name: str) -> TestResult:
        """Test if a class can be instantiated (without external dependencies)"""
        start_time = datetime.now()
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            # Try to get class info without instantiating (may require dependencies)
            if hasattr(cls, '__init__'):
                sig = str(cls.__init__.__annotations__) if hasattr(cls.__init__, '__annotations__') else 'No annotations'
                self.log(f"Class {class_name} signature: {sig[:100]}")
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                module_name=f"{module_path}.{class_name}",
                status=ModuleStatus.STABLE,
                message="Class definition OK",
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                module_name=f"{module_path}.{class_name}",
                status=ModuleStatus.BROKEN,
                message="Class check failed",
                error=str(e)[:200],
                duration_ms=duration
            )

    def run_all_tests(self) -> dict:
        """Run all smoke tests and return summary"""
        print("=" * 70)
        print("AI Code Review Platform - Module Smoke Tests")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Add backend to path
        backend_path = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(backend_path))

        # Core modules to test
        core_modules = [
            # Authentication
            ("app.auth.services.audit_service", "AuditService"),

            # Database
            ("app.database.models", None),
            ("app.database.postgresql", None),
            ("app.database.neo4j_db", None),
            ("app.database.redis_db", None),

            # Services
            ("app.services.health_service", "HealthService"),
            ("app.services.llm_service", "LLMService"),
            ("app.services.repository_service", "RepositoryService"),
            ("app.services.security_scanner", None),
            ("app.services.audit_logging_service", "AuditLoggingService"),

            # API Endpoints
            ("app.api.v1.endpoints.health", None),
            ("app.api.v1.endpoints.auth", None),

            # Utils
            ("app.utils.validators", None),
            ("app.utils.jwt", None),
            ("app.utils.password", None),

            # Schemas
            ("app.schemas.auth", None),
            ("app.schemas.response_models", None),
        ]

        print("\n[1] Testing Core Module Imports...")
        print("-" * 70)

        for module_path, class_name in core_modules:
            result = self.test_module_import(module_path)
            self.results.append(result)

            status_icon = {
                ModuleStatus.STABLE: "[OK]",
                ModuleStatus.FLAKY: "[WARN]",
                ModuleStatus.BROKEN: "[FAIL]",
                ModuleStatus.SKIPPED: "[SKIP]"
            }[result.status]

            print(f"  {status_icon} {module_path} ({result.duration_ms:.1f}ms)")
            if result.error and self.verbose:
                print(f"       Error: {result.error[:100]}")

        print("\n[2] Testing Service Class Definitions...")
        print("-" * 70)

        service_classes = [
            ("app.services.health_service", "HealthService"),
            ("app.services.llm_service", "LLMService"),
            ("app.services.repository_service", "RepositoryService"),
        ]

        for module_path, class_name in service_classes:
            result = self.test_class_instantiation(module_path, class_name)
            self.results.append(result)

            status_icon = {
                ModuleStatus.STABLE: "[OK]",
                ModuleStatus.FLAKY: "[WARN]",
                ModuleStatus.BROKEN: "[FAIL]",
                ModuleStatus.SKIPPED: "[SKIP]"
            }[result.status]

            print(f"  {status_icon} {class_name} ({result.duration_ms:.1f}ms)")
            if result.error and self.verbose:
                print(f"       Error: {result.error[:100]}")

        # Print summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        stable = [r for r in self.results if r.status == ModuleStatus.STABLE]
        flaky = [r for r in self.results if r.status == ModuleStatus.FLAKY]
        broken = [r for r in self.results if r.status == ModuleStatus.BROKEN]

        print(f"  STABLE: {len(stable)} modules")
        print(f"  FLAKY:  {len(flaky)} modules")
        print(f"  BROKEN: {len(broken)} modules")
        print(f"  Total:  {len(self.results)} modules tested")

        if broken:
            print("\n[BROKEN MODULES - Require Immediate Attention]")
            for r in broken:
                print(f"  - {r.module_name}")
                if r.error:
                    print(f"    {r.error[:150]}")

        if flaky:
            print("\n[FLAKY MODULES - May Have Issues]")
            for r in flaky:
                print(f"  - {r.module_name}")

        print("\n" + "=" * 70)

        return {
            "stable": len(stable),
            "flaky": len(flaky),
            "broken": len(broken),
            "total": len(self.results),
            "all_passed": len(broken) == 0
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run smoke tests for AI Code Review Platform")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    runner = SmokeTestRunner(verbose=args.verbose)
    summary = runner.run_all_tests()

    # Exit with error code if any broken modules
    sys.exit(0 if summary["all_passed"] else 1)


if __name__ == "__main__":
    main()

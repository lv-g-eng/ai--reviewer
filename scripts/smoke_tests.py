#!/usr/bin/env python3
"""
Production Environment Smoke Tests

This script runs comprehensive smoke tests to verify that all critical
system components are functioning correctly after deployment.

Requirements: 5.8
"""

import os
import sys
import time
import json
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse


@dataclass
class TestResult:
    """Result of a single test"""
    name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    details: Optional[Dict] = None


class SmokeTestRunner:
    """Runs smoke tests against the production environment"""
    
    def __init__(self, backend_url: str, frontend_url: str, timeout: int = 10):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/')
        self.timeout = timeout
        self.results: List[TestResult] = []
        
    def run_all_tests(self) -> bool:
        """
        Run all smoke tests
        
        Returns:
            True if all tests passed, False otherwise
        """
        print("=" * 70)
        print("Production Environment Smoke Tests")
        print("=" * 70)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Timeout: {self.timeout}s")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()
        
        # Run all test categories
        self._test_health_endpoints()
        self._test_api_endpoints()
        self._test_database_connectivity()
        self._test_authentication()
        self._test_frontend()
        
        # Print summary
        self._print_summary()
        
        # Return overall result
        return all(result.passed for result in self.results)
    
    def _test_health_endpoints(self):
        """Test health check endpoints"""
        print("Testing Health Endpoints...")
        print("-" * 70)
        
        # Test 1: Main health endpoint
        self._run_test(
            "Health Endpoint",
            lambda: self._check_endpoint(f"{self.backend_url}/api/v1/health")
        )
        
        # Test 2: Readiness endpoint
        self._run_test(
            "Readiness Endpoint",
            lambda: self._check_endpoint(f"{self.backend_url}/api/v1/health/ready")
        )
        
        # Test 3: Liveness endpoint
        self._run_test(
            "Liveness Endpoint",
            lambda: self._check_endpoint(f"{self.backend_url}/api/v1/health/live")
        )
        
        print()
    
    def _test_api_endpoints(self):
        """Test critical API endpoints"""
        print("Testing API Endpoints...")
        print("-" * 70)
        
        # Test 1: API root
        self._run_test(
            "API Root",
            lambda: self._check_endpoint(f"{self.backend_url}/api/v1/")
        )
        
        # Test 2: Metrics endpoint
        self._run_test(
            "Metrics Endpoint",
            lambda: self._check_endpoint(f"{self.backend_url}/metrics"),
            critical=False  # Non-critical
        )
        
        # Test 3: OpenAPI docs
        self._run_test(
            "OpenAPI Documentation",
            lambda: self._check_endpoint(f"{self.backend_url}/docs"),
            critical=False  # Non-critical
        )
        
        print()
    
    def _test_database_connectivity(self):
        """Test database connectivity through API"""
        print("Testing Database Connectivity...")
        print("-" * 70)
        
        # Test 1: PostgreSQL connectivity (via health endpoint)
        def check_postgres():
            response = requests.get(
                f"{self.backend_url}/api/v1/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if 'database' in data and data['database'].get('status') == 'healthy':
                return True, data
            else:
                raise Exception(f"PostgreSQL not healthy: {data}")
        
        self._run_test(
            "PostgreSQL Connectivity",
            check_postgres
        )
        
        # Test 2: Neo4j connectivity (via health endpoint)
        def check_neo4j():
            response = requests.get(
                f"{self.backend_url}/api/v1/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if 'neo4j' in data and data['neo4j'].get('status') == 'healthy':
                return True, data
            elif 'graph_database' in data and data['graph_database'].get('status') == 'healthy':
                return True, data
            else:
                # Neo4j might not be critical for all deployments
                raise Exception(f"Neo4j not healthy: {data}")
        
        self._run_test(
            "Neo4j Connectivity",
            check_neo4j,
            critical=False  # Non-critical if not used
        )
        
        # Test 3: Redis connectivity (via health endpoint)
        def check_redis():
            response = requests.get(
                f"{self.backend_url}/api/v1/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if 'redis' in data and data['redis'].get('status') == 'healthy':
                return True, data
            elif 'cache' in data and data['cache'].get('status') == 'healthy':
                return True, data
            else:
                raise Exception(f"Redis not healthy: {data}")
        
        self._run_test(
            "Redis Connectivity",
            check_redis,
            critical=False  # Non-critical if not used
        )
        
        print()
    
    def _test_authentication(self):
        """Test authentication endpoints"""
        print("Testing Authentication...")
        print("-" * 70)
        
        # Test 1: Auth endpoint exists
        self._run_test(
            "Auth Endpoint Available",
            lambda: self._check_endpoint(
                f"{self.backend_url}/api/v1/auth/login",
                expected_status=[200, 401, 422]  # Any of these is fine
            ),
            critical=False  # Non-critical for smoke test
        )
        
        print()
    
    def _test_frontend(self):
        """Test frontend availability"""
        print("Testing Frontend...")
        print("-" * 70)
        
        # Test 1: Frontend root
        self._run_test(
            "Frontend Root",
            lambda: self._check_endpoint(self.frontend_url),
            critical=False  # Non-critical if frontend is separate
        )
        
        # Test 2: Frontend health (if available)
        self._run_test(
            "Frontend Health",
            lambda: self._check_endpoint(f"{self.frontend_url}/api/health"),
            critical=False  # Non-critical
        )
        
        print()
    
    def _run_test(self, name: str, test_func, critical: bool = True):
        """
        Run a single test and record the result
        
        Args:
            name: Test name
            test_func: Function that runs the test
            critical: Whether this test is critical for deployment
        """
        start_time = time.time()
        
        try:
            result = test_func()
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract details if returned
            details = None
            if isinstance(result, tuple):
                _, details = result
            
            test_result = TestResult(
                name=name,
                passed=True,
                duration_ms=duration_ms,
                details=details
            )
            
            self.results.append(test_result)
            
            status = "✓ PASS" if critical else "✓ PASS (non-critical)"
            print(f"  {status:25} {name:35} ({duration_ms:.0f}ms)")
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            test_result = TestResult(
                name=name,
                passed=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            
            self.results.append(test_result)
            
            status = "✗ FAIL" if critical else "⚠ FAIL (non-critical)"
            print(f"  {status:25} {name:35} ({duration_ms:.0f}ms)")
            if critical:
                print(f"    Error: {str(e)}")
    
    def _check_endpoint(
        self,
        url: str,
        expected_status: List[int] = None
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Check if an endpoint is responding
        
        Args:
            url: URL to check
            expected_status: List of acceptable status codes (default: [200])
            
        Returns:
            Tuple of (success, response_data)
        """
        if expected_status is None:
            expected_status = [200]
        
        response = requests.get(url, timeout=self.timeout)
        
        if response.status_code not in expected_status:
            raise Exception(
                f"Unexpected status code: {response.status_code} "
                f"(expected one of {expected_status})"
            )
        
        # Try to parse JSON response
        try:
            data = response.json()
            return True, data
        except (requests.RequestException, ValueError) as e:
            # Return success with no data if parsing fails
            return True, None
    
    def _print_summary(self):
        """Print test summary"""
        print("=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration_ms for r in self.results)
        
        print(f"Total Tests:    {total_tests}")
        print(f"Passed:         {passed_tests} ✓")
        print(f"Failed:         {failed_tests} ✗")
        print(f"Success Rate:   {(passed_tests/total_tests*100):.1f}%")
        print(f"Total Duration: {total_duration:.0f}ms")
        print()
        
        if failed_tests > 0:
            print("Failed Tests:")
            print("-" * 70)
            for result in self.results:
                if not result.passed:
                    print(f"  ✗ {result.name}")
                    if result.error:
                        print(f"    Error: {result.error}")
            print()
        
        print("=" * 70)
        
        if failed_tests == 0:
            print("✓ All smoke tests passed!")
        else:
            print(f"✗ {failed_tests} test(s) failed")
        
        print("=" * 70)
    
    def save_results(self, output_file: str):
        """Save test results to JSON file"""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "backend_url": self.backend_url,
            "frontend_url": self.frontend_url,
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.passed),
            "failed_tests": sum(1 for r in self.results if not r.passed),
            "total_duration_ms": sum(r.duration_ms for r in self.results),
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "error": r.error,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run smoke tests against production environment"
    )
    parser.add_argument(
        "--backend-url",
        default=os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000"),
        help="Backend API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--frontend-url",
        default=os.getenv("NEXT_PUBLIC_FRONTEND_URL", "http://localhost:3000"),
        help="Frontend URL (default: http://localhost:3000)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--output",
        help="Output file for test results (JSON format)"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = SmokeTestRunner(
        backend_url=args.backend_url,
        frontend_url=args.frontend_url,
        timeout=args.timeout
    )
    
    # Run tests
    success = runner.run_all_tests()
    
    # Save results if output file specified
    if args.output:
        runner.save_results(args.output)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

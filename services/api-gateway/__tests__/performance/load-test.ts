/**
 * Load Testing Script for API Gateway
 * 
 * This script tests the API Gateway under various load conditions:
 * - Throughput: 1000 requests per second
 * - Response times: p50, p95, p99
 * - Memory usage under load
 * - Identifies bottlenecks
 * 
 * Usage:
 *   npm run test:performance
 *   or
 *   ts-node __tests__/performance/load-test.ts
 */

import autocannon from 'autocannon';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

interface LoadTestResult {
  testName: string;
  duration: number;
  connections: number;
  pipelining: number;
  requests: {
    total: number;
    average: number;
    mean: number;
    stddev: number;
    min: number;
    max: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
  };
  latency: {
    average: number;
    mean: number;
    stddev: number;
    min: number;
    max: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
  };
  throughput: {
    average: number;
    mean: number;
    stddev: number;
    min: number;
    max: number;
  };
  errors: number;
  timeouts: number;
  non2xx: number;
}

interface PerformanceReport {
  timestamp: string;
  tests: LoadTestResult[];
  summary: {
    passed: boolean;
    totalTests: number;
    passedTests: number;
    failedTests: number;
    bottlenecks: string[];
    recommendations: string[];
  };
}

class PerformanceTester {
  private serverProcess: ChildProcess | null = null;
  private readonly baseUrl = 'http://localhost:3000';
  private readonly resultsDir = path.join(__dirname, 'results');
  private results: LoadTestResult[] = [];

  constructor() {
    // Ensure results directory exists
    if (!fs.existsSync(this.resultsDir)) {
      fs.mkdirSync(this.resultsDir, { recursive: true });
    }
  }

  /**
   * Start the API Gateway server for testing
   */
  private async startServer(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log('🚀 Starting API Gateway server...');
      
      this.serverProcess = spawn('npm', ['run', 'dev'], {
        cwd: path.join(__dirname, '../..'),
        stdio: 'pipe',
        shell: true,
      });

      let output = '';

      this.serverProcess.stdout?.on('data', (data) => {
        output += data.toString();
        if (output.includes('API Gateway started on port')) {
          console.log('✅ Server started successfully');
          // Wait a bit for server to be fully ready
          setTimeout(resolve, 2000);
        }
      });

      this.serverProcess.stderr?.on('data', (data) => {
        console.error('Server error:', data.toString());
      });

      this.serverProcess.on('error', (error) => {
        reject(error);
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        reject(new Error('Server startup timeout'));
      }, 30000);
    });
  }

  /**
   * Stop the API Gateway server
   */
  private async stopServer(): Promise<void> {
    if (this.serverProcess) {
      console.log('🛑 Stopping API Gateway server...');
      this.serverProcess.kill('SIGTERM');
      
      return new Promise((resolve) => {
        this.serverProcess?.on('exit', () => {
          console.log('✅ Server stopped');
          resolve();
        });
        
        // Force kill after 5 seconds
        setTimeout(() => {
          this.serverProcess?.kill('SIGKILL');
          resolve();
        }, 5000);
      });
    }
  }

  /**
   * Run a single load test
   */
  private async runLoadTest(
    testName: string,
    options: autocannon.Options
  ): Promise<LoadTestResult> {
    console.log(`\n📊 Running test: ${testName}`);
    console.log(`   Duration: ${options.duration}s`);
    console.log(`   Connections: ${options.connections}`);
    console.log(`   Pipelining: ${options.pipelining}`);

    return new Promise((resolve, reject) => {
      const instance = autocannon(options, (err, result) => {
        if (err) {
          reject(err);
          return;
        }

        const testResult: LoadTestResult = {
          testName,
          duration: options.duration || 10,
          connections: options.connections || 10,
          pipelining: options.pipelining || 1,
          requests: {
            total: result.requests.total,
            average: result.requests.average,
            mean: result.requests.mean,
            stddev: result.requests.stddev,
            min: result.requests.min,
            max: result.requests.max,
            p50: result.requests.p50,
            p75: result.requests.p75,
            p90: result.requests.p90,
            p95: result.requests.p95,
            p99: result.requests.p99,
          },
          latency: {
            average: result.latency.average,
            mean: result.latency.mean,
            stddev: result.latency.stddev,
            min: result.latency.min,
            max: result.latency.max,
            p50: result.latency.p50,
            p75: result.latency.p75,
            p90: result.latency.p90,
            p95: result.latency.p95,
            p99: result.latency.p99,
          },
          throughput: {
            average: result.throughput.average,
            mean: result.throughput.mean,
            stddev: result.throughput.stddev,
            min: result.throughput.min,
            max: result.throughput.max,
          },
          errors: result.errors,
          timeouts: result.timeouts,
          non2xx: result.non2xx,
        };

        console.log(`   ✅ Completed`);
        console.log(`   Requests/sec: ${result.requests.average.toFixed(2)}`);
        console.log(`   Latency p50: ${result.latency.p50}ms`);
        console.log(`   Latency p95: ${result.latency.p95}ms`);
        console.log(`   Latency p99: ${result.latency.p99}ms`);
        console.log(`   Errors: ${result.errors}`);

        resolve(testResult);
      });

      // Track progress
      autocannon.track(instance, { renderProgressBar: true });
    });
  }

  /**
   * Test 1: Health Check Endpoint (Baseline)
   */
  private async testHealthCheck(): Promise<LoadTestResult> {
    return this.runLoadTest('Health Check Baseline', {
      url: `${this.baseUrl}/health`,
      connections: 10,
      pipelining: 1,
      duration: 10,
    });
  }

  /**
   * Test 2: Target Load (1000 req/s)
   */
  private async testTargetLoad(): Promise<LoadTestResult> {
    return this.runLoadTest('Target Load (1000 req/s)', {
      url: `${this.baseUrl}/health`,
      connections: 100,
      pipelining: 10,
      duration: 30,
      amount: 30000, // 1000 req/s * 30s
    });
  }

  /**
   * Test 3: Stress Test (High Load)
   */
  private async testStressLoad(): Promise<LoadTestResult> {
    return this.runLoadTest('Stress Test (5000 req/s)', {
      url: `${this.baseUrl}/health`,
      connections: 500,
      pipelining: 10,
      duration: 20,
      amount: 100000, // 5000 req/s * 20s
    });
  }

  /**
   * Test 4: Sustained Load
   */
  private async testSustainedLoad(): Promise<LoadTestResult> {
    return this.runLoadTest('Sustained Load (60s)', {
      url: `${this.baseUrl}/health`,
      connections: 100,
      pipelining: 10,
      duration: 60,
    });
  }

  /**
   * Test 5: API Endpoint with Middleware
   */
  private async testApiEndpoint(): Promise<LoadTestResult> {
    return this.runLoadTest('API Endpoint (with middleware)', {
      url: `${this.baseUrl}/api/v1/projects`,
      connections: 50,
      pipelining: 5,
      duration: 20,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token',
      },
    });
  }

  /**
   * Analyze results and identify bottlenecks
   */
  private analyzeResults(): PerformanceReport {
    const bottlenecks: string[] = [];
    const recommendations: string[] = [];
    let passedTests = 0;

    // Check each test against requirements
    this.results.forEach((result) => {
      let testPassed = true;

      // Requirement: 1000 req/s
      if (result.testName.includes('Target Load')) {
        if (result.requests.average < 1000) {
          bottlenecks.push(
            `Throughput below target: ${result.requests.average.toFixed(2)} req/s (target: 1000 req/s)`
          );
          recommendations.push('Consider optimizing middleware chain');
          recommendations.push('Enable HTTP keep-alive connections');
          testPassed = false;
        }
      }

      // Requirement: <50ms routing overhead
      if (result.latency.p50 > 50) {
        bottlenecks.push(
          `High p50 latency: ${result.latency.p50}ms (target: <50ms)`
        );
        recommendations.push('Review middleware execution time');
        recommendations.push('Consider caching frequently accessed data');
        testPassed = false;
      }

      if (result.latency.p95 > 100) {
        bottlenecks.push(
          `High p95 latency: ${result.latency.p95}ms (target: <100ms)`
        );
        recommendations.push('Investigate slow requests');
        testPassed = false;
      }

      // Check for errors
      if (result.errors > 0 || result.timeouts > 0) {
        bottlenecks.push(
          `Errors detected: ${result.errors} errors, ${result.timeouts} timeouts`
        );
        recommendations.push('Review error logs for failure patterns');
        testPassed = false;
      }

      if (testPassed) {
        passedTests++;
      }
    });

    // Remove duplicate recommendations
    const uniqueRecommendations = [...new Set(recommendations)];

    return {
      timestamp: new Date().toISOString(),
      tests: this.results,
      summary: {
        passed: passedTests === this.results.length,
        totalTests: this.results.length,
        passedTests,
        failedTests: this.results.length - passedTests,
        bottlenecks,
        recommendations: uniqueRecommendations,
      },
    };
  }

  /**
   * Save results to file
   */
  private saveResults(report: PerformanceReport): void {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `performance-report-${timestamp}.json`;
    const filepath = path.join(this.resultsDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(report, null, 2));
    console.log(`\n📄 Results saved to: ${filepath}`);

    // Also save a summary markdown file
    const mdFilename = `performance-report-${timestamp}.md`;
    const mdFilepath = path.join(this.resultsDir, mdFilename);
    const markdown = this.generateMarkdownReport(report);
    fs.writeFileSync(mdFilepath, markdown);
    console.log(`📄 Summary saved to: ${mdFilepath}`);
  }

  /**
   * Generate markdown report
   */
  private generateMarkdownReport(report: PerformanceReport): string {
    let md = `# API Gateway Performance Test Report\n\n`;
    md += `**Date:** ${new Date(report.timestamp).toLocaleString()}\n\n`;
    md += `**Status:** ${report.summary.passed ? '✅ PASSED' : '❌ FAILED'}\n\n`;
    md += `**Tests:** ${report.summary.passedTests}/${report.summary.totalTests} passed\n\n`;

    md += `## Summary\n\n`;
    md += `| Metric | Value |\n`;
    md += `|--------|-------|\n`;
    md += `| Total Tests | ${report.summary.totalTests} |\n`;
    md += `| Passed | ${report.summary.passedTests} |\n`;
    md += `| Failed | ${report.summary.failedTests} |\n`;
    md += `| Bottlenecks Found | ${report.summary.bottlenecks.length} |\n\n`;

    md += `## Test Results\n\n`;
    report.tests.forEach((test) => {
      md += `### ${test.testName}\n\n`;
      md += `**Configuration:**\n`;
      md += `- Duration: ${test.duration}s\n`;
      md += `- Connections: ${test.connections}\n`;
      md += `- Pipelining: ${test.pipelining}\n\n`;

      md += `**Throughput:**\n`;
      md += `- Average: ${test.requests.average.toFixed(2)} req/s\n`;
      md += `- Total Requests: ${test.requests.total}\n\n`;

      md += `**Latency:**\n`;
      md += `| Percentile | Latency (ms) |\n`;
      md += `|------------|-------------|\n`;
      md += `| p50 | ${test.latency.p50} |\n`;
      md += `| p75 | ${test.latency.p75} |\n`;
      md += `| p90 | ${test.latency.p90} |\n`;
      md += `| p95 | ${test.latency.p95} |\n`;
      md += `| p99 | ${test.latency.p99} |\n\n`;

      md += `**Errors:**\n`;
      md += `- Errors: ${test.errors}\n`;
      md += `- Timeouts: ${test.timeouts}\n`;
      md += `- Non-2xx: ${test.non2xx}\n\n`;
    });

    if (report.summary.bottlenecks.length > 0) {
      md += `## 🚨 Bottlenecks Identified\n\n`;
      report.summary.bottlenecks.forEach((bottleneck, index) => {
        md += `${index + 1}. ${bottleneck}\n`;
      });
      md += `\n`;
    }

    if (report.summary.recommendations.length > 0) {
      md += `## 💡 Recommendations\n\n`;
      report.summary.recommendations.forEach((rec, index) => {
        md += `${index + 1}. ${rec}\n`;
      });
      md += `\n`;
    }

    md += `## Requirements Check\n\n`;
    md += `| Requirement | Target | Status |\n`;
    md += `|-------------|--------|--------|\n`;
    
    const targetLoadTest = report.tests.find(t => t.testName.includes('Target Load'));
    if (targetLoadTest) {
      md += `| Throughput | 1000 req/s | ${targetLoadTest.requests.average >= 1000 ? '✅' : '❌'} ${targetLoadTest.requests.average.toFixed(2)} req/s |\n`;
      md += `| Latency p50 | <50ms | ${targetLoadTest.latency.p50 < 50 ? '✅' : '❌'} ${targetLoadTest.latency.p50}ms |\n`;
      md += `| Latency p95 | <100ms | ${targetLoadTest.latency.p95 < 100 ? '✅' : '❌'} ${targetLoadTest.latency.p95}ms |\n`;
      md += `| Latency p99 | <200ms | ${targetLoadTest.latency.p99 < 200 ? '✅' : '❌'} ${targetLoadTest.latency.p99}ms |\n`;
    }

    return md;
  }

  /**
   * Print summary to console
   */
  private printSummary(report: PerformanceReport): void {
    console.log('\n' + '='.repeat(80));
    console.log('📊 PERFORMANCE TEST SUMMARY');
    console.log('='.repeat(80));
    console.log(`\nStatus: ${report.summary.passed ? '✅ PASSED' : '❌ FAILED'}`);
    console.log(`Tests: ${report.summary.passedTests}/${report.summary.totalTests} passed\n`);

    if (report.summary.bottlenecks.length > 0) {
      console.log('🚨 Bottlenecks Identified:');
      report.summary.bottlenecks.forEach((bottleneck, index) => {
        console.log(`   ${index + 1}. ${bottleneck}`);
      });
      console.log('');
    }

    if (report.summary.recommendations.length > 0) {
      console.log('💡 Recommendations:');
      report.summary.recommendations.forEach((rec, index) => {
        console.log(`   ${index + 1}. ${rec}`);
      });
      console.log('');
    }

    console.log('='.repeat(80));
  }

  /**
   * Run all performance tests
   */
  async runAllTests(): Promise<void> {
    try {
      // Start server
      await this.startServer();

      // Run tests
      console.log('\n🧪 Starting performance tests...\n');

      this.results.push(await this.testHealthCheck());
      this.results.push(await this.testTargetLoad());
      this.results.push(await this.testStressLoad());
      this.results.push(await this.testSustainedLoad());
      this.results.push(await this.testApiEndpoint());

      // Analyze and report
      const report = this.analyzeResults();
      this.printSummary(report);
      this.saveResults(report);

      // Exit with appropriate code
      process.exit(report.summary.passed ? 0 : 1);
    } catch (error) {
      console.error('❌ Performance test failed:', error);
      process.exit(1);
    } finally {
      await this.stopServer();
    }
  }
}

// Run tests if executed directly
if (require.main === module) {
  const tester = new PerformanceTester();
  tester.runAllTests();
}

export { PerformanceTester, LoadTestResult, PerformanceReport };

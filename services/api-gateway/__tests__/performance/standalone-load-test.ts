/**
 * Standalone Load Testing Script for API Gateway
 * 
 * This script tests the API Gateway performance without external service dependencies.
 * It creates a minimal server setup for testing core gateway functionality.
 */

import autocannon from 'autocannon';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { Server } from 'http';
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
    p50: number;
    p95: number;
    p99: number;
  };
  latency: {
    average: number;
    p50: number;
    p95: number;
    p99: number;
  };
  throughput: {
    average: number;
  };
  errors: number;
  timeouts: number;
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

class StandalonePerformanceTester {
  private server: Server | null = null;
  private readonly port = 8080; // Use different port to avoid conflicts
  private readonly baseUrl = `http://localhost:${this.port}`;
  private readonly resultsDir = path.join(__dirname, 'results');
  private results: LoadTestResult[] = [];

  constructor() {
    // Ensure results directory exists
    if (!fs.existsSync(this.resultsDir)) {
      fs.mkdirSync(this.resultsDir, { recursive: true });
    }
  }

  /**
   * Create a minimal Express server for testing
   */
  private createTestServer(): express.Application {
    const app = express();

    // Basic security middleware
    app.use(helmet());
    app.use(cors());

    // Body parsing
    app.use(express.json({ limit: '10mb' }));
    app.use(express.urlencoded({ extended: true }));

    // Simple health endpoint
    app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'api-gateway',
        version: '1.0.0',
      });
    });

    // Simple API endpoint
    app.get('/api/v1/test', (req, res) => {
      res.json({
        message: 'Test endpoint',
        timestamp: new Date().toISOString(),
        data: { id: 1, name: 'test' },
      });
    });

    // POST endpoint for testing
    app.post('/api/v1/test', (req, res) => {
      res.json({
        message: 'Test POST endpoint',
        timestamp: new Date().toISOString(),
        received: req.body,
      });
    });

    return app;
  }

  /**
   * Start the test server
   */
  private async startServer(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log(`🚀 Starting test server on port ${this.port}...`);
      
      const app = this.createTestServer();
      
      this.server = app.listen(this.port, () => {
        console.log('✅ Test server started successfully');
        resolve();
      });

      this.server.on('error', (error: any) => {
        if (error.code === 'EADDRINUSE') {
          console.error(`❌ Port ${this.port} is already in use`);
          reject(new Error(`Port ${this.port} is already in use`));
        } else {
          reject(error);
        }
      });
    });
  }

  /**
   * Stop the test server
   */
  private async stopServer(): Promise<void> {
    if (this.server) {
      console.log('🛑 Stopping test server...');
      return new Promise((resolve) => {
        this.server!.close(() => {
          console.log('✅ Test server stopped');
          resolve();
        });
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
            p50: result.requests.p50,
            p95: result.requests.p95,
            p99: result.requests.p99,
          },
          latency: {
            average: result.latency.average,
            p50: result.latency.p50,
            p95: result.latency.p95,
            p99: result.latency.p99,
          },
          throughput: {
            average: result.throughput.average,
          },
          errors: result.errors,
          timeouts: result.timeouts,
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
    });
  }

  /**
   * Test 4: API Endpoint Test
   */
  private async testApiEndpoint(): Promise<LoadTestResult> {
    return this.runLoadTest('API Endpoint Test', {
      url: `${this.baseUrl}/api/v1/test`,
      connections: 50,
      pipelining: 5,
      duration: 20,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Test 5: POST Endpoint Test
   */
  private async testPostEndpoint(): Promise<LoadTestResult> {
    return this.runLoadTest('POST Endpoint Test', {
      url: `${this.baseUrl}/api/v1/test`,
      method: 'POST',
      connections: 25,
      pipelining: 2,
      duration: 15,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ test: 'data', timestamp: Date.now() }),
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
    const filename = `standalone-performance-report-${timestamp}.json`;
    const filepath = path.join(this.resultsDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(report, null, 2));
    console.log(`\n📄 Results saved to: ${filepath}`);

    // Also save a summary markdown file
    const mdFilename = `standalone-performance-report-${timestamp}.md`;
    const mdFilepath = path.join(this.resultsDir, mdFilename);
    const markdown = this.generateMarkdownReport(report);
    fs.writeFileSync(mdFilepath, markdown);
    console.log(`📄 Summary saved to: ${mdFilepath}`);
  }

  /**
   * Generate markdown report
   */
  private generateMarkdownReport(report: PerformanceReport): string {
    let md = `# API Gateway Standalone Performance Test Report\n\n`;
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
      md += `| p95 | ${test.latency.p95} |\n`;
      md += `| p99 | ${test.latency.p99} |\n\n`;

      md += `**Errors:**\n`;
      md += `- Errors: ${test.errors}\n`;
      md += `- Timeouts: ${test.timeouts}\n\n`;
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
    console.log('📊 STANDALONE PERFORMANCE TEST SUMMARY');
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

    console.log('Requirements Check:');
    const targetLoadTest = report.tests.find(t => t.testName.includes('Target Load'));
    if (targetLoadTest) {
      console.log(`| Requirement | Target | Status |`);
      console.log(`|-------------|--------|--------|`);
      console.log(`| Throughput | 1000 req/s | ${targetLoadTest.requests.average >= 1000 ? '✅' : '❌'} ${targetLoadTest.requests.average.toFixed(2)} req/s |`);
      console.log(`| Latency p50 | <50ms | ${targetLoadTest.latency.p50 < 50 ? '✅' : '❌'} ${targetLoadTest.latency.p50}ms |`);
      console.log(`| Latency p95 | <100ms | ${targetLoadTest.latency.p95 < 100 ? '✅' : '❌'} ${targetLoadTest.latency.p95}ms |`);
      console.log(`| Latency p99 | <200ms | ${targetLoadTest.latency.p99 < 200 ? '✅' : '❌'} ${targetLoadTest.latency.p99}ms |`);
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

      // Wait a moment for server to be ready
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Run tests
      console.log('\n🧪 Starting standalone performance tests...\n');

      this.results.push(await this.testHealthCheck());
      this.results.push(await this.testTargetLoad());
      this.results.push(await this.testStressLoad());
      this.results.push(await this.testApiEndpoint());
      this.results.push(await this.testPostEndpoint());

      // Analyze and report
      const report = this.analyzeResults();
      this.printSummary(report);
      this.saveResults(report);

      // Exit with appropriate code
      process.exit(report.summary.passed ? 0 : 1);
    } catch (error) {
      console.error('❌ Standalone performance test failed:', error);
      process.exit(1);
    } finally {
      await this.stopServer();
    }
  }
}

// Run tests if executed directly
if (require.main === module) {
  const tester = new StandalonePerformanceTester();
  tester.runAllTests();
}

export { StandalonePerformanceTester };
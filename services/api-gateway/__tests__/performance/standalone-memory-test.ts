/**
 * Standalone Memory Testing Script for API Gateway
 * 
 * This script tests memory usage and detects memory leaks during load testing.
 */

import autocannon from 'autocannon';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { Server } from 'http';
import * as path from 'path';
import * as fs from 'fs';

interface MemorySnapshot {
  timestamp: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
  rss: number;
}

interface MemoryTestResult {
  testName: string;
  duration: number;
  memoryLimit: number;
  snapshots: MemorySnapshot[];
  maxMemory: {
    heapUsed: number;
    heapTotal: number;
    external: number;
    rss: number;
  };
  memoryGrowth: {
    heapUsed: number;
    heapTotal: number;
    external: number;
    rss: number;
  };
  passed: boolean;
  leakDetected: boolean;
}

interface MemoryReport {
  timestamp: string;
  tests: MemoryTestResult[];
  summary: {
    passed: boolean;
    totalTests: number;
    passedTests: number;
    failedTests: number;
    memoryLeaksDetected: number;
    recommendations: string[];
  };
}

class StandaloneMemoryTester {
  private server: Server | null = null;
  private readonly port = 8081;
  private readonly baseUrl = `http://localhost:${this.port}`;
  private readonly resultsDir = path.join(__dirname, 'results');
  private readonly memoryLimit = 512 * 1024 * 1024; // 512MB in bytes
  private results: MemoryTestResult[] = [];

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

    // Memory-intensive endpoint for testing
    app.get('/api/v1/memory-test', (req, res) => {
      // Create some temporary data to simulate processing
      const data = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        name: `item-${i}`,
        data: Buffer.alloc(1024, 'test'), // 1KB buffer
        timestamp: new Date().toISOString(),
      }));

      res.json({
        message: 'Memory test endpoint',
        timestamp: new Date().toISOString(),
        itemCount: data.length,
        totalSize: data.length * 1024,
      });
    });

    return app;
  }

  /**
   * Start the test server
   */
  private async startServer(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log(`🚀 Starting memory test server on port ${this.port}...`);
      
      const app = this.createTestServer();
      
      this.server = app.listen(this.port, () => {
        console.log('✅ Memory test server started successfully');
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
      console.log('🛑 Stopping memory test server...');
      return new Promise((resolve) => {
        this.server!.close(() => {
          console.log('✅ Memory test server stopped');
          resolve();
        });
      });
    }
  }

  /**
   * Take a memory snapshot
   */
  private takeMemorySnapshot(): MemorySnapshot {
    const memUsage = process.memoryUsage();
    return {
      timestamp: Date.now(),
      heapUsed: memUsage.heapUsed,
      heapTotal: memUsage.heapTotal,
      external: memUsage.external,
      rss: memUsage.rss,
    };
  }

  /**
   * Format bytes to human readable format
   */
  private formatBytes(bytes: number): string {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  }

  /**
   * Run memory test with load
   */
  private async runMemoryTest(
    testName: string,
    duration: number,
    url: string,
    connections: number = 50,
    pipelining: number = 5
  ): Promise<MemoryTestResult> {
    console.log(`\n📊 Running memory test: ${testName}`);
    console.log(`   Duration: ${duration}s`);
    console.log(`   URL: ${url}`);
    console.log(`   Connections: ${connections}`);

    const snapshots: MemorySnapshot[] = [];
    const samplingInterval = 1000; // 1 second

    // Take initial snapshot
    const initialSnapshot = this.takeMemorySnapshot();
    snapshots.push(initialSnapshot);

    // Start load test
    const loadTestPromise = new Promise<void>((resolve, reject) => {
      const instance = autocannon({
        url,
        connections,
        pipelining,
        duration,
      }, (err, result) => {
        if (err) {
          reject(err);
        } else {
          console.log(`   Load test completed: ${result.requests.average.toFixed(2)} req/s`);
          resolve();
        }
      });
    });

    // Start memory monitoring
    const memoryMonitoringPromise = new Promise<void>((resolve) => {
      const startTime = Date.now();
      const interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        if (elapsed >= duration * 1000) {
          clearInterval(interval);
          resolve();
        } else {
          snapshots.push(this.takeMemorySnapshot());
        }
      }, samplingInterval);
    });

    // Wait for both to complete
    await Promise.all([loadTestPromise, memoryMonitoringPromise]);

    // Take final snapshot
    const finalSnapshot = this.takeMemorySnapshot();
    snapshots.push(finalSnapshot);

    // Analyze results
    const maxMemory = {
      heapUsed: Math.max(...snapshots.map(s => s.heapUsed)),
      heapTotal: Math.max(...snapshots.map(s => s.heapTotal)),
      external: Math.max(...snapshots.map(s => s.external)),
      rss: Math.max(...snapshots.map(s => s.rss)),
    };

    const memoryGrowth = {
      heapUsed: finalSnapshot.heapUsed - initialSnapshot.heapUsed,
      heapTotal: finalSnapshot.heapTotal - initialSnapshot.heapTotal,
      external: finalSnapshot.external - initialSnapshot.external,
      rss: finalSnapshot.rss - initialSnapshot.rss,
    };

    // Check if memory limit exceeded
    const passed = maxMemory.rss <= this.memoryLimit;

    // Detect memory leak (growth > 50% of initial)
    const leakDetected = memoryGrowth.rss > (initialSnapshot.rss * 0.5);

    console.log(`   Max RSS: ${this.formatBytes(maxMemory.rss)}`);
    console.log(`   Memory Growth: ${this.formatBytes(memoryGrowth.rss)}`);
    console.log(`   Status: ${passed ? '✅' : '❌'}`);
    console.log(`   Leak Detected: ${leakDetected ? '⚠️' : '✅'}`);

    return {
      testName,
      duration,
      memoryLimit: this.memoryLimit,
      snapshots,
      maxMemory,
      memoryGrowth,
      passed,
      leakDetected,
    };
  }

  /**
   * Test 1: Short Duration Memory Test
   */
  private async testShortDuration(): Promise<MemoryTestResult> {
    return this.runMemoryTest(
      'Short Duration (30s)',
      30,
      `${this.baseUrl}/health`,
      25,
      2
    );
  }

  /**
   * Test 2: Medium Duration Memory Test
   */
  private async testMediumDuration(): Promise<MemoryTestResult> {
    return this.runMemoryTest(
      'Medium Duration (60s)',
      60,
      `${this.baseUrl}/health`,
      50,
      5
    );
  }

  /**
   * Test 3: Long Duration Memory Test
   */
  private async testLongDuration(): Promise<MemoryTestResult> {
    return this.runMemoryTest(
      'Long Duration (120s)',
      120,
      `${this.baseUrl}/health`,
      100,
      10
    );
  }

  /**
   * Test 4: Memory-Intensive Endpoint Test
   */
  private async testMemoryIntensive(): Promise<MemoryTestResult> {
    return this.runMemoryTest(
      'Memory-Intensive Endpoint (60s)',
      60,
      `${this.baseUrl}/api/v1/memory-test`,
      25,
      2
    );
  }

  /**
   * Analyze results and generate recommendations
   */
  private analyzeResults(): MemoryReport {
    const recommendations: string[] = [];
    let passedTests = 0;
    let memoryLeaksDetected = 0;

    this.results.forEach((result) => {
      if (result.passed) {
        passedTests++;
      } else {
        recommendations.push(`${result.testName}: Memory usage exceeded limit (${this.formatBytes(result.maxMemory.rss)} > ${this.formatBytes(this.memoryLimit)})`);
      }

      if (result.leakDetected) {
        memoryLeaksDetected++;
        recommendations.push(`${result.testName}: Potential memory leak detected (growth: ${this.formatBytes(result.memoryGrowth.rss)})`);
      }
    });

    // General recommendations
    if (memoryLeaksDetected > 0) {
      recommendations.push('Review code for unclosed connections, event listeners, or large caches');
      recommendations.push('Consider using memory profiling tools to identify leak sources');
    }

    if (passedTests < this.results.length) {
      recommendations.push('Consider optimizing memory usage in middleware and request handlers');
      recommendations.push('Review buffer sizes and temporary object creation');
    }

    return {
      timestamp: new Date().toISOString(),
      tests: this.results,
      summary: {
        passed: passedTests === this.results.length && memoryLeaksDetected === 0,
        totalTests: this.results.length,
        passedTests,
        failedTests: this.results.length - passedTests,
        memoryLeaksDetected,
        recommendations: [...new Set(recommendations)],
      },
    };
  }

  /**
   * Save results to file
   */
  private saveResults(report: MemoryReport): void {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `standalone-memory-report-${timestamp}.json`;
    const filepath = path.join(this.resultsDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(report, null, 2));
    console.log(`\n📄 Results saved to: ${filepath}`);

    // Also save a summary markdown file
    const mdFilename = `standalone-memory-report-${timestamp}.md`;
    const mdFilepath = path.join(this.resultsDir, mdFilename);
    const markdown = this.generateMarkdownReport(report);
    fs.writeFileSync(mdFilepath, markdown);
    console.log(`📄 Summary saved to: ${mdFilepath}`);
  }

  /**
   * Generate markdown report
   */
  private generateMarkdownReport(report: MemoryReport): string {
    let md = `# API Gateway Standalone Memory Test Report\n\n`;
    md += `**Date:** ${new Date(report.timestamp).toLocaleString()}\n\n`;
    md += `**Status:** ${report.summary.passed ? '✅ PASSED' : '❌ FAILED'}\n\n`;
    md += `**Memory Limit:** ${this.formatBytes(this.memoryLimit)}\n\n`;

    md += `## Summary\n\n`;
    md += `| Metric | Value |\n`;
    md += `|--------|-------|\n`;
    md += `| Total Tests | ${report.summary.totalTests} |\n`;
    md += `| Passed | ${report.summary.passedTests} |\n`;
    md += `| Failed | ${report.summary.failedTests} |\n`;
    md += `| Memory Leaks Detected | ${report.summary.memoryLeaksDetected} |\n\n`;

    md += `## Test Results\n\n`;
    report.tests.forEach((test) => {
      md += `### ${test.testName}\n\n`;
      md += `**Configuration:**\n`;
      md += `- Duration: ${test.duration}s\n`;
      md += `- Memory Limit: ${this.formatBytes(test.memoryLimit)}\n\n`;

      md += `**Memory Usage:**\n`;
      md += `| Metric | Max Usage | Growth |\n`;
      md += `|--------|-----------|--------|\n`;
      md += `| Heap Used | ${this.formatBytes(test.maxMemory.heapUsed)} | ${this.formatBytes(test.memoryGrowth.heapUsed)} |\n`;
      md += `| Heap Total | ${this.formatBytes(test.maxMemory.heapTotal)} | ${this.formatBytes(test.memoryGrowth.heapTotal)} |\n`;
      md += `| RSS | ${this.formatBytes(test.maxMemory.rss)} | ${this.formatBytes(test.memoryGrowth.rss)} |\n`;
      md += `| External | ${this.formatBytes(test.maxMemory.external)} | ${this.formatBytes(test.memoryGrowth.external)} |\n\n`;

      md += `**Status:**\n`;
      md += `- Memory Limit Check: ${test.passed ? '✅ PASSED' : '❌ FAILED'}\n`;
      md += `- Memory Leak Check: ${test.leakDetected ? '⚠️ DETECTED' : '✅ NONE'}\n\n`;

      // Memory usage chart (simplified)
      md += `**Memory Usage Over Time:**\n`;
      md += `\`\`\`\n`;
      test.snapshots.forEach((snapshot, index) => {
        const elapsed = Math.round((snapshot.timestamp - test.snapshots[0].timestamp) / 1000);
        const rssPercent = Math.round((snapshot.rss / this.memoryLimit) * 100);
        const bar = '█'.repeat(Math.min(rssPercent / 2, 50));
        md += `${elapsed.toString().padStart(3)}s: ${bar} ${this.formatBytes(snapshot.rss)}\n`;
      });
      md += `\`\`\`\n\n`;
    });

    if (report.summary.recommendations.length > 0) {
      md += `## 💡 Recommendations\n\n`;
      report.summary.recommendations.forEach((rec, index) => {
        md += `${index + 1}. ${rec}\n`;
      });
      md += `\n`;
    }

    return md;
  }

  /**
   * Print summary to console
   */
  private printSummary(report: MemoryReport): void {
    console.log('\n' + '='.repeat(80));
    console.log('📊 STANDALONE MEMORY TEST SUMMARY');
    console.log('='.repeat(80));
    console.log(`\nStatus: ${report.summary.passed ? '✅ PASSED' : '❌ FAILED'}`);
    console.log(`Memory Limit: ${this.formatBytes(this.memoryLimit)}\n`);

    report.tests.forEach((test) => {
      console.log(`${test.testName}:`);
      console.log(`  Max RSS: ${this.formatBytes(test.maxMemory.rss)}`);
      console.log(`  Status: ${test.passed ? '✅' : '❌'}`);
      if (test.leakDetected) {
        console.log(`  ⚠️  Memory leak detected (growth: ${this.formatBytes(test.memoryGrowth.rss)})`);
      }
      console.log('');
    });

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
   * Run all memory tests
   */
  async runAllTests(): Promise<void> {
    try {
      // Start server
      await this.startServer();

      // Wait a moment for server to be ready
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Run tests
      console.log('\n🧪 Starting standalone memory tests...\n');

      this.results.push(await this.testShortDuration());
      this.results.push(await this.testMediumDuration());
      this.results.push(await this.testLongDuration());
      this.results.push(await this.testMemoryIntensive());

      // Analyze and report
      const report = this.analyzeResults();
      this.printSummary(report);
      this.saveResults(report);

      // Exit with appropriate code
      process.exit(report.summary.passed ? 0 : 1);
    } catch (error) {
      console.error('❌ Standalone memory test failed:', error);
      process.exit(1);
    } finally {
      await this.stopServer();
    }
  }
}

// Run tests if executed directly
if (require.main === module) {
  const tester = new StandaloneMemoryTester();
  tester.runAllTests();
}

export { StandaloneMemoryTester };
/**
 * Memory Usage Testing Script for API Gateway
 * 
 * This script monitors memory usage under load to detect:
 * - Memory leaks
 * - Memory usage patterns
 * - Peak memory consumption
 * - Memory growth over time
 * 
 * Target: Memory usage should stay under 512MB under load
 */

import autocannon from 'autocannon';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

interface MemorySample {
  timestamp: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
  rss: number;
  arrayBuffers: number;
}

interface MemoryTestResult {
  testName: string;
  duration: number;
  samples: MemorySample[];
  statistics: {
    heapUsed: {
      min: number;
      max: number;
      average: number;
      final: number;
    };
    rss: {
      min: number;
      max: number;
      average: number;
      final: number;
    };
    growth: {
      heapUsed: number;
      rss: number;
    };
  };
  passed: boolean;
  issues: string[];
}

class MemoryTester {
  private serverProcess: ChildProcess | null = null;
  private readonly baseUrl = 'http://localhost:3000';
  private readonly resultsDir = path.join(__dirname, 'results');
  private readonly memoryLimit = 512 * 1024 * 1024; // 512MB in bytes
  private memorySamples: MemorySample[] = [];
  private samplingInterval: NodeJS.Timeout | null = null;

  constructor() {
    if (!fs.existsSync(this.resultsDir)) {
      fs.mkdirSync(this.resultsDir, { recursive: true });
    }
  }

  /**
   * Start the API Gateway server
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
          setTimeout(resolve, 2000);
        }
      });

      this.serverProcess.stderr?.on('data', (data) => {
        console.error('Server error:', data.toString());
      });

      this.serverProcess.on('error', reject);

      setTimeout(() => reject(new Error('Server startup timeout')), 30000);
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
        
        setTimeout(() => {
          this.serverProcess?.kill('SIGKILL');
          resolve();
        }, 5000);
      });
    }
  }

  /**
   * Sample memory usage from the server process
   */
  private sampleMemory(): void {
    if (!this.serverProcess || !this.serverProcess.pid) {
      return;
    }

    try {
      // Get memory usage from the process
      const memUsage = process.memoryUsage();
      
      const sample: MemorySample = {
        timestamp: Date.now(),
        heapUsed: memUsage.heapUsed,
        heapTotal: memUsage.heapTotal,
        external: memUsage.external,
        rss: memUsage.rss,
        arrayBuffers: memUsage.arrayBuffers || 0,
      };

      this.memorySamples.push(sample);
    } catch (error) {
      console.error('Error sampling memory:', error);
    }
  }

  /**
   * Start memory sampling
   */
  private startMemorySampling(intervalMs: number = 1000): void {
    console.log(`📊 Starting memory sampling (interval: ${intervalMs}ms)`);
    this.memorySamples = [];
    this.samplingInterval = setInterval(() => {
      this.sampleMemory();
    }, intervalMs);
  }

  /**
   * Stop memory sampling
   */
  private stopMemorySampling(): void {
    if (this.samplingInterval) {
      clearInterval(this.samplingInterval);
      this.samplingInterval = null;
      console.log('✅ Memory sampling stopped');
    }
  }

  /**
   * Run load test while monitoring memory
   */
  private async runLoadTestWithMemoryMonitoring(
    testName: string,
    duration: number
  ): Promise<MemoryTestResult> {
    console.log(`\n🧪 Running memory test: ${testName}`);
    console.log(`   Duration: ${duration}s`);

    // Start memory sampling
    this.startMemorySampling(1000);

    // Run load test
    await new Promise<void>((resolve, reject) => {
      const instance = autocannon({
        url: `${this.baseUrl}/health`,
        connections: 100,
        pipelining: 10,
        duration,
      }, (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });

      autocannon.track(instance, { renderProgressBar: true });
    });

    // Stop sampling
    this.stopMemorySampling();

    // Analyze results
    return this.analyzeMemoryUsage(testName, duration);
  }

  /**
   * Analyze memory usage patterns
   */
  private analyzeMemoryUsage(testName: string, duration: number): MemoryTestResult {
    const issues: string[] = [];

    // Calculate statistics
    const heapUsedValues = this.memorySamples.map(s => s.heapUsed);
    const rssValues = this.memorySamples.map(s => s.rss);

    const heapUsedMin = Math.min(...heapUsedValues);
    const heapUsedMax = Math.max(...heapUsedValues);
    const heapUsedAvg = heapUsedValues.reduce((a, b) => a + b, 0) / heapUsedValues.length;
    const heapUsedFinal = heapUsedValues[heapUsedValues.length - 1];

    const rssMin = Math.min(...rssValues);
    const rssMax = Math.max(...rssValues);
    const rssAvg = rssValues.reduce((a, b) => a + b, 0) / rssValues.length;
    const rssFinal = rssValues[rssValues.length - 1];

    // Calculate growth
    const heapGrowth = heapUsedFinal - heapUsedValues[0];
    const rssGrowth = rssFinal - rssValues[0];

    // Check against requirements
    let passed = true;

    // Check if memory exceeds limit
    if (rssMax > this.memoryLimit) {
      issues.push(
        `Memory exceeded limit: ${this.formatBytes(rssMax)} (limit: ${this.formatBytes(this.memoryLimit)})`
      );
      passed = false;
    }

    // Check for memory leaks (significant growth over time)
    const heapGrowthPercent = (heapGrowth / heapUsedValues[0]) * 100;
    if (heapGrowthPercent > 50) {
      issues.push(
        `Potential memory leak detected: heap grew by ${heapGrowthPercent.toFixed(2)}%`
      );
      passed = false;
    }

    // Check for excessive memory usage
    if (heapUsedAvg > this.memoryLimit * 0.8) {
      issues.push(
        `High average memory usage: ${this.formatBytes(heapUsedAvg)} (80% of limit)`
      );
      passed = false;
    }

    console.log(`   Heap Used: ${this.formatBytes(heapUsedMin)} - ${this.formatBytes(heapUsedMax)} (avg: ${this.formatBytes(heapUsedAvg)})`);
    console.log(`   RSS: ${this.formatBytes(rssMin)} - ${this.formatBytes(rssMax)} (avg: ${this.formatBytes(rssAvg)})`);
    console.log(`   Growth: Heap ${this.formatBytes(heapGrowth)}, RSS ${this.formatBytes(rssGrowth)}`);
    console.log(`   Status: ${passed ? '✅ PASSED' : '❌ FAILED'}`);

    return {
      testName,
      duration,
      samples: this.memorySamples,
      statistics: {
        heapUsed: {
          min: heapUsedMin,
          max: heapUsedMax,
          average: heapUsedAvg,
          final: heapUsedFinal,
        },
        rss: {
          min: rssMin,
          max: rssMax,
          average: rssAvg,
          final: rssFinal,
        },
        growth: {
          heapUsed: heapGrowth,
          rss: rssGrowth,
        },
      },
      passed,
      issues,
    };
  }

  /**
   * Format bytes to human-readable format
   */
  private formatBytes(bytes: number): string {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  }

  /**
   * Generate memory usage chart (ASCII)
   */
  private generateMemoryChart(samples: MemorySample[]): string {
    const height = 20;
    const width = 80;
    
    const rssValues = samples.map(s => s.rss);
    const maxRss = Math.max(...rssValues);
    const minRss = Math.min(...rssValues);
    const range = maxRss - minRss;

    let chart = '\nMemory Usage Over Time (RSS):\n\n';
    chart += `${this.formatBytes(maxRss)} ┤\n`;

    for (let i = height; i >= 0; i--) {
      const threshold = minRss + (range * i / height);
      let line = '           │';
      
      for (let j = 0; j < width; j++) {
        const sampleIndex = Math.floor((j / width) * samples.length);
        const value = rssValues[sampleIndex];
        
        if (value >= threshold) {
          line += '█';
        } else {
          line += ' ';
        }
      }
      
      chart += line + '\n';
    }

    chart += `${this.formatBytes(minRss)} └${'─'.repeat(width)}\n`;
    chart += `           0s${' '.repeat(width - 15)}${samples.length}s\n`;

    return chart;
  }

  /**
   * Save results to file
   */
  private saveResults(results: MemoryTestResult[]): void {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `memory-test-${timestamp}.json`;
    const filepath = path.join(this.resultsDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(results, null, 2));
    console.log(`\n📄 Results saved to: ${filepath}`);

    // Generate markdown report
    const mdFilename = `memory-test-${timestamp}.md`;
    const mdFilepath = path.join(this.resultsDir, mdFilename);
    const markdown = this.generateMarkdownReport(results);
    fs.writeFileSync(mdFilepath, markdown);
    console.log(`📄 Summary saved to: ${mdFilepath}`);
  }

  /**
   * Generate markdown report
   */
  private generateMarkdownReport(results: MemoryTestResult[]): string {
    let md = `# API Gateway Memory Test Report\n\n`;
    md += `**Date:** ${new Date().toLocaleString()}\n\n`;
    md += `**Memory Limit:** ${this.formatBytes(this.memoryLimit)}\n\n`;

    const allPassed = results.every(r => r.passed);
    md += `**Status:** ${allPassed ? '✅ PASSED' : '❌ FAILED'}\n\n`;

    md += `## Test Results\n\n`;

    results.forEach((result) => {
      md += `### ${result.testName}\n\n`;
      md += `**Duration:** ${result.duration}s\n\n`;

      md += `**Heap Used:**\n`;
      md += `- Min: ${this.formatBytes(result.statistics.heapUsed.min)}\n`;
      md += `- Max: ${this.formatBytes(result.statistics.heapUsed.max)}\n`;
      md += `- Average: ${this.formatBytes(result.statistics.heapUsed.average)}\n`;
      md += `- Final: ${this.formatBytes(result.statistics.heapUsed.final)}\n`;
      md += `- Growth: ${this.formatBytes(result.statistics.growth.heapUsed)}\n\n`;

      md += `**RSS (Resident Set Size):**\n`;
      md += `- Min: ${this.formatBytes(result.statistics.rss.min)}\n`;
      md += `- Max: ${this.formatBytes(result.statistics.rss.max)}\n`;
      md += `- Average: ${this.formatBytes(result.statistics.rss.average)}\n`;
      md += `- Final: ${this.formatBytes(result.statistics.rss.final)}\n`;
      md += `- Growth: ${this.formatBytes(result.statistics.growth.rss)}\n\n`;

      md += `**Status:** ${result.passed ? '✅ PASSED' : '❌ FAILED'}\n\n`;

      if (result.issues.length > 0) {
        md += `**Issues:**\n`;
        result.issues.forEach((issue) => {
          md += `- ${issue}\n`;
        });
        md += `\n`;
      }

      md += this.generateMemoryChart(result.samples);
      md += `\n`;
    });

    return md;
  }

  /**
   * Run all memory tests
   */
  async runAllTests(): Promise<void> {
    const results: MemoryTestResult[] = [];

    try {
      await this.startServer();

      console.log('\n🧪 Starting memory tests...\n');

      // Test 1: Short duration (30s)
      results.push(await this.runLoadTestWithMemoryMonitoring('Short Duration Test', 30));

      // Test 2: Medium duration (60s)
      results.push(await this.runLoadTestWithMemoryMonitoring('Medium Duration Test', 60));

      // Test 3: Long duration (120s)
      results.push(await this.runLoadTestWithMemoryMonitoring('Long Duration Test', 120));

      // Save results
      this.saveResults(results);

      // Print summary
      console.log('\n' + '='.repeat(80));
      console.log('📊 MEMORY TEST SUMMARY');
      console.log('='.repeat(80));
      
      const allPassed = results.every(r => r.passed);
      console.log(`\nStatus: ${allPassed ? '✅ PASSED' : '❌ FAILED'}`);
      console.log(`Memory Limit: ${this.formatBytes(this.memoryLimit)}\n`);

      results.forEach((result) => {
        console.log(`${result.testName}:`);
        console.log(`  Max RSS: ${this.formatBytes(result.statistics.rss.max)}`);
        console.log(`  Status: ${result.passed ? '✅' : '❌'}`);
        if (result.issues.length > 0) {
          result.issues.forEach((issue) => {
            console.log(`  ⚠️  ${issue}`);
          });
        }
        console.log('');
      });

      console.log('='.repeat(80));

      process.exit(allPassed ? 0 : 1);
    } catch (error) {
      console.error('❌ Memory test failed:', error);
      process.exit(1);
    } finally {
      await this.stopServer();
    }
  }
}

// Run tests if executed directly
if (require.main === module) {
  const tester = new MemoryTester();
  tester.runAllTests();
}

export { MemoryTester, MemoryTestResult };

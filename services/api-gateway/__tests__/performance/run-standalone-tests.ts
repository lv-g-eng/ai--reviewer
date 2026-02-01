/**
 * Comprehensive Standalone Performance Test Suite
 * 
 * This script runs both load tests and memory tests for the API Gateway
 * without requiring external service dependencies.
 */

import { StandalonePerformanceTester } from './standalone-load-test';
import { StandaloneMemoryTester } from './standalone-memory-test';
import * as path from 'path';
import * as fs from 'fs';

interface ComprehensiveReport {
  timestamp: string;
  loadTests: {
    passed: boolean;
    summary: string;
    reportFile: string;
  };
  memoryTests: {
    passed: boolean;
    summary: string;
    reportFile: string;
  };
  overall: {
    passed: boolean;
    summary: string;
    bottlenecks: string[];
    recommendations: string[];
  };
}

class ComprehensivePerformanceTester {
  private readonly resultsDir = path.join(__dirname, 'results');

  constructor() {
    // Ensure results directory exists
    if (!fs.existsSync(this.resultsDir)) {
      fs.mkdirSync(this.resultsDir, { recursive: true });
    }
  }

  /**
   * Run load tests
   */
  private async runLoadTests(): Promise<{ passed: boolean; summary: string; reportFile: string }> {
    console.log('╔════════════════════════════════════════════════════════════════════════════╗');
    console.log('║                           LOAD TESTS                                      ║');
    console.log('╚════════════════════════════════════════════════════════════════════════════╝');

    return new Promise((resolve) => {
      const tester = new StandalonePerformanceTester();
      
      // Override the exit behavior to capture results
      const originalExit = process.exit;
      let exitCode = 0;
      
      process.exit = ((code: number = 0) => {
        exitCode = code;
        // Don't actually exit, just capture the code
      }) as any;

      tester.runAllTests().then(() => {
        // Restore original exit
        process.exit = originalExit;
        
        // Find the latest report file
        const files = fs.readdirSync(this.resultsDir)
          .filter(f => f.startsWith('standalone-performance-report-') && f.endsWith('.json'))
          .sort()
          .reverse();
        
        const reportFile = files[0] || 'not-found';
        
        resolve({
          passed: exitCode === 0,
          summary: exitCode === 0 ? 'All load tests passed' : 'Some load tests failed',
          reportFile,
        });
      }).catch((error) => {
        // Restore original exit
        process.exit = originalExit;
        
        resolve({
          passed: false,
          summary: `Load tests failed: ${error.message}`,
          reportFile: 'error',
        });
      });
    });
  }

  /**
   * Run memory tests
   */
  private async runMemoryTests(): Promise<{ passed: boolean; summary: string; reportFile: string }> {
    console.log('\n╔════════════════════════════════════════════════════════════════════════════╗');
    console.log('║                          MEMORY TESTS                                     ║');
    console.log('╚════════════════════════════════════════════════════════════════════════════╝');

    return new Promise((resolve) => {
      const tester = new StandaloneMemoryTester();
      
      // Override the exit behavior to capture results
      const originalExit = process.exit;
      let exitCode = 0;
      
      process.exit = ((code: number = 0) => {
        exitCode = code;
        // Don't actually exit, just capture the code
      }) as any;

      tester.runAllTests().then(() => {
        // Restore original exit
        process.exit = originalExit;
        
        // Find the latest memory report file
        const files = fs.readdirSync(this.resultsDir)
          .filter(f => f.startsWith('standalone-memory-report-') && f.endsWith('.json'))
          .sort()
          .reverse();
        
        const reportFile = files[0] || 'not-found';
        
        resolve({
          passed: exitCode === 0,
          summary: exitCode === 0 ? 'All memory tests passed' : 'Some memory tests failed',
          reportFile,
        });
      }).catch((error) => {
        // Restore original exit
        process.exit = originalExit;
        
        resolve({
          passed: false,
          summary: `Memory tests failed: ${error.message}`,
          reportFile: 'error',
        });
      });
    });
  }

  /**
   * Generate comprehensive report
   */
  private generateComprehensiveReport(
    loadResults: { passed: boolean; summary: string; reportFile: string },
    memoryResults: { passed: boolean; summary: string; reportFile: string }
  ): ComprehensiveReport {
    const bottlenecks: string[] = [];
    const recommendations: string[] = [];

    // Analyze load test results
    if (!loadResults.passed) {
      bottlenecks.push('Load test failures detected');
      recommendations.push('Review load test results for specific performance issues');
    }

    // Analyze memory test results
    if (!memoryResults.passed) {
      bottlenecks.push('Memory test failures detected');
      recommendations.push('Review memory test results for memory leaks or excessive usage');
    }

    // General recommendations
    if (!loadResults.passed || !memoryResults.passed) {
      recommendations.push('Consider optimizing middleware chain');
      recommendations.push('Review server configuration and resource limits');
      recommendations.push('Implement performance monitoring in production');
    }

    const overallPassed = loadResults.passed && memoryResults.passed;

    return {
      timestamp: new Date().toISOString(),
      loadTests: loadResults,
      memoryTests: memoryResults,
      overall: {
        passed: overallPassed,
        summary: overallPassed 
          ? 'All performance tests passed successfully' 
          : 'Some performance tests failed',
        bottlenecks,
        recommendations,
      },
    };
  }

  /**
   * Save comprehensive report
   */
  private saveComprehensiveReport(report: ComprehensiveReport): void {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `comprehensive-performance-report-${timestamp}.json`;
    const filepath = path.join(this.resultsDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(report, null, 2));
    console.log(`\n📄 Comprehensive report saved to: ${filepath}`);

    // Also save a summary markdown file
    const mdFilename = `comprehensive-performance-report-${timestamp}.md`;
    const mdFilepath = path.join(this.resultsDir, mdFilename);
    const markdown = this.generateMarkdownReport(report);
    fs.writeFileSync(mdFilepath, markdown);
    console.log(`📄 Summary saved to: ${mdFilepath}`);
  }

  /**
   * Generate markdown report
   */
  private generateMarkdownReport(report: ComprehensiveReport): string {
    let md = `# API Gateway Comprehensive Performance Test Report\n\n`;
    md += `**Date:** ${new Date(report.timestamp).toLocaleString()}\n\n`;
    md += `**Overall Status:** ${report.overall.passed ? '✅ PASSED' : '❌ FAILED'}\n\n`;

    md += `## Executive Summary\n\n`;
    md += `${report.overall.summary}\n\n`;

    md += `## Test Results Overview\n\n`;
    md += `| Test Suite | Status | Summary |\n`;
    md += `|------------|--------|----------|\n`;
    md += `| Load Tests | ${report.loadTests.passed ? '✅ PASSED' : '❌ FAILED'} | ${report.loadTests.summary} |\n`;
    md += `| Memory Tests | ${report.memoryTests.passed ? '✅ PASSED' : '❌ FAILED'} | ${report.memoryTests.summary} |\n\n`;

    md += `## Performance Requirements Status\n\n`;
    md += `| Requirement | Target | Status | Notes |\n`;
    md += `|-------------|--------|--------|-------|\n`;
    md += `| Throughput | 1000 req/s | ${report.loadTests.passed ? '✅' : '❌'} | See load test report |\n`;
    md += `| Response Time | <50ms routing overhead | ${report.loadTests.passed ? '✅' : '❌'} | See load test report |\n`;
    md += `| Memory Usage | <512MB under load | ${report.memoryTests.passed ? '✅' : '❌'} | See memory test report |\n\n`;

    if (report.overall.bottlenecks.length > 0) {
      md += `## 🚨 Bottlenecks Identified\n\n`;
      report.overall.bottlenecks.forEach((bottleneck, index) => {
        md += `${index + 1}. ${bottleneck}\n`;
      });
      md += `\n`;
    }

    if (report.overall.recommendations.length > 0) {
      md += `## 💡 Recommendations\n\n`;
      report.overall.recommendations.forEach((rec, index) => {
        md += `${index + 1}. ${rec}\n`;
      });
      md += `\n`;
    }

    md += `## Detailed Reports\n\n`;
    md += `- **Load Test Report:** \`${report.loadTests.reportFile}\`\n`;
    md += `- **Memory Test Report:** \`${report.memoryTests.reportFile}\`\n\n`;

    md += `## Next Steps\n\n`;
    if (report.overall.passed) {
      md += `✅ All performance tests passed. The API Gateway meets the performance requirements.\n\n`;
      md += `**Recommended actions:**\n`;
      md += `1. Deploy to staging environment for integration testing\n`;
      md += `2. Set up performance monitoring in production\n`;
      md += `3. Establish performance regression testing in CI/CD pipeline\n`;
    } else {
      md += `❌ Some performance tests failed. Address the issues before deployment.\n\n`;
      md += `**Required actions:**\n`;
      md += `1. Review detailed test reports for specific issues\n`;
      md += `2. Implement recommended optimizations\n`;
      md += `3. Re-run performance tests to verify fixes\n`;
      md += `4. Consider load testing with realistic backend services\n`;
    }

    return md;
  }

  /**
   * Print comprehensive summary
   */
  private printComprehensiveSummary(report: ComprehensiveReport): void {
    console.log('\n' + '╔' + '═'.repeat(78) + '╗');
    console.log('║' + ' '.repeat(20) + 'COMPREHENSIVE PERFORMANCE SUMMARY' + ' '.repeat(25) + '║');
    console.log('╚' + '═'.repeat(78) + '╝');
    
    console.log(`\n📊 Overall Status: ${report.overall.passed ? '✅ PASSED' : '❌ FAILED'}`);
    console.log(`📝 Summary: ${report.overall.summary}\n`);

    console.log('Test Results:');
    console.log(`  Load Tests:   ${report.loadTests.passed ? '✅ PASSED' : '❌ FAILED'} - ${report.loadTests.summary}`);
    console.log(`  Memory Tests: ${report.memoryTests.passed ? '✅ PASSED' : '❌ FAILED'} - ${report.memoryTests.summary}\n`);

    if (report.overall.bottlenecks.length > 0) {
      console.log('🚨 Bottlenecks Identified:');
      report.overall.bottlenecks.forEach((bottleneck, index) => {
        console.log(`   ${index + 1}. ${bottleneck}`);
      });
      console.log('');
    }

    if (report.overall.recommendations.length > 0) {
      console.log('💡 Recommendations:');
      report.overall.recommendations.forEach((rec, index) => {
        console.log(`   ${index + 1}. ${rec}`);
      });
      console.log('');
    }

    console.log('Detailed Reports:');
    console.log(`  Load Test:   ${report.loadTests.reportFile}`);
    console.log(`  Memory Test: ${report.memoryTests.reportFile}`);

    console.log('\n' + '═'.repeat(80));
  }

  /**
   * Run all performance tests
   */
  async runAllTests(): Promise<void> {
    console.log('╔════════════════════════════════════════════════════════════════════════════╗');
    console.log('║              API GATEWAY COMPREHENSIVE PERFORMANCE TEST SUITE              ║');
    console.log('╚════════════════════════════════════════════════════════════════════════════╝');
    console.log('\nThis test suite will:');
    console.log('  1. Run load tests (throughput, latency, response times)');
    console.log('  2. Run memory tests (memory usage, leak detection)');
    console.log('  3. Generate comprehensive performance report');
    console.log('\n⏱️  Estimated time: 10-15 minutes\n');

    try {
      // Run load tests
      const loadResults = await this.runLoadTests();
      
      // Wait a moment between test suites
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Run memory tests
      const memoryResults = await this.runMemoryTests();

      // Generate comprehensive report
      const report = this.generateComprehensiveReport(loadResults, memoryResults);
      this.printComprehensiveSummary(report);
      this.saveComprehensiveReport(report);

      // Exit with appropriate code
      process.exit(report.overall.passed ? 0 : 1);
    } catch (error) {
      console.error('❌ Comprehensive performance test failed:', error);
      process.exit(1);
    }
  }
}

// Run tests if executed directly
if (require.main === module) {
  const tester = new ComprehensivePerformanceTester();
  tester.runAllTests();
}

export { ComprehensivePerformanceTester };
/**
 * Bottleneck Analysis Script for API Gateway
 * 
 * This script analyzes performance test results and identifies specific bottlenecks
 * with actionable recommendations for optimization.
 */

import * as fs from 'fs';
import * as path from 'path';

interface BottleneckAnalysis {
  timestamp: string;
  analysisResults: {
    throughputBottlenecks: string[];
    latencyBottlenecks: string[];
    memoryBottlenecks: string[];
    errorBottlenecks: string[];
  };
  recommendations: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
  };
  prioritizedActions: {
    priority: 'HIGH' | 'MEDIUM' | 'LOW';
    action: string;
    impact: string;
    effort: string;
  }[];
}

class BottleneckAnalyzer {
  private readonly resultsDir = path.join(__dirname, 'results');

  /**
   * Analyze load test results for bottlenecks
   */
  private analyzeLoadTestResults(loadTestData: any): {
    throughputBottlenecks: string[];
    latencyBottlenecks: string[];
    errorBottlenecks: string[];
  } {
    const throughputBottlenecks: string[] = [];
    const latencyBottlenecks: string[] = [];
    const errorBottlenecks: string[] = [];

    if (loadTestData && loadTestData.tests) {
      loadTestData.tests.forEach((test: any) => {
        // Throughput analysis
        if (test.testName.includes('Target Load') && test.requests.average < 1000) {
          throughputBottlenecks.push(
            `Target load test achieved only ${test.requests.average.toFixed(2)} req/s (target: 1000 req/s)`
          );
          
          if (test.requests.average < 500) {
            throughputBottlenecks.push('Severely low throughput indicates major performance issues');
          } else if (test.requests.average < 750) {
            throughputBottlenecks.push('Moderate throughput issues - likely middleware or I/O bottlenecks');
          }
        }

        // Latency analysis
        if (test.latency.p50 > 50) {
          latencyBottlenecks.push(
            `High p50 latency in ${test.testName}: ${test.latency.p50}ms (target: <50ms)`
          );
        }

        if (test.latency.p95 > 100) {
          latencyBottlenecks.push(
            `High p95 latency in ${test.testName}: ${test.latency.p95}ms (target: <100ms)`
          );
        }

        if (test.latency.p99 > 200) {
          latencyBottlenecks.push(
            `High p99 latency in ${test.testName}: ${test.latency.p99}ms (target: <200ms)`
          );
        }

        // Latency pattern analysis
        if (test.latency.p99 > test.latency.p50 * 10) {
          latencyBottlenecks.push(
            `High latency variance in ${test.testName} suggests inconsistent performance`
          );
        }

        // Error analysis
        if (test.errors > 0) {
          errorBottlenecks.push(
            `${test.testName} had ${test.errors} errors - indicates service instability`
          );
        }

        if (test.timeouts > 0) {
          errorBottlenecks.push(
            `${test.testName} had ${test.timeouts} timeouts - suggests slow response times`
          );
        }
      });
    }

    return { throughputBottlenecks, latencyBottlenecks, errorBottlenecks };
  }

  /**
   * Analyze memory test results for bottlenecks
   */
  private analyzeMemoryTestResults(memoryTestData: any): string[] {
    const memoryBottlenecks: string[] = [];

    if (memoryTestData && memoryTestData.tests) {
      memoryTestData.tests.forEach((test: any) => {
        // Memory limit analysis
        if (!test.passed) {
          memoryBottlenecks.push(
            `${test.testName} exceeded memory limit: ${this.formatBytes(test.maxMemory.rss)} > ${this.formatBytes(test.memoryLimit)}`
          );
        }

        // Memory leak analysis
        if (test.leakDetected) {
          memoryBottlenecks.push(
            `Potential memory leak in ${test.testName}: ${this.formatBytes(test.memoryGrowth.rss)} growth`
          );
        }

        // Memory usage patterns
        if (test.maxMemory.rss > test.memoryLimit * 0.8) {
          memoryBottlenecks.push(
            `High memory usage in ${test.testName}: ${this.formatBytes(test.maxMemory.rss)} (80%+ of limit)`
          );
        }

        // Heap vs RSS analysis
        if (test.maxMemory.rss > test.maxMemory.heapUsed * 3) {
          memoryBottlenecks.push(
            `High RSS to heap ratio in ${test.testName} suggests memory fragmentation or native memory usage`
          );
        }
      });
    }

    return memoryBottlenecks;
  }

  /**
   * Generate recommendations based on bottlenecks
   */
  private generateRecommendations(bottlenecks: {
    throughputBottlenecks: string[];
    latencyBottlenecks: string[];
    memoryBottlenecks: string[];
    errorBottlenecks: string[];
  }): {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
  } {
    const immediate: string[] = [];
    const shortTerm: string[] = [];
    const longTerm: string[] = [];

    // Immediate actions (can be done now)
    if (bottlenecks.errorBottlenecks.length > 0) {
      immediate.push('Fix error handling and timeout issues');
      immediate.push('Review server logs for error patterns');
    }

    if (bottlenecks.memoryBottlenecks.some(b => b.includes('leak'))) {
      immediate.push('Investigate and fix memory leaks');
      immediate.push('Review event listeners and connection cleanup');
    }

    // Short-term optimizations (1-2 weeks)
    if (bottlenecks.latencyBottlenecks.length > 0) {
      shortTerm.push('Optimize middleware chain execution order');
      shortTerm.push('Implement response caching for frequently accessed data');
      shortTerm.push('Review and optimize database queries');
    }

    if (bottlenecks.throughputBottlenecks.length > 0) {
      shortTerm.push('Enable HTTP keep-alive connections');
      shortTerm.push('Implement connection pooling for backend services');
      shortTerm.push('Optimize JSON parsing and serialization');
    }

    if (bottlenecks.memoryBottlenecks.length > 0) {
      shortTerm.push('Optimize memory usage in request handlers');
      shortTerm.push('Implement proper buffer management');
      shortTerm.push('Review and optimize caching strategies');
    }

    // Long-term improvements (1+ months)
    if (bottlenecks.throughputBottlenecks.length > 0 || bottlenecks.latencyBottlenecks.length > 0) {
      longTerm.push('Consider implementing horizontal scaling');
      longTerm.push('Evaluate alternative web frameworks (Fastify, etc.)');
      longTerm.push('Implement advanced caching strategies (Redis, CDN)');
    }

    longTerm.push('Set up comprehensive performance monitoring');
    longTerm.push('Implement automated performance regression testing');
    longTerm.push('Consider microservice architecture optimizations');

    return { immediate, shortTerm, longTerm };
  }

  /**
   * Generate prioritized action items
   */
  private generatePrioritizedActions(bottlenecks: {
    throughputBottlenecks: string[];
    latencyBottlenecks: string[];
    memoryBottlenecks: string[];
    errorBottlenecks: string[];
  }): {
    priority: 'HIGH' | 'MEDIUM' | 'LOW';
    action: string;
    impact: string;
    effort: string;
  }[] {
    const actions: {
      priority: 'HIGH' | 'MEDIUM' | 'LOW';
      action: string;
      impact: string;
      effort: string;
    }[] = [];

    // High priority actions
    if (bottlenecks.errorBottlenecks.length > 0) {
      actions.push({
        priority: 'HIGH',
        action: 'Fix error handling and eliminate timeouts',
        impact: 'Prevents service failures and improves reliability',
        effort: 'Low - Medium',
      });
    }

    if (bottlenecks.memoryBottlenecks.some(b => b.includes('leak'))) {
      actions.push({
        priority: 'HIGH',
        action: 'Fix memory leaks',
        impact: 'Prevents service crashes and improves stability',
        effort: 'Medium',
      });
    }

    if (bottlenecks.throughputBottlenecks.some(b => b.includes('Severely low'))) {
      actions.push({
        priority: 'HIGH',
        action: 'Address severe throughput bottlenecks',
        impact: 'Critical for meeting performance requirements',
        effort: 'High',
      });
    }

    // Medium priority actions
    if (bottlenecks.latencyBottlenecks.length > 0) {
      actions.push({
        priority: 'MEDIUM',
        action: 'Optimize middleware chain and reduce latency',
        impact: 'Improves user experience and response times',
        effort: 'Medium',
      });
    }

    if (bottlenecks.throughputBottlenecks.length > 0) {
      actions.push({
        priority: 'MEDIUM',
        action: 'Implement connection pooling and keep-alive',
        impact: 'Improves throughput and resource utilization',
        effort: 'Low - Medium',
      });
    }

    // Low priority actions
    actions.push({
      priority: 'LOW',
      action: 'Set up performance monitoring and alerting',
      impact: 'Enables proactive performance management',
      effort: 'Medium',
    });

    actions.push({
      priority: 'LOW',
      action: 'Implement automated performance testing in CI/CD',
      impact: 'Prevents performance regressions',
      effort: 'Medium - High',
    });

    return actions;
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
   * Find latest test result files
   */
  private findLatestTestResults(): { loadTest: string | null; memoryTest: string | null } {
    if (!fs.existsSync(this.resultsDir)) {
      return { loadTest: null, memoryTest: null };
    }

    const files = fs.readdirSync(this.resultsDir);

    const loadTestFiles = files
      .filter(f => f.startsWith('standalone-performance-report-') && f.endsWith('.json'))
      .sort()
      .reverse();

    const memoryTestFiles = files
      .filter(f => f.startsWith('standalone-memory-report-') && f.endsWith('.json'))
      .sort()
      .reverse();

    return {
      loadTest: loadTestFiles[0] || null,
      memoryTest: memoryTestFiles[0] || null,
    };
  }

  /**
   * Analyze bottlenecks from test results
   */
  async analyzeBottlenecks(): Promise<BottleneckAnalysis> {
    console.log('🔍 Analyzing performance test results for bottlenecks...\n');

    const testFiles = this.findLatestTestResults();

    let loadTestData = null;
    let memoryTestData = null;

    // Load test results
    if (testFiles.loadTest) {
      const loadTestPath = path.join(this.resultsDir, testFiles.loadTest);
      console.log(`📊 Analyzing load test results: ${testFiles.loadTest}`);
      loadTestData = JSON.parse(fs.readFileSync(loadTestPath, 'utf8'));
    } else {
      console.log('⚠️  No load test results found');
    }

    if (testFiles.memoryTest) {
      const memoryTestPath = path.join(this.resultsDir, testFiles.memoryTest);
      console.log(`🧠 Analyzing memory test results: ${testFiles.memoryTest}`);
      memoryTestData = JSON.parse(fs.readFileSync(memoryTestPath, 'utf8'));
    } else {
      console.log('⚠️  No memory test results found');
    }

    // Analyze bottlenecks
    const loadBottlenecks = this.analyzeLoadTestResults(loadTestData);
    const memoryBottlenecks = this.analyzeMemoryTestResults(memoryTestData);

    const allBottlenecks = {
      throughputBottlenecks: loadBottlenecks.throughputBottlenecks,
      latencyBottlenecks: loadBottlenecks.latencyBottlenecks,
      memoryBottlenecks,
      errorBottlenecks: loadBottlenecks.errorBottlenecks,
    };

    // Generate recommendations
    const recommendations = this.generateRecommendations(allBottlenecks);
    const prioritizedActions = this.generatePrioritizedActions(allBottlenecks);

    return {
      timestamp: new Date().toISOString(),
      analysisResults: allBottlenecks,
      recommendations,
      prioritizedActions,
    };
  }

  /**
   * Save analysis results
   */
  private saveAnalysis(analysis: BottleneckAnalysis): void {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `bottleneck-analysis-${timestamp}.json`;
    const filepath = path.join(this.resultsDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(analysis, null, 2));
    console.log(`\n📄 Analysis saved to: ${filepath}`);

    // Also save a markdown report
    const mdFilename = `bottleneck-analysis-${timestamp}.md`;
    const mdFilepath = path.join(this.resultsDir, mdFilename);
    const markdown = this.generateMarkdownReport(analysis);
    fs.writeFileSync(mdFilepath, markdown);
    console.log(`📄 Report saved to: ${mdFilepath}`);
  }

  /**
   * Generate markdown report
   */
  private generateMarkdownReport(analysis: BottleneckAnalysis): string {
    let md = `# API Gateway Bottleneck Analysis Report\n\n`;
    md += `**Date:** ${new Date(analysis.timestamp).toLocaleString()}\n\n`;

    // Executive Summary
    const totalBottlenecks = 
      analysis.analysisResults.throughputBottlenecks.length +
      analysis.analysisResults.latencyBottlenecks.length +
      analysis.analysisResults.memoryBottlenecks.length +
      analysis.analysisResults.errorBottlenecks.length;

    md += `## Executive Summary\n\n`;
    if (totalBottlenecks === 0) {
      md += `✅ **No significant bottlenecks detected.** The API Gateway is performing within acceptable parameters.\n\n`;
    } else {
      md += `⚠️  **${totalBottlenecks} bottlenecks identified** that require attention to meet performance requirements.\n\n`;
    }

    // Bottleneck Analysis
    md += `## Bottleneck Analysis\n\n`;

    if (analysis.analysisResults.throughputBottlenecks.length > 0) {
      md += `### 🚀 Throughput Bottlenecks\n\n`;
      analysis.analysisResults.throughputBottlenecks.forEach((bottleneck, index) => {
        md += `${index + 1}. ${bottleneck}\n`;
      });
      md += `\n`;
    }

    if (analysis.analysisResults.latencyBottlenecks.length > 0) {
      md += `### ⏱️ Latency Bottlenecks\n\n`;
      analysis.analysisResults.latencyBottlenecks.forEach((bottleneck, index) => {
        md += `${index + 1}. ${bottleneck}\n`;
      });
      md += `\n`;
    }

    if (analysis.analysisResults.memoryBottlenecks.length > 0) {
      md += `### 🧠 Memory Bottlenecks\n\n`;
      analysis.analysisResults.memoryBottlenecks.forEach((bottleneck, index) => {
        md += `${index + 1}. ${bottleneck}\n`;
      });
      md += `\n`;
    }

    if (analysis.analysisResults.errorBottlenecks.length > 0) {
      md += `### ❌ Error Bottlenecks\n\n`;
      analysis.analysisResults.errorBottlenecks.forEach((bottleneck, index) => {
        md += `${index + 1}. ${bottleneck}\n`;
      });
      md += `\n`;
    }

    // Recommendations
    md += `## Recommendations\n\n`;

    if (analysis.recommendations.immediate.length > 0) {
      md += `### 🚨 Immediate Actions (Do Now)\n\n`;
      analysis.recommendations.immediate.forEach((rec, index) => {
        md += `${index + 1}. ${rec}\n`;
      });
      md += `\n`;
    }

    if (analysis.recommendations.shortTerm.length > 0) {
      md += `### 📅 Short-term Optimizations (1-2 weeks)\n\n`;
      analysis.recommendations.shortTerm.forEach((rec, index) => {
        md += `${index + 1}. ${rec}\n`;
      });
      md += `\n`;
    }

    if (analysis.recommendations.longTerm.length > 0) {
      md += `### 🎯 Long-term Improvements (1+ months)\n\n`;
      analysis.recommendations.longTerm.forEach((rec, index) => {
        md += `${index + 1}. ${rec}\n`;
      });
      md += `\n`;
    }

    // Prioritized Actions
    md += `## Prioritized Action Plan\n\n`;
    md += `| Priority | Action | Impact | Effort |\n`;
    md += `|----------|--------|--------|--------|\n`;
    analysis.prioritizedActions.forEach((action) => {
      const priorityIcon = action.priority === 'HIGH' ? '🔴' : action.priority === 'MEDIUM' ? '🟡' : '🟢';
      md += `| ${priorityIcon} ${action.priority} | ${action.action} | ${action.impact} | ${action.effort} |\n`;
    });
    md += `\n`;

    return md;
  }

  /**
   * Print analysis summary
   */
  private printSummary(analysis: BottleneckAnalysis): void {
    console.log('\n' + '═'.repeat(80));
    console.log('🔍 BOTTLENECK ANALYSIS SUMMARY');
    console.log('═'.repeat(80));

    const totalBottlenecks = 
      analysis.analysisResults.throughputBottlenecks.length +
      analysis.analysisResults.latencyBottlenecks.length +
      analysis.analysisResults.memoryBottlenecks.length +
      analysis.analysisResults.errorBottlenecks.length;

    console.log(`\n📊 Total Bottlenecks Found: ${totalBottlenecks}\n`);

    if (analysis.analysisResults.throughputBottlenecks.length > 0) {
      console.log(`🚀 Throughput Issues: ${analysis.analysisResults.throughputBottlenecks.length}`);
    }
    if (analysis.analysisResults.latencyBottlenecks.length > 0) {
      console.log(`⏱️  Latency Issues: ${analysis.analysisResults.latencyBottlenecks.length}`);
    }
    if (analysis.analysisResults.memoryBottlenecks.length > 0) {
      console.log(`🧠 Memory Issues: ${analysis.analysisResults.memoryBottlenecks.length}`);
    }
    if (analysis.analysisResults.errorBottlenecks.length > 0) {
      console.log(`❌ Error Issues: ${analysis.analysisResults.errorBottlenecks.length}`);
    }

    if (totalBottlenecks === 0) {
      console.log('✅ No significant bottlenecks detected!');
    } else {
      console.log('\n🎯 Top Priority Actions:');
      analysis.prioritizedActions
        .filter(a => a.priority === 'HIGH')
        .slice(0, 3)
        .forEach((action, index) => {
          console.log(`   ${index + 1}. ${action.action}`);
        });
    }

    console.log('\n' + '═'.repeat(80));
  }

  /**
   * Run bottleneck analysis
   */
  async run(): Promise<void> {
    try {
      const analysis = await this.analyzeBottlenecks();
      this.printSummary(analysis);
      this.saveAnalysis(analysis);
    } catch (error) {
      console.error('❌ Bottleneck analysis failed:', error);
      process.exit(1);
    }
  }
}

// Run analysis if executed directly
if (require.main === module) {
  const analyzer = new BottleneckAnalyzer();
  analyzer.run();
}

export { BottleneckAnalyzer };
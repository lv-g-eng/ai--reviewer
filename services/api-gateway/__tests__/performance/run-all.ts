/**
 * Run All Performance Tests
 * 
 * This script runs all performance tests in sequence:
 * 1. Load tests (throughput, latency)
 * 2. Memory tests (memory usage, leaks)
 * 
 * Usage:
 *   npm run test:performance
 */

import { PerformanceTester } from './load-test';
import { MemoryTester } from './memory-test';

async function runAllPerformanceTests() {
  console.log('╔════════════════════════════════════════════════════════════════════════════╗');
  console.log('║                  API GATEWAY PERFORMANCE TEST SUITE                        ║');
  console.log('╚════════════════════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log('This test suite will:');
  console.log('  1. Run load tests (throughput, latency, response times)');
  console.log('  2. Run memory tests (memory usage, leak detection)');
  console.log('');
  console.log('⏱️  Estimated time: 5-10 minutes');
  console.log('');

  let loadTestsPassed = false;
  let memoryTestsPassed = false;

  try {
    // Run load tests
    console.log('\n' + '═'.repeat(80));
    console.log('PHASE 1: LOAD TESTS');
    console.log('═'.repeat(80));
    
    const loadTester = new PerformanceTester();
    await loadTester.runAllTests();
    loadTestsPassed = true;
  } catch (error) {
    console.error('❌ Load tests failed:', error);
    loadTestsPassed = false;
  }

  try {
    // Run memory tests
    console.log('\n' + '═'.repeat(80));
    console.log('PHASE 2: MEMORY TESTS');
    console.log('═'.repeat(80));
    
    const memoryTester = new MemoryTester();
    await memoryTester.runAllTests();
    memoryTestsPassed = true;
  } catch (error) {
    console.error('❌ Memory tests failed:', error);
    memoryTestsPassed = false;
  }

  // Final summary
  console.log('\n' + '╔' + '═'.repeat(78) + '╗');
  console.log('║' + ' '.repeat(25) + 'FINAL SUMMARY' + ' '.repeat(40) + '║');
  console.log('╚' + '═'.repeat(78) + '╝');
  console.log('');
  console.log(`Load Tests:   ${loadTestsPassed ? '✅ PASSED' : '❌ FAILED'}`);
  console.log(`Memory Tests: ${memoryTestsPassed ? '✅ PASSED' : '❌ FAILED'}`);
  console.log('');

  const allPassed = loadTestsPassed && memoryTestsPassed;
  console.log(`Overall Status: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
  console.log('');

  if (!allPassed) {
    console.log('⚠️  Please review the test reports in __tests__/performance/results/');
    console.log('');
  }

  process.exit(allPassed ? 0 : 1);
}

// Run if executed directly
if (require.main === module) {
  runAllPerformanceTests().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { runAllPerformanceTests };

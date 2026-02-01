/**
 * Validate Performance Test Setup
 * 
 * Quick validation script to ensure all dependencies are installed
 * and the performance testing infrastructure is ready.
 */

import * as fs from 'fs';
import * as path from 'path';

console.log('🔍 Validating Performance Test Setup...\n');

let allChecks = true;

// Check 1: Autocannon installed
try {
  require('autocannon');
  console.log('✅ autocannon is installed');
} catch (error) {
  console.log('❌ autocannon is NOT installed');
  console.log('   Run: npm install --save-dev autocannon');
  allChecks = false;
}

// Check 2: Test files exist
const testFiles = [
  '__tests__/performance/load-test.ts',
  '__tests__/performance/memory-test.ts',
  '__tests__/performance/run-all.ts',
  '__tests__/performance/README.md',
];

testFiles.forEach((file) => {
  const filepath = path.join(__dirname, '../..', file);
  if (fs.existsSync(filepath)) {
    console.log(`✅ ${file} exists`);
  } else {
    console.log(`❌ ${file} is missing`);
    allChecks = false;
  }
});

// Check 3: Results directory
const resultsDir = path.join(__dirname, 'results');
if (!fs.existsSync(resultsDir)) {
  fs.mkdirSync(resultsDir, { recursive: true });
  console.log('✅ Created results directory');
} else {
  console.log('✅ Results directory exists');
}

// Check 4: Package.json scripts
const packageJsonPath = path.join(__dirname, '../..', 'package.json');
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
  const requiredScripts = [
    'test:performance',
    'test:performance:load',
    'test:performance:memory',
  ];

  requiredScripts.forEach((script) => {
    if (packageJson.scripts && packageJson.scripts[script]) {
      console.log(`✅ npm script "${script}" is configured`);
    } else {
      console.log(`❌ npm script "${script}" is missing`);
      allChecks = false;
    }
  });
}

// Check 5: Server file exists
const serverFile = path.join(__dirname, '../..', 'src/index.ts');
if (fs.existsSync(serverFile)) {
  console.log('✅ Server file (src/index.ts) exists');
} else {
  console.log('❌ Server file (src/index.ts) is missing');
  allChecks = false;
}

// Summary
console.log('\n' + '='.repeat(60));
if (allChecks) {
  console.log('✅ All checks passed! Performance tests are ready to run.');
  console.log('\nTo run performance tests:');
  console.log('  npm run test:performance');
  process.exit(0);
} else {
  console.log('❌ Some checks failed. Please fix the issues above.');
  process.exit(1);
}

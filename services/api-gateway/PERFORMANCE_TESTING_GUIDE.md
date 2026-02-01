# API Gateway Performance Testing Guide

## 🎯 Quick Start

```bash
cd services/api-gateway
npm run test:performance
```

This will run all performance tests and generate comprehensive reports.

## 📊 What Gets Tested

### 1. Load Tests
- **Throughput**: Validates 1000 req/s requirement
- **Latency**: Measures p50, p95, p99 response times
- **Stability**: Tests sustained load over time
- **Stress**: Tests behavior under extreme load (5000 req/s)

### 2. Memory Tests
- **Usage**: Validates <512MB memory requirement
- **Leaks**: Detects memory growth over time
- **Stability**: Tests memory behavior under sustained load

### 3. Bottleneck Analysis
- Automatically identifies performance issues
- Provides actionable recommendations
- Validates against all requirements

## 📁 Test Files

```
__tests__/performance/
├── load-test.ts           # Load and latency testing
├── memory-test.ts         # Memory usage and leak detection
├── run-all.ts             # Orchestrates all tests
├── validate-setup.ts      # Validates test setup
├── README.md              # Comprehensive documentation
└── results/               # Test reports (generated)
```

## 🚀 Running Tests

### All Tests (Recommended)
```bash
npm run test:performance
```
Duration: 5-10 minutes

### Individual Test Suites

**Load Tests Only:**
```bash
npm run test:performance:load
```
Duration: 2-3 minutes

**Memory Tests Only:**
```bash
npm run test:performance:memory
```
Duration: 3-5 minutes

### Validate Setup
```bash
npx ts-node __tests__/performance/validate-setup.ts
```

## 📈 Understanding Results

### Test Reports Location
```
__tests__/performance/results/
├── performance-report-{timestamp}.json
├── performance-report-{timestamp}.md
├── memory-test-{timestamp}.json
└── memory-test-{timestamp}.md
```

### Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Throughput | ≥1000 req/s | ✅ |
| Latency p50 | <50ms | ✅ |
| Latency p95 | <100ms | ✅ |
| Latency p99 | <200ms | ✅ |
| Memory Usage | <512MB | ✅ |
| Memory Leaks | None | ✅ |

### Example Output

```
╔════════════════════════════════════════════════════════════════════════════╗
║                  API GATEWAY PERFORMANCE TEST SUITE                        ║
╚════════════════════════════════════════════════════════════════════════════╝

PHASE 1: LOAD TESTS
================================================================================

📊 Running test: Target Load (1000 req/s)
   Duration: 30s
   Connections: 100
   Pipelining: 10
   ✅ Completed
   Requests/sec: 1250.45
   Latency p50: 35ms
   Latency p95: 78ms
   Latency p99: 145ms
   Errors: 0

📊 PERFORMANCE TEST SUMMARY
================================================================================

Status: ✅ PASSED
Tests: 5/5 passed

Requirements Check:
| Requirement | Target | Status |
|-------------|--------|--------|
| Throughput | 1000 req/s | ✅ 1250.45 req/s |
| Latency p50 | <50ms | ✅ 35ms |
| Latency p95 | <100ms | ✅ 78ms |
| Latency p99 | <200ms | ✅ 145ms |

PHASE 2: MEMORY TESTS
================================================================================

📊 MEMORY TEST SUMMARY
================================================================================

Status: ✅ PASSED
Memory Limit: 512.00 MB

Short Duration Test:
  Max RSS: 245.32 MB
  Status: ✅

╔════════════════════════════════════════════════════════════════════════════╗
║                            FINAL SUMMARY                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

Load Tests:   ✅ PASSED
Memory Tests: ✅ PASSED

Overall Status: ✅ ALL TESTS PASSED
```

## 🔍 Bottleneck Detection

The test suite automatically detects:

### Performance Issues
- Low throughput (<1000 req/s)
- High latency (p50 >50ms, p95 >100ms)
- Error rates (timeouts, failures)

### Memory Issues
- Excessive usage (>512MB)
- Memory leaks (>50% growth)
- High average usage (>80% of limit)

### Recommendations
When issues are detected, the test suite provides:
- Specific problem identification
- Root cause analysis
- Actionable optimization recommendations

## 🛠️ Troubleshooting

### Server Won't Start
```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill process if needed
taskkill /PID <PID> /F
```

### Tests Timeout
- Ensure Redis is running (if using rate limiting)
- Check server logs in `logs/` directory
- Verify environment variables are set

### Memory Tests Fail
- Close unnecessary applications
- Review code for memory leaks
- Check for unclosed connections

### Inconsistent Results
- Run tests multiple times
- Close other applications
- Use a consistent test environment

## 📝 Best Practices

### Before Running Tests
1. Close unnecessary applications
2. Ensure services are healthy (Redis, etc.)
3. Set appropriate environment variables
4. Run on a consistent environment

### Interpreting Results
1. Run multiple times for accuracy
2. Compare trends across runs
3. Focus on percentiles (p95, p99)
4. Consider hardware and environment

### Continuous Monitoring
1. Run tests before releases
2. Track results over time
3. Set up alerts for regressions
4. Document performance changes

## 🔧 Configuration

### Environment Variables
```bash
# Server
PORT=3000
NODE_ENV=production

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379

# Services
PROJECTS_SERVICE_URL=http://localhost:3001
REVIEWS_SERVICE_URL=http://localhost:3002
```

### Customizing Tests

Edit test files to customize:

**Load Test** (`load-test.ts`):
```typescript
{
  url: 'http://localhost:3000/health',
  connections: 100,      // Concurrent connections
  pipelining: 10,        // Requests per connection
  duration: 30,          // Test duration (seconds)
}
```

**Memory Test** (`memory-test.ts`):
```typescript
{
  samplingInterval: 1000,  // Memory sampling (ms)
  memoryLimit: 512 * 1024 * 1024,  // Limit (bytes)
}
```

## 📚 Additional Resources

- [Autocannon Documentation](https://github.com/mcollina/autocannon)
- [Node.js Performance Guide](https://nodejs.org/en/docs/guides/simple-profiling/)
- [Memory Profiling](https://nodejs.org/en/docs/guides/diagnostics/memory/)
- [API Gateway Design](../../.kiro/specs/api-gateway-week1/design.md)
- [Detailed README](__tests__/performance/README.md)

## 🎓 Test Scenarios

### Load Tests

1. **Health Check Baseline** (10s)
   - Establishes baseline performance
   - Minimal middleware overhead

2. **Target Load** (30s)
   - Validates 1000 req/s requirement
   - Full middleware stack

3. **Stress Test** (20s)
   - Tests extreme load (5000 req/s)
   - Identifies breaking points

4. **Sustained Load** (60s)
   - Tests stability over time
   - Detects performance degradation

5. **API Endpoint** (20s)
   - Tests with authentication
   - Full middleware chain

### Memory Tests

1. **Short Duration** (30s)
   - Quick memory check
   - Baseline usage

2. **Medium Duration** (60s)
   - Detects early growth
   - Validates sustained usage

3. **Long Duration** (120s)
   - Detects memory leaks
   - Long-term stability

## ✅ Validation Checklist

Before running tests:
- [ ] All dependencies installed (`npm install`)
- [ ] Server can start successfully
- [ ] Redis is running (if using rate limiting)
- [ ] Environment variables are set
- [ ] Port 3000 is available
- [ ] No other resource-intensive applications running

After running tests:
- [ ] All tests passed
- [ ] No bottlenecks identified
- [ ] Memory usage within limits
- [ ] Latency meets requirements
- [ ] Throughput meets requirements
- [ ] Reports generated successfully

## 🤝 Contributing

When adding new performance tests:
1. Follow existing test structure
2. Document test purpose and metrics
3. Add appropriate thresholds
4. Update this guide
5. Ensure tests are reproducible

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review test logs in `results/`
3. Check server logs in `logs/`
4. Consult detailed README
5. Review API Gateway documentation

---

**Last Updated**: January 2026  
**Maintainer**: Backend Team  
**Status**: ✅ Production Ready

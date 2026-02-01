# API Gateway Performance Testing

This directory contains comprehensive performance testing tools for the API Gateway service.

## 📋 Overview

The performance test suite includes:

1. **Load Tests** - Test throughput, latency, and response times under various load conditions
2. **Memory Tests** - Monitor memory usage and detect memory leaks
3. **Bottleneck Analysis** - Identify performance bottlenecks and provide recommendations

## 🎯 Performance Requirements

Based on the API Gateway Week 1 specification:

| Metric | Target | Description |
|--------|--------|-------------|
| Throughput | 1000 req/s | Requests per second under normal load |
| Routing Overhead | <50ms | Additional latency introduced by the gateway |
| Memory Usage | <512MB | Maximum memory consumption under load |
| Response Time (p50) | <50ms | 50th percentile response time |
| Response Time (p95) | <100ms | 95th percentile response time |
| Response Time (p99) | <200ms | 99th percentile response time |

## 🚀 Quick Start

### Run All Performance Tests

```bash
npm run test:performance
```

This will run both load tests and memory tests in sequence (takes 5-10 minutes).

### Run Individual Test Suites

**Load Tests Only:**
```bash
npm run test:performance:load
```

**Memory Tests Only:**
```bash
npm run test:performance:memory
```

## 📊 Test Suites

### 1. Load Tests (`load-test.ts`)

Tests the API Gateway under various load conditions:

#### Test Scenarios

1. **Health Check Baseline** (10s)
   - Connections: 10
   - Pipelining: 1
   - Purpose: Establish baseline performance

2. **Target Load** (30s)
   - Connections: 100
   - Pipelining: 10
   - Target: 1000 req/s
   - Purpose: Verify target throughput requirement

3. **Stress Test** (20s)
   - Connections: 500
   - Pipelining: 10
   - Target: 5000 req/s
   - Purpose: Test behavior under extreme load

4. **Sustained Load** (60s)
   - Connections: 100
   - Pipelining: 10
   - Purpose: Test stability over time

5. **API Endpoint Test** (20s)
   - Connections: 50
   - Pipelining: 5
   - Purpose: Test with full middleware stack

#### Metrics Collected

- **Throughput**: Requests per second (average, min, max)
- **Latency**: Response times at p50, p75, p90, p95, p99
- **Errors**: Error count, timeouts, non-2xx responses
- **Requests**: Total requests, request distribution

### 2. Memory Tests (`memory-test.ts`)

Monitors memory usage under load to detect leaks and excessive consumption:

#### Test Scenarios

1. **Short Duration** (30s)
   - Purpose: Quick memory check

2. **Medium Duration** (60s)
   - Purpose: Detect early memory growth

3. **Long Duration** (120s)
   - Purpose: Detect memory leaks over time

#### Metrics Collected

- **Heap Used**: JavaScript heap memory usage
- **RSS**: Resident Set Size (total memory)
- **External**: C++ objects bound to JavaScript
- **Memory Growth**: Change in memory over test duration

#### Memory Leak Detection

The test automatically detects potential memory leaks by:
- Tracking memory growth over time
- Calculating growth percentage
- Flagging growth >50% as potential leak

## 📈 Understanding Results

### Load Test Results

Results are saved in `__tests__/performance/results/` as:
- `performance-report-{timestamp}.json` - Raw data
- `performance-report-{timestamp}.md` - Human-readable summary

#### Example Output

```
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
```

### Memory Test Results

Results are saved in `__tests__/performance/results/` as:
- `memory-test-{timestamp}.json` - Raw data
- `memory-test-{timestamp}.md` - Human-readable summary with charts

#### Example Output

```
📊 MEMORY TEST SUMMARY
================================================================================

Status: ✅ PASSED
Memory Limit: 512.00 MB

Short Duration Test:
  Max RSS: 245.32 MB
  Status: ✅

Medium Duration Test:
  Max RSS: 268.45 MB
  Status: ✅

Long Duration Test:
  Max RSS: 289.12 MB
  Status: ✅
```

## 🔍 Bottleneck Analysis

The test suite automatically identifies bottlenecks and provides recommendations:

### Common Bottlenecks

1. **Low Throughput**
   - Symptom: <1000 req/s
   - Possible causes: Middleware overhead, synchronous operations
   - Recommendations: Optimize middleware chain, use async operations

2. **High Latency**
   - Symptom: p50 >50ms or p95 >100ms
   - Possible causes: Slow middleware, database queries, external API calls
   - Recommendations: Add caching, optimize queries, use connection pooling

3. **Memory Growth**
   - Symptom: Memory increases over time
   - Possible causes: Memory leaks, unclosed connections, large caches
   - Recommendations: Review event listeners, close connections, limit cache size

4. **High Error Rate**
   - Symptom: Errors or timeouts during tests
   - Possible causes: Service unavailability, timeout issues, rate limiting
   - Recommendations: Review error logs, adjust timeouts, check service health

## 🛠️ Troubleshooting

### Server Won't Start

**Problem**: Server fails to start during tests

**Solutions**:
1. Check if port 3000 is already in use
2. Ensure all dependencies are installed: `npm install`
3. Check environment variables are set correctly
4. Review server logs for errors

### Tests Timeout

**Problem**: Tests hang or timeout

**Solutions**:
1. Increase timeout in test configuration
2. Check if server is responding: `curl http://localhost:3000/health`
3. Review server logs for blocking operations
4. Ensure Redis is running (if using rate limiting)

### Memory Tests Fail

**Problem**: Memory usage exceeds limits

**Solutions**:
1. Review code for memory leaks
2. Check for unclosed connections or event listeners
3. Reduce cache sizes
4. Use memory profiling tools: `node --inspect`

### Inconsistent Results

**Problem**: Test results vary significantly between runs

**Solutions**:
1. Ensure no other processes are consuming resources
2. Run tests multiple times and average results
3. Close unnecessary applications
4. Use a dedicated test environment

## 📝 Best Practices

### Before Running Tests

1. **Close unnecessary applications** to free up resources
2. **Ensure services are healthy** (Redis, backend services)
3. **Set appropriate environment variables**
4. **Run on a consistent environment** for comparable results

### Interpreting Results

1. **Run multiple times** - Single runs can have anomalies
2. **Compare trends** - Look for patterns across multiple runs
3. **Consider context** - Results vary based on hardware and environment
4. **Focus on percentiles** - p95 and p99 are more important than averages

### Continuous Monitoring

1. **Run tests regularly** - Before releases, after changes
2. **Track results over time** - Detect performance regressions
3. **Set up alerts** - Notify when metrics exceed thresholds
4. **Document changes** - Note what caused performance changes

## 🔧 Configuration

### Customizing Tests

Edit the test files to customize:

**Load Test Configuration** (`load-test.ts`):
```typescript
{
  url: 'http://localhost:3000/health',
  connections: 100,      // Number of concurrent connections
  pipelining: 10,        // Requests per connection
  duration: 30,          // Test duration in seconds
  amount: 30000,         // Total requests (optional)
}
```

**Memory Test Configuration** (`memory-test.ts`):
```typescript
{
  samplingInterval: 1000,  // Memory sampling interval (ms)
  memoryLimit: 512 * 1024 * 1024,  // Memory limit in bytes
}
```

### Environment Variables

```bash
# Server configuration
PORT=3000
NODE_ENV=production

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379

# Service URLs
PROJECTS_SERVICE_URL=http://localhost:3001
REVIEWS_SERVICE_URL=http://localhost:3002
```

## 📚 Additional Resources

- [Autocannon Documentation](https://github.com/mcollina/autocannon)
- [Node.js Performance Best Practices](https://nodejs.org/en/docs/guides/simple-profiling/)
- [Memory Profiling in Node.js](https://nodejs.org/en/docs/guides/diagnostics/memory/)
- [API Gateway Design Specification](../../.kiro/specs/api-gateway-week1/design.md)

## 🤝 Contributing

When adding new performance tests:

1. Follow the existing test structure
2. Document test purpose and metrics
3. Add appropriate thresholds and validations
4. Update this README with new test information
5. Ensure tests are reproducible

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test logs in `__tests__/performance/results/`
3. Check server logs in `logs/`
4. Consult the API Gateway documentation

---

**Last Updated**: January 2026  
**Maintainer**: Backend Team

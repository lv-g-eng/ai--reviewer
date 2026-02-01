# API Gateway Performance Test Report

**Date:** 2026/1/22 17:21:59

**Status:** ❌ FAILED

**Tests:** 0/5 passed

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 5 |
| Passed | 0 |
| Failed | 5 |
| Bottlenecks Found | 7 |

## Test Results

### Health Check Baseline

**Configuration:**
- Duration: 10s
- Connections: 10
- Pipelining: 1

**Throughput:**
- Average: 0.10 req/s
- Total Requests: 1

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 601 |
| p75 | 601 |
| p90 | 601 |
| p95 | undefined |
| p99 | 601 |

**Errors:**
- Errors: 10344
- Timeouts: 0
- Non-2xx: 0

### Target Load (1000 req/s)

**Configuration:**
- Duration: 30s
- Connections: 100
- Pipelining: 10

**Throughput:**
- Average: 0.00 req/s
- Total Requests: 0

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 0 |
| p75 | 0 |
| p90 | 0 |
| p95 | undefined |
| p99 | 0 |

**Errors:**
- Errors: 3000
- Timeouts: 0
- Non-2xx: 0

### Stress Test (5000 req/s)

**Configuration:**
- Duration: 20s
- Connections: 500
- Pipelining: 10

**Throughput:**
- Average: 0.00 req/s
- Total Requests: 0

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 0 |
| p75 | 0 |
| p90 | 0 |
| p95 | undefined |
| p99 | 0 |

**Errors:**
- Errors: 10000
- Timeouts: 0
- Non-2xx: 0

### Sustained Load (60s)

**Configuration:**
- Duration: 60s
- Connections: 100
- Pipelining: 10

**Throughput:**
- Average: 0.00 req/s
- Total Requests: 0

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 0 |
| p75 | 0 |
| p90 | 0 |
| p95 | undefined |
| p99 | 0 |

**Errors:**
- Errors: 64787
- Timeouts: 10
- Non-2xx: 0

### API Endpoint (with middleware)

**Configuration:**
- Duration: 20s
- Connections: 50
- Pipelining: 5

**Throughput:**
- Average: 0.00 req/s
- Total Requests: 0

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 0 |
| p75 | 0 |
| p90 | 0 |
| p95 | undefined |
| p99 | 0 |

**Errors:**
- Errors: 15591
- Timeouts: 0
- Non-2xx: 0

## 🚨 Bottlenecks Identified

1. High p50 latency: 601ms (target: <50ms)
2. Errors detected: 10344 errors, 0 timeouts
3. Throughput below target: 0.00 req/s (target: 1000 req/s)
4. Errors detected: 3000 errors, 0 timeouts
5. Errors detected: 10000 errors, 0 timeouts
6. Errors detected: 64787 errors, 10 timeouts
7. Errors detected: 15591 errors, 0 timeouts

## 💡 Recommendations

1. Review middleware execution time
2. Consider caching frequently accessed data
3. Review error logs for failure patterns
4. Consider optimizing middleware chain
5. Enable HTTP keep-alive connections

## Requirements Check

| Requirement | Target | Status |
|-------------|--------|--------|
| Throughput | 1000 req/s | ❌ 0.00 req/s |
| Latency p50 | <50ms | ✅ 0ms |
| Latency p95 | <100ms | ❌ undefinedms |
| Latency p99 | <200ms | ✅ 0ms |

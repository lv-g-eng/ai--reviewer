# API Gateway Standalone Performance Test Report

**Date:** 2026/1/22 17:26:00

**Status:** ❌ FAILED

**Tests:** 3/5 passed

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 5 |
| Passed | 3 |
| Failed | 2 |
| Bottlenecks Found | 3 |

## Test Results

### Health Check Baseline

**Configuration:**
- Duration: 10s
- Connections: 10
- Pipelining: 1

**Throughput:**
- Average: 3987.00 req/s
- Total Requests: 39860

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 2 |
| p95 | undefined |
| p99 | 5 |

**Errors:**
- Errors: 0
- Timeouts: 0

### Target Load (1000 req/s)

**Configuration:**
- Duration: 30s
- Connections: 100
- Pipelining: 10

**Throughput:**
- Average: 5724.73 req/s
- Total Requests: 165960

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 176 |
| p95 | undefined |
| p99 | 286 |

**Errors:**
- Errors: 0
- Timeouts: 0

### Stress Test (5000 req/s)

**Configuration:**
- Duration: 20s
- Connections: 500
- Pipelining: 10

**Throughput:**
- Average: 5159.43 req/s
- Total Requests: 98010

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 1174 |
| p95 | undefined |
| p99 | 5976 |

**Errors:**
- Errors: 516
- Timeouts: 0

### API Endpoint Test

**Configuration:**
- Duration: 20s
- Connections: 50
- Pipelining: 5

**Throughput:**
- Average: 5163.70 req/s
- Total Requests: 103250

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 45 |
| p95 | undefined |
| p99 | 87 |

**Errors:**
- Errors: 0
- Timeouts: 0

### POST Endpoint Test

**Configuration:**
- Duration: 15s
- Connections: 25
- Pipelining: 2

**Throughput:**
- Average: 3857.60 req/s
- Total Requests: 57850

**Latency:**
| Percentile | Latency (ms) |
|------------|-------------|
| p50 | 12 |
| p95 | undefined |
| p99 | 26 |

**Errors:**
- Errors: 0
- Timeouts: 0

## 🚨 Bottlenecks Identified

1. High p50 latency: 176ms (target: <50ms)
2. High p50 latency: 1174ms (target: <50ms)
3. Errors detected: 516 errors, 0 timeouts

## 💡 Recommendations

1. Review middleware execution time
2. Consider caching frequently accessed data
3. Review error logs for failure patterns

## Requirements Check

| Requirement | Target | Status |
|-------------|--------|--------|
| Throughput | 1000 req/s | ✅ 5724.73 req/s |
| Latency p50 | <50ms | ❌ 176ms |
| Latency p95 | <100ms | ❌ undefinedms |
| Latency p99 | <200ms | ❌ 286ms |

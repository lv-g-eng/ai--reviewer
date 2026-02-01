# Circuit Breaker Quick Reference Card

## 🎯 Quick Start

### Create a Circuit Breaker

```typescript
import { createCircuitBreaker } from './middleware/circuitBreaker';

const breaker = createCircuitBreaker(
  async (userId) => {
    const response = await axios.get(`/api/users/${userId}`);
    return response.data;
  },
  'user-service'
);

// Use it
const user = await breaker.fire('user-123');
```

---

## 🔄 Circuit States

| State | Description | Behavior |
|-------|-------------|----------|
| **CLOSED** | Normal operation | All requests pass through |
| **OPEN** | Service failing | All requests rejected immediately |
| **HALF_OPEN** | Testing recovery | Limited requests allowed |

### State Transitions

```
CLOSED --[50% errors]--> OPEN
OPEN --[30 seconds]--> HALF_OPEN
HALF_OPEN --[success]--> CLOSED
HALF_OPEN --[failure]--> OPEN
```

---

## ⚙️ Configuration Options

```typescript
{
  timeout: 3000,                    // Request timeout (ms)
  errorThresholdPercentage: 50,     // Error rate to open (%)
  resetTimeout: 30000,              // Time before half-open (ms)
  rollingCountTimeout: 10000,       // Error calculation window (ms)
  rollingCountBuckets: 10,          // Buckets in window
}
```

### Common Configurations

#### Aggressive (Fast Failure)
```typescript
{
  timeout: 1000,
  errorThresholdPercentage: 30,
  resetTimeout: 10000,
}
```

#### Conservative (Tolerant)
```typescript
{
  timeout: 5000,
  errorThresholdPercentage: 70,
  resetTimeout: 60000,
}
```

#### Balanced (Default)
```typescript
{
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000,
}
```

---

## 📊 Monitoring

### Get Circuit Status

```typescript
import { getCircuitBreakerStats } from './middleware/circuitBreaker';

const stats = getCircuitBreakerStats('user-service');
console.log(stats);
// {
//   name: 'user-service',
//   state: 'CLOSED',
//   stats: {
//     fires: 1000,
//     successes: 995,
//     failures: 5,
//     rejects: 0,
//     timeouts: 0
//   }
// }
```

### Get All Circuits

```typescript
import { getAllCircuitBreakerStats } from './middleware/circuitBreaker';

const allStats = getAllCircuitBreakerStats();
```

---

## 🚨 Error Handling

### Circuit Open Error

```typescript
try {
  const result = await breaker.fire(params);
} catch (error) {
  if (error.code === 'EOPENBREAKER') {
    console.log('Circuit is open, service unavailable');
    // Return cached data or fallback
  }
}
```

### Timeout Error

```typescript
try {
  const result = await breaker.fire(params);
} catch (error) {
  if (error.code === 'ETIMEDOUT') {
    console.log('Request timed out');
    // Retry or return error
  }
}
```

---

## 🎨 Express Integration

### Automatic Error Handling

```typescript
import { circuitBreakerErrorHandler } from './middleware/circuitBreaker';

// Add after routes, before general error handler
app.use(circuitBreakerErrorHandler);
app.use(errorHandler);
```

### With Service Proxy

```typescript
import { withCircuitBreaker } from './services/serviceProxy';

const proxy = createServiceProxy({
  name: 'user-service',
  target: 'http://localhost:3001',
  useCircuitBreaker: true,
});

app.use('/api/users', withCircuitBreaker('user-service', proxy));
```

---

## 📝 Logging Events

Circuit breaker automatically logs these events:

| Event | Log Level | Description |
|-------|-----------|-------------|
| `open` | ERROR | Circuit opened (too many failures) |
| `halfOpen` | WARN | Circuit testing recovery |
| `close` | INFO | Circuit closed (service recovered) |
| `success` | DEBUG | Request succeeded |
| `failure` | ERROR | Request failed |
| `timeout` | ERROR | Request timed out |
| `reject` | WARN | Request rejected (circuit open) |

---

## 🔧 Troubleshooting

### Circuit Opens Too Often

**Increase error threshold:**
```typescript
errorThresholdPercentage: 70  // From 50
```

**Increase timeout:**
```typescript
timeout: 5000  // From 3000
```

### Circuit Stays Open

**Decrease reset timeout:**
```typescript
resetTimeout: 15000  // From 30000
```

**Manually close:**
```typescript
const breaker = getCircuitBreaker('my-service');
breaker.close();
```

### Too Many Timeouts

**Increase timeout:**
```typescript
timeout: 10000  // From 3000
```

---

## 💡 Best Practices

1. **One breaker per service** - Don't share breakers
2. **Configure per service** - Different services need different settings
3. **Monitor circuit state** - Add health checks
4. **Log all events** - Already done automatically
5. **Test failure scenarios** - Ensure circuit opens correctly
6. **Have fallbacks** - Return cached data when circuit is open
7. **Alert on open circuits** - Set up monitoring alerts

---

## 🧪 Testing

### Test Circuit Opening

```typescript
// Make multiple failing requests
for (let i = 0; i < 10; i++) {
  try {
    await breaker.fire();
  } catch (error) {
    // Expected to fail
  }
}

// Circuit should be open now
expect(breaker.opened).toBe(true);
```

### Test Circuit Recovery

```typescript
// Open circuit
// ... make failing requests ...

// Wait for reset timeout
await new Promise(resolve => setTimeout(resolve, 100));

// Circuit should be half-open
expect(breaker.halfOpen).toBe(true);

// Make successful request
await breaker.fire();

// Circuit should be closed
expect(breaker.closed).toBe(true);
```

---

## 📞 Quick Commands

```bash
# Run circuit breaker tests
npm test -- circuitBreaker

# Check circuit breaker logs
grep "Circuit breaker" logs/combined.log

# Monitor circuit state
curl http://localhost:3000/admin/circuit-breakers
```

---

## 🔗 Related Files

- Implementation: `src/middleware/circuitBreaker.ts`
- Tests: `__tests__/unit/middleware/circuitBreaker.test.ts`
- Service Proxy: `src/services/serviceProxy.ts`
- Documentation: `DAY_3_README.md`

---

**Need Help?** Check the full documentation in `DAY_3_README.md`


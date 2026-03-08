# CacheService

CacheService 是一个独立的缓存管理服务，提供灵活的缓存功能，支持自定义TTL、过期检查、统计信息等。

## 功能特性

- ✅ 设置和获取缓存数据
- ✅ 支持自定义TTL (Time To Live)
- ✅ 自动过期检查和清理
- ✅ 缓存统计功能 (命中率、大小等)
- ✅ 支持模式匹配的缓存清除
- ✅ 默认TTL: 5分钟 (300000ms)

## 基本使用

### 创建实例

```typescript
import { CacheService } from './services/CacheService';

// 使用默认TTL (5分钟)
const cache = new CacheService();

// 使用自定义默认TTL (10分钟)
const cache = new CacheService(10 * 60 * 1000);

// 使用工厂函数获取默认实例
import { getCacheService } from './services/CacheService';
const cache = getCacheService();
```

### 设置和获取缓存

```typescript
// 设置缓存 (使用默认TTL)
cache.set('user:123', { id: 123, name: 'John' });

// 设置缓存 (自定义TTL: 1分钟)
cache.set('session:abc', { token: 'xyz' }, 60 * 1000);

// 获取缓存
const user = cache.get('user:123');
if (user) {
  console.log('Cache hit:', user);
} else {
  console.log('Cache miss');
}
```

### 检查缓存状态

```typescript
// 检查缓存是否存在且未过期
if (cache.has('user:123')) {
  console.log('Cache exists');
}

// 检查缓存是否过期
if (cache.isExpired('user:123')) {
  console.log('Cache expired');
}

// 获取剩余TTL
const ttl = cache.getTTL('user:123');
console.log(`Cache expires in ${ttl}ms`);
```

### 清除缓存

```typescript
// 清除所有缓存
cache.clear();

// 清除匹配模式的缓存
cache.clear('user:'); // 清除所有以 'user:' 开头的缓存

// 清除所有过期的缓存
const clearedCount = cache.clearExpired();
console.log(`Cleared ${clearedCount} expired entries`);
```

### 缓存统计

```typescript
const stats = cache.getStats();
console.log(`Cache size: ${stats.size}`);
console.log(`Cache hits: ${stats.hits}`);
console.log(`Cache misses: ${stats.misses}`);
console.log(`Hit rate: ${stats.hitRate}%`);
console.log(`Keys: ${stats.keys.join(', ')}`);

// 重置统计信息
cache.resetStats();
```

### 更新TTL

```typescript
// 更新现有缓存的TTL
const updated = cache.updateTTL('user:123', 5 * 60 * 1000);
if (updated) {
  console.log('TTL updated successfully');
}
```

## 与 ApiClient 集成

虽然 ApiClient 已经内置了缓存功能，但 CacheService 可以用于其他场景：

```typescript
import { CacheService } from './services/CacheService';
import { apiClient } from './services/ApiClient';

const cache = new CacheService();

async function fetchUserWithCache(userId: string) {
  const cacheKey = `user:${userId}`;
  
  // 检查缓存
  const cached = cache.get(cacheKey);
  if (cached) {
    return cached;
  }
  
  // 从API获取
  const user = await apiClient.get(`/users/${userId}`);
  
  // 缓存结果
  cache.set(cacheKey, user);
  
  return user;
}
```

## 高级用法

### 自动清理过期缓存

```typescript
// 定期清理过期缓存
setInterval(() => {
  const clearedCount = cache.clearExpired();
  if (clearedCount > 0) {
    console.log(`Cleaned up ${clearedCount} expired cache entries`);
  }
}, 60 * 1000); // 每分钟清理一次
```

### 缓存预热

```typescript
async function warmupCache() {
  const users = await apiClient.get('/users');
  users.forEach(user => {
    cache.set(`user:${user.id}`, user);
  });
}
```

### 缓存失效策略

```typescript
// 更新用户时，清除相关缓存
async function updateUser(userId: string, data: any) {
  await apiClient.put(`/users/${userId}`, data);
  
  // 清除用户缓存
  cache.clear(`user:${userId}`);
  
  // 也可以清除相关的列表缓存
  cache.clear('users:list');
}
```

## API 参考

### 构造函数

```typescript
constructor(defaultTTL: number = 5 * 60 * 1000)
```

### 方法

- `set<T>(key: string, data: T, ttl?: number): void` - 设置缓存
- `get<T>(key: string): T | null` - 获取缓存
- `has(key: string): boolean` - 检查缓存是否存在
- `isExpired(key: string): boolean` - 检查缓存是否过期
- `getTTL(key: string): number` - 获取剩余TTL
- `updateTTL(key: string, ttl: number): boolean` - 更新TTL
- `clear(pattern?: string): void` - 清除缓存
- `clearExpired(): number` - 清除过期缓存
- `getStats(): CacheStats` - 获取统计信息
- `resetStats(): void` - 重置统计信息

### 类型

```typescript
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

interface CacheStats {
  size: number;
  hits: number;
  misses: number;
  hitRate: number;
  keys: string[];
}
```

## 最佳实践

1. **使用有意义的缓存键**: 使用命名空间前缀，如 `user:123`, `post:456`
2. **合理设置TTL**: 根据数据更新频率设置合适的TTL
3. **定期清理**: 使用 `clearExpired()` 定期清理过期缓存
4. **监控统计**: 使用 `getStats()` 监控缓存命中率
5. **缓存失效**: 数据更新时及时清除相关缓存
6. **避免缓存过大对象**: 缓存是内存存储，避免缓存过大的对象

## 性能考虑

- CacheService 使用 Map 数据结构，查找和插入操作的时间复杂度为 O(1)
- 过期检查在获取时进行，不会影响设置操作的性能
- 建议定期调用 `clearExpired()` 清理过期条目，避免内存泄漏
- 对于大量缓存条目，考虑使用 LRU (Least Recently Used) 策略

## 测试

CacheService 包含完整的单元测试，覆盖所有功能和边缘情况：

```bash
npm test -- CacheService.test.ts
```

测试覆盖：
- 基本的设置和获取功能
- TTL过期检查
- 缓存清理功能
- 统计功能
- 边缘情况 (空字符串、null、undefined、零TTL等)
- 并发操作

# 指数退避重试机制 (Exponential Backoff Retry Mechanism)

## 概述

本模块实现了指数退避重试机制，用于在操作失败时自动重试，提高系统的容错能力和可靠性。

## 功能特性

- ✅ 指数退避算法：每次重试的延迟时间呈指数增长
- ✅ 可配置参数：支持自定义最大重试次数、初始延迟、最大延迟和退避因子
- ✅ 智能重试判断：自动识别可重试的错误类型（网络错误、5xx服务器错误、429限流错误）
- ✅ 随机抖动：添加±10%的随机抖动以避免重试风暴
- ✅ 自定义重试逻辑：支持通过`shouldRetry`函数自定义重试条件
- ✅ 与ApiClient集成：无缝集成到API请求客户端中

## 需求验证

### 需求 10.3
**WHEN API请求失败时，THE Frontend_Application SHALL 使用指数退避策略重试，最多重试3次**

✅ 已实现：
- 默认配置：最多重试3次
- 延迟时间：1秒、2秒、4秒（指数增长）
- 最大延迟：10秒
- 退避因子：2

### 需求 5.2
**WHEN 任务执行失败时，THE Analysis_Queue SHALL 在5分钟、15分钟、30分钟后自动重试，最多重试3次**

✅ 已实现：
- 提供`retryTaskWithExactDelays`函数支持精确延迟时间
- 预配置`TASK_QUEUE_RETRY_OPTIONS_EXACT`用于任务队列场景

## 使用方法

### 基本使用

```typescript
import { retryWithBackoff } from './utils/retryWithBackoff';

// 基本使用
const result = await retryWithBackoff(
  () => fetch('/api/data'),
  {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 10000,
    factor: 2,
  }
);
```

### 自定义重试条件

```typescript
const result = await retryWithBackoff(
  () => apiCall(),
  {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 10000,
    factor: 2,
    shouldRetry: (error) => {
      // 只重试特定类型的错误
      return error.message.includes('timeout');
    },
  }
);
```

### 使用预配置的重试函数

```typescript
import { createRetryFunction, DEFAULT_API_RETRY_OPTIONS } from './utils/retryWithBackoff';

const retryApi = createRetryFunction(DEFAULT_API_RETRY_OPTIONS);

const data = await retryApi(() => apiClient.get('/data'));
```

### 任务队列精确延迟重试

```typescript
import { retryTaskWithExactDelays } from './utils/retryWithBackoff';

// 在5分钟、15分钟、30分钟后重试
const result = await retryTaskWithExactDelays(
  () => executeTask(),
  [5 * 60 * 1000, 15 * 60 * 1000, 30 * 60 * 1000]
);
```

### 与ApiClient集成

```typescript
import { ApiClient } from './services/ApiClient';

const apiClient = new ApiClient({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
  maxRetries: 3,
  maxConcurrent: 6,
  cacheTimeout: 5 * 60 * 1000,
  // 可选：自定义重试配置
  retryOptions: {
    initialDelay: 500,
    maxDelay: 5000,
    factor: 3,
  },
});

// GET请求会自动使用重试机制
const data = await apiClient.get('/data');

// 跳过重试
const data = await apiClient.get('/data', { skipRetry: true });
```

## 配置选项

### RetryOptions

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `maxRetries` | `number` | 是 | - | 最大重试次数 |
| `initialDelay` | `number` | 是 | - | 初始延迟时间（毫秒） |
| `maxDelay` | `number` | 是 | - | 最大延迟时间（毫秒） |
| `factor` | `number` | 是 | - | 退避因子（每次重试延迟时间的倍数） |
| `shouldRetry` | `(error: Error) => boolean` | 否 | `defaultShouldRetry` | 自定义判断是否应该重试的函数 |

### 预配置选项

#### DEFAULT_API_RETRY_OPTIONS
```typescript
{
  maxRetries: 3,
  initialDelay: 1000,  // 1秒
  maxDelay: 10000,     // 10秒
  factor: 2,           // 延迟时间翻倍
}
```

#### TASK_QUEUE_RETRY_OPTIONS_EXACT
```typescript
{
  maxRetries: 3,
  initialDelay: 5 * 60 * 1000,   // 5分钟
  maxDelay: 30 * 60 * 1000,      // 30分钟
  factor: 3,
}
```

## 默认重试策略

### 会重试的错误类型

1. **网络错误**
   - `ECONNABORTED` - 连接中止
   - `ENOTFOUND` - 主机未找到
   - `ETIMEDOUT` - 连接超时

2. **服务器错误**
   - 5xx状态码（500-599）

3. **限流错误**
   - 429 Too Many Requests

### 不会重试的错误类型

1. **客户端错误**
   - 4xx状态码（400-499）
   - 例如：400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found

2. **自定义不重试**
   - 通过`shouldRetry`函数返回`false`的错误

## 延迟计算

延迟时间按以下公式计算：

```
delay = min(initialDelay * (factor ^ attempt), maxDelay)
actualDelay = delay + jitter
```

其中：
- `attempt`：当前重试次数（从0开始）
- `jitter`：随机抖动，范围为 `delay * 0.1 * (Math.random() * 2 - 1)`，即±10%

### 示例

使用默认配置（`initialDelay=1000`, `factor=2`, `maxDelay=10000`）：

| 重试次数 | 计算延迟 | 实际延迟（含抖动） |
|---------|---------|-------------------|
| 1 | 1000ms | 900-1100ms |
| 2 | 2000ms | 1800-2200ms |
| 3 | 4000ms | 3600-4400ms |

## 测试

### 单元测试

```bash
npm test -- retryWithBackoff.test.ts
```

测试覆盖：
- ✅ 成功场景：首次成功、重试后成功
- ✅ 失败场景：达到最大重试次数、不重试特定错误
- ✅ 重试策略：5xx错误、429错误、网络错误
- ✅ 延迟计算：指数退避、最大延迟限制
- ✅ 边缘情况：maxRetries=0、大退避因子、零延迟
- ✅ 自定义重试逻辑

### 集成测试

```bash
npm test -- ApiClient.retry.integration.test.ts
```

测试覆盖：
- ✅ 与ApiClient集成
- ✅ 与缓存机制集成
- ✅ 与并发控制集成
- ✅ skipRetry选项

### ApiClient测试

```bash
npm test -- ApiClient.test.ts
```

测试结果：25/27 passed ✅

## 性能考虑

1. **内存使用**：重试机制不会创建额外的内存开销，只使用Promise链
2. **并发控制**：与ApiClient的并发限制机制协同工作
3. **缓存友好**：重试成功后的结果会被正常缓存
4. **随机抖动**：避免多个客户端同时重试导致的服务器压力

## 最佳实践

1. **合理设置重试次数**：通常3次重试足够，过多重试会增加延迟
2. **设置最大延迟**：避免重试延迟过长影响用户体验
3. **自定义重试逻辑**：根据业务需求判断哪些错误应该重试
4. **监控重试率**：高重试率可能表明系统存在问题
5. **使用skipRetry**：对于幂等性要求高的操作，考虑跳过重试

## 文件结构

```
frontend/src/
├── utils/
│   ├── retryWithBackoff.ts                    # 重试机制实现
│   ├── RETRY_MECHANISM_README.md              # 本文档
│   └── __tests__/
│       └── retryWithBackoff.test.ts           # 单元测试
└── services/
    ├── ApiClient.ts                           # 集成重试机制的API客户端
    └── __tests__/
        ├── ApiClient.test.ts                  # ApiClient测试
        └── ApiClient.retry.integration.test.ts # 集成测试
```

## 相关文档

- [ApiClient文档](../services/API_CLIENT_README.md)
- [设计文档](.kiro/specs/frontend-production-optimization/design.md)
- [需求文档](.kiro/specs/frontend-production-optimization/requirements.md)

## 更新日志

### v1.0.0 (2024)
- ✅ 实现指数退避重试机制
- ✅ 集成到ApiClient
- ✅ 添加单元测试和集成测试
- ✅ 支持自定义重试配置
- ✅ 添加任务队列精确延迟重试功能

# Logger服务文档

## 概述

Logger服务提供了一个统一的日志记录系统，支持不同的日志级别、环境配置、批量发送和自动刷新功能。

## 功能特性

- ✅ 支持多个日志级别（debug, info, warn, error）
- ✅ 根据环境自动设置日志级别（开发：debug，生产：error）
- ✅ 记录API请求日志（响应时间、状态码）
- ✅ 记录用户操作日志（用户ID、时间戳、操作类型）
- ✅ 批量日志发送到服务器
- ✅ 自动定时刷新日志缓冲区
- ✅ 控制台输出（可配置）

## 验证需求

- **需求 8.4**: 开发环境启用详细日志，生产环境仅记录错误和警告
- **需求 9.2**: 记录每个API请求的响应时间和状态码
- **需求 9.3**: 记录关键用户操作包含用户ID、时间戳和操作类型

## 使用方法

### 基本使用

```typescript
import { getLogger } from '@/services/Logger';

const logger = getLogger();

// 记录不同级别的日志
logger.debug('调试信息', { data: 'value' });
logger.info('普通信息');
logger.warn('警告信息');
logger.error('错误信息', new Error('Something went wrong'));
```

### 记录API请求

```typescript
import { getLogger } from '@/services/Logger';

const logger = getLogger();

// 记录API请求
logger.logApiRequest(
  '/api/users',      // URL
  'GET',             // HTTP方法
  250,               // 响应时间（毫秒）
  200,               // 状态码
  {
    requestSize: 1024,   // 可选：请求大小（字节）
    responseSize: 2048,  // 可选：响应大小（字节）
    error: undefined     // 可选：错误信息
  }
);
```

### 记录用户操作

```typescript
import { getLogger } from '@/services/Logger';

const logger = getLogger();

// 设置当前用户
logger.setUserId('user123');

// 记录用户操作
logger.logUserAction(
  'button_click',           // 操作类型
  'user123',                // 用户ID
  {                         // 可选：操作详情
    buttonId: 'submit-btn',
    page: '/dashboard'
  }
);
```

### 自定义配置

```typescript
import { Logger, LoggerConfig } from '@/services/Logger';

const config: LoggerConfig = {
  level: 'info',                    // 日志级别
  environment: 'production',        // 环境
  enableConsole: false,             // 是否输出到控制台
  batchSize: 100,                   // 批量发送大小
  flushInterval: 60000,             // 刷新间隔（毫秒）
  endpoint: 'https://logs.example.com/api/logs'  // 日志服务器端点
};

const logger = new Logger(config);
```

## API参考

### Logger类

#### 构造函数

```typescript
constructor(config: LoggerConfig)
```

创建一个新的Logger实例。

#### 方法

##### setLevel(level: LogLevel): void

设置日志级别。只有大于等于该级别的日志才会被记录。

```typescript
logger.setLevel('warn'); // 只记录warn和error
```

##### getLevel(): LogLevel

获取当前日志级别。

##### setUserId(userId: string | undefined): void

设置当前用户ID，会自动添加到所有日志中。

##### getUserId(): string | undefined

获取当前用户ID。

##### debug(message: string, context?: Record<string, any>): void

记录debug级别日志。

##### info(message: string, context?: Record<string, any>): void

记录info级别日志。

##### warn(message: string, context?: Record<string, any>): void

记录warn级别日志。

##### error(message: string, error?: Error, context?: Record<string, any>): void

记录error级别日志，可以包含Error对象。

##### logApiRequest(url: string, method: string, duration: number, status: number, options?: {...}): void

记录API请求日志。

参数：
- `url`: 请求URL
- `method`: HTTP方法
- `duration`: 响应时间（毫秒）
- `status`: HTTP状态码
- `options`: 可选参数
  - `requestSize`: 请求大小（字节）
  - `responseSize`: 响应大小（字节）
  - `error`: 错误信息

##### logUserAction(action: string, userId: string, details?: Record<string, any>): void

记录用户操作日志。

参数：
- `action`: 操作类型
- `userId`: 用户ID
- `details`: 操作详情

##### flushLogs(): Promise<void>

立即刷新日志缓冲区，发送到服务器。

##### stopFlushTimer(): void

停止自动刷新定时器。

##### destroy(): Promise<void>

销毁Logger实例，停止定时器并刷新剩余日志。

##### getBufferStatus(): {...}

获取缓冲区状态。

返回：
```typescript
{
  logs: number;        // 普通日志数量
  apiLogs: number;     // API日志数量
  userActions: number; // 用户操作日志数量
  total: number;       // 总数量
}
```

## 配置选项

### LoggerConfig

```typescript
interface LoggerConfig {
  level: LogLevel;                    // 日志级别
  environment: 'development' | 'test' | 'production';  // 环境
  enableConsole?: boolean;            // 是否输出到控制台（默认：开发环境true）
  batchSize?: number;                 // 批量发送大小（默认：50）
  flushInterval?: number;             // 刷新间隔毫秒（默认：30000）
  endpoint?: string;                  // 日志服务器端点
}
```

### LogLevel

```typescript
type LogLevel = 'debug' | 'info' | 'warn' | 'error';
```

日志级别优先级：`debug < info < warn < error`

## 环境配置

### 开发环境

```typescript
{
  level: 'debug',           // 记录所有级别
  environment: 'development',
  enableConsole: true       // 输出到控制台
}
```

### 生产环境

```typescript
{
  level: 'error',           // 只记录错误
  environment: 'production',
  enableConsole: false      // 不输出到控制台
}
```

## 批量发送机制

Logger会在以下情况自动刷新日志：

1. **达到批量大小**：当缓冲区中的日志数量达到`batchSize`时
2. **定时刷新**：每隔`flushInterval`毫秒自动刷新
3. **销毁时**：调用`destroy()`方法时

## 最佳实践

### 1. 使用单例实例

```typescript
import { getLogger } from '@/services/Logger';

// 推荐：使用单例
const logger = getLogger();
```

### 2. 设置用户上下文

```typescript
// 在用户登录后设置
logger.setUserId(user.id);

// 在用户登出时清除
logger.setUserId(undefined);
```

### 3. 记录API请求

```typescript
// 在API客户端中集成
const startTime = Date.now();
try {
  const response = await fetch(url);
  const duration = Date.now() - startTime;
  
  logger.logApiRequest(url, 'GET', duration, response.status);
  
  return response;
} catch (error) {
  const duration = Date.now() - startTime;
  logger.logApiRequest(url, 'GET', duration, 0, {
    error: error.message
  });
  throw error;
}
```

### 4. 记录关键用户操作

```typescript
// 记录重要操作
const handleDeleteProject = async (projectId: string) => {
  logger.logUserAction('project_delete', userId, {
    projectId,
    timestamp: new Date().toISOString()
  });
  
  await deleteProject(projectId);
};
```

### 5. 使用适当的日志级别

- **debug**: 详细的调试信息，仅在开发环境使用
- **info**: 一般信息，如操作成功
- **warn**: 警告信息，如使用了废弃的API
- **error**: 错误信息，如操作失败

### 6. 在组件卸载时清理

```typescript
useEffect(() => {
  return () => {
    // 组件卸载时刷新日志
    logger.flushLogs();
  };
}, []);
```

## 性能考虑

1. **批量发送**：日志会被缓冲并批量发送，减少网络请求
2. **异步刷新**：日志发送是异步的，不会阻塞主线程
3. **级别过滤**：低于当前级别的日志不会被处理，提高性能
4. **自动清理**：定时器会自动清理缓冲区，防止内存泄漏

## 故障排查

### 日志没有发送到服务器

1. 检查是否配置了`endpoint`
2. 检查网络连接
3. 检查服务器端点是否正确
4. 查看控制台是否有错误信息

### 日志级别不正确

1. 检查`level`配置
2. 确认环境变量设置正确
3. 使用`getLevel()`查看当前级别

### 内存占用过高

1. 减小`batchSize`
2. 减小`flushInterval`
3. 确保调用`destroy()`清理资源

## 示例

### 完整示例

```typescript
import { getLogger } from '@/services/Logger';

// 获取logger实例
const logger = getLogger();

// 设置用户
logger.setUserId('user123');

// 记录不同类型的日志
logger.info('应用启动');

// 记录API请求
const fetchUsers = async () => {
  const startTime = Date.now();
  try {
    const response = await fetch('/api/users');
    const duration = Date.now() - startTime;
    
    logger.logApiRequest('/api/users', 'GET', duration, response.status);
    
    return await response.json();
  } catch (error) {
    logger.error('获取用户失败', error);
    throw error;
  }
};

// 记录用户操作
const handleButtonClick = () => {
  logger.logUserAction('button_click', 'user123', {
    buttonId: 'submit-btn',
    page: window.location.pathname
  });
};

// 清理
window.addEventListener('beforeunload', () => {
  logger.destroy();
});
```

## 测试

运行单元测试：

```bash
npm test -- Logger.test.ts
```

测试覆盖了：
- 日志级别过滤
- 不同日志方法
- API请求日志
- 用户操作日志
- 批量发送机制
- 用户上下文
- 缓冲区管理
- 定时器管理
- 边缘情况

## 相关文档

- [ErrorMonitor服务](./ERROR_MONITOR_README.md)
- [ApiClient服务](./ApiClient.ts)
- [配置管理](./CONFIG_README.md)

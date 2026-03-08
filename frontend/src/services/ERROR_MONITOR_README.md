# ErrorMonitor Service

## 概述

ErrorMonitor服务提供了完整的错误监控、上报和告警功能，用于生产环境的错误追踪和质量监控。

## 功能特性

- ✅ 错误捕获和上报
- ✅ 错误分类（网络、验证、授权、服务器、客户端）
- ✅ 用户上下文跟踪
- ✅ 错误率监控（5分钟窗口）
- ✅ 自动告警触发（10%阈值）
- ✅ 全局错误处理
- ✅ Sentry集成支持
- ✅ 单例模式

## 验证需求

- **需求 9.1**: 将未捕获的错误发送到监控服务
- **需求 9.4**: 错误报告包含用户浏览器信息、页面URL和错误堆栈
- **需求 9.5**: 错误率在5分钟内超过10%时触发告警通知

## 使用方法

### 基本初始化

```typescript
import { getErrorMonitor } from '@/services';

// 初始化ErrorMonitor
const errorMonitor = getErrorMonitor({
  environment: 'production',
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  enableDebugMode: false,
  sampleRate: 1.0,
});

errorMonitor.initialize();
```

### 捕获错误

```typescript
try {
  // 可能抛出错误的代码
  await riskyOperation();
} catch (error) {
  errorMonitor.captureError(error as Error, {
    userId: currentUser.id,
    url: window.location.href,
    additionalData: {
      operation: 'riskyOperation',
      params: { /* ... */ },
    },
  });
}
```

### 设置用户上下文

```typescript
// 用户登录后
errorMonitor.setUser({
  id: user.id,
  email: user.email,
  username: user.username,
});

// 用户登出后
errorMonitor.setUser(null);
```

### 记录API请求（用于错误率监控）

```typescript
try {
  const response = await apiClient.get('/api/data');
  errorMonitor.recordRequest(true); // 成功
  return response;
} catch (error) {
  errorMonitor.recordRequest(false); // 失败
  throw error;
}
```

### 注册告警回调

```typescript
errorMonitor.onAlert((message) => {
  // 发送告警通知（邮件、Slack等）
  console.error('ALERT:', message);
  
  // 可以集成其他告警服务
  sendSlackNotification(message);
  sendEmailAlert(message);
});
```

### 捕获消息

```typescript
// 记录信息
errorMonitor.captureMessage('User completed checkout', 'info');

// 记录警告
errorMonitor.captureMessage('API response time exceeded 3s', 'warning');

// 记录错误
errorMonitor.captureMessage('Critical system error', 'error');
```

## 配置选项

```typescript
interface MonitorConfig {
  // Sentry DSN（可选）
  dsn?: string;
  
  // 环境：development, test, production
  environment: 'development' | 'test' | 'production';
  
  // 是否启用调试模式（输出到控制台）
  enableDebugMode?: boolean;
  
  // 采样率（0.0 - 1.0）
  sampleRate?: number;
  
  // 错误上报前的钩子函数
  beforeSend?: (error: ErrorReport) => ErrorReport | null;
}
```

## 错误分类

ErrorMonitor会自动将错误分类为以下类型：

- **network**: 网络错误、超时、fetch失败
- **validation**: 验证错误、无效输入
- **authorization**: 授权错误（401、403）
- **server**: 服务器错误（5xx）
- **client**: 客户端错误（TypeError、ReferenceError）
- **unknown**: 未知错误类型

## 错误率监控

ErrorMonitor会在5分钟的滑动窗口内监控错误率：

- 窗口大小：5分钟
- 告警阈值：10%
- 最小样本数：10个请求

当错误率超过阈值时，会触发告警并调用所有注册的告警回调。

### 获取错误统计

```typescript
// 获取当前错误率
const errorRate = errorMonitor.getErrorRate();
console.log(`Current error rate: ${(errorRate * 100).toFixed(2)}%`);

// 获取详细统计
const stats = errorMonitor.getErrorStats();
console.log(`Errors: ${stats.errorCount}/${stats.totalRequests}`);
console.log(`Alert triggered: ${stats.alertTriggered}`);
```

## 全局错误处理

ErrorMonitor会自动捕获以下全局错误：

- `window.onerror` - JavaScript运行时错误
- `window.onunhandledrejection` - 未处理的Promise拒绝

这些错误会自动上报到监控服务。

## 与Sentry集成

在生产环境中，ErrorMonitor可以与Sentry集成：

```typescript
// 1. 安装Sentry SDK
// npm install @sentry/nextjs

// 2. 配置ErrorMonitor
const errorMonitor = getErrorMonitor({
  environment: 'production',
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  sampleRate: 1.0,
  beforeSend: (error) => {
    // 过滤敏感信息
    if (error.context.additionalData?.password) {
      delete error.context.additionalData.password;
    }
    return error;
  },
});

// 3. 在ErrorMonitor.ts中取消注释Sentry相关代码
```

## 最佳实践

### 1. 在应用启动时初始化

```typescript
// app/layout.tsx 或 _app.tsx
import { getErrorMonitor } from '@/services';

const errorMonitor = getErrorMonitor({
  environment: process.env.NODE_ENV as any,
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  enableDebugMode: process.env.NODE_ENV === 'development',
});

errorMonitor.initialize();
```

### 2. 在API客户端中集成

```typescript
class ApiClient {
  async request(config: RequestConfig) {
    try {
      const response = await axios(config);
      errorMonitor.recordRequest(true);
      return response;
    } catch (error) {
      errorMonitor.recordRequest(false);
      errorMonitor.captureError(error as Error, {
        additionalData: {
          url: config.url,
          method: config.method,
        },
      });
      throw error;
    }
  }
}
```

### 3. 在React组件中使用

```typescript
// 使用ErrorBoundary包裹组件
import { ErrorBoundary } from '@/components/ErrorBoundary';

function MyComponent() {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        errorMonitor.captureError(error, {
          additionalData: {
            componentStack: errorInfo.componentStack,
          },
        });
      }}
    >
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### 4. 过滤敏感信息

```typescript
const errorMonitor = getErrorMonitor({
  environment: 'production',
  beforeSend: (error) => {
    // 移除敏感字段
    const sensitiveFields = ['password', 'token', 'apiKey', 'secret'];
    
    if (error.context.additionalData) {
      sensitiveFields.forEach(field => {
        delete error.context.additionalData?.[field];
      });
    }
    
    return error;
  },
});
```

### 5. 设置告警通知

```typescript
// 集成Slack通知
errorMonitor.onAlert(async (message) => {
  await fetch(process.env.SLACK_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: `🚨 Error Alert: ${message}`,
      channel: '#alerts',
    }),
  });
});

// 集成邮件通知
errorMonitor.onAlert(async (message) => {
  await sendEmail({
    to: 'ops@example.com',
    subject: 'Error Rate Alert',
    body: message,
  });
});
```

## 测试

ErrorMonitor包含完整的单元测试覆盖：

```bash
# 运行测试
npm test -- ErrorMonitor.test.ts

# 运行测试并查看覆盖率
npm test -- ErrorMonitor.test.ts --coverage
```

## 性能考虑

- 错误上报是异步的，不会阻塞主线程
- 使用滑动窗口算法，内存占用恒定
- 告警触发后设置标志位，避免重复告警
- 支持采样率配置，减少生产环境负载

## 故障排查

### 错误没有被上报

1. 检查ErrorMonitor是否已初始化
2. 检查`enableDebugMode`是否为true（开发环境）
3. 检查`beforeSend`钩子是否返回null
4. 检查Sentry DSN是否正确配置

### 告警没有触发

1. 检查错误率是否真的超过10%
2. 检查请求数是否达到最小样本数（10个）
3. 检查是否已注册告警回调
4. 检查告警是否已经触发过（每个窗口只触发一次）

### 内存泄漏

1. 确保在组件卸载时清理告警回调
2. 使用`clearAlertCallbacks()`清理不需要的回调

## 相关文档

- [需求文档](../../../.kiro/specs/frontend-production-optimization/requirements.md)
- [设计文档](../../../.kiro/specs/frontend-production-optimization/design.md)
- [Sentry文档](https://docs.sentry.io/)

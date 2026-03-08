# ErrorBoundary Component

## 概述

ErrorBoundary是一个React类组件，用于捕获子组件树中的JavaScript错误，防止整个应用崩溃。它提供了友好的降级UI，并将错误上报到监控服务。

## 功能特性

- ✅ 捕获React组件树中的错误
- ✅ 显示友好的降级UI
- ✅ 集成ErrorMonitor自动上报错误
- ✅ 提供"重新加载"功能
- ✅ 提供"报告问题"功能
- ✅ 支持自定义降级UI
- ✅ 开发环境显示详细错误信息
- ✅ 支持错误和重置回调

## 验证需求

- **需求 1.3**: WHEN Dashboard组件发生错误时，THE Error_Boundary SHALL 捕获错误并显示友好的错误提示

## 使用方法

### 基础用法

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### 包裹页面组件

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  );
}
```

### 自定义降级UI

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary
      fallback={(error, errorInfo, reset) => (
        <div>
          <h1>Oops! Something went wrong</h1>
          <p>{error.message}</p>
          <button onClick={reset}>Try Again</button>
        </div>
      )}
    >
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### 使用错误回调

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  const handleError = (error: Error, errorInfo: ErrorInfo) => {
    // 自定义错误处理逻辑
    console.log('Error caught:', error);
    // 可以发送到自定义分析服务
  };

  const handleReset = () => {
    // 重置应用状态
    console.log('Error boundary reset');
  };

  return (
    <ErrorBoundary onError={handleError} onReset={handleReset}>
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### 嵌套ErrorBoundary

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Header />
      <ErrorBoundary>
        <MainContent />
      </ErrorBoundary>
      <ErrorBoundary>
        <Sidebar />
      </ErrorBoundary>
      <Footer />
    </ErrorBoundary>
  );
}
```

## API

### Props

| Prop | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `children` | `ReactNode` | ✅ | - | 要保护的子组件 |
| `fallback` | `(error: Error, errorInfo: ErrorInfo, reset: () => void) => ReactNode` | ❌ | 默认UI | 自定义降级UI渲染函数 |
| `onError` | `(error: Error, errorInfo: ErrorInfo) => void` | ❌ | - | 错误发生时的回调函数 |
| `onReset` | `() => void` | ❌ | - | 重置错误状态时的回调函数 |

### 默认降级UI功能

默认降级UI提供以下功能：

1. **Try Again**: 重置错误状态，尝试重新渲染子组件
2. **Reload Page**: 重新加载整个页面
3. **Report Issue**: 打开邮件客户端，预填充错误报告信息

### 开发模式特性

在开发环境（`NODE_ENV === 'development'`）下，降级UI会显示：

- 错误消息
- 完整的错误堆栈
- React组件堆栈

这些信息在生产环境中会被隐藏，以保护应用内部实现细节。

## 错误上报

ErrorBoundary自动将捕获的错误上报到ErrorMonitor服务，包含以下信息：

- 错误消息和堆栈
- 当前页面URL
- 用户代理信息
- React组件堆栈
- 时间戳

确保在使用ErrorBoundary之前初始化ErrorMonitor：

```tsx
import { getErrorMonitor } from './services/ErrorMonitor';

const monitor = getErrorMonitor({
  environment: 'production',
  dsn: 'your-sentry-dsn',
});
monitor.initialize();
```

## 最佳实践

### 1. 在应用顶层使用

```tsx
// App.tsx
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes />
      </Router>
    </ErrorBoundary>
  );
}
```

### 2. 为关键功能区域使用独立边界

```tsx
function Dashboard() {
  return (
    <div>
      <ErrorBoundary>
        <CriticalWidget />
      </ErrorBoundary>
      <ErrorBoundary>
        <AnotherWidget />
      </ErrorBoundary>
    </div>
  );
}
```

### 3. 提供有意义的降级UI

```tsx
<ErrorBoundary
  fallback={(error, errorInfo, reset) => (
    <div className="error-container">
      <h2>Unable to load dashboard</h2>
      <p>Please try refreshing the page or contact support if the problem persists.</p>
      <button onClick={reset}>Retry</button>
    </div>
  )}
>
  <Dashboard />
</ErrorBoundary>
```

### 4. 结合路由使用

```tsx
import { useNavigate } from 'react-router-dom';

function AppWithErrorBoundary() {
  const navigate = useNavigate();

  return (
    <ErrorBoundary
      onReset={() => {
        // 重置时导航到首页
        navigate('/');
      }}
    >
      <App />
    </ErrorBoundary>
  );
}
```

## 注意事项

### ErrorBoundary无法捕获的错误

ErrorBoundary **不能**捕获以下类型的错误：

1. **事件处理器中的错误**
   ```tsx
   // ❌ ErrorBoundary无法捕获
   <button onClick={() => { throw new Error('Error in handler'); }}>
     Click me
   </button>
   
   // ✅ 需要手动try-catch
   <button onClick={() => {
     try {
       riskyOperation();
     } catch (error) {
       errorMonitor.captureError(error);
     }
   }}>
     Click me
   </button>
   ```

2. **异步代码中的错误**
   ```tsx
   // ❌ ErrorBoundary无法捕获
   useEffect(() => {
     setTimeout(() => {
       throw new Error('Async error');
     }, 1000);
   }, []);
   
   // ✅ 需要手动捕获
   useEffect(() => {
     setTimeout(() => {
       try {
         riskyOperation();
       } catch (error) {
         errorMonitor.captureError(error);
       }
     }, 1000);
   }, []);
   ```

3. **服务端渲染（SSR）中的错误**

4. **ErrorBoundary自身的错误**

### 性能考虑

- ErrorBoundary是轻量级的，对性能影响极小
- 只在错误发生时才会重新渲染
- 建议在应用的关键边界使用，而不是包裹每个小组件

## 测试

### 单元测试示例

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary } from './ErrorBoundary';

const ThrowError = () => {
  throw new Error('Test error');
};

test('should catch and display error', () => {
  render(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  );

  expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
});

test('should reset error state', () => {
  const { rerender } = render(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  );

  fireEvent.click(screen.getByText(/try again/i));

  rerender(
    <ErrorBoundary>
      <div>Normal content</div>
    </ErrorBoundary>
  );

  expect(screen.getByText('Normal content')).toBeInTheDocument();
});
```

## 相关文档

- [ErrorMonitor服务文档](../services/ERROR_MONITOR_README.md)
- [React Error Boundaries官方文档](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)

## 实现细节

### 错误捕获流程

1. 子组件抛出错误
2. `getDerivedStateFromError` 更新状态为错误状态
3. `componentDidCatch` 被调用：
   - 上报错误到ErrorMonitor
   - 调用`onError`回调（如果提供）
4. 渲染降级UI

### 重置流程

1. 用户点击"Try Again"按钮
2. `handleReset` 被调用：
   - 重置状态为无错误状态
   - 调用`onReset`回调（如果提供）
3. 重新渲染子组件

## 版本历史

- **v1.0.0** (2024-01): 初始实现
  - 基础错误捕获功能
  - 默认降级UI
  - ErrorMonitor集成
  - 重新加载和报告问题功能

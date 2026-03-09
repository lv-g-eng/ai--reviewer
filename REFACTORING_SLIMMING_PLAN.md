# 代码瘦身计划书

**Code Refactoring & Slimming Plan**

**制定日期**: 2026-03-09  
**制定者**: 资深重构专家  
**项目**: AI Code Review Platform

---

## 📋 执行摘要

本计划书旨在通过系统性的重构，消除项目中的冗余代码、重复逻辑和未使用的依赖，在不改变系统外部行为的前提下，提升代码质量和可维护性。

### 预期成果

| 指标             | 当前状态 | 目标状态 | 改进幅度 |
| ---------------- | -------- | -------- | -------- |
| 重复代码行数     | ~2,280行 | <500行   | 78% ↓    |
| 死代码文件       | 22个     | 0个      | 100% ↓   |
| 未使用依赖       | 4个      | 0个      | 100% ↓   |
| 平均文件复杂度   | 高       | 中       | 40% ↓    |
| 代码可维护性指数 | 65       | 85       | 31% ↑    |

---

## 🔍 Step 1: 冗余普查结果

### 1.1 重复代码模式 (Top 10)

#### 🔴 高优先级 (P0)

**模式 #1: API错误处理 + Toast通知**

- **类型**: 错误处理
- **影响范围**: 10+ 文件，15+ 处重复
- **重复代码行数**: ~150行
- **文件示例**:
  - `frontend/src/app/login/page.tsx:50-65`
  - `frontend/src/app/register/page.tsx:89-107`
  - `frontend/src/app/profile/page.tsx:108-123`
- **相似度**: 95%
- **重构方案**: 创建 `useApiCall` hook 统一处理异步调用和错误提示

---

**模式 #2: Loading状态管理 + 异步操作**

- **类型**: 状态管理
- **影响范围**: 15+ 文件，20+ 处重复
- **重复代码行数**: ~200行
- **文件示例**:
  - `frontend/src/contexts/AuthContext.tsx:186-189`
  - `frontend/src/pages/Metrics.tsx:295-308`
  - `frontend/src/pages/AnalysisQueue.tsx:150-192`
- **相似度**: 90%
- **重构方案**: 创建 `useAsyncAction` hook 封装异步操作状态管理

---

**模式 #3: 数据库操作模式**

- **类型**: 数据库操作
- **影响范围**: 8+ 文件
- **重复代码行数**: ~200行
- **文件示例**:
  - `backend/app/auth/services/rbac_service.py:161-197`
  - `backend/app/auth/services/rbac_service.py:216-245`
  - `backend/app/auth/services/auth_service.py:327-344`
- **相似度**: 95%
- **重构方案**: 提取 `BaseRepository` 类，统一 CRUD 操作和事务管理

---

**模式 #4: CRUD + 审计日志模式**

- **类型**: 服务层逻辑
- **影响范围**: 10+ endpoint
- **重复代码行数**: ~400行
- **文件示例**:
  - `backend/app/api/v1/endpoints/rbac_users.py:169-185`
  - `backend/app/api/v1/endpoints/rbac_projects.py:340-372`
- **相似度**: 85%
- **重构方案**: 创建 `GenericCRUDEndpoint` 基类或装饰器

---

#### 🟡 中优先级 (P1)

**模式 #5: Console日志记录**

- **类型**: 调试/错误处理
- **影响范围**: 20+ 文件，50+ 处重复
- **重复代码行数**: ~100行
- **重构方案**: 创建统一的 `Logger` 工具类

---

**模式 #6: GitHub API缓存模式**

- **类型**: 服务层逻辑
- **影响范围**: 6个方法
- **重复代码行数**: ~180行
- **文件示例**:
  - `backend/app/services/github_circuit_breaker.py:110-138`
  - `backend/app/services/github_circuit_breaker.py:140-174`
- **相似度**: 92%
- **重构方案**: 提取为 `with_circuit_breaker_and_cache` 装饰器

---

**模式 #7: 图形可视化状态管理**

- **类型**: 状态管理
- **影响范围**: 3个组件
- **重复代码行数**: ~120行
- **文件示例**:
  - `frontend/src/components/visualizations/DependencyGraphVisualization.tsx:197-204`
  - `frontend/src/components/visualizations/Neo4jGraphVisualization.tsx:146-169`
- **相似度**: 85%
- **重构方案**: 提取共享的 `useGraphState` hook

---

**模式 #8: 批量操作模式**

- **类型**: 组件逻辑
- **影响范围**: 1个文件，3个函数
- **重复代码行数**: ~150行
- **文件示例**:
  - `frontend/src/pages/Projects.tsx:381-527`
- **相似度**: 90%
- **重构方案**: 创建 `useBatchOperation` hook

---

**模式 #9: 异常处理模式**

- **类型**: 异常处理
- **影响范围**: 6+ 文件
- **重复代码行数**: ~150行
- **文件示例**:
  - `backend/app/auth/services/audit_service.py:71-96`
  - `backend/app/services/audit_service.py:43-89`
- **相似度**: 90%
- **重构方案**: 创建 `AuditLogger` 基类

---

**模式 #10: 响应模型构建**

- **类型**: 数据转换
- **影响范围**: 8+ endpoint
- **重复代码行数**: ~160行
- **文件示例**:
  - `backend/app/api/v1/endpoints/rbac_projects.py:251-263`
- **相似度**: 95%
- **重构方案**: 在 Model 中添加 `to_response()` 方法

---

### 1.2 死代码清单

#### 前端死代码 (13项)

| 类型       | 文件                                                 | 说明                        | 建议操作  |
| ---------- | ---------------------------------------------------- | --------------------------- | --------- |
| 未使用依赖 | `package.json`                                       | `react-to-image` 包从未使用 | 删除依赖  |
| 未使用组件 | `components/examples/VirtualListExample.tsx`         | 示例组件未被使用            | 删除文件  |
| 未使用组件 | `components/visualizations/lazy.ts`                  | lazy导出未使用              | 删除文件  |
| 未使用组件 | `components/optimized/MemoizedComponents.tsx`        | 记忆化组件未使用            | 删除导出  |
| 未使用组件 | `components/optimized/LazyLoadingComponents.tsx`     | 懒加载组件未使用            | 删除文件  |
| 未使用组件 | `components/admin/FeatureFlagsManager.tsx`           | Admin组件未使用             | 删除文件  |
| 未使用服务 | `lib/feature-flags.ts`                               | Feature Flags服务未使用     | 删除文件  |
| 未使用组件 | `components/visualizations/ArchitectureTimeline.tsx` | Timeline组件未使用          | 删除文件  |
| 未使用组件 | `pages/Projects.tsx`                                 | 旧版页面组件                | 删除文件  |
| 未使用组件 | `components/QueryClientWrapper.tsx`                  | QueryClient包装器未使用     | 删除文件  |
| 未使用组件 | `components/common/advanced-filter.tsx`              | 高级过滤组件未使用          | 删除文件  |
| 未使用组件 | `components/ProtectedRoute.tsx`                      | 路由保护组件未使用          | 删除文件  |
| 重复代码   | `lib/api-client-enhanced.ts`                         | API客户端重复实现           | 删除/合并 |

---

#### 后端死代码 (13项)

| 类型         | 文件                             | 说明                       | 建议操作   |
| ------------ | -------------------------------- | -------------------------- | ---------- |
| 未使用依赖   | `requirements.txt`               | `pytz` 未直接使用          | 删除依赖   |
| 未使用依赖   | `requirements.txt`               | `humanize` 未直接使用      | 删除依赖   |
| 未使用依赖   | `requirements.txt`               | `esprima` 仅作为备选       | 评估后决定 |
| 未使用Schema | `schemas/openapi_models.py`      | 响应模型未被使用           | 删除文件   |
| 未使用Schema | `schemas/validation.py`          | 验证模型未被使用           | 删除文件   |
| 未使用Schema | `schemas/response_models.py`     | 响应模型未被使用           | 删除文件   |
| 未使用Schema | `schemas/ai_pr_review_models.py` | AI审查模型未被使用         | 删除文件   |
| 未使用类     | `shared/exceptions.py`           | 10个异常类未使用           | 删除未用类 |
| 未使用类     | `schemas/architecture.py`        | 部分类未使用               | 删除未用类 |
| 未使用函数   | `schemas/architecture.py`        | 辅助方法未使用             | 删除方法   |
| 未使用文件   | `main_optimized.py`              | 优化版入口未使用           | 删除文件   |
| 未使用导入   | `database/optimizations.py`      | `asyncio` 未使用           | 删除导入   |
| 未使用变量   | `main.py`                        | `validation_result` 未使用 | 删除变量   |

---

### 1.3 冗余依赖分析

#### 前端依赖

| 依赖包           | 版本   | 使用情况                | 建议                      |
| ---------------- | ------ | ----------------------- | ------------------------- |
| `react-to-image` | ^0.1.0 | ❌ 未使用               | 删除                      |
| `axios-retry`    | ^4.5.0 | ⚠️ 仅在api-client中使用 | 评估是否可用原生fetch替代 |
| `@dnd-kit/*`     | ^6.3.1 | ⚠️ 仅在少数组件使用     | 保留，但考虑使用频率      |

#### 后端依赖

| 依赖包     | 版本   | 使用情况                    | 建议           |
| ---------- | ------ | --------------------------- | -------------- |
| `pytz`     | 2024.2 | ❌ 未直接使用（仅传递依赖） | 删除           |
| `humanize` | 4.15.0 | ❌ 未直接使用（仅传递依赖） | 删除           |
| `esprima`  | 4.0.1  | ⚠️ 仅作为备选解析器         | 评估后决定     |
| `passlib`  | 1.7.4  | ⚠️ 与bcrypt功能重叠         | 统一使用bcrypt |

---

## 📐 Step 2: 提取与抽象方案

### 2.1 通用工具函数/Hooks

#### 前端 Hooks

```typescript
// 1. useApiCall - 统一API调用和错误处理
export function useApiCall() {
  const { toast } = useToast();

  return async <T>(
    apiCall: () => Promise<T>,
    options?: {
      onSuccess?: (data: T) => void;
      successMessage?: string;
      errorMessage?: string;
    }
  ) => {
    /* 实现 */
  };
}

// 2. useAsyncAction - 异步操作状态管理
export function useAsyncAction<T>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (action: () => Promise<T>, onSuccess?: (data: T) => void) => {
    /* 实现 */
  }, []);

  return { loading, error, execute };
}

// 3. useGraphState - 图形可视化状态
export function useGraphState(initialFilters?: Partial<GraphFilters>) {
  const [state, setState] = useState<GraphState>({
    /* ... */
  });
  // 实现
  return { ...state, setSelectedNode, setSearchTerm /* ... */ };
}

// 4. useBatchOperation - 批量操作
export function useBatchOperation<T>(
  items: T[],
  setItems: React.Dispatch<React.SetStateAction<T[]>>,
  config: BatchOperationConfig<T>
) {
  /* 实现 */
}
```

#### 后端基类和装饰器

```python
# 1. BaseRepository - 数据库操作基类
class BaseRepository(Generic[ModelType, SchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    async def get(self, id: str) -> Optional[ModelType]: ...
    async def create(self, schema: SchemaType) -> ModelType: ...
    async def update(self, id: str, schema: SchemaType) -> ModelType: ...
    async def delete(self, id: str) -> bool: ...

# 2. with_audit_log - 审计日志装饰器
def with_audit_log(action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            # 记录审计日志
            return result
        return wrapper
    return decorator

# 3. with_circuit_breaker_and_cache - 熔断和缓存装饰器
def with_circuit_breaker_and_cache(
    cache_key_template: str,
    circuit_breaker: CircuitBreaker
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 检查缓存 -> 熔断器 -> 调用函数 -> 缓存结果
            pass
        return wrapper
    return decorator

# 4. Logger - 统一日志工具
class Logger:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def debug(self, message: str, data?: any): ...
    def error(self, message: str, error?: any): ...
    def warn(self, message: str, data?: any): ...
```

---

### 2.2 目录结构优化

#### 当前问题

1. **职责重叠**:
   - `lib/` 和 `services/` 都包含API客户端代码
   - `components/` 和 `pages/` 都包含页面组件
   - `schemas/` 中大量未使用的模型定义

2. **命名不一致**:
   - `api-client.ts`, `api-client-enhanced.ts`, `api-client-optimized.ts` 共存
   - `rbac_service.py` 和 `auth_service.py` 部分功能重叠

#### 优化方案

```
frontend/src/
├── hooks/
│   ├── useApiCall.ts          # 新增：统一API调用
│   ├── useAsyncAction.ts      # 新增：异步操作
│   ├── useGraphState.ts       # 新增：图形状态
│   └── useBatchOperation.ts   # 新增：批量操作
├── lib/
│   ├── api/
│   │   ├── client.ts          # 合并后的API客户端
│   │   └── types.ts           # API类型定义
│   └── utils/
│       └── logger.ts          # 新增：日志工具
├── components/
│   ├── common/                # 通用组件
│   ├── visualizations/        # 可视化组件
│   └── [删除 examples/, admin/, optimized/]
└── [删除 pages/ 目录]

backend/app/
├── core/
│   ├── repository.py          # 新增：BaseRepository
│   ├── decorators.py          # 新增：装饰器
│   └── logger.py              # 新增：Logger
├── services/
│   └── base.py                # 新增：BaseService
├── schemas/
│   ├── [删除未使用的模型]
│   └── models.py              # 合并常用模型
└── [删除 main_optimized.py]
```

---

## ⚠️ Step 3: 安全实施计划

### 3.1 风险评估

| 重构项        | 风险等级 | 影响范围     | 测试覆盖   | 风险缓解措施           |
| ------------- | -------- | ------------ | ---------- | ---------------------- |
| 创建hooks     | 🟢 低    | 新增代码     | 需补充     | 渐进式替换，保留旧代码 |
| 删除死代码    | 🟡 中    | 删除文件     | 需验证     | 全局搜索确认无引用     |
| 合并API客户端 | 🔴 高    | 核心功能     | 需完整测试 | 保持接口兼容，渐进迁移 |
| 删除依赖      | 🟡 中    | package.json | 需验证     | 检查传递依赖           |
| 后端基类提取  | 🟡 中    | 服务层       | 需补充     | 单元测试先行           |

---

### 3.2 实施步骤（小步迭代）

#### Phase 1: 准备阶段 (Day 1-2)

**目标**: 建立安全网，确保重构不破坏现有功能

- [ ] **Step 1.1**: 运行现有测试套件，记录基准通过率

  ```bash
  cd frontend && npm test
  cd backend && pytest
  ```

- [ ] **Step 1.2**: 为关键重复代码补充测试
  - 前端：API调用错误处理逻辑
  - 后端：数据库CRUD操作
- [ ] **Step 1.3**: 创建重构分支
  ```bash
  git checkout -b refactor/slimming-phase1
  ```

---

#### Phase 2: 低风险重构 (Day 3-5)

**目标**: 删除死代码，减少代码量

- [ ] **Step 2.1**: 删除前端死代码（按文件逐个删除）

  **第1批** (测试后提交):
  - 删除 `components/examples/` 目录
  - 删除 `components/admin/` 目录
  - 运行测试: `npm test`
  - 提交: `git commit -m "refactor: 删除未使用的示例和admin组件"`

  **第2批** (测试后提交):
  - 删除 `components/visualizations/lazy.ts`
  - 删除 `components/QueryClientWrapper.tsx`
  - 删除 `components/ProtectedRoute.tsx`
  - 运行测试: `npm test`
  - 提交: `git commit -m "refactor: 删除未使用的辅助组件"`

  **第3批** (测试后提交):
  - 删除 `components/common/advanced-filter.tsx`
  - 删除 `components/visualizations/ArchitectureTimeline.tsx`
  - 删除 `pages/Projects.tsx`
  - 运行测试: `npm test`
  - 提交: `git commit -m "refactor: 删除未使用的页面和可视化组件"`

- [ ] **Step 2.2**: 删除后端死代码（按文件逐个删除）

  **第1批** (测试后提交):
  - 删除 `backend/app/schemas/openapi_models.py`
  - 删除 `backend/app/schemas/validation.py`
  - 删除 `backend/app/schemas/response_models.py`
  - 运行测试: `pytest`
  - 提交: `git commit -m "refactor: 删除未使用的schema文件"`

  **第2批** (测试后提交):
  - 删除 `backend/app/schemas/ai_pr_review_models.py`
  - 清理 `backend/app/shared/exceptions.py` 中未使用的异常类
  - 运行测试: `pytest`
  - 提交: `git commit -m "refactor: 清理未使用的异常类"`

  **第3批** (测试后提交):
  - 删除 `backend/app/main_optimized.py`
  - 清理 `backend/app/database/optimizations.py` 未使用导入
  - 运行测试: `pytest`
  - 提交: `git commit -m "refactor: 删除未使用的优化入口文件"`

- [ ] **Step 2.3**: 清理依赖
  - 从 `package.json` 删除 `react-to-image`
  - 从 `requirements.txt` 删除 `pytz`, `humanize`
  - 运行完整测试
  - 提交: `git commit -m "refactor: 移除未使用的依赖包"`

---

#### Phase 3: 中风险重构 (Day 6-10)

**目标**: 提取通用工具，减少重复代码

- [ ] **Step 3.1**: 前端 - 创建通用Hooks

  **优先级顺序**:
  1. `useApiCall` hook (影响最大)
     - 创建 `frontend/src/hooks/useApiCall.ts`
     - 编写单元测试
     - 在一个页面组件中试用
     - 验证功能正确后逐步推广
  2. `useAsyncAction` hook
     - 创建 `frontend/src/hooks/useAsyncAction.ts`
     - 编写单元测试
     - 在 `AuthContext` 中试用
  3. `Logger` 工具
     - 创建 `frontend/src/lib/utils/logger.ts`
     - 替换 `api-client.ts` 中的 console 调用
     - 验证日志输出

- [ ] **Step 3.2**: 后端 - 提取基类和装饰器

  **优先级顺序**:
  1. `Logger` 类
     - 创建 `backend/app/core/logger.py`
     - 替换现有的 console.error/log
  2. `BaseRepository` 类
     - 创建 `backend/app/core/repository.py`
     - 在一个 service 中试用
     - 编写单元测试
  3. `with_audit_log` 装饰器
     - 创建 `backend/app/core/decorators.py`
     - 在一个 endpoint 中试用

---

#### Phase 4: 高风险重构 (Day 11-15)

**目标**: 合并重复实现，优化核心功能

- [ ] **Step 4.1**: 合并API客户端

  **步骤**:
  1. 分析三个API客户端的差异
  2. 创建统一的 `lib/api/client.ts`
  3. 保持所有接口签名兼容
  4. 逐个替换导入路径
  5. 删除旧文件

- [ ] **Step 4.2**: 合并Service层重复逻辑

  **步骤**:
  1. 提取 `rbac_service.py` 和 `auth_service.py` 的公共逻辑
  2. 创建基类或共享函数
  3. 编写单元测试
  4. 渐进式替换

---

### 3.3 测试检查清单

每次重构后必须执行的测试：

#### 前端测试

```bash
# 1. 单元测试
cd frontend
npm test

# 2. 类型检查
npm run type-check

# 3. Lint检查
npm run lint

# 4. 构建测试
npm run build

# 5. E2E测试（如有）
npm run test:e2e
```

#### 后端测试

```bash
# 1. 单元测试
cd backend
pytest tests/ -v

# 2. 类型检查
pyright app/

# 3. 覆盖率检查
pytest --cov=app --cov-report=term-missing

# 4. 集成测试
pytest tests/integration/ -v
```

---

### 3.4 回滚策略

每个Phase创建独立分支，失败时可以快速回滚：

```bash
# Phase 1 失败回滚
git checkout main
git branch -D refactor/slimming-phase1

# Phase 2 失败回滚
git checkout refactor/slimming-phase1
git branch -D refactor/slimming-phase2

# 依此类推
```

---

## 📊 成功指标

### 代码质量指标

| 指标             | 当前值 | 目标值 | 验证方法                           |
| ---------------- | ------ | ------ | ---------------------------------- |
| 重复代码行数     | ~2,280 | <500   | 使用 `jscpd` 工具扫描              |
| 代码覆盖率       | 未知   | >80%   | `pytest --cov` / `jest --coverage` |
| TypeScript错误数 | 未知   | 0      | `npm run type-check`               |
| ESLint警告数     | 未知   | 0      | `npm run lint`                     |
| 平均文件复杂度   | 高     | 中     | SonarQube分析                      |

### 功能验证指标

| 功能     | 验证方法       | 通过标准           |
| -------- | -------------- | ------------------ |
| 用户登录 | 手动测试 + E2E | 成功登录并跳转     |
| 项目创建 | 手动测试 + E2E | 成功创建项目       |
| 代码分析 | 手动测试       | 成功触发分析       |
| 审计日志 | 数据库查询     | 日志正确记录       |
| 权限控制 | 边界测试       | 正确拒绝未授权访问 |

---

## 🚀 执行时间表

| 阶段    | 时间      | 任务       | 产出                     |
| ------- | --------- | ---------- | ------------------------ |
| Phase 1 | Day 1-2   | 准备阶段   | 测试基准、重构分支       |
| Phase 2 | Day 3-5   | 低风险重构 | 删除26个死代码文件       |
| Phase 3 | Day 6-10  | 中风险重构 | 6个通用工具/hook         |
| Phase 4 | Day 11-15 | 高风险重构 | 合并API客户端、Service层 |
| 验收    | Day 16    | 最终验证   | 测试报告、重构总结       |

---

## 📝 注意事项

### 约束条件

1. ✅ **测试先行**: 任何重构前，确保相关测试通过
2. ✅ **小步提交**: 每个小功能点独立提交，便于回滚
3. ✅ **保持兼容**: 不改变外部API和接口签名
4. ✅ **文档更新**: 重构后及时更新相关文档
5. ✅ **团队沟通**: 重构前通知团队，避免并行修改

### 禁止事项

1. ❌ 不在重构时添加新功能
2. ❌ 不修改数据库Schema
3. ❌ 不改变API响应格式
4. ❌ 不删除有测试覆盖的代码（除非先删除测试）
5. ❌ 不在Phase 4前合并核心模块

---

## ✅ 执行确认

在开始执行前，请确认以下事项：

- [ ] 已阅读完整的瘦身计划书
- [ ] 已备份重要数据
- [ ] 已通知团队成员
- [ ] 已创建重构分支
- [ ] 已运行并记录基准测试结果
- [ ] 已准备好回滚方案

**确认人**: ******\_\_\_\_******  
**确认日期**: ******\_\_\_\_******  
**开始时间**: ******\_\_\_\_******

---

**下一步**: 请确认是否开始执行 Phase 1，或需要对计划进行调整。

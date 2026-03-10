# Common Library

通用基础库，包含前后端共享的工具函数和组件。

## 项目优化成果

本库是项目优化的结果，实现了以下目标：
- 将全局通用的非业务逻辑（加解密、日期转换、网络请求封装等）进行原子化抽离
- 统一迁移至 `common` 库中，强制删除原项目中的分散实现
- 提炼具有高属性配置性的基础UI组件库
- 定义统一的异常处理、日志拦截器及DTO转换逻辑，消除跨Controller/Service的样板代码
- **🔧 枚举类型整合**: 识别并整合了15+个重复冲突的枚举类型，消除了不一致性

## 🔧 枚举类型整合 (Enum Consolidation)

### 解决的关键问题
- ✅ **Role枚举冲突**: 3个不同的Role枚举，值不一致（大小写冲突）
- ✅ **Severity枚举重复**: 4个不同的严重性级别枚举
- ✅ **CircuitBreaker状态重复**: 2个不同的熔断器状态枚举
- ✅ **Repository状态重复**: 2个不同的仓库状态枚举

### 整合后的枚举文件
- `common/shared/enums.py` - Python统一枚举定义（45+个枚举）
- `common/shared/enums.ts` - TypeScript统一枚举定义（45+个枚举）

### 枚举分类
1. **RBAC & 认证** - Role, Permission
2. **严重性 & 优先级** - Severity, TaskPriority  
3. **状态管理** - RepositoryStatus, TaskStatus, HealthStatus, PRStatus
4. **系统 & 基础设施** - CircuitBreakerState, ServiceState, CacheKeyPrefix
5. **分析 & 审查** - ReviewSeverity, ReviewCategory, AnalysisType, ComplianceStatus
6. **架构 & 图形** - NodeType, RelationshipType, ComponentType, DependencyType
7. **仓库 & Git** - RepositoryURLFormat, GitHubConnectionType
8. **LLM & AI** - LLMProvider, ModelType
9. **质量 & 合规** - ComplianceFramework, ScanTool, Confidence
10. **审计 & 项目管理** - AuditAction, InvitationStatus, ProjectRole, ErrorType

### 使用方式
```python
# Python
from common.shared.enums import Role, Permission, Severity, TaskStatus

# 使用统一的枚举值
user_role = Role.ADMIN
task_priority = TaskPriority.CRITICAL
```

```typescript
// TypeScript
import { Role, Permission, Severity, ErrorType } from '../../common/shared/enums';

// 使用统一的枚举值
const userRole = Role.ADMIN;
const errorType = ErrorType.NETWORK_ERROR;
```

## 目录结构

```
common/
├── frontend/                 # 前端通用库
│   ├── components/          # UI组件库
│   │   ├── common/          # 基础组件
│   │   │   ├── Modal.tsx    # 统一模态框组件
│   │   │   ├── StatusBadge.tsx # 状态徽章组件
│   │   │   └── DataTable.tsx # 数据表格组件
│   │   └── index.ts         # 组件统一导出
│   ├── utils/               # 工具函数库
│   │   ├── retry.ts         # 重试机制
│   │   ├── network.ts       # 网络请求
│   │   ├── cache.ts         # 缓存管理
│   │   ├── formatters.ts    # 格式化工具
│   │   ├── validators.ts    # 验证工具
│   │   ├── encryption.ts    # 加密工具
│   │   ├── scheduler.ts     # 任务调度
│   │   ├── constants.ts     # 常量定义
│   │   └── index.ts         # 工具统一导出
│   ├── hooks/               # React Hooks
│   │   ├── useFormValidation.ts # 表单验证Hook
│   │   └── index.ts         # Hooks统一导出
│   └── services/            # 服务封装
├── backend/                 # 后端通用库
│   ├── decorators/          # 装饰器库
│   │   ├── audit.py         # 审计日志装饰器
│   │   ├── error_handling.py # 错误处理装饰器
│   │   ├── validation.py    # 输入验证装饰器
│   │   ├── permission.py    # 权限检查装饰器
│   │   ├── caching.py       # 缓存装饰器
│   │   ├── rate_limiting.py # 限流装饰器
│   │   └── __init__.py      # 装饰器统一导出
│   ├── services/            # 基础服务
│   │   ├── base_service.py  # 基础CRUD服务
│   │   ├── response_formatter.py # 响应格式化
│   │   ├── dto_converter.py # DTO转换器
│   │   ├── permission_checker.py # 权限检查器
│   │   └── __init__.py      # 服务统一导出
│   └── utils/               # 工具函数
└── shared/                  # 前后端共享
    ├── types/               # 类型定义
    ├── constants/           # 常量定义
    └── validators/          # 验证规则
```

## 快速开始

### 安装

#### 前端
```bash
cd common && npm install
```

#### 后端
```bash
cd common && pip install -e .
```

### 前端使用

#### 基础导入
```typescript
// 工具函数
import { 
  retryWithBackoff, 
  api, 
  cache, 
  formatTime, 
  validators,
  RETRY_CONFIGS 
} from '@common/frontend/utils';

// 组件
import { 
  Modal, 
  StatusBadge, 
  DataTable,
  ConfirmModal 
} from '@common/frontend/components';

// Hooks
import { 
  useFormValidation 
} from '@common/frontend/hooks';
```

#### 网络请求示例
```typescript
// 基础请求
const userData = await api.get('/users/me');
const newUser = await api.post('/users', { name: 'John', email: 'john@example.com' });

// 带重试的请求
const data = await retryWithBackoff(
  () => api.get('/api/data'),
  RETRY_CONFIGS.API
);

// 自定义重试配置
const result = await retryWithBackoff(
  () => fetch('/api/critical-data'),
  {
    maxRetries: 5,
    initialDelay: 2000,
    maxDelay: 30000,
    factor: 2,
    shouldRetry: (error) => error.status >= 500
  }
);
```

#### 缓存使用示例
```typescript
// 设置缓存（5分钟TTL）
cache.set('user-preferences', userPrefs, 300000);

// 获取缓存
const cachedPrefs = cache.get('user-preferences');

// 检查缓存是否存在
if (cache.has('user-data')) {
  const userData = cache.get('user-data');
}

// 清除特定模式的缓存
cache.clear('user-*');

// 获取缓存统计
const stats = cache.stats();
console.log(`缓存命中率: ${stats.hitRate}%`);
```

#### UI组件示例
```typescript
// 模态框
const [isOpen, setIsOpen] = useState(false);

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="用户设置"
  size="lg"
  footer={
    <div className="flex justify-end space-x-2">
      <button onClick={() => setIsOpen(false)}>取消</button>
      <button onClick={handleSave}>保存</button>
    </div>
  }
>
  <UserSettingsForm />
</Modal>

// 确认对话框
<ConfirmModal
  isOpen={showConfirm}
  onClose={() => setShowConfirm(false)}
  onConfirm={handleDelete}
  title="确认删除"
  message="确定要删除这个用户吗？此操作不可撤销。"
  confirmText="删除"
  confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
/>

// 状态徽章
<StatusBadge status="completed" size="md" />
<StatusBadge status="failed" size="sm" showText={false} />

// 数据表格
<DataTable
  data={users}
  columns={[
    { key: 'name', title: '姓名' },
    { key: 'email', title: '邮箱' },
    { 
      key: 'status', 
      title: '状态',
      render: (status) => <StatusBadge status={status} />
    }
  ]}
  loading={isLoading}
  pagination={{
    current: page,
    pageSize: 20,
    total: totalUsers,
    onChange: (page, size) => setPage(page)
  }}
/>
```

### 后端使用

#### 基础导入
```python
# 装饰器
from common.backend.decorators import (
    with_audit_log, 
    handle_errors, 
    require_permission,
    validate_input,
    cache_result,
    rate_limit
)

# 服务
from common.backend.services import (
    BaseService, 
    CRUDService,
    ResponseFormatter,
    DTOConverter,
    PermissionChecker
)
```

#### 服务类示例
```python
from sqlalchemy.ext.asyncio import AsyncSession
from common.backend.services import CRUDService, ResponseFormatter
from common.backend.decorators import with_audit_log, handle_errors

class UserService(CRUDService[User, UserCreate, UserUpdate]):
    
    @with_audit_log("user.create", include_args=True)
    @handle_errors()
    async def create_user(
        self, 
        db: AsyncSession, 
        user_data: UserCreate,
        current_user_id: str
    ) -> dict:
        # 检查邮箱是否已存在
        existing = await self.get_by_field(db, 'email', user_data.email)
        if existing:
            return ResponseFormatter.conflict("邮箱已存在")
        
        # 创建用户
        user = await self.create(db, user_data)
        
        return ResponseFormatter.created(
            DTOConverter.to_dto(user, UserResponse),
            "用户创建成功",
            resource_id=str(user.id)
        )
    
    @with_audit_log("user.list")
    @handle_errors()
    @cache_result(ttl=300)  # 缓存5分钟
    async def get_users(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20
    ) -> dict:
        users = await self.get_multi(db, skip=skip, limit=limit)
        total = await self.count(db)
        
        user_dtos = DTOConverter.to_dto_list(users, UserResponse)
        
        return ResponseFormatter.paginated(
            user_dtos, 
            total, 
            skip // limit + 1, 
            limit
        )
```

## 主要功能特性

### 前端优化成果

#### 1. 统一的网络请求
- **整合前**: 项目中有3个不同的API客户端实现
- **整合后**: 统一的NetworkClient，支持：
  - 自动重试机制（指数退避）
  - 请求缓存（GET请求5分钟TTL）
  - 请求去重（1秒内相同请求合并）
  - 并发控制（最多6个并发请求）
  - 自动认证token处理

#### 2. 统一的缓存管理
- **整合前**: 分散在各个service中的缓存逻辑
- **整合后**: 统一的CacheManager，支持：
  - TTL过期机制
  - LRU淘汰策略
  - 模式匹配清理
  - 缓存统计（命中率、大小等）

#### 3. 通用UI组件库
- **Modal**: 高度可配置的模态框，支持多种尺寸、动画、焦点管理
- **StatusBadge**: 统一的状态徽章，支持自定义颜色、大小、变体
- **DataTable**: 通用数据表格，支持分页、排序、自定义渲染

### 后端优化成果

#### 1. 统一的装饰器系统
- **@with_audit_log**: 自动审计日志记录，支持参数包含、结果记录
- **@handle_errors**: 统一错误处理，支持自定义错误映射
- **@require_permission**: 权限检查，支持角色和资源级权限
- **@validate_input/@validate_output**: 输入输出验证
- **@cache_result**: 结果缓存，支持TTL和条件缓存
- **@rate_limit**: 限流控制，支持用户级、IP级、端点级限流

#### 2. 基础服务类
- **BaseService**: 提供通用CRUD操作（get、create、update、delete、count等）
- **CRUDService**: 扩展BaseService，添加便捷方法（get_or_404、get_by_field等）
- **批量操作**: 支持bulk_create、bulk_update等批量操作

#### 3. 响应格式化
- **ResponseFormatter**: 统一API响应格式
- **标准响应**: success、error、warning三种状态
- **专用响应**: created、updated、deleted、paginated等

## 配置说明

### 前端配置

在项目的 `tsconfig.json` 中添加路径映射：
```json
{
  "compilerOptions": {
    "paths": {
      "@common/*": ["../common/*"],
      "@common/frontend/*": ["../common/frontend/*"]
    }
  }
}
```

### 后端配置

在 `requirements.txt` 中添加：
```
-e ../common
```

## 预期收益

### 代码质量提升
- **重复代码减少**: 消除了多个API客户端、缓存实现等重复代码
- **一致性提升**: 统一的UI组件和API响应格式
- **可维护性**: 集中管理的通用库更容易维护和升级

### 开发效率提升
- **开发速度**: 新功能开发可直接使用通用组件，减少重复开发
- **代码复用**: 高度可配置的组件支持多种使用场景
- **错误减少**: 经过优化的通用组件减少了常见错误

通过本通用库，项目实现了代码的高度复用和标准化，显著提升了开发效率和代码质量。
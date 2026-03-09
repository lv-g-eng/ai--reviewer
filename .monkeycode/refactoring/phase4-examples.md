# Phase 4 重构示例和指南

**目标**: 展示如何应用 Phase 3 创建的工具重构现有代码

---

## 示例 1: 应用 Logger 工具

### 重构前

```typescript
// ❌ 旧代码 - 分散的console调用
console.log('[AuthContext] Fetching current user...');
console.log('[AuthContext] Response:', response.status);
console.error('[AuthContext] Failed:', error);
```

### 重构后

```typescript
// ✅ 新代码 - 统一的Logger
import { createLogger } from '@/lib/utils/logger';

const logger = createLogger('AuthContext');

logger.debug('Fetching current user');
logger.info('Response received', { status: response.status });
logger.error('Request failed', error);
```

**改进点**:

- 环境感知（生产环境不显示debug）
- 敏感信息自动过滤
- 统一格式

---

## 示例 2: 应用 useAsyncAction Hook

### 重构前

```typescript
// ❌ 旧代码 - 重复的状态管理
const [loading, setLoading] = useState(false);
const [error, setError] = useState<Error | null>(null);

const fetchData = async () => {
  setLoading(true);
  setError(null);
  try {
    const data = await apiClient.get('/api/data');
    setData(data);
  } catch (err) {
    setError(err instanceof Error ? err : new Error('Unknown error'));
  } finally {
    setLoading(false);
  }
};
```

### 重构后

```typescript
// ✅ 新代码 - 简洁的状态管理
import { useAsyncAction } from '@/hooks/useAsyncAction';

const { execute, loading, error } = useAsyncAction();

const fetchData = async () => {
  const data = await execute(() => apiClient.get('/api/data'));
  if (data) {
    setData(data);
  }
};
```

**改进点**:

- 减少 10+ 行重复代码
- 统一错误处理
- 自动状态管理

---

## 示例 3: 应用 useApiCall Hook

### 重构前

```typescript
// ❌ 旧代码 - 重复的try-catch + toast
const handleSubmit = async (data: FormData) => {
  try {
    await apiClient.post('/api/users', data);
    toast({
      title: 'Success',
      description: 'User created successfully',
    });
  } catch (err: any) {
    const message = err?.response?.data?.detail || 'Failed to create user';
    toast({
      variant: 'destructive',
      title: 'Error',
      description: message,
    });
  }
};
```

### 重构后

```typescript
// ✅ 新代码 - 简洁的API调用
import { useApiCall } from '@/hooks/useApiCall';

const { execute } = useApiCall();

const handleSubmit = async (data: FormData) => {
  await execute(() => apiClient.post('/api/users', data), {
    successMessage: 'User created successfully',
    errorMessage: 'Failed to create user',
  });
};
```

**改进点**:

- 减少 15+ 行重复代码
- 自动错误提取
- 可选的成功回调

---

## 示例 4: 应用 BaseRepository

### 重构前

```python
# ❌ 旧代码 - 重复的数据库操作
class UserService:
    async def get_user(self, user_id: str):
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except Exception as e:
            await self.db.rollback()
            raise

    async def create_user(self, user_data: UserCreate):
        try:
            user = User(**user_data.dict())
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise
```

### 重构后

```python
# ✅ 新代码 - 继承BaseRepository
from app.core.repository import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    # 自定义查询方法
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    # CRUD方法已由BaseRepository提供:
    # - get(id)
    # - get_multi(skip, limit)
    # - create(schema)
    # - update(id, schema)
    # - delete(id)
```

**改进点**:

- 减少 100+ 行重复代码
- 统一事务管理
- 标准化错误处理

---

## 示例 5: 应用 with_audit_log

### 重构前

```python
# ❌ 旧代码 - 手动审计日志
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request
):
    user = User(**user_data.dict())
    db.add(user)

    # 手动记录审计日志
    audit = AuditLog(
        user_id=current_user.id,
        action="user.create",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else "unknown"
    )
    db.add(audit)
    await db.commit()

    return user
```

### 重构后

```python
# ✅ 新代码 - 装饰器自动处理
from app.core.decorators import with_audit_log

@router.post("/users")
@with_audit_log("user.create")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request
):
    user = User(**user_data.dict())
    db.add(user)
    await db.commit()
    return user
```

**改进点**:

- 减少 10+ 行重复代码
- 自动IP提取
- 统一审计格式

---

## 重构优先级

### 高优先级（立即执行）

1. **Logger 应用** - 影响20+文件，风险低
2. **useAsyncAction 应用** - 影响15+文件，风险低

### 中优先级（后续迭代）

3. **useApiCall 应用** - 影响10+文件，风险中
4. **BaseRepository 应用** - 影响8+文件，风险中

### 低优先级（长期规划）

5. **with_audit_log 应用** - 影响10+文件，需谨慎测试

---

## 重构检查清单

每次重构前检查:

- [ ] 确认目标文件有测试覆盖
- [ ] 理解现有代码逻辑
- [ ] 确保功能行为不变
- [ ] 小步提交，便于回滚

重构后验证:

- [ ] 运行单元测试
- [ ] 运行类型检查
- [ ] 手动测试功能
- [ ] 检查代码可读性

---

## 批量重构脚本示例

```bash
# 查找所有需要应用Logger的文件
find frontend/src -name "*.tsx" -o -name "*.ts" | \
xargs grep -l "console\." | \
grep -v node_modules

# 统计可减少的代码行数
grep -r "console\." frontend/src --include="*.ts" --include="*.tsx" | wc -l
```

---

**文档创建时间**: 2026-03-09
**适用分支**: refactor/slimming-phase1

# AI Code Review Platform - 编码规范

本文档定义了项目的编码规范，确保代码质量和一致性。

## 目录

- [通用规范](#通用规范)
- [Python规范](#python规范)
- [TypeScript/JavaScript规范](#typescriptjavascript规范)
- [React组件规范](#react组件规范)
- [API设计规范](#api设计规范)
- [数据库规范](#数据库规范)
- [测试规范](#测试规范)
- [Git提交规范](#git提交规范)

## 通用规范

### 文件命名

- **Python**: 使用小写字母和下划线：`user_service.py`
- **TypeScript/JavaScript**: 使用小驼峰命名：`userService.ts`
- **组件文件**: 使用大驼峰命名：`UserProfile.tsx`
- **测试文件**: 添加`_test`或`.test`后缀：`user_service_test.py`

### 代码注释

- **语言**: 统一使用英文注释
- **函数文档字符串**: 使用Google风格或NumPy风格
- **行内注释**: 简洁明了，解释"为什么"而非"是什么"

```python
# Good
def calculate_discount(price: float, discount_rate: float) -> float:
    """
    Calculate the discounted price.

    Args:
        price: Original price
        discount_rate: Discount rate (0.0 to 1.0)

    Returns:
        Discounted price

    Example:
        >>> calculate_discount(100.0, 0.2)
        80.0
    """
    return price * (1 - discount_rate)
```

### 错误处理

- **避免**使用过于宽泛的`except Exception`
- 使用具体的异常类型
- 提供有意义的错误消息

```python
# Bad
try:
    result = perform_operation()
except Exception as e:
    logger.error(f"Error: {e}")

# Good
try:
    result = perform_operation()
except DatabaseConnectionError as e:
    logger.error(f"Database connection failed: {e}")
    raise ServiceUnavailableError("Database is unavailable")
except ValidationError as e:
    logger.warning(f"Validation error: {e}")
    raise BadRequestError(f"Invalid input: {e}")
```

## Python规范

遵循 [PEP 8](https://pep8.org/) 规范，并遵守以下额外规则：

### 命名规范

```python
# 类名：大驼峰
class UserService:
    pass

# 函数和变量：小写下划线
def get_user(user_id: int) -> User:
    user_name = ""
    return user

# 常量：大写下划线
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# 私有方法：单下划线前缀
def _internal_method(self):
    pass

# 受保护成员：单下划线前缀
class MyClass:
    def __init__(self):
        self._protected_attr = None
```

### 类型注解

```python
from typing import List, Optional, Dict, Any

# 函数必须有类型注解
def process_data(data: List[str]) -> Dict[str, Any]:
    result = {}
    for item in data:
        result[item] = len(item)
    return result

# 使用Optional表示可选参数
def find_user(user_id: int) -> Optional[User]:
    if user_id == 1:
        return User(id=1, name="Alice")
    return None
```

### 字符串格式化

```python
# 使用f-strings (Python 3.6+)
name = "Alice"
greeting = f"Hello, {name}!"

# 避免使用旧式格式化
greeting = "Hello, %s!" % name  # Bad
greeting = "Hello, {}!".format(name)  # Less preferred
```

### 异步编程

```python
import asyncio

async def fetch_data(url: str) -> dict:
    """Fetch data asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    data = await fetch_data("https://api.example.com")
    print(data)

# 正确运行异步代码
asyncio.run(main())
```

## TypeScript/JavaScript规范

### 命名规范

```typescript
// 类名：大驼峰
class UserService {
  private userName: string;

  public getUserName(): string {
    return this.userName;
  }
}

// 接口：大驼峰，可选I前缀
interface User {
  id: number;
  name: string;
  email?: string;
}

// 类型别名：大驼峰
type UserRole = 'admin' | 'user' | 'guest';

// 枚举：大驼峰
enum UserStatus {
  Active = 'active',
  Inactive = 'inactive',
}

// 变量和函数：小驼峰
const maxRetryCount = 3;
function getUserById(id: number): User {
  return {} as User;
}

// 常量：大写下划线
const API_BASE_URL = 'https://api.example.com';

// 布尔值：is/has/should前缀
const isLoading = false;
const hasPermission = true;
const shouldUpdate = true;
```

### 类型定义

```typescript
// 避免使用any
function processUser(user: any) {
  // Bad
  console.log(user.name);
}

// 使用明确的类型
interface User {
  id: number;
  name: string;
  email: string;
}

function processUser(user: User) {
  // Good
  console.log(user.name);
}

// 使用泛型
function first<T>(items: T[]): T | undefined {
  return items[0];
}

// 使用联合类型
type Result<T, E = Error> = { success: true; data: T } | { success: false; error: E };
```

### 异步编程

```typescript
// 使用async/await
async function fetchUser(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  return data;
}

// 正确处理错误
async function getUserSafe(id: number): Promise<User | null> {
  try {
    return await fetchUser(id);
  } catch (error) {
    console.error('Failed to fetch user:', error);
    return null;
  }
}
```

## React组件规范

### 组件结构

```typescript
import React from 'react';
import { useState, useEffect } from 'react';

// Props接口定义
interface UserProfileProps {
  userId: number;
  onUpdate?: (user: User) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  // Hooks声明（按顺序）
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Effects
  useEffect(() => {
    fetchUser(userId)
      .then(setUser)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [userId]);

  // 事件处理函数
  const handleUpdate = (updatedUser: User) => {
    setUser(updatedUser);
    onUpdate?.(updatedUser);
  };

  // 渲染函数
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!user) return null;

  return (
    <div className="user-profile">
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <button onClick={() => handleUpdate(user)}>
        Update
      </button>
    </div>
  );
};

export default UserProfile;
```

### 组件命名

```typescript
// 组件使用大驼峰
const UserProfile: React.FC<UserProfileProps> = () => {};

// Hook使用use前缀
const useUserData = (userId: number) => {};

// Context使用Context后缀
const UserContext = React.createContext<User | null>(null);

// Provider使用Provider后缀
const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {};
```

## API设计规范

### RESTful API设计

```
GET    /api/v1/users           # 获取用户列表
GET    /api/v1/users/{id}      # 获取单个用户
POST   /api/v1/users           # 创建用户
PUT    /api/v1/users/{id}      # 更新用户（全部字段）
PATCH  /api/v1/users/{id}      # 更新用户（部分字段）
DELETE /api/v1/users/{id}      # 删除用户
```

### 统一响应格式

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Alice"
  },
  "message": "Operation successful",
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "abc123"
  }
}
```

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

## 数据库规范

### 表命名

- 使用复数形式：`users`, `projects`, `reviews`
- 使用小写字母和下划线：`user_roles`, `project_members`

### 字段命名

- 使用小写字母和下划线：`user_id`, `created_at`, `updated_at`
- 主键：`id`
- 外键：`{table}_id`：`user_id`, `project_id`
- 时间戳：`created_at`, `updated_at`

### 索引命名

```sql
-- 主键索引：pk_{table}
PRIMARY KEY (id)  -- pk_users

-- 唯一索引：uk_{table}_{column}
UNIQUE KEY uk_users_email (email)

-- 普通索引：idx_{table}_{column}
INDEX idx_users_email (email)

-- 复合索引：idx_{table}_{column1}_{column2}
INDEX idx_projects_user_id_status (user_id, status)
```

## 测试规范

### 单元测试

```python
# 使用pytest
import pytest
from app.services.user_service import UserService

@pytest.fixture
def user_service(db_session):
    return UserService(db_session)

def test_get_user_success(user_service):
    user = user_service.get_user(1)
    assert user is not None
    assert user.id == 1

def test_get_user_not_found(user_service):
    user = user_service.get_user(999)
    assert user is None

@pytest.mark.asyncio
async def test_create_user(user_service):
    user_data = {"name": "Alice", "email": "alice@example.com"}
    user = await user_service.create_user(user_data)
    assert user.id is not None
    assert user.name == "Alice"
```

### 组件测试

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import UserProfile from './UserProfile';

describe('UserProfile', () => {
  it('renders user name', () => {
    const mockUser = { id: 1, name: 'Alice', email: 'alice@example.com' };
    render(<UserProfile user={mockUser} />);
    expect(screen.getByText('Alice')).toBeInTheDocument();
  });

  it('calls onUpdate when button is clicked', () => {
    const mockOnUpdate = jest.fn();
    const mockUser = { id: 1, name: 'Alice', email: 'alice@example.com' };
    render(<UserProfile user={mockUser} onUpdate={mockOnUpdate} />);

    fireEvent.click(screen.getByRole('button'));
    expect(mockOnUpdate).toHaveBeenCalledWith(mockUser);
  });
});
```

## Git提交规范

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型（type）

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 代码重构（不是新功能也不是修复）
- `test`: 测试相关
- `chore`: 构建/工具链相关

### 示例

```
feat(auth): add GitHub OAuth login

Implement GitHub OAuth 2.0 authentication
with user profile synchronization.

Closes #123
```

```
fix(api): handle null response from external service

When external service returns null, log error
and return appropriate error response instead of
crashing.

Fixes #456
```

## 代码审查清单

提交代码前，请检查：

- [ ] 代码符合本规范
- [ ] 所有函数都有类型注解
- [ ] 所有函数都有文档字符串
- [ ] 没有使用`any`类型（除非必要）
- [ ] 错误处理完善
- [ ] 没有硬编码的敏感信息
- [ ] 测试覆盖核心功能
- [ ] 代码格式化（black for Python, Prettier for JS/TS）
- [ ] 提交消息符合规范
- [ ] 代码通过所有检查（linting, type checking）

## 工具配置

### Python

```bash
# 代码格式化
black backend/

# 类型检查
mypy backend/

# 代码检查
pylint backend/

# 测试
pytest backend/tests/
```

### TypeScript/JavaScript

```bash
# 代码格式化
prettier --write frontend/

# 类型检查
tsc --noEmit

# 代码检查
eslint frontend/

# 测试
npm test
```

## 参考资源

- [PEP 8 - Python代码风格指南](https://pep8.org/)
- [Python类型提示](https://docs.python.org/3/library/typing.html)
- [TypeScript手册](https://www.typescriptlang.org/docs/)
- [React官方文档](https://react.dev/)
- [RESTful API设计指南](https://restfulapi.net/)
- [Effective Python](https://effectivepython.com/)

---

**最后更新**: 2026-03-09
**维护者**: 开发团队

# 开发者指南

本指南为开发人员提供完整的开发流程、编码规范和最佳实践。

## 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [开发流程](#开发流程)
- [编码规范](#编码规范)
- [测试指南](#测试指南)
- [部署指南](#部署指南)
- [故障排查](#故障排查)

## 开发环境搭建

### 环境要求

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Neo4j 5+
- Git

### 快速开始

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd ai-code-review-platform
```

#### 2. 配置环境变量

```bash
# 后端环境变量
cp .env.template .env
# 编辑 .env 文件，填入配置

# 前端环境变量
cp frontend/.env.example frontend/.env.local
# 编辑 frontend/.env.local 文件
```

#### 3. 安装依赖

**后端依赖**：

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**前端依赖**：

```bash
cd frontend
npm install
# 或使用 pnpm
pnpm install
```

#### 4. 启动数据库

```bash
# 使用 Docker Compose
docker-compose up -d postgres redis neo4j

# 或手动启动各数据库服务
```

#### 5. 初始化数据库

```bash
cd backend
python -m alembic upgrade head
python scripts/init_db.py
```

#### 6. 启动开发服务器

**后端服务器**：

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端服务器**：

```bash
cd frontend
npm run dev
# 或
pnpm dev
```

#### 7. 访问应用

- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 开发工具推荐

#### VS Code扩展

- Python：Python, Pylance
- JavaScript/TypeScript：ESLint, Prettier
- Git：GitLens
- Docker：Docker
- API：REST Client

#### 后端工具

- pytest：测试框架
- black：代码格式化
- pylint：代码检查
- mypy：类型检查

#### 前端工具

- ESLint：代码检查
- Prettier：代码格式化
- TypeScript：类型检查
- Jest：测试框架

## 项目结构

### 后端结构

```
backend/
├── app/
│   ├── api/                # API端点
│   │   ├── v1/
│   │   │   ├── endpoints/  # 端点实现
│   │   │   └── api.py      # 路由定义
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑
│   ├── database/           # 数据库操作
│   ├── middleware/         # 中间件
│   ├── utils/              # 工具函数
│   ├── tasks/              # 异步任务
│   └── main.py             # 应用入口
├── tests/                  # 测试代码
├── alembic/               # 数据库迁移
├── scripts/               # 脚本文件
└── requirements/          # 依赖管理
```

### 前端结构

```
frontend/
├── src/
│   ├── app/               # 页面组件
│   ├── components/        # 可复用组件
│   ├── lib/              # 工具库
│   ├── services/         # API服务
│   ├── contexts/         # React Context
│   ├── hooks/           # 自定义Hooks
│   ├── utils/           # 工具函数
│   └── types/           # TypeScript类型
├── public/               # 静态资源
└── tests/               # 测试代码
```

## 开发流程

### Git工作流

#### 分支策略

- `main` - 主分支，生产环境代码
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - Bug修复分支
- `hotfix/*` - 紧急修复分支

#### 提交规范

```
type(scope): subject

body

footer
```

**类型（type）**：

- `feat` - 新功能
- `fix` - Bug修复
- `docs` - 文档更新
- `style` - 代码格式
- `refactor` - 代码重构
- `test` - 测试相关
- `chore` - 构建/工具

**示例**：

```
feat(auth): add GitHub OAuth login

Implement GitHub OAuth 2.0 authentication
with user profile synchronization.

Closes #123
```

### 开发流程

#### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

#### 2. 开发功能

- 编写代码
- 添加测试
- 更新文档

#### 3. 代码检查

```bash
# 后端
cd backend
black .           # 格式化代码
pylint app/       # 代码检查
mypy app/         # 类型检查
pytest tests/     # 运行测试

# 前端
cd frontend
npm run lint      # 代码检查
npm run typecheck # 类型检查
npm test          # 运行测试
```

#### 4. 提交代码

```bash
git add .
git commit -m "feat(feature): add new feature"
```

#### 5. 推送代码

```bash
git push origin feature/your-feature-name
```

#### 6. 创建Pull Request

- 在GitHub上创建PR
- 填写PR模板
- 请求代码审查

#### 7. 合并代码

- 通过代码审查
- 合并到目标分支
- 删除功能分支

## 编码规范

### Python规范

#### 遵循PEP 8

```python
# 类名使用大驼峰
class UserService:
    pass

# 函数和变量使用小写下划线
def get_user(user_id: int) -> User:
    pass

# 常量使用大写下划线
MAX_RETRY_COUNT = 3
```

#### 类型注解

```python
from typing import List, Optional
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None

def get_users(limit: int = 10) -> List[UserResponse]:
    pass
```

#### 文档字符串

```python
def analyze_code(code: str) -> dict:
    """
    分析代码并返回分析结果。

    Args:
        code: 要分析的代码字符串

    Returns:
        包含分析结果的字典

    Raises:
        ValueError: 当代码为空时
    """
    if not code:
        raise ValueError("Code cannot be empty")
    # 实现
```

### JavaScript/TypeScript规范

#### 命名规范

```typescript
// 类名使用大驼峰
class UserService {
  // 方法使用小驼峰
  getUser(id: number): User {
    // 变量使用小驼峰
    const userName = '';
    return null as any;
  }
}

// 常量使用大写下划线
const MAX_RETRY_COUNT = 3;
```

#### 类型定义

```typescript
interface User {
  id: number;
  username: string;
  email?: string;
}

function getUsers(limit: number = 10): Promise<User[]> {
  return Promise.resolve([]);
}
```

#### 组件规范

```typescript
import React from 'react';

interface Props {
  title: string;
  onAction: () => void;
}

const MyComponent: React.FC<Props> = ({ title, onAction }) => {
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Click</button>
    </div>
  );
};

export default MyComponent;
```

## 测试指南

### 后端测试

#### pytest配置

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    response = client.post("/api/v1/auth/login", json={
        "username": "test",
        "password": "test123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### 测试示例

```python
def test_get_users(client, auth_headers):
    response = client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user(client):
    response = client.post("/api/v1/users", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
```

### 前端测试

#### Jest配置

```typescript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};
```

#### 测试示例

```typescript
// MyComponent.test.tsx
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders title correctly', () => {
    render(<MyComponent title="Test Title" onAction={() => {}} />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('calls onAction when button is clicked', () => {
    const mockOnAction = jest.fn();
    render(<MyComponent title="Test" onAction={mockOnAction} />);
    screen.getByRole('button').click();
    expect(mockOnAction).toHaveBeenCalledTimes(1);
  });
});
```

## 部署指南

### 本地部署

详见 [部署指南](../deployment/DEPLOYMENT_GUIDE.md)

### 生产部署

详见 [生产环境部署清单](../../PRODUCTION_DEPLOYMENT_CHECKLIST.md)

## 故障排查

### 常见问题

#### 后端问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 检查连接配置是否正确
   - 查看数据库日志

2. **导入错误**
   - 确认依赖已安装
   - 检查Python路径
   - 查看错误信息

3. **API超时**
   - 检查网络连接
   - 增加超时时间
   - 优化查询性能

#### 前端问题

1. **构建失败**
   - 清除缓存：`npm run clean`
   - 重新安装依赖：`rm -rf node_modules && npm install`
   - 检查TypeScript错误

2. **API调用失败**
   - 检查后端服务是否运行
   - 检查API地址配置
   - 查看网络请求详情

3. **性能问题**
   - 使用React DevTools分析
   - 检查不必要的重渲染
   - 优化组件结构

### 调试技巧

#### 后端调试

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 使用断点
import pdb; pdb.set_trace()

# 使用日志
logger.debug("Debug message")
logger.info("Info message")
```

#### 前端调试

```typescript
// 使用console
console.log('Debug info');
console.error('Error occurred');

// 使用React DevTools
// 组件树查看
// Props和State检查
// Performance分析

// 使用debugger
debugger; // 代码会在此处暂停
```

## 相关文档

- **[架构文档](ARCHITECTURE.md)** - 系统架构说明
- **[API文档](INTERFACES.md)** - API接口文档
- **[部署指南](../deployment/DEPLOYMENT_GUIDE.md)** - 部署相关文档
- **[故障排查](../../frontend/TROUBLESHOOTING.md)** - 详细故障排查

## 开发资源

### 官方文档

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Next.js文档](https://nextjs.org/docs)
- [React文档](https://react.dev/)
- [TypeScript文档](https://www.typescriptlang.org/)

### 工具文档

- [pytest文档](https://docs.pytest.org/)
- [Jest文档](https://jestjs.io/)
- [ESLint文档](https://eslint.org/)
- [Prettier文档](https://prettier.io/)

## 最佳实践

### 代码质量

1. 保持代码简洁清晰
2. 遵循编码规范
3. 编写有意义的注释
4. 保持函数短小
5. 避免重复代码

### 性能优化

1. 使用缓存
2. 优化数据库查询
3. 实现懒加载
4. 压缩资源
5. 使用CDN

### 安全考虑

1. 验证所有输入
2. 使用HTTPS
3. 实现认证授权
4. 防止SQL注入
5. 保护敏感信息

---

**最后更新**：2026-03-09
**文档版本**：v1.0
**维护者**：开发团队

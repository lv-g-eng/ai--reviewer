# RBAC认证系统集成计划

## 目标
将独立的 `enterprise_rbac_auth` 模块集成到 `backend` 目录中，并完成集成测试和生产环境配置。

## 集成步骤

### 阶段1: 代码集成 (30分钟)

#### 1.1 将RBAC模块移动到backend
- 将 `enterprise_rbac_auth` 重命名为 `backend/app/auth`
- 保留原有的测试在 `backend/tests/auth/`
- 更新所有导入路径

#### 1.2 集成到FastAPI应用
- 在 `backend/app/api/v1/` 下创建认证路由
- 将RBAC中间件集成到 `backend/app/api/dependencies.py`
- 更新 `backend/app/main.py` 包含认证路由

#### 1.3 数据库集成
- 将RBAC模型添加到 `backend/app/models/`
- 创建Alembic迁移脚本
- 更新数据库初始化脚本

### 阶段2: 集成测试 (45分钟)

#### 2.1 端到端认证流程测试
- 测试完整的登录→访问资源→登出流程
- 测试令牌刷新机制
- 测试会话过期处理

#### 2.2 角色访问场景测试
- Admin vs Programmer vs Visitor权限测试
- 权限边界测试
- 未授权访问测试

#### 2.3 项目隔离测试
- 多用户项目访问测试
- 项目所有权验证
- 访问授权测试

#### 2.4 审计日志集成测试
- 敏感操作记录验证
- 审计日志查询测试
- 日志不可修改验证

### 阶段3: 生产环境配置 (30分钟)

#### 3.1 环境变量配置
- JWT密钥配置
- 数据库连接配置
- CORS策略配置
- 会话过期时间配置

#### 3.2 安全配置
- HTTPS配置
- 密码策略配置
- 令牌安全配置
- 审计日志配置

#### 3.3 Docker配置
- 更新Dockerfile
- 更新docker-compose.yml
- 添加健康检查

#### 3.4 数据库迁移
- 创建生产环境迁移脚本
- PostgreSQL配置
- 备份策略

## 文件结构

### 集成后的目录结构
```
backend/
├── app/
│   ├── auth/                    # RBAC认证模块 (从enterprise_rbac_auth移动)
│   │   ├── __init__.py
│   │   ├── models/              # 认证相关模型
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   ├── project.py
│   │   │   └── audit_log.py
│   │   ├── services/            # 认证服务
│   │   │   ├── auth_service.py
│   │   │   ├── rbac_service.py
│   │   │   └── audit_service.py
│   │   ├── middleware/          # 认证中间件
│   │   │   └── auth_middleware.py
│   │   ├── schemas/             # Pydantic模型
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   └── project.py
│   │   └── config.py            # 认证配置
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py      # 认证端点
│   │       │   ├── users.py     # 用户管理端点
│   │       │   ├── projects.py  # 项目管理端点 (更新)
│   │       │   └── audit.py     # 审计日志端点
│   │       └── router.py        # 更新包含认证路由
│   └── main.py                  # 更新包含认证初始化
├── tests/
│   ├── auth/                    # 认证测试 (从enterprise_rbac_auth/tests移动)
│   │   ├── test_auth_service.py
│   │   ├── test_rbac_service.py
│   │   ├── test_auth_middleware.py
│   │   ├── test_user_management.py
│   │   ├── test_session_management.py
│   │   └── test_audit_service.py
│   └── integration/             # 新增集成测试
│       ├── test_auth_integration.py
│       ├── test_rbac_integration.py
│       └── test_audit_integration.py
└── alembic/
    └── versions/
        └── xxxx_add_rbac_tables.py  # 新增迁移脚本
```

## 配置文件更新

### backend/.env
```env
# JWT配置
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# 会话配置
SESSION_EXPIRE_MINUTES=1440

# Bcrypt配置
BCRYPT_ROUNDS=12

# 默认管理员
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123  # 生产环境必须修改

# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### backend/requirements.txt
添加依赖：
```
bcrypt>=4.0.1
PyJWT>=2.8.0
```

## 验证清单

### 功能验证
- [ ] 用户可以登录并获取JWT令牌
- [ ] 令牌验证正常工作
- [ ] 角色权限检查正常工作
- [ ] 项目访问控制正常工作
- [ ] 审计日志正常记录
- [ ] 会话管理正常工作
- [ ] 令牌刷新正常工作

### 安全验证
- [ ] 密码正确哈希
- [ ] JWT令牌安全
- [ ] HTTPS配置正确
- [ ] CORS策略正确
- [ ] 审计日志不可修改
- [ ] 最后一个管理员保护

### 性能验证
- [ ] 令牌验证 < 10ms
- [ ] 权限检查 < 5ms
- [ ] 审计日志异步写入
- [ ] 数据库查询优化

### 测试验证
- [ ] 所有单元测试通过
- [ ] 所有属性测试通过
- [ ] 所有集成测试通过
- [ ] 测试覆盖率 > 90%

## 时间估计

- 代码集成: 30分钟
- 集成测试: 45分钟
- 生产配置: 30分钟
- 验证测试: 15分钟

**总计**: 约2小时

## 风险和缓解

### 风险1: 导入路径冲突
- **缓解**: 使用相对导入，更新所有导入语句

### 风险2: 数据库迁移失败
- **缓解**: 先在开发环境测试，准备回滚脚本

### 风险3: 现有功能受影响
- **缓解**: 保持向后兼容，添加功能开关

### 风险4: 性能下降
- **缓解**: 添加缓存，优化数据库查询

## 下一步行动

1. 执行代码集成
2. 运行所有测试
3. 编写集成测试
4. 配置生产环境
5. 部署验证

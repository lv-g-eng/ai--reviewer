# API接口文档索引

本文档提供项目中所有API接口的统一索引，包括前端API、后端API和第三方集成接口。

## API分类

### 内部API

- **前端API** - 前端应用使用的内部接口
- **后端API** - 后端服务提供的RESTful API
- **服务间API** - 微服务之间的内部通信接口

### 外部API

- **GitHub API** - GitHub集成相关接口
- **LLM API** - AI模型调用接口
- **数据库API** - 数据库操作接口

## 文档导航

### 📖 核心API文档

- **[完整API文档](../../docs/api/API_DOCUMENTATION.md)** - 所有API的完整参考文档
- **[API文档指南](../../docs/api/API_DOCUMENTATION_GUIDE.md)** - API文档使用指南
- **[OpenAPI规范](../../docs/api/OPENAPI_QUICK_REFERENCE.md)** - OpenAPI快速参考

### 🏠 前端API

- **统一API客户端** - `frontend/src/lib/api-client.ts`
- **API客户端文档** - `frontend/src/lib/api-client-optimized.ts`
- **增强API客户端** - `frontend/src/lib/api-client-enhanced.ts`

### 🔧 后端API

- **API端点文档** - `docs/api/API_DOCUMENTATION.md`
- **认证接口** - `/api/auth/*`
- **用户管理接口** - `/api/users/*`
- **项目接口** - `/api/projects/*`
- **代码审查接口** - `/api/reviews/*`
- **PR分析接口** - `/api/pr/*`

### 🔌 GitHub集成API

- **GitHub OAuth设置** - `docs/integration/GITHUB_OAUTH_SETUP.md`
- **GitHub连接指南** - `docs/USER_GITHUB_CONNECTION_GUIDE.md`
- **Webhook处理** - 后端GitHub集成模块

### 🤖 AI服务API

- **AI模块架构** - `docs/AI_MODULE_ARCHITECTURE_EN.md`
- **LLM集成指南** - `docs/guides/LLM_INTEGRATION_GUIDE.md`
- **AI PR审查指南** - `docs/guides/AI_PR_REVIEWER_GUIDE.md`
- **LLM快速开始** - `docs/guides/LLM_QUICK_START.md`

### 🗄️ 数据库API

- **数据库设计** - 架构文档中的数据库章节
- **数据模型** - `backend/app/models/`
- **数据库操作** - `backend/app/database/`

## 按功能分类

### 认证和授权

- **登录/注册** - `/api/auth/login`, `/api/auth/register`
- **GitHub OAuth** - `/api/auth/github`, `/api/auth/github/callback`
- **令牌管理** - `/api/auth/refresh`, `/api/auth/verify`
- **权限验证** - 中间件和权限检查接口

### 用户管理

- **用户信息** - `/api/users/{user_id}`
- **用户列表** - `/api/users`
- **用户设置** - `/api/users/{user_id}/settings`
- **角色管理** - `/api/users/{user_id}/roles`

### 项目管理

- **项目列表** - `/api/projects`
- **项目详情** - `/api/projects/{project_id}`
- **项目创建** - `/api/projects` (POST)
- **项目更新** - `/api/projects/{project_id}` (PUT)
- **项目删除** - `/api/projects/{project_id}` (DELETE)

### 代码审查

- **审查列表** - `/api/reviews`
- **审查详情** - `/api/reviews/{review_id}`
- **创建审查** - `/api/reviews` (POST)
- **审查结果** - `/api/reviews/{review_id}/results`

### PR分析

- **PR列表** - `/api/pr`
- **PR详情** - `/api/pr/{pr_id}`
- **PR分析** - `/api/pr/{pr_id}/analyze`
- **PR历史** - `/api/pr/{pr_id}/history`

### AI分析

- **代码分析** - `/api/ai/analyze`
- **架构分析** - `/api/ai/architecture`
- **安全分析** - `/api/ai/security`
- **性能分析** - `/api/ai/performance`

## 按HTTP方法分类

### GET请求

```
GET /api/auth/verify          # 验证令牌
GET /api/users               # 获取用户列表
GET /api/projects            # 获取项目列表
GET /api/reviews             # 获取审查列表
GET /api/pr                  # 获取PR列表
```

### POST请求

```
POST /api/auth/login          # 用户登录
POST /api/auth/register       # 用户注册
POST /api/projects            # 创建项目
POST /api/reviews             # 创建审查
POST /api/pr/{id}/analyze     # 分析PR
```

### PUT请求

```
PUT /api/users/{id}           # 更新用户
PUT /api/projects/{id}        # 更新项目
PUT /api/reviews/{id}         # 更新审查
```

### DELETE请求

```
DELETE /api/projects/{id}     # 删除项目
DELETE /api/reviews/{id}      # 删除审查
```

## API版本管理

### 当前版本

- **API版本**：v1
- **基础路径**：`/api/v1/`
- **兼容性**：向后兼容

### 版本策略

- 主版本号：重大变更
- 次版本号：功能新增
- 修订版本号：Bug修复

### 弃用策略

- 弃用API保留3个月
- 返回弃用警告头
- 提供迁移指南

## 认证和授权

### 认证方式

- **JWT令牌** - 主要认证方式
- **GitHub OAuth** - 第三方登录
- **API密钥** - 服务间认证

### 认证流程

1. 客户端登录获取令牌
2. 每次请求携带令牌
3. 服务器验证令牌
4. 令牌过期自动刷新

### 权限模型

- **5级RBAC** - ADMIN, MANAGER, REVIEWER, PROGRAMMER, VISITOR
- **资源权限** - 基于资源的访问控制
- **操作权限** - 基于操作的权限控制

## 错误处理

### HTTP状态码

- **200** - 成功
- **201** - 创建成功
- **400** - 请求错误
- **401** - 未授权
- **403** - 禁止访问
- **404** - 资源不存在
- **500** - 服务器错误

### 错误响应格式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

### 常见错误码

- `AUTH_INVALID_TOKEN` - 令牌无效
- `AUTH_TOKEN_EXPIRED` - 令牌过期
- `PERMISSION_DENIED` - 权限不足
- `RESOURCE_NOT_FOUND` - 资源不存在
- `VALIDATION_ERROR` - 验证错误

## 速率限制

### 限制规则

- **默认限制**：100请求/分钟
- **认证用户**：1000请求/分钟
- **API密钥**：10000请求/分钟

### 限制头

- `X-RateLimit-Limit` - 限制数量
- `X-RateLimit-Remaining` - 剩余数量
- `X-RateLimit-Reset` - 重置时间

### 超限处理

- 返回429状态码
- 包含Retry-After头
- 提供限制信息

## 最佳实践

### 客户端使用

1. 使用统一的API客户端
2. 实现错误处理
3. 处理速率限制
4. 缓存响应数据
5. 实现重试逻辑

### 服务端实现

1. 遵循RESTful规范
2. 提供清晰的错误信息
3. 实现认证授权
4. 添加请求验证
5. 实现速率限制

### 安全考虑

1. 使用HTTPS
2. 验证所有输入
3. 实现CSRF保护
4. 限制敏感信息
5. 记录访问日志

## 相关文档

- **[API完整文档](../../docs/api/API_DOCUMENTATION.md)** - 详细API参考
- **[架构文档](ARCHITECTURE.md)** - 系统架构说明
- **[开发者指南](DEVELOPER_GUIDE.md)** - 开发指南
- **[安全文档](../security/INDEX.md)** - 安全相关文档

## API变更记录

### v1.0.0 (2026-03-09)

- 初始API版本发布
- 实现核心API端点
- 完成认证授权
- 实现RBAC权限系统

### v1.1.0 (计划中)

- 新增批量操作接口
- 优化性能查询接口
- 增强错误处理
- 添加更多元数据

---

**最后更新**：2026-03-09
**API版本**：v1.0.0
**文档版本**：v1.0
**维护者**：API开发团队

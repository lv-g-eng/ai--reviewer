# AI Code Review Platform

AI驱动的代码审查平台，提供智能代码分析、架构审查和合规性检查。

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Neo4j 5+

### 安装步骤

1. **克隆仓库**

```bash
git clone <repository-url>
cd ai-code-review-platform
```

2. **配置环境变量**

```bash
# 复制环境变量模板
cp .env.template .env
cp frontend/.env.example frontend/.env.local

# 编辑 .env 文件，填入数据库凭据
# 编辑 frontend/.env.local 文件
```

3. **启动服务**

```bash
# 使用 Docker Compose
docker-compose up -d

# 或手动启动
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

4. **访问应用**

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 默认凭据

系统提供5种角色的测试账号，所有账号的默认密码都是：`Admin123!`

| 角色       | 用户名     | 权限说明             |
| ---------- | ---------- | -------------------- |
| ADMIN      | admin      | 完全系统控制权限     |
| MANAGER    | manager    | 项目监督和ROI管理    |
| REVIEWER   | reviewer   | 代码审查和分析报告   |
| PROGRAMMER | programmer | 创建和管理自己的项目 |
| VISITOR    | visitor    | 只读访问权限         |

⚠️ **安全提示：** 生产环境中请立即修改这些默认密码！

详细的角色权限说明请参考：[RBAC角色文档](docs/RBAC_ROLES.md)

## 主要功能

- ✅ AI 驱动的代码审查
- ✅ Pull Request 自动分析
- ✅ 架构合规性检查
- ✅ 安全漏洞扫描
- ✅ 实时协作
- ✅ GitHub 集成
- ✅ 5级角色权限控制 (RBAC)

## 文档

### 📚 统一文档索引

- **[📖 文档总索引](.monkeycode/docs/INDEX.md)** - 完整的文档导航和索引（推荐从这里开始）
- **[🏗️ 系统架构](.monkeycode/docs/ARCHITECTURE.md)** - 系统架构设计和技术栈
- **[🔧 API接口文档](.monkeycode/docs/INTERFACES.md)** - 统一的API接口索引
- **[💻 开发者指南](.monkeycode/docs/DEVELOPER_GUIDE.md)** - 完整的开发指南和规范

### 🚀 快速开始

- **[快速开始指南](QUICK_START.md)** - Docker快速启动
- **[快速开始（生产）](QUICK_START_PRODUCTION.md)** - 生产环境部署
- **[快速开始（Docker）](QUICK_START_DOCKER.md)** - Docker部署详细说明

### 📖 详细文档

- **[用户指南](docs/USER_GUIDE.md)** - 用户使用手册
- **[部署指南](DEPLOYMENT.md)** - 完整部署流程
- **[运维手册](docs/OPERATIONS_RUNBOOK.md)** - 日常运维操作
- **[RBAC角色说明](docs/RBAC_ROLES.md)** - 5级角色权限体系详解
- **[RBAC迁移指南](docs/RBAC_MIGRATION_GUIDE.md)** - RBAC迁移步骤
- **[API文档](docs/api/API_DOCUMENTATION.md)** - 完整API参考

### 📁 历史文档

- **[文档归档索引](.monkeycode/docs/archive/INDEX.md)** - 历史文档导航
- **[优化总结](PROJECT_OPTIMIZATION_SUMMARY.md)** - 项目优化总览
- **[生产环境迁移](PRODUCTION_MIGRATION_SUMMARY.md)** - 生产环境迁移记录

## 技术栈

**前端:**

- Next.js 14
- React 19
- TypeScript
- TailwindCSS

**后端:**

- FastAPI
- Python 3.11
- PostgreSQL
- Redis
- Neo4j

## 许可证

MIT License

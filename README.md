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
- 用户名: admin@example.com
- 密码: admin123

## 主要功能

- ✅ AI 驱动的代码审查
- ✅ Pull Request 自动分析
- ✅ 架构合规性检查
- ✅ 安全漏洞扫描
- ✅ 实时协作
- ✅ GitHub 集成

## 文档

- [架构文档](docs/ARCHITECTURE.md)
- [用户指南](docs/USER_GUIDE.md)
- [部署指南](docs/DEPLOYMENT_GUIDE.md)
- [API 文档](docs/api/API_DOCUMENTATION.md)

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

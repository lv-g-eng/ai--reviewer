# 🚀 Quick Start Guide

**Time to Running**: 2-3 minutes
**Prerequisites**: Docker Desktop

> 💡 **注意**: 这是为Windows环境优化的Docker部署指南。删除shell脚本，改用PowerShell命令

---

## ⚡ Docker快速启动 (Windows PowerShell)

```powershell
# 1. 检查Docker环境
docker --version

docker-compose --version

# 2. 复制环境变量模板
Copy-Item .env.template .env -Force

# 3. 生成随机密码(可选)
# .env文件已经预生成安全密码，如需重新生成：
# echo "POSTGRES_PASSWORD=\$(openssl rand -hex 16)" > .env
# echo "NEO4J_PASSWORD=\$(openssl rand -hex 16)" >> .env
# echo "REDIS_PASSWORD=\$(openssl rand -hex 16)" >> .env
# echo "JWT_SECRET=\$(openssl rand -hex 32)" >> .env

# 4. 启动完整服务栈
docker-compose up -d

# 5. 等待服务启动完成
Write-Host "⏳ 等待服务启动..."
Start-Sleep -Seconds 30

# 6. 检查服务状态
docker-compose ps

# 7. 运行健康检查
.\setup-check.sh
```

**服务访问地址**:

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- pgAdmin: http://localhost:5050
- Neo4j Browser: http://localhost:7474

**pgAdmin登录**:

- 邮箱: admin@example.com
- 密码: PostgreSQL密码（见.env文件）

---

## 📋 Docker详细部署指南

### 环境要求

- **Docker Desktop** (Windows/macOS) 或 **Docker Engine** (Linux)
- 至少4GB可用内存
- 稳定网络连接

**检查Docker环境**:

```powershell
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version

# 检查Docker是否运行
docker info
```

### 🛠️ Docker部署步骤

#### 第1步：准备环境变量

.env文件已预配置了安全密码，如需要自定义：

```powershell
# 备份现有配置
Copy-Item .env .env.backup -Force

# 从模板创建新配置
Copy-Item .env.template .env -Force

# 编辑.env文件设置自定义密码
notepad .env
```

#### 第2步：启动Docker服务栈

```powershell
# 启动所有服务（支持PowerShell）
docker-compose up -d

# 或分阶段启动（推荐）
docker-compose up -d postgres redis neo4j
docker-compose up -d backend frontend celery-worker celery-beat
```

#### 第3步：验证服务状态

```powershell
# 检查所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs

# 检查特定服务日志
docker-compose logs postgres
docker-compose logs backend
```

#### 第4步：健康检查

```powershell
# 运行自动化健康检查
.\setup-check.sh

# 手动检查后端健康状态
curl http://localhost:8000/health

# 检查前端服务
Start-Process http://localhost:3000
```

#### 第5步：访问应用程序

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050
- **Neo4j Browser**: http://localhost:7474

### 🔧 管理命令

#### 查看服务状态

```powershell
# 查看所有容器状态
docker-compose ps

# 查看资源使用情况
docker stats

# 查看服务日志
docker-compose logs -f
```

#### 服务管理

```powershell
# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 重新构建并启动
docker-compose up -d --build
```

#### 数据管理

```powershell
# 查看数据库容器
docker exec -it ai_review_postgres psql -U postgres -d ai_code_review

# 备份数据卷
docker-compose down
Copy-Item -Path "volumes" -Destination "backup_volumes" -Recurse

docker-compose up -d
```

### 🌐 服务端点详情

| 服务       | 端口 | URL                        | 用途           |
| ---------- | ---- | -------------------------- | -------------- |
| 前端       | 3000 | http://localhost:3000      | 用户界面       |
| 后端       | 8000 | http://localhost:8000      | REST API       |
| API文档    | 8000 | http://localhost:8000/docs | API参考        |
| PostgreSQL | 5432 | -                          | 主数据库       |
| pgAdmin    | 5050 | http://localhost:5050      | 数据库管理     |
| Neo4j      | 7474 | http://localhost:7474      | 图数据库浏览器 |
| Redis      | 6379 | -                          | 缓存服务       |

---

## 🔑 Docker环境变量配置

### Windows PowerShell兼容的环境变量设置

### Docker环境变量配置 (.env)

.env文件已预配置了安全密码和Docker容器网络设置：

```env
# Docker容器网络配置 - 使用服务名称而非localhost
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ai_code_review
POSTGRES_USER=postgres
POSTGRES_PASSWORD=fb57f80adf003595

NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=4e06834ec994c162

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=b67dc9a7b467f09d

JWT_SECRET=f34f50c1350f6275ad5c2672a978d815

# Docker网络设置
BACKEND_HOST=backend
BACKEND_PORT=8000
FRONTEND_HOST=frontend
FRONTEND_PORT=3000
```

### 前端配置 (.env.local)

```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=local_dev_secret_minimum_32_characters_here
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000
```

### 🛡️ Windows兼容的安全配置

**Windows PowerShell中重新生成安全密码**:

```powershell
# 创建新的.env文件
Remove-Item .env -Force
Copy-Item .env.template .env -Force

# 生成安全密码
Write-Host "=== 生成安全密码 ==="
Add-Content .env "POSTGRES_PASSWORD=\$(openssl rand -hex 16)"
Add-Content .env "NEO4J_PASSWORD=\$(openssl rand -hex 16)"
Add-Content .env "REDIS_PASSWORD=\$(openssl rand -hex 16)"
Add-Content .env "JWT_SECRET=\$(openssl rand -hex 32)"

Write-Host "✅ 安全密码已生成"
```

**如果openssl不可用，使用PowerShell内置方法**:

```powershell
# 使用PowerShell内置随机数生成器
function Get-RandomHex {
    param([int]$Length)
    -join ((48..57) + (97..102) | Get-Random -Count $Length | ForEach-Object {[char]$_})
}

# 更新.env文件
Set-Content .env "POSTGRES_PASSWORD=\$(Get-RandomHex 32)"
Add-Content .env "NEO4J_PASSWORD=\$(Get-RandomHex 32)"
Add-Content .env "REDIS_PASSWORD=\$(Get-RandomHex 32)"
Add-Content .env "JWT_SECRET=\$(Get-RandomHex 64)"
```

**重要**: .env文件包含敏感信息，请确保：

- ❌ 不提交到版本控制
- ✅ 定期轮换密码
- ✅ 使用不同环境的不同配置

---

## ✅ 验证安装

```powershell
# 检查服务状态
docker-compose ps

# 检查后端健康状态
Invoke-WebRequest http://localhost:8000/health

# 打开API文档
Start-Process http://localhost:8000/docs

# 打开前端应用
Start-Process http://localhost:3000

# 运行自动化健康检查
.\setup-check.sh
```

### Windows兼容的curl替代方案

如果你的PowerShell没有Invoke-WebRequest，可以使用：

```powershell
# 方法1：使用浏览器测试
Start-Process http://localhost:8000/health

# 方法2：使用PowerShell 5.1+
try {
    Invoke-WebRequest http://localhost:8000/health
    Write-Host "✅ 后端服务健康"
} catch {
    Write-Host "❌ 后端服务异常"
}
```

---

## ⏹️ 停止服务

```powershell
# 停止并清理所有容器
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 仅停止服务但不删除容器
docker-compose stop

# 强制停止所有服务（紧急情况）
docker-compose down --remove-orphans
```

---

## 🚨 Troubleshooting

### Python 3.13 Compatibility Issue

**Error**: `asyncpg` fails to build with compilation errors

**Solution**: Use Python 3.11 or 3.12

```bash
# Install Python 3.11 or 3.12 from python.org
# Then create venv with correct version:
py -3.11 -m venv backend/venv
backend\venv\Scripts\activate
pip install --no-cache-dir -r backend/requirements.txt
```

See [backend/INSTALL_FIX.md](backend/INSTALL_FIX.md) for detailed solutions.

### Backend Won't Start

```bash
# Check port 8000 is not in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Check logs
cd backend
tail -f app.log

# Verify database connection
docker-compose ps postgres
```

### Frontend Can't Connect to Backend

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check environment variables
cat frontend/.env.local

# Check CORS settings in backend
```

### Database Connection Failed

```bash
# Check services are running
docker-compose ps

# Restart services
docker-compose restart postgres redis neo4j

# Check logs
docker-compose logs postgres
```

### Tests Failing

```bash
# Frontend
cd frontend
rm -rf node_modules .next
npm install
npm test

# Backend
cd backend
pip install -r requirements.txt
pytest --cache-clear
```

### Clean Orphan Containers

If you see warnings about orphan containers:

```bash
docker-compose down --remove-orphans
docker-compose up -d postgres redis neo4j
```

---

## 📚 Next Steps

### For Developers

1. **Read the docs**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
2. **Explore the API**: http://localhost:8000/docs
3. **Run tests**: `npm test` (frontend) or `pytest` (backend)
4. **Check code quality**: `npm run lint`

### For Project Managers

1. **Review architecture**: [README.md](README.md#architecture)
2. **Check project status**: [README.md](README.md#project-status)
3. **View documentation**: [docs/README.md](docs/README.md)

### Common Tasks

- **Add a feature**: See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **Run tests**: See [Testing](#testing) section
- **Deploy**: See [README.md](README.md#deployment)
- **Troubleshoot**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📞 Getting Help

1. **Check documentation**: [docs/README.md](docs/README.md)
2. **Common issues**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Quick reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. **Create an issue**: GitHub Issues

---

## ⏱️ Performance Notes

- Infrastructure starts in ~15 seconds
- Backend starts in ~15-20 seconds
- Frontend starts in ~10-15 seconds
- **Total time to running**: ~45-60 seconds

**Optimization Tips**:

- Use `--workers 1` for faster backend startup (increase for production)
- Use `--log-level warning` to reduce startup overhead
- Keep Docker Desktop running for faster container starts

---

## 📦 数据迁移指南

### 从本地数据库迁移到 Docker

#### PostgreSQL 数据迁移

```powershell
# 1. 备份本地PostgreSQL数据库
docker exec -it ai_review_postgres pg_dump -U postgres ai_code_review > backup_postgres_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# 2. 恢复数据到Docker容器
docker exec -i ai_review_postgres psql -U postgres -d ai_code_review < backup_file.sql

# 3. 验证迁移
docker exec ai_review_postgres psql -U postgres -d ai_code_review -c "\dt"
```

**使用 pgAdmin 迁移**:
1. 打开 pgAdmin (http://localhost:5050)
2. 连接本地PostgreSQL和Docker PostgreSQL
3. 使用 "Backup/Restore" 功能导出导入

#### Neo4j 数据迁移

```powershell
# 1. 导出本地Neo4j数据
docker exec -it ai_review_neo4j neo4j-admin database dump neo4j --to-path=/logs/

# 2. 复制备份文件
docker cp ai_review_neo4j:/logs/neo4j.dump ./

# 3. 导入到新容器
docker cp ./neo4j.dump ai_review_neo4j:/logs/
docker exec -it ai_review_neo4j neo4j-admin database load neo4j --from=/logs/neo4j.dump --overwrite-destination=true
```

**使用 Neo4j Browser 导出/导入**:
1. 访问 http://localhost:7474
2. 使用 `:export all to file` 导出数据
3. 在新环境中使用 `:source file` 导入

---

## ✅ 验证测试

### 自动化连接测试

```powershell
# 运行Docker网络连接测试
cd scripts
python test_docker_connections.py

# 运行数据库连接测试
python test_db_connections.py
```

### 手动验证步骤

```powershell
# 1. 检查所有服务状态
docker-compose ps

# 2. 检查健康状态
curl http://localhost:8000/health

# 3. 检查PostgreSQL
docker exec -it ai_review_postgres psql -U postgres -d ai_code_review -c "SELECT 1;"

# 4. 检查Neo4j
docker exec ai_review_neo4j cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "RETURN 1;"

# 5. 检查Redis
docker exec ai_review_redis redis-cli -a "${REDIS_PASSWORD}" ping
```

### 预期输出

| 服务 | 验证命令 | 预期结果 |
| ---- | -------- | -------- |
| PostgreSQL | `pg_isready -U postgres` | "accepting connections" |
| Neo4j | `cypher-shell "RETURN 1;"` | "1 row" |
| Redis | `redis-cli ping` | "PONG" |
| Backend | `curl /health` | `{"status":"healthy"}` |

---

## 🔄 错误处理与重试机制

### 后端自动重试配置

后端服务已配置自动重试机制，连接数据库时：

```python
# backend/app/core/database.py 中的重试逻辑
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30))
async def connect_to_database():
    # 数据库连接逻辑
    pass
```

**重试策略**:
- 最多重试 5 次
- 指数退避: 2秒 -> 4秒 -> 8秒 -> 16秒 -> 30秒
- 总计等待时间: 约 60 秒

### Docker 服务依赖健康检查

```yaml
# docker-compose.yml 中的健康检查依赖
services:
  backend:
    depends_on:
      postgres:
        condition: service_healthy  # 等待PostgreSQL健康
      redis:
        condition: service_healthy  # 等待Redis健康
      neo4j:
        condition: service_healthy  # 等待Neo4j健康
```

### 常见错误处理

#### 1. 数据库连接超时

```powershell
# 解决: 等待服务完全启动
Start-Sleep -Seconds 30

# 重启数据库服务
docker-compose restart postgres redis neo4j
```

#### 2. 端口冲突

```powershell
# 检查占用端口的进程
netstat -ano | findstr :5432  # PostgreSQL
netstat -ano | findstr :7474   # Neo4j
netstat -ano | findstr :6379   # Redis

# 停止冲突进程或修改docker-compose.yml中的端口映射
```

#### 3. 内存不足

```powershell
# 查看容器资源使用
docker stats

# 减少服务资源限制 (修改docker-compose.yml)
# 或增加Docker Desktop内存分配
```

#### 4. 网络连接失败

```powershell
# 检查Docker网络
docker network inspect ai_review_network

# 重建网络
docker-compose down
docker network prune
docker-compose up -d
```

### 监控与告警

```powershell
# 查看服务日志
docker-compose logs -f --tail=100

# 查看错误日志
docker-compose logs | Select-String "ERROR"

# 实时监控
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

---

## 🎯 快速故障排查清单

- [ ] Docker daemon 正在运行
- [ ] 所有端口未被占用
- [ ] `.env` 文件已正确配置
- [ ] 所有服务状态为 "healthy" 或 "running"
- [ ] 网络 `ai_review_network` 存在且正常
- [ ] 数据卷已正确挂载
- [ ] 防火墙允许本地连接

---

**🎉 配置完成！现在可以开始使用 Docker 化的 AI Code Review Platform。**

如有问题，请查看 [故障排查](#troubleshooting) 部分或运行:

```powershell
.\setup-check.sh
```

# AI Code Review Platform - 故障排查指南

本文档提供常见问题的诊断和解决方案。

## 目录

- [快速诊断](#快速诊断)
- [后端问题](#后端问题)
- [前端问题](#前端问题)
- [数据库问题](#数据库问题)
- [认证和授权问题](#认证和授权问题)
- [性能问题](#性能问题)
- [部署问题](#部署问题)
- [日志分析](#日志分析)

## 快速诊断

### 健康检查

```bash
# 检查所有服务状态
docker-compose ps

# 检查服务日志
docker-compose logs --tail=100 backend
docker-compose logs --tail=100 frontend
docker-compose logs --tail=100 postgres
docker-compose logs --tail=100 redis
```

### 端口检查

```bash
# 检查端口是否被占用
netstat -tuln | grep -E ':(3000|8000|5432|6379|7474)'

# 或使用ss命令
ss -tuln | grep -E ':(3000|8000|5432|6379|7474)'
```

### 服务连通性

```bash
# 从后端容器检查数据库连接
docker-compose exec backend python -c "
from app.database.postgresql import get_db
import asyncio
async def test():
    try:
        async for db in get_db():
            print('Database connection successful')
            break
    except Exception as e:
        print(f'Database connection failed: {e}')
asyncio.run(test())
"
```

## 后端问题

### 服务无法启动

#### 症状

- 后端容器反复重启
- 访问`http://localhost:8000`无响应

#### 诊断步骤

1. **检查容器状态**

   ```bash
   docker-compose ps backend
   ```

2. **查看详细日志**

   ```bash
   docker-compose logs backend --tail=200
   ```

3. **检查环境变量**
   ```bash
   docker-compose config | grep -A 20 "backend:"
   ```

#### 常见原因和解决方案

**原因1: 数据库连接失败**

```bash
# 检查PostgreSQL是否运行
docker-compose ps postgres

# 重启数据库
docker-compose restart postgres

# 等待数据库就绪
docker-compose exec postgres pg_isready -U postgres
```

**原因2: 依赖安装失败**

```bash
# 重新构建镜像
docker-compose build --no-cache backend

# 检查requirements.txt
cat backend/requirements.txt
```

**原因3: 端口冲突**

```bash
# 查找占用8000端口的进程
lsof -i :8000

# 或使用netstat
netstat -tuln | grep :8000

# 停止占用端口的进程
kill -9 <PID>
```

### API请求失败

#### 症状

- 前端无法调用后端API
- 返回500错误

#### 诊断步骤

1. **检查API日志**

   ```bash
   docker-compose logs backend --tail=100 | grep -i error
   ```

2. **测试API端点**

   ```bash
   # 测试健康检查
   curl http://localhost:8000/health

   # 测试API文档
   curl http://localhost:8000/docs
   ```

3. **检查数据库连接**
   ```bash
   docker-compose exec backend python -c "
   from app.database.postgresql import engine
   print('Database URL:', engine.url)
   "
   ```

#### 常见原因和解决方案

**原因1: 数据库连接池耗尽**

```bash
# 检查活跃连接
docker-compose exec postgres psql -U postgres -d ai_code_review -c "
SELECT count(*) FROM pg_stat_activity;
"

# 增加连接池大小
# 编辑 .env 文件
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=20

# 重启服务
docker-compose restart backend
```

**原因2: Redis连接失败**

```bash
# 检查Redis状态
docker-compose ps redis

# 测试Redis连接
docker-compose exec redis redis-cli ping

# 重启Redis
docker-compose restart redis
```

**原因3: 环境变量错误**

```bash
# 检查关键环境变量
docker-compose exec backend env | grep -E 'DATABASE_URL|REDIS_URL|NEO4J_URI'

# 验证环境变量格式
```

### Celery任务不执行

#### 症状

- 异步任务没有被执行
- 任务状态一直是PENDING

#### 诊断步骤

1. **检查Celery worker状态**

   ```bash
   docker-compose ps celery_worker
   docker-compose logs celery_worker --tail=50
   ```

2. **检查Celery beat状态**

   ```bash
   docker-compose ps celery_beat
   docker-compose logs celery_beat --tail=50
   ```

3. **检查Redis连接**
   ```bash
   # 检查Celery使用的Redis keys
   docker-compose exec redis redis-cli
   KEYS celery*
   ```

#### 常见原因和解决方案

**原因1: Celery worker没有启动**

```bash
# 重启Celery worker
docker-compose restart celery_worker

# 检查worker日志
docker-compose logs celery_worker -f
```

**原因2: 任务注册失败**

```python
# 检查任务是否正确注册
from app.celery_config import app

# 列出所有注册的任务
print(app.tasks.keys())
```

**原因3: 任务执行超时**

```bash
# 增加任务超时时间
# 编辑 .env 文件
CELERY_TASK_TIME_LIMIT=7200
CELERY_TASK_SOFT_TIME_LIMIT=6600

# 重启Celery worker
docker-compose restart celery_worker
```

## 前端问题

### 页面无法加载

#### 症状

- 浏览器显示空白页
- 控制台有错误

#### 诊断步骤

1. **检查前端容器状态**

   ```bash
   docker-compose ps frontend
   ```

2. **查看前端日志**

   ```bash
   docker-compose logs frontend --tail=100
   ```

3. **打开浏览器开发者工具**
   - 查看Console标签的错误信息
   - 查看Network标签的请求状态

#### 常见原因和解决方案

**原因1: 依赖安装失败**

```bash
# 重新构建镜像
docker-compose build --no-cache frontend

# 清理node_modules
docker-compose exec frontend rm -rf node_modules
docker-compose exec frontend npm install
```

**原因2: 端口冲突**

```bash
# 查找占用3000端口的进程
lsof -i :3000

# 停止占用端口的进程
kill -9 <PID>

# 或修改端口
# 编辑 docker-compose.yml
ports:
  - '3001:3000'  # 使用3001端口
```

**原因3: 环境变量缺失**

```bash
# 检查前端环境变量
docker-compose exec frontend env | grep NEXT_PUBLIC

# 编辑 frontend/.env.local 添加缺失的变量
```

### API请求失败

#### 症状

- 前端无法调用后端API
- 显示网络错误

#### 诊断步骤

1. **打开浏览器开发者工具**
   - Network标签查看请求详情
   - 检查请求URL是否正确
   - 检查响应状态码

2. **检查CORS配置**

   ```python
   # 后端 main.py 检查CORS设置
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **测试API端点**

   ```bash
   # 直接测试后端API
   curl http://localhost:8000/api/v1/health

   # 测试跨域请求
   curl -H "Origin: http://localhost:3000" \
        http://localhost:8000/api/v1/health
   ```

#### 常见原因和解决方案

**原因1: CORS配置错误**

```python
# 更新CORS允许的源
allow_origins=["http://localhost:3000", "http://localhost:3001"]
```

**原因2: API地址配置错误**

```javascript
// 检查前端API地址配置
// frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**原因3: 认证令牌过期**

```bash
# 清除浏览器存储
localStorage.clear()
sessionStorage.clear()

# 重新登录
```

## 数据库问题

### PostgreSQL连接失败

#### 症状

- 无法连接到数据库
- 数据库查询失败

#### 诊断步骤

1. **检查PostgreSQL状态**

   ```bash
   docker-compose ps postgres
   docker-compose logs postgres --tail=50
   ```

2. **测试数据库连接**

   ```bash
   docker-compose exec postgres psql -U postgres -d ai_code_review -c "SELECT version();"
   ```

3. **检查数据库日志**
   ```bash
   docker-compose exec postgres tail -f /var/log/postgresql/postgresql-16-main.log
   ```

#### 常见原因和解决方案

**原因1: 数据库未就绪**

```bash
# 等待数据库启动完成
docker-compose exec postgres pg_isready -U postgres

# 重启数据库
docker-compose restart postgres
```

**原因2: 数据损坏**

```bash
# 重建数据库（谨慎操作！）
docker-compose down
docker volume rm ai_review_postgres_data
docker-compose up -d postgres
```

**原因3: 连接数过多**

```bash
# 查看活跃连接
docker-compose exec postgres psql -U postgres -d ai_code_review -c "
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
"

# 终止空闲连接
docker-compose exec postgres psql -U postgres -d ai_code_review -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND pid <> pg_backend_pid();
"
```

### Redis连接失败

#### 症状

- 缓存操作失败
- 会话管理失效

#### 诊断步骤

1. **检查Redis状态**

   ```bash
   docker-compose ps redis
   docker-compose logs redis --tail=50
   ```

2. **测试Redis连接**

   ```bash
   docker-compose exec redis redis-cli ping
   # 应该返回 PONG
   ```

3. **检查Redis内存使用**
   ```bash
   docker-compose exec redis redis-cli INFO memory
   ```

#### 常见原因和解决方案

**原因1: Redis内存不足**

```bash
# 清空所有keys（谨慎操作！）
docker-compose exec redis redis-cli FLUSHALL

# 或增加Redis内存限制
# 编辑 docker-compose.yml
command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

**原因2: Redis持久化问题**

```bash
# 检查持久化状态
docker-compose exec redis redis-cli INFO persistence

# 手动触发快照
docker-compose exec redis redis-cli SAVE
```

### Neo4j连接失败

#### 症状

- 图数据库操作失败
- 依赖关系查询失败

#### 诊断步骤

1. **检查Neo4j状态**

   ```bash
   docker-compose ps neo4j
   docker-compose logs neo4j --tail=50
   ```

2. **测试Neo4j连接**

   ```bash
   curl http://localhost:7474
   ```

3. **检查Neo4j浏览器**
   ```bash
   # 访问 http://localhost:7474
   # 默认用户名: neo4j
   # 默认密码: 在 .env 中配置
   ```

#### 常见原因和解决方案

**原因1: 认证失败**

```bash
# 重置Neo4j密码
docker-compose exec neo4j neo4j-admin set-initial-password new_password

# 更新 .env 文件中的 NEO4J_PASSWORD
```

**原因2: 内存不足**

```bash
# 增加Neo4j内存
# 编辑 docker-compose.yml
environment:
  NEO4J_server_memory_heap_max__size: 2G
  NEO4J_server_memory_pagecache_size: 2G
```

## 认证和授权问题

### 登录失败

#### 症状

- 无法登录
- 显示"账户锁定"错误

#### 诊断步骤

1. **检查账户锁定状态**

   ```python
   from app.services.account_lockout_service import AccountLockoutService
   from app.services.redis_cache_service import get_cache_service

   async def check_lockout(user_id):
       cache = await get_cache_service()
       lockout_service = AccountLockoutService(cache.redis)
       is_locked, unlock_time = await lockout_service.is_account_locked(user_id)
       if is_locked:
           print(f"Account locked until: {unlock_time}")
       return is_locked
   ```

2. **查看认证日志**
   ```bash
   docker-compose logs backend | grep -i "auth\|login"
   ```

#### 常见原因和解决方案

**原因1: 账户被锁定**

```bash
# 手动解锁账户（需要管理员权限）
# 创建管理脚本
python scripts/unlock_account.py --user-id 123
```

**原因2: 密码错误**

```bash
# 重置用户密码
python scripts/reset_password.py --email user@example.com --new-password newpass123
```

**原因3: 账户未激活**

```python
# 激活账户
UPDATE users SET is_active = true WHERE email = 'user@example.com';
```

### 权限不足

#### 症状

- 无法访问某些资源
- 显示"权限不足"错误

#### 诊断步骤

1. **检查用户角色**

   ```python
   from app.database.postgresql import get_db
   from sqlalchemy import select
   from app.models import User

   async def get_user_role(user_id):
       async for db in get_db():
           result = await db.execute(select(User).where(User.id == user_id))
           user = result.scalar_one()
           print(f"User role: {user.role}")
           return user.role
   ```

2. **检查RBAC配置**
   ```bash
   # 查看权限配置
   cat backend/app/core/permissions.py
   ```

#### 常见原因和解决方案

**原因1: 角色权限配置错误**

```python
# 更新角色权限
# 编辑 backend/app/core/permissions.py
```

**原因2: 权限缓存问题**

```bash
# 清除权限缓存
docker-compose exec redis redis-cli KEYS "permission:*" | xargs redis-cli DEL
```

## 性能问题

### 响应时间慢

#### 诊断步骤

1. **检查API响应时间**

   ```bash
   # 使用curl测量响应时间
   time curl http://localhost:8000/api/v1/projects
   ```

2. **查看慢查询日志**

   ```bash
   docker-compose logs backend | grep "slow query"
   ```

3. **检查系统资源使用**
   ```bash
   docker stats
   ```

#### 优化建议

**数据库查询优化**

```python
# 添加索引
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_reviews_project_id ON reviews(project_id);

# 使用查询优化
# 使用 select() 而不是 query()
# 使用 join() 减少查询次数
# 使用分页避免返回大量数据
```

**缓存优化**

```python
# 增加Redis缓存命中率
# 分析缓存键
docker-compose exec redis redis-cli KEYS "cache:*" | wc -l

# 清理过期缓存
docker-compose exec redis redis-cli --scan --pattern "cache:*" | xargs redis-cli DEL
```

**前端性能优化**

```javascript
// 使用代码分割
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// 使用React.memo避免不必要的重渲染
const MyComponent = React.memo(function MyComponent(props) {
  // ...
});

// 使用虚拟滚动处理大列表
import { FixedSizeList } from 'react-window';
```

### 内存使用过高

#### 诊断步骤

1. **检查容器内存使用**

   ```bash
   docker stats --no-stream
   ```

2. **查看Python内存使用**

   ```python
   import psutil
   import os

   process = psutil.Process(os.getpid())
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

3. **查看Redis内存使用**
   ```bash
   docker-compose exec redis redis-cli INFO memory
   ```

#### 优化建议

**清理未使用的资源**

```python
# 定期清理过期会话
await cache.delete_expired_sessions()

# 清理旧的分析结果
await cleanup_old_analyses(days=30)
```

**优化内存使用**

```python
# 使用生成器而非列表
def process_large_data():
    for item in data:
        yield process_item(item)

# 使用__slots__减少内存占用
class User:
    __slots__ = ['id', 'name', 'email']
```

## 部署问题

### Docker构建失败

#### 症状

- Docker构建失败
- 镜像无法创建

#### 诊断步骤

1. **查看构建日志**

   ```bash
   docker-compose build backend 2>&1 | tee build.log
   ```

2. **检查Dockerfile语法**

   ```bash
   docker build --no-cache -t test-image ./backend
   ```

3. **检查磁盘空间**
   ```bash
   df -h
   docker system df
   ```

#### 常见原因和解决方案

**原因1: 磁盘空间不足**

```bash
# 清理未使用的Docker资源
docker system prune -a

# 清理构建缓存
docker builder prune -a
```

**原因2: 网络问题**

```bash
# 使用国内镜像加速
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
}

# 重启Docker
sudo systemctl restart docker
```

**原因3: 依赖下载失败**

```bash
# 使用代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

docker-compose build
```

### Kubernetes部署失败

#### 症状

- Pod无法启动
- 服务无法访问

#### 诊断步骤

1. **检查Pod状态**

   ```bash
   kubectl get pods
   kubectl describe pod <pod-name>
   ```

2. **查看Pod日志**

   ```bash
   kubectl logs <pod-name>
   kubectl logs -f <pod-name>  # 实时查看
   ```

3. **检查Service状态**
   ```bash
   kubectl get services
   kubectl describe service <service-name>
   ```

#### 常见原因和解决方案

**原因1: 镜像拉取失败**

```bash
# 检查镜像是否存在
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'

# 手动拉取镜像
docker pull <image-name>
```

**原因2: 资源限制**

```bash
# 检查资源使用
kubectl top nodes
kubectl top pods

# 调整资源限制
# 编辑 deployment.yaml
resources:
  limits:
    memory: "2Gi"
    cpu: "2"
  requests:
    memory: "1Gi"
    cpu: "1"
```

**原因3: 配置错误**

```bash
# 验证配置文件
kubectl apply --dry-run=client -f deployment.yaml

# 检查配置
kubectl get configmaps
kubectl get secrets
```

## 日志分析

### 查看实时日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近N行日志
docker-compose logs --tail=100 backend
```

### 日志级别配置

```python
# 编辑 .env 文件
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 重启服务
docker-compose restart backend
```

### 结构化日志

```python
import structlog

logger = structlog.get_logger()

logger.info("User login", user_id=123, ip="192.168.1.1")
logger.error("Database error", error=str(e), query="SELECT * FROM users")
```

## 获取帮助

如果以上方法无法解决问题：

1. **查看文档**
   - [API文档](.monkeycode/docs/INTERFACES.md)
   - [开发者指南](.monkeycode/docs/DEVELOPER_GUIDE.md)
   - [部署指南](DEPLOYMENT.md)

2. **检查Issue**
   - [GitHub Issues](https://github.com/your-org/ai-code-review-platform/issues)

3. **创建新Issue**
   - 提供详细的错误信息
   - 包含复现步骤
   - 附上相关日志

---

**最后更新**: 2026-03-09
**维护者**: 运维团队

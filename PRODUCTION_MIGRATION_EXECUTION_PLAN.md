# 生产化迁移执行计划

**项目**: AI Code Review Platform  
**目标**: 从开发阶段完全迁移到生产环境  
**估计工作量**: 40-60 小时  
**执行人员**: DevOps、后端、前端、QA 团队

---

## Phase 1: 代码审查和清理 (8-12 小时)

### 任务 1.1: 移除调试代码和 Print 语句

#### 文件 1: `backend/app/main.py`

**修改点**:

- 第 49 行: `print("🧪 Testing mode...")` → 使用 logger
- 第 65 行: `print(f"⚠️  PostgreSQL not available...")` → 使用 logger
- 第 72 行: `print(f"⚠️  Neo4j not available...")` → 使用 logger
- 第 81 行: `print("🧪 Testing mode...")` → 使用 logger
- 第 90-103 行: 所有 print() 调用替换为 logger

**修改策略**:

```python
import logging

logger = logging.getLogger(__name__)

# 替换
logger.info("Testing mode: Skipping startup validation")
logger.warning("PostgreSQL not available: %s", str(e))
logger.info("Checking for pending migrations...")
logger.info("Database is up to date")
logger.error("Migration errors: %s", errors)
```

#### 文件 2: `backend/app/tasks/__init__.py`

**修改点**:

- 第 114 行: `print(f"Error parsing...")` → logger.error()
- 第 256-258 行: `debug_task()` 函数 → 移除调试任务

#### 文件 3: `backend/app/tasks/pull_request_analysis.py`

**修改点**:

- 第 171 行: `print(f"✓ Parsed...")` → logger.info()
- 第 175 行: `print(f"⚠️  Error parsing...")` → logger.error()
- 第 207 行: `print(f"❌ Error parsing...")` → logger.error()
- 第 324 行: `print(f"✓ Built graph...")` → logger.info()
- 第 333 行: `print(f"❌ Error building...")` → logger.error()

#### 文件 4: `backend/app/utils/jwt.py`

**修改点**:

- 第 227 行: `print()` 移除或改为 logger
- 第 248 行: `print()` 移除或改为 logger

#### 文件 5: `backend/app/utils/password.py`

**修改点**:

- 第 62 行: 确保调试信息仅在 logger.debug() 中
- 第 93 行: 错误类型仅记录在日志中

### 任务 1.2: 删除测试文件和临时脚本

**要删除的文件**:

```
backend/test_db.py
backend/test_db_conn.py
backend/test_psycopg_conn.py
backend/test_connection.py
backend/test_import.py
backend/debug_imports.py
backend/debug_imports_v2.py
backend/create_tables.py → 移动到 scripts/setup_initial_tables.py
backend/create_test_user.py → 移动到 scripts/create_test_user.py
backend/summarize_collection_errors.py → 删除
backend/read_log.py → 删除
```

**操作**:

```bash
# 备份后删除
mv backend/create_tables.py scripts/setup_initial_tables.py
mv backend/create_test_user.py scripts/create_test_user.py
rm backend/test_*.py
rm backend/debug_*.py
rm backend/summarize_collection_errors.py
```

### 任务 1.3: 清理日志和临时输出文件

**要删除的文件**:

```
backend/app.log
backend/collection_errors.log
backend/import_error.log
backend/test_auth_error.log
backend/test_error.log
backend/test_failures*.log
backend/test_full_error.log
backend/test_long_error.log
backend/test_traceback.log
```

**验证 .gitignore**:

```
# 添加到 .gitignore
*.log
test_*.txt
test_*.log
failures*.txt
errors.json
coverage.json
```

### 任务 1.4: 禁用生产环境的 API 文档

#### 文件: `backend/app/main.py` (第 240-250 行)

**修改前**:

```python
app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
)
```

**修改后**:

```python
# 在生产环境禁用 API 文档
if settings.ENVIRONMENT == "production":
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    app = FastAPI(
        docs_url="/docs",
        redoc_url="/redoc",
    )
```

---

## Phase 2: 环境配置迁移 (6-8 小时)

### 任务 2.1: 创建生产环境配置模板

#### 文件: `backend/.env.production`

**重点修改**:

1. **调试标记**:

```dotenv
# 修改前
DEBUG=true
LOG_LEVEL=DEBUG

# 修改后
DEBUG=false
LOG_LEVEL=WARNING
```

2. **数据库配置** (使用 AWS Secrets):

```dotenv
# 修改前
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=postgres
NEO4J_PASSWORD=neo4j_dev_password

# 修改后
POSTGRES_HOST=${AWS_SECRET:production/database/postgres_host}
POSTGRES_PASSWORD=${AWS_SECRET:production/database/postgres_password}
NEO4J_PASSWORD=${AWS_SECRET:production/database/neo4j_password}
```

3. **密钥配置** (使用 AWS Secrets):

```dotenv
# 修改前
SECRET_KEY=dev_secret_key_change_in_production
JWT_SECRET=dev_jwt_secret_change_in_production

# 修改后
SECRET_KEY=${AWS_SECRET:production/app/secret_key}
JWT_SECRET=${AWS_SECRET:production/app/jwt_secret}
```

4. **性能参数**:

```dotenv
# 修改前
WORKERS=2
CELERY_WORKER_CONCURRENCY=2
DB_POOL_SIZE=5

# 修改后
WORKERS=8
CELERY_WORKER_CONCURRENCY=8
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

5. **安全性**:

```dotenv
# 修改前
SSL_ENABLED=false
CORS_ORIGINS=*

# 修改后
SSL_ENABLED=true
CORS_ORIGINS=https://app.example.com,https://www.example.com
RATE_LIMIT_PER_MINUTE=200
```

#### 文件: `frontend/.env.production`

**重点修改**:

1. **API 端点**:

```dotenv
# 修改前
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# 修改后
NEXT_PUBLIC_API_URL=https://api.example.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.example.com/ws
```

2. **调试标记**:

```dotenv
# 修改前
NEXT_PUBLIC_ENABLE_DEBUG_MODE=true

# 修改后
NEXT_PUBLIC_ENABLE_DEBUG_MODE=false
```

3. **认证**:

```dotenv
NEXTAUTH_URL=https://app.example.com
NEXTAUTH_SECRET=${AWS_SECRET:production/frontend/nextauth_secret}
```

### 任务 2.2: 更新 Docker Compose 生产配置

#### 文件: `docker-compose.prod.yml`

**修改点**:

1. **PostgreSQL 内存优化** (第 ~15 行):

```yaml
# 修改前
POSTGRES_SHARED_BUFFERS: 256MB
POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
POSTGRES_WORK_MEM: 64MB

# 修改后
POSTGRES_SHARED_BUFFERS: 2GB
POSTGRES_EFFECTIVE_CACHE_SIZE: 8GB
POSTGRES_WORK_MEM: 256MB
POSTGRES_MAX_CONNECTIONS: 200
```

2. **Redis 配置** (第 ~30 行):

```yaml
# 修改前
command: redis-server --maxmemory 512mb

# 修改后
command: redis-server --maxmemory 4gb --maxmemory-policy allkeys-lru --appendonly yes
```

3. **Neo4j 内存** (第 ~45 行):

```yaml
# 修改前
NEO4J_dbms_memory_heap_max__size: 2G

# 修改后
NEO4J_dbms_memory_heap_max__size: 4G
NEO4J_dbms_memory_pagecache_size: 2G
```

### 任务 2.3: 验证环境变量安全

**检查清单**:

- [ ] 没有硬编码的 API 密钥
- [ ] 没有明文密码
- [ ] 所有敏感值使用 AWS Secrets 引用
- [ ] 生产 .env 文件在 .gitignore 中
- [ ] 没有测试凭证

---

## Phase 3: 安全加固 (10-14 小时)

### 任务 3.1: 禁用默认测试账户

#### 创建迁移脚本: `backend/alembic/versions/0XX_disable_default_test_accounts.py`

**操作**:

```python
def upgrade():
    # 删除或禁用默认测试账户
    op.execute("""
        DELETE FROM users WHERE username IN
        ('admin', 'manager', 'reviewer', 'programmer', 'visitor');
    """)

def downgrade():
    # 如需回滚，重新创建（仅用于开发）
    pass
```

### 任务 3.2: 启用 CORS 安全头

#### 文件: `backend/app/middleware/cors_middleware.py`

**修改**:

```python
# 添加 production_origins 配置
production_origins = [
    "https://app.example.com",
    "https://www.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 任务 3.3: 添加安全响应头

#### 文件: 创建 `backend/app/middleware/security_headers.py`

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 任务 3.4: 配置审计日志

#### 文件: 验证 `backend/app/core/audit_logging.py`

**验证**:

- 所有用户操作都被记录
- 敏感数据被掩蔽
- 日志存储在安全位置
- 激活审计日志导出到 CloudWatch

### 任务 3.5: 启用数据加密

#### 文件: `backend/app/core/encryption.py`

**验证**:

```python
# 使用 AWS KMS 密钥
encryption_key = get_kms_key()
cipher_suite = Fernet(encryption_key)
```

---

## Phase 4: 性能优化 (6-8 小时)

### 任务 4.1: 数据库连接池优化

#### 文件: `backend/app/database/postgresql.py`

**修改**:

```python
# 生产环境连接池配置
pool_size = 20  # 开发: 5
max_overflow = 10  # 开发: 5
pool_recycle = 3600
pool_pre_ping = True  # 验证连接有效性
```

### 任务 4.2: 缓存策略优化

#### 文件: `backend/app/services/cache_service.py`

**添加**:

```python
# 生产级缓存策略
CACHE_TTL_SHORT = 300  # 5 分钟
CACHE_TTL_MEDIUM = 3600  # 1 小时
CACHE_TTL_LONG = 86400  # 1 天

# 缓存键压缩策略
redis_client.config_set('maxmemory-policy', 'allkeys-lru')
```

### 任务 4.3: 异步任务优化

#### 文件: `backend/app/celery_config.py`

**修改**:

```python
# 生产 Celery 配置
CELERY_WORKER_CONCURRENCY = 8  # 开发: 2
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TIME_LIMIT = 1800  # 30 分钟
CELERY_TASK_SOFT_TIME_LIMIT = 1650
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
```

### 任务 4.4: 查询优化

#### 文件: `backend/app/database/queries.py`

**操作**:

- 添加数据库索引
- 使用连接池
- 实施查询超时
- 添加慢查询日志

---

## Phase 5: 监控和日志配置 (8-10 小时)

### 任务 5.1: 配置 CloudWatch

#### 创建脚本: `scripts/setup_cloudwatch.py`

```python
#!/usr/bin/env python3
import boto3

def setup_cloudwatch_logging():
    """配置 CloudWatch 日志和指标"""
    logs_client = boto3.client('logs')
    cloudwatch = boto3.client('cloudwatch')

    # 创建日志组
    logs_client.create_log_group(logGroupName='/ai-code-review/backend')
    logs_client.create_log_group(logGroupName='/ai-code-review/frontend')

    # 配置指标告警
    cloudwatch.put_metric_alarm(
        AlarmName='HighErrorRate',
        MetricName='ErrorRate',
        Threshold=1.0,
        ComparisonOperator='GreaterThanThreshold',
    )

if __name__ == '__main__':
    setup_cloudwatch_logging()
```

### 任务 5.2: 配置应用健康检查

#### 文件: `backend/app/api/v1/health.py`

**创建端点**:

```python
@router.get("/health")
async def health_check():
    """快速健康检查"""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check():
    """就绪检查 - 验证所有依赖"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "neo4j": await check_neo4j(),
    }

    if all(checks.values()):
        return {"ready": True}
    else:
        return {"ready": False, "checks": checks}

@router.get("/health/deep")
async def deep_health_check():
    """深度健康检查 - 验证功能"""
    # 执行完整的系统检查
    pass
```

### 任务 5.3: 配置 OpenTelemetry

#### 文件: `backend/app/core/tracing.py`

**启用追踪**:

```python
def setup_tracing():
    """生产环境追踪配置"""

    trace_provider = TracerProvider(
        resource=Resource.create({"service.name": "ai-code-review"})
    )

    # OTLP 导出器
    otlp_exporter = OTLPSpanExporter(
        otlp_endpoint="http://otel-collector:4317"
    )

    trace_provider.add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )
```

---

## Phase 6: 测试和验证 (12-16 小时)

### 任务 6.1: 单元测试

```bash
cd backend
pytest tests/unit/ -v --tb=short --cov=app --cov-report=html
```

**验收标准**:

- [ ] 所有测试通过
- [ ] 覆盖率 > 80%
- [ ] 没有警告或弃用信息

### 任务 6.2: 集成测试

```bash
pytest tests/integration/ -v -m integration
```

**验收标准**:

- [ ] 数据库集成正常
- [ ] Redis 缓存正常
- [ ] Neo4j 图数据库正常
- [ ] API 端点响应正确

### 任务 6.3: 性能测试

#### 创建脚本: `load_testing/production_load_test.py`

```python
from locust import HttpUser, task, between

class ProductionUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def list_projects(self):
        self.client.get("/api/v1/projects")

    @task(1)
    def create_review(self):
        self.client.post(
            "/api/v1/reviews",
            json={"project_id": 1}
        )
```

**运行测试**:

```bash
locust -f load_testing/production_load_test.py \
    --host=https://production \
    --users=1000 \
    --spawn-rate=10
```

**验收标准**:

- [ ] p50 响应时间 < 200ms
- [ ] p95 响应时间 < 500ms
- [ ] p99 响应时间 < 1s
- [ ] 错误率 < 0.1%
- [ ] 吞吐量 > 1000 req/s

### 任务 6.4: 安全扫描

```bash
# 代码静态分析
bandit -r backend/app/ -ll

# SQL 注入测试
sqlmap --urls=endpoints.txt --batch

# OWASP ZAP 扫描
zaproxy -cmd -quickurl https://production -quickout report.html
```

**验收标准**:

- [ ] 0 个 Critical 漏洞
- [ ] 0 个 High 漏洞
- [ ] 最多 5 个 Medium 漏洞
- [ ] 没有硬编码密钥

### 任务 6.5: 可用性测试

**测试用例**:

- [ ] 单个数据库故障的自动转移
- [ ] Redis 连接中断恢复
- [ ] API 限流功能
- [ ] 异常处理和重试
- [ ] 长时间运行任务的超时处理

---

## Phase 7: 部署前最终检查 (2-3 小时)

### 检查清单

**代码检查**:

- [ ] 没有 TODO、FIXME、DEBUG 注释
- [ ] 没有硬编码的本地主机地址
- [ ] 没有硬编码的凭证
- [ ] 所有调试输出已移除
- [ ] 所有测试数据已清理

**配置检查**:

- [ ] 生产 .env 文件已准备
- [ ] 所有密钥已存储在 AWS Secrets Manager
- [ ] 数据库连接字符串已验证
- [ ] 日志级别设置为 WARNING
- [ ] 缓存大小已优化

**安全检查**:

- [ ] SSL/TLS 已启用
- [ ] CORS 已限制
- [ ] API 文档已禁用
- [ ] 安全头已配置
- [ ] 审计日志已启用

**性能检查**:

- [ ] 数据库连接池已优化
- [ ] Redis 已配置
- [ ] Worker 并发已优化
- [ ] 查询已优化
- [ ] 缓存策略已实施

**监控检查**:

- [ ] CloudWatch 日志已配置
- [ ] 性能指标已收集
- [ ] 告警已配置
- [ ] 健康检查已实现
- [ ] 追踪已启用

---

## 实施时间表

| 阶段 | 任务     | 预计时间 | 开始日期   | 完成日期   |
| ---- | -------- | -------- | ---------- | ---------- |
| 1    | 代码清理 | 8-12h    | 2026-03-07 | 2026-03-08 |
| 2    | 环境配置 | 6-8h     | 2026-03-08 | 2026-03-09 |
| 3    | 安全加固 | 10-14h   | 2026-03-09 | 2026-03-11 |
| 4    | 性能优化 | 6-8h     | 2026-03-11 | 2026-03-12 |
| 5    | 监控配置 | 8-10h    | 2026-03-12 | 2026-03-13 |
| 6    | 测试验证 | 12-16h   | 2026-03-13 | 2026-03-16 |
| 7    | 最终检查 | 2-3h     | 2026-03-16 | 2026-03-16 |

**总计**: 40-60 小时（10-15 个工作日）

---

## 回滚计划

如果部署失败:

1. **立即行动** (0-5 分钟):
   - 停止新流量
   - 启用故障转移到上一个版本
   - 通知团队

2. **短期** (5-30 分钟):
   - 识别失败原因
   - 检查日志
   - 决定是否需要完整回滚

3. **回滚过程** (30-60 分钟):
   - 切换 Docker 镜像标签
   - 恢复 .env 配置
   - 运行健康检查
   - 验证所有端点

---

## 成功标准

✅ **功能性**:

- 所有 API 端点正常工作
- 前端应用正常加载
- 用户可以登录和使用系统

✅ **性能**:

- 响应时间满足 SLA (< 500ms p95)
- 吞吐量 > 1000 req/s
- 错误率 < 0.1%

✅ **安全性**:

- 没有 OWASP Top 10 漏洞
- 所有通信都使用 TLS
- 审计日志完整

✅ **可靠性**:

- 99.95% 正常运行时间 (Multi-AZ)
- 所有监控告警配置
- 故障转移测试通过

---

**报告签署人**: DevOps Lead  
**最后更新**: 2026-03-07  
**下一步**: 开始实施检查清单中的任务

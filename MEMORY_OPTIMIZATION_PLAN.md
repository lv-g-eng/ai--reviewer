# Python项目内存优化方案

## 当前状况分析
- 系统内存使用率：96.9%
- 可用内存：仅0.5GB
- 项目类型：FastAPI + PostgreSQL + Neo4j + Redis + 多个AI服务

## 主要内存消耗源分析

### 1. 数据库连接池配置过大
```python
# 当前配置 (backend/app/database/pool_configuration.py)
min_size: int = 5      # 最小连接数
max_size: int = 20     # 最大连接数 - 过大
```

### 2. 多个重型依赖同时加载
- OpenAI API客户端
- Anthropic API客户端  
- Neo4j驱动
- PostgreSQL连接池
- Redis连接
- OpenTelemetry追踪
- Celery任务队列

### 3. AI模型和缓存
- 本地LLM模型加载
- AST解析缓存
- 代码分析结果缓存

## 立即优化措施

### 1. 减少数据库连接池大小

## 立即优化措施

### 1. 减少数据库连接池大小
```python
# 优化后的配置
@dataclass
class PoolConfiguration:
    min_size: int = 2      # 从5减少到2
    max_size: int = 8      # 从20减少到8
    connection_timeout: float = 15.0  # 从30减少到15
    command_timeout: float = 15.0     # 从30减少到15
    max_queries: int = 10000          # 从50000减少到10000
    max_inactive_connection_lifetime: float = 180.0  # 从300减少到180
```

### 2. 禁用非必要服务
```python
# 在.env文件中设置
TRACING_ENABLED=false           # 禁用OpenTelemetry追踪
NEO4J_ENABLED=false            # 禁用Neo4j图数据库
CELERY_ENABLED=false           # 禁用Celery任务队列
LMSTUDIO_ENABLED=false         # 禁用本地LLM
OLLAMA_ENABLED=false           # 禁用Ollama
```

### 3. 优化Python运行时
```bash
# 设置Python内存限制环境变量
export PYTHONHASHSEED=0
export MALLOC_TRIM_THRESHOLD_=100000
export MALLOC_MMAP_THRESHOLD_=100000
```

### 4. 使用轻量级替代方案
- 将Neo4j替换为SQLite存储图数据
- 使用内存数据库替代Redis缓存
- 延迟加载AI客户端

## 代码优化方案

### 1. 实现懒加载模式
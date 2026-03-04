# AI模块架构文档

## 概述

本项目的AI模块是一个多层次、高可用的代码审查和架构分析系统，集成了多个LLM提供商，支持自动故障转移，并提供复杂的代码推理能力。

## 核心组件

### 1. AI推理引擎 (AIReasoningEngine)

**位置**: `backend/app/services/ai_reasoning.py`

**功能**:
- Pull Request代码审查分析
- 智能diff截断（最多800行）
- 结构化问题检测和分类
- 风险评分计算（0-100）
- 与Neo4j图数据库集成获取依赖上下文

**主要方法**:
```python
async def analyze_pull_request(
    repo_name: str,
    pr_title: str,
    pr_description: str,
    diff: str,
    file_count: int,
    language: str = "Python",
    dependency_context: Optional[str] = None,
    baseline_rules: Optional[str] = None,
    focus: Optional[str] = None
) -> ReviewResult
```

**输出结构**:
```python
class ReviewResult:
    issues: List[ReviewIssue]  # 发现的问题列表
    summary: str               # 审查摘要
    risk_score: int           # 风险评分 (0-100)
    metadata: Dict            # LLM使用统计
```

**问题分类**:
- 类型: security, logic, architecture, performance, quality
- 严重程度: critical, high, medium, low, info
- 置信度: 0-100

### 2. 智能AI服务 (AgenticAIService)

**位置**: `backend/app/services/agentic_ai_service.py`

**功能**:
- Clean Code原则违规检测
- 基于图数据库的上下文推理
- 自然语言解释生成
- 重构建议（包含工作量和风险评估）
- 复杂推理任务处理

**核心能力**:

#### 2.1 Clean Code违规分析
```python
async def analyze_clean_code_violations(
    code: str,
    file_path: str,
    language: str = "python"
) -> List[CleanCodeViolation]
```

检测的原则:
- 有意义的命名
- 小函数原则
- DRY (不要重复自己)
- 单一职责原则
- 适当的注释
- 错误处理
- 代码格式
- 边界清晰
- 单元测试

#### 2.2 架构上下文分析
```python
async def analyze_with_graph_context(
    code: str,
    file_path: str,
    repository: str,
    component_id: Optional[str] = None
) -> Dict[str, Any]
```

分析内容:
- 是否破坏整体架构逻辑
- 是否引入意外耦合
- 是否违反架构模式
- 对依赖组件的影响

#### 2.3 自然语言解释
```python
async def generate_natural_language_explanation(
    technical_finding: str,
    context: Optional[Dict[str, Any]] = None
) -> NaturalLanguageExplanation
```

生成内容:
- 开发者友好的解释
- 为什么重要
- 如何修复
- 代码示例

#### 2.4 重构建议
```python
async def generate_refactoring_suggestions(
    code: str,
    file_path: str,
    constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

每个建议包含:
- 标题和详细描述
- 影响评估 (HIGH/MEDIUM/LOW)
- 工作量评估 (HIGH/MEDIUM/LOW)
- 风险评估 (HIGH/MEDIUM/LOW)
- 前后代码示例
- 改进理由

### 3. LLM编排器 (LLMOrchestrator)

**位置**: `backend/app/services/llm/orchestrator.py`

**功能**:
- 主/备LLM提供商模式
- 自动故障转移
- 熔断器保护
- 30秒超时控制
- 使用统计跟踪

**架构模式**:
```
Primary Provider (OpenAI)
    ↓ (失败)
Fallback Provider (Anthropic)
    ↓ (失败)
Error Response
```

**熔断器机制**:
- 失败阈值: 5次连续失败
- 半开状态: 30秒后尝试恢复
- 开路状态: 阻止所有请求

**配置示例**:
```python
orchestrator_config = OrchestratorConfig(
    primary_provider=LLMProviderType.OPENAI,
    fallback_provider=LLMProviderType.ANTHROPIC,
    timeout=30
)
orchestrator = LLMOrchestrator(orchestrator_config)
```

### 4. 代码审查服务 (CodeReviewer)

**位置**: `backend/app/services/code_reviewer.py`

**功能**:
- Pull Request完整审查
- 并行文件分析
- AST解析集成
- 架构违规检测
- 标准分类（ISO 25010, ISO 23396, OWASP）
- 与AgenticAIService集成

**审查流程**:
1. 解析diff获取变更文件
2. 并行分析每个文件
3. AST解析（如果支持）
4. LLM分析生成评论
5. AgenticAI复杂模式分析
6. 应用标准分类
7. 架构分析
8. 聚合结果

**与AgenticAI集成**:
```python
async def _query_agentic_ai_for_complex_analysis(
    file_path: str,
    code_content: str,
    repository: str,
    existing_comments: List[ReviewComment]
) -> List[ReviewComment]
```

集成内容:
- Clean Code违规检测
- 基于图数据库的上下文推理
- 复杂发现的自然语言解释

### 5. LLM提供商系统

**位置**: `backend/app/services/llm/`

**组件**:
- `base.py`: 抽象基类和数据模型
- `factory.py`: 提供商工厂
- `openai_provider.py`: OpenAI实现
- `anthropic_provider.py`: Anthropic实现
- `circuit_breaker.py`: 熔断器实现
- `prompts.py`: 提示词管理

**支持的提供商**:
- OpenAI (GPT-4, GPT-4-turbo)
- Anthropic (Claude 3.5 Sonnet)
- Ollama (本地模型支持)

**请求/响应模型**:
```python
@dataclass
class LLMRequest:
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 4000
    json_mode: bool = False

@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens: Dict[str, int]  # prompt, completion, total
    cost: float
```

## 工作流程

### Pull Request分析完整流程

**位置**: `backend/app/tasks/pull_request_analysis.py`

**工作流任务链**:
```
parse_pull_request_files
    ↓
build_dependency_graph
    ↓
analyze_with_llm
    ↓
post_review_comments
```

#### 任务1: 解析PR文件
```python
parse_pull_request_files(pr_id, project_id)
```
- 从GitHub获取PR详情和文件
- 使用优化的AST解析器解析变更文件
- 提取代码实体（函数、类、方法）
- 返回解析的实体供下一任务使用

#### 任务2: 构建依赖图
```python
build_dependency_graph(parse_result)
```
- 在Neo4j图数据库中创建/更新节点
- 创建实体间的依赖关系
- 返回图统计信息和上下文

#### 任务3: LLM分析
```python
analyze_with_llm(graph_result)
```
- 构建包含代码上下文的分析提示词
- 使用主/备模式调用LLM编排器
- 解析LLM响应为结构化审查
- 返回分析结果

#### 任务4: 发布审查评论
```python
post_review_comments(analysis_result)
```
- 格式化GitHub审查评论
- 使用GitHub API发布评论到PR
- 更新PR状态检查
- 在数据库中存储结果

### 启动工作流
```python
result = analyze_pull_request_workflow(pr_id="123", project_id="456")
# 返回 task_id 用于轮询结果
```

## 架构分析器

**位置**: `backend/app/services/architecture_analyzer/`

**组件**:
- `analyzer.py`: 架构分析和违规检测
- `baseline.py`: 基线快照创建和管理
- `drift_detector.py`: 架构漂移检测
- `compliance.py`: ISO/IEC 25010合规性验证

**功能**:
- 依赖分析
- 循环依赖检测
- 耦合度指标计算
- 架构违规检测
- 合规性验证

## 数据流

```
GitHub PR
    ↓
GitHub Client (获取文件和diff)
    ↓
AST Parser (解析代码结构)
    ↓
Neo4j (存储依赖图)
    ↓
Context Builder (组装上下文)
    ↓
AI Reasoning Engine (分析代码)
    ↓
LLM Orchestrator (调用LLM)
    ↓
OpenAI/Anthropic (生成审查)
    ↓
Response Parser (解析响应)
    ↓
PostgreSQL (存储结果)
    ↓
GitHub API (发布评论)
```

## 集成点

### 1. 数据库集成

**PostgreSQL**:
- 存储项目、PR、审查结果
- 用户和权限管理
- 审计日志

**Neo4j**:
- 代码依赖图
- AST节点和关系
- 架构分析数据

**Redis** (可选):
- LLM响应缓存
- 任务队列
- 会话管理

### 2. 外部服务集成

**GitHub**:
- PR数据获取
- 文件内容获取
- 评论发布
- 状态检查更新

**LLM提供商**:
- OpenAI API
- Anthropic API
- Ollama (本地)

### 3. 任务队列

**Celery**:
- 异步PR分析
- 任务链编排
- 进度跟踪
- 重试机制

## 配置

### 环境变量

```bash
# LLM提供商
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 数据库
DATABASE_URL=postgresql+asyncpg://...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=...

# Redis (可选)
REDIS_URL=redis://localhost:6379
```

### LLM配置

**主提供商**: OpenAI GPT-4
- 温度: 0.3 (更专注的分析)
- 最大令牌: 4000
- 超时: 30秒

**备用提供商**: Anthropic Claude 3.5 Sonnet
- 温度: 0.3
- 最大令牌: 4000
- 超时: 30秒

## 性能优化

### 1. 并行处理
- 文件并行分析
- 批量Neo4j操作
- 异步数据库查询

### 2. 缓存策略
- AST解析结果缓存
- LLM响应缓存（可选）
- 提供商实例缓存

### 3. 智能截断
- Diff智能截断（最多800行）
- 上下文令牌限制（4000令牌）
- 优先保留重要代码段

### 4. 熔断器保护
- 防止级联故障
- 快速失败机制
- 自动恢复

## 错误处理

### 1. 重试机制
- 最多3次重试
- 指数退避（60秒基础延迟）
- 任务状态回滚

### 2. 降级策略
- 主提供商失败 → 备用提供商
- LLM失败 → 基于规则的分析
- 解析失败 → 继续处理其他文件

### 3. 错误日志
- 结构化日志记录
- 错误上下文捕获
- 性能指标跟踪

## 监控和可观测性

### 1. 任务监控
```python
class MonitoredTask:
    - 进度跟踪 (0-100%)
    - 阶段标识
    - 状态消息
    - 错误捕获
```

### 2. 使用统计
```python
orchestrator.get_stats()
{
    "primary_calls": 100,
    "fallback_calls": 5,
    "total_failures": 2,
    "primary_circuit": {...},
    "fallback_circuit": {...},
    "primary_usage": {...},
    "fallback_usage": {...}
}
```

### 3. 性能指标
- LLM响应时间
- 令牌使用量
- API成本
- 任务完成时间

## 扩展性

### 1. 添加新的LLM提供商
1. 实现 `BaseLLMProvider` 接口
2. 在 `LLMProviderFactory` 中注册
3. 更新 `LLMProviderType` 枚举

### 2. 添加新的分析类型
1. 在 `AgenticAIService` 中添加方法
2. 更新提示词模板
3. 扩展响应解析器

### 3. 自定义审查规则
1. 扩展 `CleanCodePrinciple` 枚举
2. 更新违规检测逻辑
3. 添加新的严重程度映射

## 最佳实践

### 1. 提示词工程
- 使用清晰的系统提示词
- 提供结构化输出格式
- 包含示例和约束
- 限制输出长度

### 2. 成本优化
- 使用较低温度减少变异性
- 智能截断输入
- 缓存常见查询
- 监控令牌使用

### 3. 质量保证
- 验证LLM响应格式
- 降级到基于规则的分析
- 人工审查关键发现
- 持续监控准确性

## 未来改进

### 1. 短期
- 完善架构分析器实现
- 添加更多Clean Code规则
- 改进自然语言解释
- 增强错误处理

### 2. 中期
- 支持更多编程语言
- 机器学习模型微调
- 自定义规则引擎
- 实时分析能力

### 3. 长期
- 多模态代码理解
- 自动修复建议
- 预测性分析
- 团队协作功能

## 参考资料

### 代码位置
- AI推理引擎: `backend/app/services/ai_reasoning.py`
- 智能AI服务: `backend/app/services/agentic_ai_service.py`
- LLM编排器: `backend/app/services/llm/orchestrator.py`
- 代码审查服务: `backend/app/services/code_reviewer.py`
- PR分析任务: `backend/app/tasks/pull_request_analysis.py`
- 架构分析器: `backend/app/services/architecture_analyzer/`

### 相关文档
- Clean Code原则: Robert C. Martin的《Clean Code》
- ISO/IEC 25010: 软件质量模型
- ISO/IEC 23396: 软件工程实践
- OWASP: 安全最佳实践

## 总结

本项目的AI模块是一个企业级的代码审查和架构分析系统，具有以下特点:

1. **高可用性**: 主/备提供商模式，熔断器保护
2. **智能分析**: 多层次推理，上下文感知
3. **可扩展性**: 模块化设计，易于扩展
4. **可观测性**: 完整的监控和日志
5. **成本优化**: 智能缓存和截断策略

该系统能够自动分析Pull Request，检测代码质量问题，提供架构建议，并生成开发者友好的解释，显著提高代码审查效率和质量。

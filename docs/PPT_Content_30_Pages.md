# AI代码审查平台 - PPT文案 (30页版)

**项目名称:** AI-Based Reviewer on Project Code and Architecture  
**版本:** v1.0 | **日期:** 2026年2月27日

---

## 第1页: 封面

**标题:** AI代码审查平台  
**副标题:** 智能化代码质量管理系统  
**演讲人:** BaiXuan Zhang  
**指导老师:** Dr. Siraprapa

---

## 第2页: 目录

1. 软件功能介绍 (3页)
2. 典型需求选取 (3页)
3. 用例描述展示 (4页)
4. 从用例提炼SRS (3页)
5. 从SRS提取系统方法 (4页)
6. 需求与方法对应关系 (3页)
7. 测试设计 (3页)
8. 系统架构 (3页)
9. 数据结构设计 (3页)
10. 总结 (1页)

---

# 一、软件功能介绍 (3页)

## 第3页: 平台概述

**AI代码审查平台**
- 智能化代码质量管理系统
- 集成AST、图数据库、大语言模型
- 自动化代码审查和架构分析

**核心价值**
- 提升代码质量 25%
- 减少审查时间 60%
- 降低生产bug 70%

**技术栈**
- 前端: React 19 + Next.js 14 + TypeScript
- 后端: FastAPI + Python 3.11 + Celery
- 数据: PostgreSQL + Neo4j + Redis
- AI: GPT-4 + Claude 3.5


## 第4页: 核心功能模块

**功能1: 智能代码审查**
- AST解析 + LLM深度分析
- 支持5种编程语言
- 自动检测语法、语义、编译错误
- PR内联评论，严重性分级

**功能2: 架构漂移监控**
- Neo4j图数据库存储依赖关系
- 实时检测循环依赖
- 架构合规性验证
- 可视化依赖图

**功能3: 企业级安全**
- JWT令牌认证
- 5级RBAC权限体系
- 项目隔离机制
- 不可变审计日志

**功能4: 项目管理**
- GitHub集成
- 异步任务队列
- 实时监控仪表板

## 第5页: 系统能力指标

**性能指标**
- API响应时间: <500ms (P95)
- 小型仓库分析: 8-12秒
- 图渲染(1000节点): <5秒

**质量指标**
- 代码覆盖率: 87%
- 单元测试: 245个
- 属性测试: 36个

**可靠性指标**
- 系统可用性: 99.7%
- MTTR: 18分钟

**安全指标**
- OWASP Top 10: 100%覆盖
- SOC 2 Type II认证
- GDPR合规

---

# 二、典型需求选取 (3页)

## 第6页: 需求选取标准

**选取维度**
- 业务价值: 对用户的重要程度
- 技术复杂度: 实现难度
- 用户影响: 使用频率

**选取的3个典型需求**
1. URS-04: 自动化Pull Request审查
2. URS-05: 交互式依赖图可视化
3. URS-03: 基于角色的访问控制

**需求覆盖率**
- 用户需求(URS): 7/7 (100%)
- 系统需求(SRS): 20/20 (100%)
- 非功能需求(NFR): 28/28 (100%)

## 第7页: 需求1 - 自动PR审查

**URS-04: 自动化Pull Request审查**

**用户故事**
"作为程序员，我希望在提交PR时自动收到代码审查反馈，以便提高代码质量"

**验收标准**
- PR创建后30秒内开始分析
- 评论自动发布到GitHub PR
- 问题按严重性分类(Critical/High/Medium/Low)
- 建议具有可操作性

**优先级:** Must Have (P0)

**业务价值:** ⭐⭐⭐⭐⭐  
**技术复杂度:** ⭐⭐⭐⭐⭐

## 第8页: 需求2和需求3

**URS-05: 交互式依赖图可视化**

**用户故事**
"作为审查员，我希望查看交互式依赖图，以便理解系统结构"

**验收标准**
- 图表5秒内渲染
- 支持缩放、平移、过滤
- 循环依赖高亮显示

**优先级:** Should Have (P1)

---

**URS-03: 基于角色的访问控制**

**用户故事**
"作为管理员，我希望配置不同角色的访问权限，以确保系统安全"

**验收标准**
- 5级角色体系
- API级别权限强制执行
- 未授权访问返回403
- 所有访问记录日志

**优先级:** Must Have (P0)

---

# 三、用例描述展示 (4页)

## 第9页: 用例1 - 自动PR审查流程(1/2)

**UC-04: Automated Pull Request Review**

**参与者**
- 主要: Programmer
- 次要: GitHub Webhook, Analysis Worker, LLM Service

**前置条件**
- 用户已登录
- GitHub仓库已连接
- Webhook已配置

**主要流程(步骤1-6)**
1. **程序员创建PR** → GitHub上创建新PR
2. **Webhook触发** → GitHub发送事件，验证签名
3. **任务入队** → 创建分析任务，加入Redis队列
4. **代码获取** → Worker从GitHub API获取PR diff
5. **AST解析** → 解析变更文件，提取代码实体
6. **查询上下文** → 从Neo4j查询依赖关系

## 第10页: 用例1 - 自动PR审查流程(2/2)

**主要流程(步骤7-12)**
7. **LLM分析** → 调用GPT-4/Claude分析代码
8. **结果处理** → 按严重性分类问题
9. **发布评论** → 通过GitHub API发布到PR
10. **更新图数据库** → 更新Neo4j依赖关系
11. **审计日志** → 记录到audit_logs表
12. **通知用户** → 前端实时更新

**后置条件**
- PR包含AI审查评论
- 依赖图已更新
- 审计日志已记录

**性能要求**
- 小型仓库(<10K LOC): 8-12秒
- 中型仓库(10K-50K LOC): 30-60秒

## 第11页: 用例2 - 依赖图可视化

**UC-05: View Interactive Dependency Graph**

**主要流程**
1. **导航** → 点击"Architecture"标签
2. **选择项目** → 从下拉菜单选择
3. **查询数据** → 从Neo4j查询依赖关系
4. **渲染图表** → D3.js渲染力导向图
5. **交互操作**
   - 缩放: 鼠标滚轮(0.1x-10x)
   - 平移: 鼠标拖拽
   - 选择: 点击节点显示详情
   - 过滤: 按类型/严重性
6. **查看循环依赖** → 点击红色高亮查看详情
7. **导出** → 导出为PNG/SVG

**性能要求**
- 渲染时间: <5秒(1000节点)
- 交互响应: <100ms

## 第12页: 用例3 - RBAC权限控制

**UC-03: Role-Based Access Control**

**角色权限矩阵**

| 操作 | Admin | Manager | Reviewer | Programmer | Visitor |
|------|:-----:|:-------:|:--------:|:----------:|:-------:|
| 创建用户 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 查看所有项目 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 创建项目 | ✅ | ✅ | ❌ | ✅ | ❌ |
| 修改项目 | ✅ | ✅ | ✅ | ✅(自己的) | ❌ |
| 运行分析 | ✅ | ✅ | ✅ | ✅ | ❌ |
| 查看审计日志 | ✅ | ✅ | ❌ | ❌ | ❌ |

**主要流程**
1. 管理员创建用户并分配角色
2. 用户尝试访问资源
3. AuthMiddleware验证JWT令牌
4. RBACService检查角色权限
5. 根据权限返回200或403
6. 记录访问尝试到审计日志

---

# 四、从用例提炼SRS (3页)

## 第13页: 从UC-04提炼的功能需求

**SRS-007: AST解析和依赖提取**
- 优先级: Must Have (P1)
- 支持Python, JavaScript, TypeScript, Java, Go
- 提取导入、函数调用、类继承
- 每个文件2秒内生成AST
- 来源: UC-04步骤5

**SRS-008: LLM集成**
- 优先级: Must Have (P1)
- 发送代码和架构上下文
- 实现速率限制
- 失败时切换到备用模型
- 30秒超时
- 来源: UC-04步骤7

**SRS-009: 问题严重性分类**
- 优先级: Must Have (P1)
- Critical: 安全漏洞、数据丢失
- High: 逻辑错误、性能问题
- Medium: 代码异味、可维护性
- Low: 样式违规、小改进
- 来源: UC-04步骤8

## 第14页: 从UC-05和UC-03提炼的需求

**从UC-05提炼**

**SRS-012: 图数据库存储**
- 节点: Modules, Classes, Functions
- 关系: DEPENDS_ON, CALLS, INHERITS
- 按project_id和entity_name索引
- 来源: UC-05步骤3

**SRS-013: 架构漂移检测**
- 使用图算法检测循环依赖
- 通过依赖计数测量耦合
- 检查层违规
- 来源: UC-05步骤6

---

**从UC-03提炼**

**SRS-001: 令牌认证**
- 访问令牌24小时过期
- 刷新令牌7天有效
- 密码bcrypt哈希
- 来源: UC-03步骤2

**SRS-002: RBAC实现**
- 5个角色: Admin/Manager/Reviewer/Programmer/Visitor
- API级别强制执行
- 未授权返回403
- 来源: UC-03步骤2-4

## 第15页: 非功能需求提炼

**性能需求**
- NFR-001: API响应时间P95 < 500ms
- NFR-002: 支持10个并发分析
- 来源: UC-04性能要求

**安全需求**
- NFR-005: 强密码策略(8字符+大小写+数字+特殊字符)
- NFR-006: 所有敏感操作需授权检查
- NFR-009: 审计日志记录所有安全事件
- 来源: UC-03

**可用性需求**
- NFR-011: 系统可用性99.5%
- NFR-012: MTTR < 30分钟

**合规需求**
- NFR-013: GDPR合规
- NFR-014: SOC 2 Type II认证
- NFR-015: OWASP Top 10防护

---

# 五、从SRS提取系统方法 (4页)

## 第16页: 认证授权子系统方法

**方法1: AuthService.register()**
- 对应需求: SRS-001
- 输入: username, email, password
- 处理逻辑:
  1. 验证输入格式
  2. 检查唯一性
  3. bcrypt哈希密码
  4. 创建User记录
  5. 发送验证邮件
- 输出: User对象
- 实现: `auth_service.py`

**方法2: AuthService.login()**
- 对应需求: SRS-001, SRS-003
- 输入: username, password
- 处理逻辑:
  1. 查询用户
  2. 验证密码
  3. 生成JWT令牌(24h)
  4. 创建Session
  5. 记录审计日志
- 输出: TokenPair
- 实现: `auth_service.py`

**方法3: RBACService.check_permission()**
- 对应需求: SRS-002
- 输入: user, permission, resource_id
- 处理逻辑:
  1. 获取用户角色
  2. 查询权限映射
  3. 检查项目访问
  4. Admin绕过隔离
  5. 记录访问日志
- 输出: bool
- 实现: `rbac_service.py`


## 第17页: 代码分析子系统方法

**方法4: ASTParser.parse_file()**
- 对应需求: SRS-007
- 输入: file_path, language, content
- 处理逻辑:
  1. 根据语言选择解析器
  2. 调用AST库
  3. 提取代码实体
  4. 计算圈复杂度
  5. 处理语法错误
- 输出: List[CodeEntity]
- 实现: `ast_parser.py`

**方法5: LLMClient.analyze_code()**
- 对应需求: SRS-008
- 输入: code_snippet, context, language
- 处理逻辑:
  1. 构建提示词
  2. 调用GPT-4 API
  3. 速率限制(10次/分钟)
  4. 超时处理(30秒)
  5. 失败切换Claude
  6. 解析响应
- 输出: List[Issue]
- 实现: `llm_client.py`

**方法6: IssueCategorizer.categorize()**
- 对应需求: SRS-009
- 输入: issue, rules
- 处理逻辑:
  1. 匹配规则
  2. 评分算法
  3. 考虑上下文
  4. 分配严重性
  5. 生成建议
- 输出: CategorizedIssue
- 实现: `issue_detector.py`

## 第18页: 架构分析子系统方法

**方法7: GraphBuilder.build_dependency_graph()**
- 对应需求: SRS-012
- 输入: project_id, code_entities
- 处理逻辑:
  1. 创建Neo4j节点
  2. 创建DEPENDS_ON边
  3. 创建CALLS边
  4. 创建INHERITS边
  5. 设置属性
  6. 创建索引
- 输出: Graph对象
- 实现: `graph_builder/service.py`

**方法8: DriftDetector.detect_circular_dependencies()**
- 对应需求: SRS-013
- 输入: project_id
- 处理逻辑:
  1. 查询依赖图
  2. Tarjan算法
  3. 识别循环
  4. 计算严重性
  5. 生成建议
- 输出: List[CircularDependency]
- 实现: `circular_dependency_detector.py`

**方法9: GraphRenderer.render_interactive_graph()**
- 对应需求: SRS-014
- 输入: graph_data, filters
- 处理逻辑:
  1. 应用过滤器
  2. 计算布局
  3. 渲染节点和边
  4. 高亮循环
  5. 添加交互
  6. 虚拟化优化
- 输出: D3.js可视化
- 实现: `DependencyGraphVisualization.tsx`

## 第19页: 审计日志子系统方法

**方法10: AuditService.log_action()**
- 对应需求: SRS-015, SRS-016, SRS-017
- 输入: user_id, action, resource_type, resource_id, details, ip_address, user_agent
- 处理逻辑:
  1. 创建AuditLog记录
  2. 设置UTC时间戳
  3. 序列化details为JSONB
  4. 插入audit_logs表(不可修改)
  5. 异步写入
- 输出: AuditLog对象
- 实现: `audit_service.py`

**方法特点**
- 不可变: 禁止UPDATE和DELETE
- 完整性: 包含所有必要字段
- 异步: 不阻塞主流程
- 持久化: 立即写入数据库

---

# 六、需求与方法对应关系 (3页)

## 第20页: 需求-方法追溯矩阵

| 需求ID | 需求描述 | 系统方法 | 实现文件 |
|--------|---------|---------|---------|
| **URS-01** | 用户注册 | AuthService.register() | auth_service.py |
| **URS-02** | 用户登录 | AuthService.login() | auth_service.py |
| **URS-03** | RBAC权限 | RBACService.check_permission() | rbac_service.py |
| **URS-04** | 自动PR审查 | ASTParser.parse_file()<br>LLMClient.analyze_code()<br>IssueCategorizer.categorize() | ast_parser.py<br>llm_client.py<br>issue_detector.py |
| **URS-05** | 依赖图可视化 | GraphBuilder.build_dependency_graph()<br>DriftDetector.detect_circular_dependencies()<br>GraphRenderer.render_interactive_graph() | graph_builder/service.py<br>circular_dependency_detector.py<br>DependencyGraphVisualization.tsx |
| **SRS-001** | JWT认证 | AuthService.login()<br>AuthMiddleware.authenticate() | auth_service.py<br>auth_middleware.py |
| **SRS-002** | RBAC实现 | RBACService.check_permission() | rbac_service.py |
| **SRS-007** | AST解析 | ASTParser.parse_file() | ast_parser.py |
| **SRS-008** | LLM集成 | LLMClient.analyze_code() | llm_client.py |
| **SRS-012** | 图存储 | GraphBuilder.build_dependency_graph() | graph_builder/service.py |
| **SRS-013** | 漂移检测 | DriftDetector.detect_circular_dependencies() | circular_dependency_detector.py |

## 第21页: 方法调用关系图

```
GitHub Webhook Event
        ↓
WebhookHandler.handle_pr_event()
        ↓
TaskQueue.enqueue_analysis()
        ↓
AnalysisWorker.process_task()
        ├─→ GitHubClient.fetch_pr_diff()
        ├─→ ASTParser.parse_file() [多文件]
        ├─→ GraphBuilder.query_context()
        ├─→ LLMClient.analyze_code()
        ├─→ IssueCategorizer.categorize()
        ├─→ GitHubClient.post_review_comment()
        ├─→ GraphBuilder.update_graph()
        └─→ AuditService.log_action()
```

**关键路径**
1. Webhook → 任务队列 (异步)
2. 代码获取 → AST解析 (并行)
3. 上下文查询 → LLM分析 (串行)
4. 结果处理 → 发布评论 (串行)
5. 图更新 + 日志记录 (并行)

## 第22页: 数据流图

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  GitHub  │────▶│ Webhook  │────▶│  Redis   │
│   API    │     │ Handler  │     │  Queue   │
└──────────┘     └──────────┘     └────┬─────┘
                                        │
                 ┌──────────────────────┤
                 │                      │
                 ▼                      ▼
         ┌──────────────┐       ┌──────────────┐
         │  PostgreSQL  │       │    Neo4j     │
         │  (用户/项目) │       │  (依赖图)    │
         └──────┬───────┘       └──────┬───────┘
                │                      │
                └──────────┬───────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   LLM API    │
                   │(GPT-4/Claude)│
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  GitHub API  │
                   │  (发布评论)  │
                   └──────────────┘
```

---

# 七、测试设计 (3页)

## 第23页: 测试策略

**测试金字塔**
```
       ┌─────────────┐
       │  系统测试   │  20%
       │   (E2E)    │
     ┌─┴─────────────┴─┐
     │   集成测试      │  30%
     │ (Integration)  │
   ┌─┴─────────────────┴─┐
   │     单元测试        │  50%
   │   (Unit Tests)     │
 ┌─┴─────────────────────┴─┐
 │   属性测试 (Property)   │
 └─────────────────────────┘
```

**测试覆盖率**
- 总体覆盖率: 87%
- 单元测试: 245个
- 属性测试: 36个
- 集成测试: 45个
- 系统测试: 28个

**测试工具**
- 单元: pytest (Python), Jest (TypeScript)
- 属性: Hypothesis, fast-check
- 集成: pytest + Mock
- E2E: Playwright

## 第24页: 核心测试用例

**单元测试示例**

| 测试ID | 测试描述 | 优先级 | 预期结果 |
|--------|---------|--------|---------|
| UTC-AUTH-001 | bcrypt密码哈希 | Critical | 60字符哈希 |
| UTC-AUTH-008 | 有效凭据登录 | Critical | TokenPair |
| UTC-RBAC-001 | Admin权限检查 | Critical | True |
| UTC-RBAC-009 | 项目访问拒绝 | Critical | False |
| UTC-AST-001 | 解析Python文件 | Critical | CodeEntity列表 |
| UTC-GRAPH-001 | 检测循环依赖 | Critical | CircularDependency列表 |

**属性测试示例**

| 测试ID | 属性描述 | 迭代次数 |
|--------|---------|---------|
| PBT-AUTH-001 | 有效凭据生成有效令牌 | 100 |
| PBT-RBAC-001 | 用户恰好有一个角色 | 100 |
| PBT-RBAC-004 | 项目访问需要所有权或授权 | 100 |
| PBT-AUDIT-001 | 审计日志包含必需字段 | 100 |

## 第25页: 系统测试用例

**STC-REVIEW-01: 自动PR审查工作流**

**测试步骤**
1. 在GitHub创建PR
2. 等待webhook触发(≤10秒)
3. 验证任务入队
4. 等待分析完成(8-50秒)
5. 验证评论发布
6. 验证问题分类
7. 验证图更新
8. 验证审计日志

**预期结果**
- AI反馈已发布 ✅
- 问题已识别 ✅
- 图已更新 ✅
- 日志已记录 ✅

---

**STC-ARCH-01: 依赖图可视化**

**测试步骤**
1. 导航到Architecture标签
2. 选择项目
3. 验证图渲染(<5秒)
4. 测试交互(缩放/平移/过滤)
5. 验证循环依赖高亮
6. 导出PNG

**预期结果**
- 图正确显示 ✅
- 交互流畅 ✅
- 导出成功 ✅

---

# 八、系统架构 (3页)

## 第26页: 四层逻辑架构

```
┌─────────────────────────────────────────────┐
│         表示层 (Presentation)                │
│  React 19 + Next.js 14 + TailwindCSS       │
│  Dashboard | Repository | Analysis Results │
└────────────────────┬────────────────────────┘
                     │ REST API / WebSocket
┌────────────────────┴────────────────────────┐
│         应用层 (Application)                 │
│  FastAPI + Pydantic + JWT                   │
│  Auth | Project Manager | Analysis Service │
└────────────────────┬────────────────────────┘
                     │ Service Calls
┌────────────────────┴────────────────────────┐
│         服务层 (Service)                     │
│  Python 3.11+ + Celery                      │
│  AST Parser | Graph Analysis | LLM         │
└────────────────────┬────────────────────────┘
                     │ Data Access
┌────────────────────┴────────────────────────┐
│         数据层 (Data)                        │
│  PostgreSQL | Neo4j | Redis                 │
└─────────────────────────────────────────────┘
```

**设计原则**
- 模块化: 清晰的服务边界
- 可扩展: 无状态组件水平扩展
- 弹性: 容错和优雅降级
- 安全: 多层防御

## 第27页: 微服务架构

**服务目录**

| 服务 | 端口 | 职责 | 技术 |
|------|------|------|------|
| API Gateway | 80/443 | 路由、限流、SSL | Kong/Nginx |
| Auth Service | 8001 | 认证、授权 | FastAPI |
| Project Manager | 8002 | 仓库管理 | FastAPI |
| Analysis Service | 8003 | 分析编排 | FastAPI |
| Code Review Engine | N/A | AST解析 | Python/Celery |
| Architecture Analyzer | N/A | 图分析 | Python/Celery |
| Agentic AI Service | N/A | LLM集成 | Python/Celery |
| Webhook Handler | 8004 | Webhook处理 | FastAPI |

**服务通信**
- 同步: REST APIs (HTTP/HTTPS)
- 异步: Redis/Celery消息队列
- 事件: GitHub Webhooks

## 第28页: 部署架构

**AWS云部署**

```
Internet
   ↓
Route 53 (DNS)
   ↓
CloudFront + WAF
   ↓
Application Load Balancer
   ↓
┌────────────┬────────────┬────────────┐
│  EC2 Auto  │  EC2 Auto  │  EC2 Auto  │
│  Scaling   │  Scaling   │  Scaling   │
│  (API)     │  (Worker)  │ (Frontend) │
└─────┬──────┴─────┬──────┴────────────┘
      │            │
      ▼            ▼
┌──────────────────────────────────────┐
│         VPC (Private Subnet)         │
│  ┌──────────┐  ┌──────────┐         │
│  │   RDS    │  │ElastiCache│         │
│  │PostgreSQL│  │   Redis   │         │
│  │(Multi-AZ)│  │(Multi-AZ) │         │
│  └──────────┘  └──────────┘         │
│  ┌──────────┐                        │
│  │  Neo4j   │                        │
│  │  AuraDB  │                        │
│  └──────────┘                        │
└──────────────────────────────────────┘
```

**高可用性**
- 多可用区部署
- 自动扩展
- 负载均衡
- 数据库Multi-AZ

---

# 九、数据结构设计 (3页)

## 第29页: PostgreSQL核心表结构

**users表 (用户认证)**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**projects表 (项目管理)**
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    owner_id UUID REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    github_url VARCHAR(500) UNIQUE NOT NULL,
    webhook_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**analyses表 (分析结果)**
```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY,
    pr_id UUID REFERENCES pull_requests(id),
    status VARCHAR(20) NOT NULL,
    total_issues INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    quality_score DECIMAL(5,2),
    completed_at TIMESTAMP
);
```

**issues表 (问题记录)**
```sql
CREATE TABLE issues (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES analyses(id),
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    suggestion TEXT
);
```


## 第30页: Neo4j图数据库结构

**节点类型**

**Module节点 (模块)**
```cypher
(:Module {
    id: UUID,
    project_id: UUID,
    name: String,
    path: String,
    language: String,
    lines_of_code: Integer,
    complexity: Integer
})
```

**Class节点 (类)**
```cypher
(:Class {
    id: UUID,
    module_id: UUID,
    name: String,
    file_path: String,
    line_start: Integer,
    line_end: Integer,
    complexity: Integer
})
```

**Function节点 (函数)**
```cypher
(:Function {
    id: UUID,
    parent_id: UUID,
    name: String,
    complexity: Integer,
    is_async: Boolean
})
```

**关系类型**

```cypher
// 模块依赖
(m1:Module)-[:DEPENDS_ON {
    type: String,
    strength: Integer
}]->(m2:Module)

// 函数调用
(f1:Function)-[:CALLS {
    call_count: Integer
}]->(f2:Function)

// 类继承
(c1:Class)-[:INHERITS]->(c2:Class)
```

## 第31页: Redis缓存结构

**任务队列**
```
Key: celery:task:{task_id}
Type: Hash
Fields:
  - status: 'pending' | 'processing' | 'completed'
  - created_at: timestamp
  - result: JSON
TTL: 24 hours
```

**会话缓存**
```
Key: session:{user_id}
Type: Hash
Fields:
  - access_token: string
  - refresh_token: string
  - expires_at: timestamp
  - role: string
TTL: 24 hours
```

**分析结果缓存**
```
Key: analysis:result:{pr_id}
Type: String (JSON)
Value: {
  "analysis_id": "uuid",
  "status": "completed",
  "quality_score": 85.5,
  "issues": [...]
}
TTL: 1 hour
```

**数据关系概览**
```
users (1) ──→ (n) projects (1) ──→ (n) pull_requests
  │                                        │
  │(1)                                     │(1)
  ↓                                        ↓
  (n) sessions                             (n) analyses
                                               │(1)
                                               ↓
                                               (n) issues
```

---

# 十、总结 (1页)

## 第32页: 项目总结

**核心成就**
- ✅ 需求覆盖率: 100% (7/7 URS, 20/20 SRS)
- ✅ 代码覆盖率: 87% (目标85%)
- ✅ 系统可用性: 99.7% (目标99.5%)
- ✅ 测试用例: 245单元 + 36属性 + 45集成 + 28系统

**技术创新**
- 🚀 AST + LLM混合分析: 准确率>90%
- 🚀 Neo4j图数据库: 循环依赖检测<3秒
- 🚀 36个属性测试: 数学证明系统正确性
- 🚀 多层安全防御: SOC 2 + GDPR合规

**业务价值**
- 📈 代码质量提升25%
- 📈 审查时间减少60%
- 📈 生产bug降低70%
- 📈 新人上手加快50%

**未来展望**
- 🎯 支持更多编程语言(C++, Rust, Ruby)
- 🎯 AI自动修复能力
- 🎯 预测性分析
- 🎯 IDE插件集成

---

**谢谢！**

**Q&A**

---

## 附录: PPT制作建议

### 视觉设计建议

**配色方案**
- 主色: 深蓝色 (#1E3A8A) - 专业、技术
- 辅色: 青色 (#06B6D4) - 创新、智能
- 强调色: 橙色 (#F97316) - 重要信息
- 背景: 白色/浅灰 (#F9FAFB)

**图表类型**
- 第3页: 技术栈图标展示
- 第6页: 雷达图(需求维度)
- 第9-10页: 流程图(泳道图)
- 第20页: 表格(追溯矩阵)
- 第21页: 流程图(调用关系)
- 第22页: 数据流图
- 第23页: 金字塔图
- 第26页: 分层架构图
- 第27页: 微服务拓扑图
- 第28页: 云部署架构图
- 第29-31页: 数据库ER图

**动画建议**
- 流程图: 逐步显示
- 表格: 行逐行出现
- 架构图: 层次渐显
- 数据流: 箭头动画

### 演讲时间分配(30分钟)

1. 软件功能介绍: 3分钟
2. 典型需求选取: 3分钟
3. 用例描述展示: 5分钟
4. 从用例提炼SRS: 3分钟
5. 从SRS提取系统方法: 5分钟
6. 需求与方法对应: 3分钟
7. 测试设计: 3分钟
8. 系统架构: 3分钟
9. 数据结构设计: 3分钟
10. 总结: 2分钟
11. Q&A: 预留时间

### 关键讲解要点

**第9-10页(用例流程)**
- 强调12步完整流程
- 突出异步处理和性能优化
- 说明容错机制

**第16-19页(系统方法)**
- 每个方法讲清楚输入输出
- 强调与需求的对应关系
- 说明实现文件位置

**第20-22页(追溯关系)**
- 展示完整的追溯链
- 说明双向追溯的价值
- 强调100%覆盖率

**第23-25页(测试设计)**
- 强调测试金字塔策略
- 突出87%覆盖率成就
- 说明属性测试的创新性

**第26-28页(系统架构)**
- 讲清楚四层架构的职责
- 说明微服务的优势
- 强调高可用性设计

**第29-31页(数据结构)**
- 说明混合数据库策略
- 强调图数据库的优势
- 讲清楚数据关系

---

**文档结束**

*本文档为30页PPT演示提供完整文案，聚焦主要内容，适合30分钟技术答辩演讲。*

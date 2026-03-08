# Chinese-English Terminology Mapping Table
# 双语对照映射表

## Purpose
This document provides a comprehensive mapping of Chinese terms to their English equivalents used throughout the codebase. It ensures consistency in terminology across all source code, configuration files, comments, and user interfaces.

## General Terms | 通用术语

| Chinese | English | Context |
|---------|---------|---------|
| 用户 | User | General |
| 权限 | Permission | Authorization |
| 认证 | Authentication | Security |
| 授权 | Authorization | Security |
| 项目 | Project | Domain |
| 仓库 | Repository | Domain |
| 分支 | Branch | Git |
| 提交 | Commit | Git |
| 拉取请求 | Pull Request | Git |
| 合并 | Merge | Git |
| 代码审查 | Code Review | Domain |
| 架构 | Architecture | Domain |
| 依赖 | Dependency | Technical |
| 模块 | Module | Technical |
| 组件 | Component | Technical |
| 服务 | Service | Technical |
| 接口 | Interface/API | Technical |
| 请求 | Request | HTTP |
| 响应 | Response | HTTP |
| 缓存 | Cache | Performance |
| 队列 | Queue | Technical |
| 配置 | Configuration | Technical |
| 环境 | Environment | Technical |

## API Terms | API 术语

| Chinese | English | Context |
|---------|---------|---------|
| 端点 | Endpoint | API |
| 参数 | Parameter | API |
| 返回值 | Return Value | API |
| 状态码 | Status Code | HTTP |
| 请求体 | Request Body | HTTP |
| 响应体 | Response Body | HTTP |
| 头部 | Header | HTTP |
| 拦截器 | Interceptor | HTTP |
| 重试 | Retry | API |
| 超时 | Timeout | API |
| 去重 | Deduplication | API |
| 并发 | Concurrency | API |

## Database Terms | 数据库术语

| Chinese | English | Context |
|---------|---------|---------|
| 数据库 | Database | Storage |
| 表 | Table | Database |
| 字段 | Field/Column | Database |
| 记录 | Record/Row | Database |
| 索引 | Index | Database |
| 查询 | Query | Database |
| 事务 | Transaction | Database |
| 会话 | Session | Database |

## Status Terms | 状态术语

| Chinese | English | Context |
|---------|---------|---------|
| 健康 | Healthy | Status |
| 降级 | Degraded | Status |
| 故障 | Down | Status |
| 待处理 | Pending | Status |
| 处理中 | Processing | Status |
| 已完成 | Completed | Status |
| 失败 | Failed | Status |
| 活跃 | Active | Status |
| 不活跃 | Inactive | Status |

## Severity Terms | 严重程度术语

| Chinese | English | Context |
|---------|---------|---------|
| 信息 | Info | Severity |
| 警告 | Warning | Severity |
| 错误 | Error | Severity |
| 严重 | Critical | Severity |
| 高 | High | Priority |
| 中 | Medium | Priority |
| 低 | Low | Priority |

## Action Terms | 动作术语

| Chinese | English | Context |
|---------|---------|---------|
| 获取 | Get/Fetch | Action |
| 创建 | Create | Action |
| 更新 | Update | Action |
| 删除 | Delete | Action |
| 触发 | Trigger | Action |
| 执行 | Execute | Action |
| 验证 | Validate | Action |
| 检查 | Check | Action |
| 加载 | Load | Action |
| 刷新 | Refresh | Action |
| 保存 | Save | Action |
| 取消 | Cancel | Action |

## Comment Translations | 注释翻译

### Backend Python Comments

| Original Chinese | English Translation |
|-----------------|---------------------|
| 触发code review | Trigger code review |
| useuserconfig的 API key进行review | Uses user-configured API key for review |
| 此endpoint符合prodenv要求 | This endpoint meets production requirements |
| 实现inputverify | Implements input validation |
| containAPIversionInfo | Contains API version info |
| provideprod级APIendpoint | Provides production-level API endpoint |
| 实现全面的errorhandle | Implements comprehensive error handling |
| verifyUUIDformat | Verify UUID format |
| get最新的reviewrecord | Get latest review record |
| checkuser是否有permission访问该project | Check if user has permission to access the project |
| create AI reviewserviceinstance | Create AI review service instance |
| 构建reviewrequest | Build review request |
| 在后台executereview | Execute review in background |
| savereviewresult到database | Save review result to database |

### Frontend TypeScript Comments

| Original Chinese | English Translation |
|-----------------|---------------------|
| 统一的APIrequest客户端 | Unified API request client |
| request去重机制 | Request deduplication mechanism |
| 并发request限制 | Concurrent request limit |
| timeout检测andhint | Timeout detection and hint |
| 指数退避retry | Exponential backoff retry |
| GETrequestcache | GET request caching |
| cache有效期 | Cache validity period |
| 去重时间窗口 | Deduplication time window |
| 自定义retryconfig | Custom retry config |
| setrequestandresponse拦截器 | Setup request and response interceptors |
| request拦截器 - addauth令牌 | Request interceptor - add auth token |
| response拦截器 | Response interceptor |
| handle未authorize访问 | Handle unauthorized access |
| 自动cache | Automatic caching |
| checkcache | Check cache |
| request去重 | Request deduplication |
| 并发控制 | Concurrency control |
| 占用槽位 | Occupy slot |
| 释放槽位 | Release slot |
| 睡眠function | Sleep function |
| 延迟初始化 | Lazy initialization |
| 向后兼容 | Backward compatible |

## UI Text Translations | UI 文本翻译

| Chinese | English | Context |
|---------|---------|---------|
| 加载中... | Loading... | UI State |
| 加载仪表板... | Loading dashboard... | UI State |
| 上次更新: | Last updated: | UI State |
| 刷新 | Refresh | Button |
| 重试 | Retry | Button |
| 活跃用户 | Active Users | Metric |
| 项目总数 | Total Projects | Metric |
| 待处理PR | Pending PRs | Metric |
| 队列任务 | Queued Tasks | Metric |
| 系统健康 | System Health | Metric |
| 数据加载失败 | Failed to load data | Error |
| 刷新数据失败 | Failed to refresh data | Error |

## Architecture Terms | 架构术语

| Chinese | English | Context |
|---------|---------|---------|
| 节点 | Node | Graph |
| 边 | Edge | Graph |
| 依赖图 | Dependency Graph | Architecture |
| 循环依赖 | Circular Dependency | Architecture |
| 组件 | Component | Architecture |
| 模块 | Module | Architecture |
| 复杂度 | Complexity | Metric |
| 健康状态 | Health Status | Metric |
| 违规 | Violation | Architecture |

## Review Terms | 审查术语

| Chinese | English | Context |
|---------|---------|---------|
| 评论 | Comment | Review |
| 建议 | Suggestion | Review |
| 严重程度 | Severity | Review |
| 类别 | Category | Review |
| 代码片段 | Code Snippet | Review |
| 摘要 | Summary | Review |
| 总文件数 | Total Files | Review |
| 总评论数 | Total Comments | Review |

---

## Notes

1. All translations follow GB/T 30269-2013 terminology standards where applicable.
2. English terms are kept concise and do not exceed the character count of the original Chinese.
3. Technical terms are translated consistently across all modules.
4. Context column helps identify the appropriate translation for ambiguous terms.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial creation with comprehensive terminology mapping |

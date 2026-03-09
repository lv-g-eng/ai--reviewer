# 技术债务跟踪

本文档记录项目中的技术债务标记（TODO、FIXME等）及其处理计划。

## 技术债务清单

### 后端 Python代码

#### backend/app/services/agentic_ai_service.py

| 行号 | 标记                                | 优先级 | 描述                       | 状态   |
| ---- | ----------------------------------- | ------ | -------------------------- | ------ |
| ?    | TODO: Implement proper JSON parsing | 中     | 需要实现正确的JSON解析逻辑 | 待处理 |
| ?    | TODO: Implement proper parsing      | 中     | 需要实现正确的解析逻辑     | 待处理 |
| ?    | TODO: Implement proper parsing      | 中     | 需要实现正确的解析逻辑     | 待处理 |

**处理计划**:

1. 评估AI服务返回的JSON结构
2. 实现健壮的JSON解析器
3. 添加错误处理和验证
4. 编写单元测试
   **预估时间**: 2-3天

#### backend/app/api/v1/endpoints/rbac_projects.py

| 行号 | 标记                                                                   | 优先级 | 描述                         | 状态   |
| ---- | ---------------------------------------------------------------------- | ------ | ---------------------------- | ------ |
| ?    | TODO: Validate GitHub CLI token format and potentially test connection | 高     | 需要验证GitHub CLI token格式 | 待处理 |

**处理计划**:

1. 实现GitHub CLI token格式验证
2. 添加连接测试功能
3. 集成到项目管理流程
   **预估时间**: 1天

#### backend/app/api/dependencies.py

| 行号 | 标记                                                                     | 优先级 | 描述                               | 状态   |
| ---- | ------------------------------------------------------------------------ | ------ | ---------------------------------- | ------ |
| ?    | TODO: Re-enable after running migrations to create token_blacklist table | 高     | 数据库迁移后需要重新启用令牌黑名单 | 待处理 |

**处理计划**:

1. 确认token_blacklist表已创建
2. 验证依赖项的正确性
3. 重新启用令牌黑名单功能
   **预估时间**: 0.5天

#### backend/examples/prompt_manager_demo.py

| 行号 | 标记                       | 优先级 | 描述             | 状态   |
| ---- | -------------------------- | ------ | ---------------- | ------ |
| ?    | TODO: Add input validation | 低     | 需要添加输入验证 | 待处理 |

**处理计划**:

1. 使用Pydantic添加输入验证
2. 添加单元测试
   **预估时间**: 0.5天

### 测试代码

#### backend/tests/test_notification_channels.py

| 行号 | 标记             | 优先级 | 描述                    | 状态     |
| ---- | ---------------- | ------ | ----------------------- | -------- |
| 多处 | XXX (测试占位符) | 低     | Slack webhook URL占位符 | 需要替换 |

**处理计划**:

1. 创建测试环境变量
2. 使用环境变量替换硬编码的URL
   **预估时间**: 0.5天

#### backend/scripts/configure_notification_channels.py

| 行号 | 标记             | 优先级 | 描述                    | 状态     |
| ---- | ---------------- | ------ | ----------------------- | -------- |
| 多处 | XXX (示例占位符) | 低     | Slack webhook URL占位符 | 需要替换 |

**处理计划**:

1. 更新文档说明如何配置真实webhook
2. 添加配置示例
   **预估时间**: 0.5天

### 前端 TypeScript代码

#### frontend/src/pages/Architecture.tsx

| 行号 | 标记                                                       | 优先级 | 描述                   | 状态   |
| ---- | ---------------------------------------------------------- | ------ | ---------------------- | ------ |
| ?    | TODO: Implement export using html-to-image directly        | 中     | 需要实现导出功能       | 待处理 |
| ?    | TODO: Re-enable when html-to-image integration is complete | 中     | 导出功能完成后重新启用 | 待处理 |

**处理计划**:

1. 完成html-to-image集成
2. 实现导出功能
3. 添加错误处理
4. 添加用户反馈
   **预估时间**: 2天

#### frontend/src/lib/error-handler.ts

| 行号 | 标记                                                            | 优先级 | 描述             | 状态   |
| ---- | --------------------------------------------------------------- | ------ | ---------------- | ------ |
| ?    | TODO: Integrate with monitoring service (Sentry, DataDog, etc.) | 中     | 需要集成监控服务 | 待处理 |

**处理计划**:

1. 选择监控服务（Sentry或DataDog）
2. 配置监控服务
3. 集成到错误处理器
4. 测试监控功能
   **预估时间**: 1-2天

## 优先级分类

### 高优先级（立即处理）

1. **backend/app/api/dependencies.py** - 令牌黑名单功能
2. **backend/app/api/v1/endpoints/rbac_projects.py** - GitHub CLI token验证

**预计总工作量**: 1.5天

### 中优先级（近期处理）

1. **backend/app/services/agentic_ai_service.py** - AI服务JSON解析
2. **frontend/src/pages/Architecture.tsx** - 导出功能
3. **frontend/src/lib/error-handler.ts** - 监控服务集成

**预计总工作量**: 5-6天

### 低优先级（长期处理）

1. **backend/examples/prompt_manager_demo.py** - 输入验证
2. **backend/tests/test_notification_channels.py** - 测试占位符
3. **backend/scripts/configure_notification_channels.py** - 配置示例

**预计总工作量**: 1.5天

## 处理策略

### 处理原则

1. **安全性优先** - 安全相关的技术债务优先处理
2. **影响评估** - 对用户体验影响大的优先处理
3. **依赖关系** - 被其他功能依赖的优先处理
4. **清理策略** - 过期的TODO标记及时删除

### 处理流程

1. **评估** - 评估技术债务的影响和优先级
2. **计划** - 制定处理计划和时间表
3. **实施** - 实施解决方案
4. **测试** - 编写测试确保修复有效
5. **记录** - 更新技术债务文档

### 预防措施

1. **代码审查** - 代码审查时检查技术债务标记
2. **定期清理** - 定期清理过期的技术债务
3. **文档记录** - 将技术债务记录到本文档
4. **团队沟通** - 团队成员共享技术债务信息

## 进度跟踪

### 2026-03-09

- 创建技术债务跟踪文档
- 识别20个技术债务标记
- 制定优先级处理计划

### 待更新

- 完成高优先级技术债务
- 更新处理状态
- 记录处理结果

## 总结

- **总标记数**: 20个
- **高优先级**: 2个
- **中优先级**: 3个
- **低优先级**: 4个
- **测试相关**: 5个
- **示例/配置**: 6个

**预计总工作量**: 8-10天

---

**创建日期**: 2026-03-09
**最后更新**: 2026-03-09
**维护者**: 开发团队

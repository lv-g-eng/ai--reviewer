# AI Code Review Platform - 文档索引

本文档提供整个项目文档的统一索引，按照功能模块和文档类型组织。

## 文档组织结构

```
.monkeycode/docs/
├── INDEX.md                      # 本文档 - 总索引
├── ARCHITECTURE.md               # 系统架构文档
├── INTERFACES.md                 # API接口文档
├── DEVELOPER_GUIDE.md            # 开发者指南
├── deployment/                   # 部署相关文档
│   ├── DEPLOYMENT_GUIDE.md       # 部署指南
│   ├── SSL_SETUP.md              # SSL配置
│   └── QUICK_START.md            # 快速开始
├── security/                     # 安全相关文档
│   ├── SECURITY_PROCEDURES.md    # 安全流程
│   ├── RBAC_ROLES.md             # RBAC角色说明
│   └── RBAC_MIGRATION.md         # RBAC迁移指南
├── architecture/                 # 架构设计文档
│   ├── SYSTEM_IMPROVEMENTS.md    # 系统改进
│   └── URS_SRS.md                # 需求规格说明书
└── archive/                      # 历史文档归档
    ├── planning/                 # 历史规划文档
    ├── merged/                   # 已合并文档
    └── analysis/                 # 历史分析文档
```

## 快速导航

### 📋 项目概览

- **[README.md](../../README.md)** - 项目主页和快速开始
- **[架构文档](ARCHITECTURE.md)** - 系统架构总览
- **[用户指南](USER_GUIDE.md)** - 用户使用手册

### 🚀 快速开始

- **[快速开始指南](../../QUICK_START.md)** - Docker快速启动
- **[生产环境快速开始](../../QUICK_START_PRODUCTION.md)** - 生产环境部署
- **[Docker快速开始](../../QUICK_START_DOCKER.md)** - Docker部署指南
- **[开发者指南](DEVELOPER_GUIDE.md)** - 开发环境搭建

### 🏗️ 架构设计

- **[系统架构](ARCHITECTURE.md)** - 整体架构设计
- **[AI模块架构](../../docs/AI_MODULE_ARCHITECTURE_EN.md)** - AI分析模块详细设计
- **[系统改进](../../docs/architecture/SYSTEM_IMPROVEMENTS.md)** - 架构改进建议
- **[需求规格](../../docs/architecture/SRS_legacy.md)** - 功能需求规格说明

### 🔧 API文档

- **[API接口文档](INTERFACES.md)** - 统一API接口索引
- **[API文档](../../docs/api/API_DOCUMENTATION.md)** - 完整API参考
- **[OpenAPI规范](../../docs/api/OPENAPI_QUICK_REFERENCE.md)** - OpenAPI快速参考

### 🔐 安全与权限

- **[RBAC角色说明](../../docs/RBAC_ROLES.md)** - 5级角色权限体系
- **[RBAC迁移指南](../../docs/RBAC_MIGRATION_GUIDE.md)** - RBAC迁移步骤
- **[安全流程](../../docs/SECURITY_PROCEDURES.md)** - 安全操作规程
- **[漏洞分类](../../docs/security/CRITICAL_VULNERABILITY_CATEGORIZATION.md)** - 安全漏洞分类

### 📦 部署指南

- **[部署指南](../../DEPLOYMENT.md)** - 完整部署流程
- **[生产环境部署清单](../../PRODUCTION_DEPLOYMENT_CHECKLIST.md)** - 部署检查清单
- **[SSL证书配置](../../docs/SSL_CERTIFICATE_SETUP.md)** - SSL配置指南
- **[环境配置](../../docs/PRODUCTION_ENVIRONMENT_SETUP.md)** - 生产环境配置

### 🛠️ 开发指南

- **[开发者指南](../../docs/guides/DEVELOPMENT.md)** - 开发规范和流程
- **[安装指南](../../docs/guides/INSTALLATION.md)** - 详细安装步骤
- **[LLM集成指南](../../docs/guides/LLM_INTEGRATION_GUIDE.md)** - LLM模型集成
- **[AI代码审查指南](../../docs/guides/AI_PR_REVIEWER_GUIDE.md)** - AI审查功能说明

### 🔍 特性指南

- **[GitHub集成](../../docs/integration/GITHUB_OAUTH_SETUP.md)** - GitHub OAuth集成
- **[数据清理指南](../../docs/guides/DATA_CLEANUP_GUIDE.md)** - 数据清理流程
- **[秘密管理](../../docs/guides/SECRETS_MIGRATION_GUIDE.md)** - 凭证管理指南

### 📊 运维手册

- **[运维手册](../../docs/OPERATIONS_RUNBOOK.md)** - 日常运维操作
- **[故障排查](../../frontend/TROUBLESHOOTING.md)** - 常见问题排查
- **[灾难恢复](../../terraform/DISASTER_RECOVERY_PROCEDURES.md)** - 灾难恢复流程
- **[快速参考](../../docs/RBAC_QUICK_REFERENCE.md)** - RBAC快速参考

### 🎯 项目优化

- **[优化总结](../../PROJECT_OPTIMIZATION_SUMMARY.md)** - 项目优化总览
- **[优化计划](../../.monkeycode/OPTIMIZATION_PLAN.md)** - 详细优化计划
- **[技术债务计划](../../.monkeycode/PHASE4_TECH_DEBT_PLAN.md)** - 技术债务偿还计划

### 📝 历史文档

- **[历史文档索引](archive/INDEX.md)** - 归档文档导航
- **[规划文档](archive/planning/INDEX.md)** - 历史规划文档
- **[已合并文档](archive/merged/INDEX.md)** - 已整合的文档

## 特性规格说明

以下特性规格存储在 `.kiro/specs/` 目录，每个特性包含需求、设计和任务：

- **[企业级RBAC认证](../../.kiro/specs/enterprise-rbac-authentication/)** - RBAC权限系统
- **[生产环境迁移](../../.kiro/specs/production-environment-migration/)** - 生产环境部署
- **[前端生产优化](../../.kiro/specs/frontend-production-optimization/)** - 前端性能优化
- **[代码改进](../../.kiro/specs/project-code-improvements/)** - 代码质量提升
- **[架构层级评估](../../.kiro/specs/architecture-layer-evaluation/)** - 架构评估

## Terraform基础设施

Terraform模块和相关文档存储在 `terraform/` 目录：

- **[Terraform使用指南](../../terraform/USAGE.md)** - Terraform使用说明
- **[快速开始](../../terraform/QUICK_START.md)** - Terraform快速开始
- **[数据库配置](../../terraform/DATABASE_SETUP_GUIDE.md)** - 数据库配置指南
- **[灾难恢复](../../terraform/DISASTER_RECOVERY_PROCEDURES.md)** - 灾难恢复流程

## 前端相关文档

前端相关的技术文档存储在 `frontend/` 目录：

- **[CDN和缓存](../../frontend/CDN_AND_CACHING.md)** - CDN部署和缓存策略
- **[构建优化](../../frontend/BUILD_OPTIMIZATION.md)** - 构建配置优化
- **[响应式设计](../../frontend/RESPONSIVE_LAYOUT_IMPLEMENTATION.md)** - 响应式布局实现
- **[可访问性](../../frontend/ACCESSIBILITY.md)** - 无障碍访问实现

## 后端相关文档

后端相关的技术文档存储在 `backend/` 目录：

- **[任务监控](../../backend/app/tasks/TASK_MONITORING_README.md)** - 任务监控系统
- **[PR分析工作流](../../backend/app/tasks/PR_ANALYSIS_WORKFLOW_README.md)** - PR分析流程
- **[Celery配置](../../backend/app/CELERY_CONFIGURATION_README.md)** - 异步任务配置
- **[服务说明](../../backend/app/services/README.md)** - 后端服务说明

## 项目记忆

- **[MEMORY.md](../../.monkeycode/MEMORY.md)** - 用户指令和项目知识记忆

## 文档状态

### 🟢 已完成

- 核心架构文档
- 部署指南
- API文档
- RBAC权限体系文档

### 🟡 进行中

- 用户使用手册更新
- 运维手册完善
- 性能优化文档

### ⚪ 计划中

- 多语言支持文档
- 高级特性使用指南
- 最佳实践文档

## 更新日志

### 2026-03-09

- 创建统一的文档索引结构
- 整合现有260个Markdown文档
- 建立清晰的文档层次结构

### 2026-03-08

- 完成RBAC权限系统迁移
- 更新AI模块架构文档
- 完成生产环境部署准备

## 文档维护

- 文档维护者：开发团队
- 最后更新：2026-03-09
- 文档版本：v1.0

## 反馈与贡献

如有文档问题或建议，请通过以下方式反馈：

- 提交Issue
- 提交Pull Request改进文档
- 联系项目维护者

---

**注意**：本索引将随着项目发展持续更新，请定期查看最新版本。

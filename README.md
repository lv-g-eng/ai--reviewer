# AI Code Review Platform

AI驱动的代码审查平台，提供智能代码分析、架构审查和合规性检查。

---

## 📋 Table of Contents

### 1. Quick Start (快速开始)

| Document                                                 | Description      |
| -------------------------------------------------------- | ---------------- |
| [QUICK_START.md](./QUICK_START.md)                       | 快速开始指南     |
| [QUICK_START_DOCKER.md](./QUICK_START_DOCKER.md)         | Docker 安装      |
| [QUICK_START_PRODUCTION.md](./QUICK_START_PRODUCTION.md) | 生产环境快速开始 |

### 2. Development (开发)

| Document                                                 | Description  |
| -------------------------------------------------------- | ------------ |
| [CODING_STANDARDS.md](./CODING_STANDARDS.md)             | 编码规范     |
| [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)   | 故障排查指南 |
| [TECHNICAL_DEBT_TRACKER.md](./TECHNICAL_DEBT_TRACKER.md) | 技术债追踪   |
| [缓存管理](#-缓存管理)                                    | 项目缓存管理 |

### 3. Deployment (部署)

| Document                                                                     | Description  |
| ---------------------------------------------------------------------------- | ------------ |
| [DEPLOYMENT.md](./DEPLOYMENT.md)                                             | 部署指南     |
| [PRODUCTION_DEPLOYMENT_CHECKLIST.md](./PRODUCTION_DEPLOYMENT_CHECKLIST.md)   | 生产部署清单 |
| [QUICK_START_PRODUCTION_MIGRATION.md](./QUICK_START_PRODUCTION_MIGRATION.md) | 迁移指南     |

### 4. Project Reports (项目报告)

| Document                                                                               | Description  |
| -------------------------------------------------------------------------------------- | ------------ |
| [PROJECT_OPTIMIZATION_FINAL_SUMMARY.md](./PROJECT_OPTIMIZATION_FINAL_SUMMARY.md)       | 优化总结     |
| [PROJECT_OPTIMIZATION_COMPLETE_SUMMARY.md](./PROJECT_OPTIMIZATION_COMPLETE_SUMMARY.md) | 完整优化报告 |
| [CLEANUP_COMPLETE_SUMMARY.md](./CLEANUP_COMPLETE_SUMMARY.md)                           | 清理总结     |

### 5. Additional (其他文档)

| Document                                                                         | Description  |
| -------------------------------------------------------------------------------- | ------------ |
| [DOCUMENTATION_CONSOLIDATION_REPORT.md](./DOCUMENTATION_CONSOLIDATION_REPORT.md) | 文档整合报告 |
| [TRANSFER_OF_KNOWLEDGE.md](./TRANSFER_OF_KNOWLEDGE.md)                           | 知识转移     |
| [HANDOFF_SUMMARY.md](./HANDOFF_SUMMARY.md)                                       | 交接总结     |

---

## 🚀 Quick Links (快速链接)

| 需求         | 前往                                                   |
| ------------ | ------------------------------------------------------ |
| 新开发者入门 | `QUICK_START.md`                                       |
| 生产部署     | `DEPLOYMENT.md` + `PRODUCTION_DEPLOYMENT_CHECKLIST.md` |
| 编码规范     | `CODING_STANDARDS.md`                                  |
| 故障排查     | `TROUBLESHOOTING_GUIDE.md`                             |
| 缓存管理     | [缓存管理](#-缓存管理)                                  |
| 架构详情     | `docs/ARCHITECTURE.md`                                 |
| API 文档     | `docs/api/`                                            |
| 安全指南     | `docs/SECURITY_PROCEDURES.md`                          |

---

## 📁 Documentation Structure (文档结构)

```
├── Root (当前目录)
│   ├── QUICK_START.md          # 主要快速开始
│   ├── DEPLOYMENT.md          # 部署指南
│   ├── CODING_STANDARDS.md    # 编码规范
│   └── ...
│
├── docs/                       # 详细文档
│   ├── ARCHITECTURE.md         # 系统架构
│   ├── SECURITY_PROCEDURES.md  # 安全指南
│   ├── OPERATIONS_RUNBOOK.md   # 运维手册
│   ├── api/                    # API 文档
│   ├── architecture/            # 架构文档
│   ├── security/               # 安全详情
│   └── ...
│
└── backend/                    # 后端源码
```

---

## 📊 Stats (统计)

| 指标                 | 数量 |
| -------------------- | ---- |
| 根目录 Markdown 文件 | 24   |
| docs 目录文件        | 94+  |
| 总文档数             | 118+ |

---

## 前置要求

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Neo4j 5+

---

## 安装步骤

详细安装步骤见 [QUICK_START.md](./QUICK_START.md)

---

## 🗂️ 缓存管理

### 缓存类型说明

本项目包含多种开发工具生成的缓存文件，用于提高工具性能：

| 缓存类型 | 目录 | 作用 | 大小 | 是否保留 |
|---------|------|------|------|----------|
| MyPy 类型检查 | `.mypy_cache/` | 存储类型检查结果，提升 MyPy 性能 | ~45MB | ✅ 保留 |
| Ruff 代码检查 | `.ruff_cache/` | 缓存 linter 分析结果 | ~8MB | ✅ 保留 |
| Python 字节码 | `__pycache__/` | 编译后的字节码，提升导入速度 | 小 | ✅ 保留 |
| Pytest 测试 | `.pytest_cache/` | 测试运行状态和结果 | 小 | ✅ 保留 |

### 清理缓存

**自动清理脚本：**
```bash
# Python 脚本（推荐）
python scripts/clean_cache.py

# Windows 批处理
scripts/clean_cache.bat
```

**手动清理：**
```bash
# 清理所有缓存
rm -rf .mypy_cache backend/.mypy_cache
rm -rf .ruff_cache backend/.ruff_cache  
rm -rf __pycache__ backend/__pycache__
rm -rf .pytest_cache backend/.pytest_cache

# Windows PowerShell
Remove-Item -Recurse -Force .mypy_cache, backend/.mypy_cache
Remove-Item -Recurse -Force .ruff_cache, backend/.ruff_cache
```

### 何时清理缓存

- 💾 **磁盘空间不足时**
- 🔧 **工具行为异常时** - 缓存可能损坏
- 🐍 **切换 Python 版本后** - 字节码不兼容
- 🔄 **大规模重构后** - 避免过时的缓存信息

### 最佳实践

- ✅ **保留缓存** - 显著提升开发体验
- ✅ **定期清理** - 建议每月清理一次
- ✅ **忽略版本控制** - 已添加到 `.gitignore`
- ✅ **使用清理脚本** - 自动化管理

> **注意：** 这些缓存文件会在下次运行相应工具时自动重新生成，删除不会影响功能。

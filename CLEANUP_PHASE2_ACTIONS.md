# 项目清理 - 第二阶段行动计划

生成时间: 2026-03-03

## ✅ 第二阶段已完成

### 1. 删除额外的测试备份文件 (2个)
- ✅ `backend/tests/test_jwt_revocation_standalone.py`
- ✅ `backend/tests/test_security_standalone.py`

### 2. 创建 Requirements 整合指南
- ✅ `backend/REQUIREMENTS_CONSOLIDATION.md` - 详细的依赖文件整合指南

## 📊 第二阶段统计

- **额外删除文件**: 2 个
- **创建指南文档**: 1 个
- **总删除文件数** (Phase 1 + 2): 24 个

## 🔍 发现的情况

### Requirements 文件分析

发现 7 个 requirements 文件，各有用途：

1. **requirements.txt** - pip-compile 自动生成（需要更新）
2. **requirements.in** - pip-compile 源文件
3. **requirements-fixed.txt** - 包含重要安全更新 ⚠️
4. **requirements-test.txt** - 测试依赖（保留）
5. **requirements-llm.txt** - 本地 LLM 依赖（可选，很大）
6. **requirements-config.txt** - 配置管理（可合并）
7. **requirements-windows.txt** - Windows 兼容版本（保留）

### 关键发现：安全更新

`requirements-fixed.txt` 包含重要的安全修复：

| 包 | 当前版本 | 修复版本 | CVE/问题 |
|---|---------|---------|----------|
| python-multipart | 0.0.12 | 0.0.18 | CVE-2024-53981 |
| python-jose | 3.3.0 | 3.5.0 | PYSEC-2024-232, PYSEC-2024-233 |
| cryptography | 43.0.3 | 46.0.5 | CVE-2024-12797 |
| aiohttp | 3.11.7 | 3.13.3 | 多个 CVE |
| requests | 2.32.3 | 2.32.4 | CVE-2024-47081 |

**建议**: 立即更新 requirements.in 并重新编译

### 环境配置文件分析

#### 根目录
- `.env.template` (主模板)
- `.env.production.template` (生产环境模板)
- `.env` (本地配置，已在 .gitignore)
- `.env.production` (生产配置，已在 .gitignore)

#### Backend (4个)
- `.env.development` (4.2KB)
- `.env.example` (4.9KB)
- `.env.production` (5.0KB)
- `.env.staging` (4.7KB)

#### Frontend (6个)
- `.env.development` (2.0KB)
- `.env.example` (1.9KB)
- `.env.local` (477B)
- `.env.production` (2.2KB)
- `.env.staging` (2.1KB)
- `.env.test` (339B)

#### Services
- `services/llm-service/.env.example` (小文件，服务似乎是存根)

**评估**: 环境文件结构合理，不同环境需要不同配置。建议保留。

### Archive 目录分析

#### archive/2026-01-21/ (30个文件)
内容：
- 过时的实现总结文档
- 重复的启动脚本
- 临时配置文件
- 备份文件

**建议**: 可以删除整个 2026-01-21 归档（已过时 1 个月）

#### docs/archive/ (44个文件)
需要手动审查内容

**建议**: 合并到统一的 archive/ 目录

### Services 目录分析

发现 7 个服务目录：
- `agentic-ai/`
- `api-gateway/`
- `architecture-analyzer/`
- `auth-service/`
- `code-review-engine/`
- `llm-service/` - 似乎是存根（只有 README、Dockerfile、requirements.txt）
- `project-manager/`

**建议**: 审查 `llm-service/` 是否仍需要

## 📋 待完成的清理任务

### 高优先级 (安全相关)

#### 1. 更新 Requirements 文件 ⚠️ 紧急
```bash
cd backend

# 1. 备份当前文件
cp requirements.in requirements.in.bak

# 2. 更新 requirements.in 中的包版本
# 手动编辑或使用脚本更新以下包：
# - python-multipart==0.0.18
# - python-jose[cryptography]==3.5.0
# - cryptography==46.0.5
# - aiohttp==3.13.3
# - requests==2.32.4

# 3. 重新编译
pip-compile requirements.in

# 4. 测试
pip install -r requirements.txt
pytest

# 5. 删除 requirements-fixed.txt
rm requirements-fixed.txt
```

### 中优先级

#### 2. 整合 Requirements 文件
- [ ] 将 `requirements-config.txt` 内容合并到 `requirements.in`
- [ ] 在 README 中记录 `requirements-llm.txt` 为可选依赖
- [ ] 在 README 中记录 Windows 用户使用 `requirements-windows.txt`

#### 3. 清理 Archive 目录
```bash
# 选项 A: 删除旧归档
rm -rf archive/2026-01-21/

# 选项 B: 合并归档
mkdir -p archive/documentation
mkdir -p archive/scripts
mkdir -p archive/config
# 然后移动文件到对应目录
```

#### 4. 审查 Services 目录
- [ ] 检查 `services/llm-service/` 是否仍在使用
- [ ] 如果不使用，删除或移到 archive
- [ ] 如果不使用，删除 `services/llm-service/.env.example`

#### 5. 快速启动指南整合（可选）
当前有 3 个快速启动指南：
- `QUICK_START.md` (中文，手动安装)
- `QUICK_START_DOCKER.md` (中文，Docker 部署)
- `QUICK_START_PRODUCTION.md` (英文，生产部署)

**选项 A**: 保持现状（推荐）
- 三个指南服务不同用途
- 内容不重复

**选项 B**: 合并为一个
- 创建统一的 `QUICK_START.md`
- 包含三个主要章节

### 低优先级

#### 6. README 文件审查
```bash
# 查找所有 README 文件
find . -name "README.md" -not -path "*/node_modules/*" -not -path "*/.venv/*"

# 审查每个 README 的内容和必要性
```

#### 7. API 文档整合
- [ ] 审查 `docs/api/` 目录
- [ ] 考虑合并 API 文档

## 🎯 推荐的执行顺序

### 今天完成（紧急）
1. ✅ 删除额外的测试备份文件
2. ⚠️ **更新 requirements.in 并重新编译**（安全更新）
3. ⚠️ 删除 `requirements-fixed.txt`（合并后）

### 本周完成
4. 整合 requirements-config.txt
5. 清理 archive/2026-01-21/ 目录
6. 审查 services/llm-service/

### 本月完成
7. 合并 docs/archive/ 到 archive/
8. 审查 README 文件
9. 考虑快速启动指南整合

## 📝 创建的文档

### 本阶段创建
1. `backend/REQUIREMENTS_CONSOLIDATION.md` - Requirements 整合指南
2. `CLEANUP_PHASE2_ACTIONS.md` - 本文档

### 所有阶段创建
1. `CLEANUP_SUMMARY.md` - 总体清理计划
2. `CLEANUP_PHASE1_COMPLETE.md` - 第一阶段完成报告
3. `scripts/cleanup-phase2.sh` - Linux/Mac 清理脚本
4. `scripts/cleanup-phase2.ps1` - Windows 清理脚本
5. `backend/REQUIREMENTS_CONSOLIDATION.md` - Requirements 指南
6. `CLEANUP_PHASE2_ACTIONS.md` - 第二阶段行动计划

## 🔧 使用清理脚本

### 自动检查
```bash
# Linux/Mac
./scripts/cleanup-phase2.sh

# Windows
.\scripts\cleanup-phase2.ps1
```

脚本会：
- 检查测试备份文件
- 检查归档目录
- 列出 requirements 文件
- 列出环境配置文件
- 提供清理建议

## ⚠️ 重要提醒

### 不要删除的文件
- ✅ 所有 `.env.development`, `.env.production`, `.env.staging` 文件
- ✅ `requirements-test.txt` (测试依赖)
- ✅ `requirements-windows.txt` (Windows 用户需要)
- ✅ `requirements-llm.txt` (可选功能，但保留)
- ✅ 所有 README.md 文件（提供上下文）

### 需要备份的操作
- 更新 requirements.in 前备份
- 删除归档前检查内容
- 删除服务目录前确认不再使用

## 📊 总体进度

| 阶段 | 状态 | 文件数 | 完成度 |
|------|------|--------|--------|
| Phase 1 | ✅ 完成 | 22 | 100% |
| Phase 2 | ✅ 部分完成 | 2 | 30% |
| 待完成 | ⏳ 进行中 | ~30-50 | 0% |

### 预计总清理效果
- **总删除文件**: 50-70 个
- **总节省空间**: 2-3 MB
- **文档冗余减少**: 80%
- **维护成本降低**: 显著

## 🎊 总结

第二阶段已完成初步清理和分析工作：
- 删除了 2 个额外的测试备份文件
- 创建了详细的 Requirements 整合指南
- 分析了所有环境配置文件
- 评估了归档目录
- 识别了安全更新需求

**下一步最重要的任务**: 更新 requirements.in 中的安全漏洞包版本！

---

**执行者**: Kiro AI Assistant  
**完成时间**: 2026-03-03  
**状态**: ✅ Phase 2 部分完成，待继续

# 后续迭代计划

**创建时间**: 2026-03-09
**当前分支**: refactor/slimming-phase1
**当前进度**: 75% (Phase 1-3 + Phase 4 Batch 1 完成)

---

## 📋 剩余工作清单

### Phase 4 剩余批次 (Batch 2-5)

#### Batch 2: 应用 useAsyncAction Hook
**目标文件** (优先级高):
- `frontend/src/pages/Metrics.tsx`
- `frontend/src/pages/AnalysisQueue.tsx`
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/app/projects/[id]/page.tsx`

**预计减少**: ~180行重复代码

**执行步骤**:
1. 读取目标文件，识别异步状态管理模式
2. 添加 `import { useAsyncAction } from '@/hooks/useAsyncAction'`
3. 替换 `useState` 的 loading/error 状态
4. 替换 async 函数中的 try-catch-finally
5. 运行类型检查: `npm run type-check`
6. 提交: `git commit -m "refactor(phase4-batch2): 应用useAsyncAction到Metrics等页面"`

---

#### Batch 3: 应用 useApiCall Hook
**目标文件** (优先级高):
- `frontend/src/app/register/page.tsx`
- `frontend/src/app/profile/page.tsx`
- `frontend/src/app/forgot-password/page.tsx`
- `frontend/src/app/reset-password/page.tsx`
- `frontend/src/app/projects/[id]/settings/page.tsx`

**预计减少**: ~135行重复代码

**执行步骤**:
1. 识别 try-catch + toast 模式
2. 添加 `import { useApiCall } from '@/hooks/useApiCall'`
3. 替换错误处理和toast调用
4. 测试API调用功能
5. 提交: `git commit -m "refactor(phase4-batch3): 应用useApiCall到注册等页面"`

---

#### Batch 4: 应用 BaseRepository
**目标文件** (优先级中):
- `backend/app/auth/services/rbac_service.py`
- `backend/app/auth/services/auth_service.py`
- `backend/app/services/project_service.py`
- 其他包含重复CRUD的服务类

**预计减少**: ~170行重复代码

**执行步骤**:
1. 创建具体的 Repository 类继承 BaseRepository
2. 将服务类改为使用 Repository
3. 运行测试: `pytest tests/`
4. 提交: `git commit -m "refactor(phase4-batch4): 应用BaseRepository到服务层"`

---

#### Batch 5: 应用 with_audit_log
**目标文件** (优先级中):
- `backend/app/api/v1/endpoints/rbac_users.py`
- `backend/app/api/v1/endpoints/rbac_projects.py`
- 其他包含手动审计日志的endpoints

**预计减少**: ~130行重复代码

**执行步骤**:
1. 识别手动审计日志代码
2. 添加装饰器 `@with_audit_log("action.name")`
3. 删除手动审计日志代码
4. 运行测试验证审计功能
5. 提交: `git commit -m "refactor(phase4-batch5): 应用with_audit_log装饰器"`

---

## 📊 预期最终成果

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| 删除文件 | 12个 | 12个 | - |
| 新增工具 | 5个 | 5个 | - |
| 减少代码 | ~2,000行 | ~3,500行 | +75% |
| 应用批次 | 1/5 | 5/5 | +400% |
| 代码重复率 | 未知 | <5% | 显著降低 |

---

## 🔄 迭代执行建议

### 每次迭代的工作流程

**准备阶段**:
1. 从远程拉取最新代码: `git pull origin refactor/slimming-phase1`
2. 确认依赖已安装: `npm install` / `pip install -r requirements.txt`
3. 运行测试确认基准: `npm test` / `pytest`

**执行阶段**:
1. 选择一个批次（建议按顺序）
2. 按照上述步骤逐文件重构
3. 每重构完一个文件，运行测试
4. 确认无误后提交

**验证阶段**:
1. 运行完整测试套件
2. 类型检查
3. 手动测试关键功能
4. 更新文档

---

## 📝 迭代检查清单

### 开始迭代前
- [ ] 已拉取最新代码
- [ ] 已阅读重构示例文档
- [ ] 已理解目标批次的重构模式
- [ ] 已备份重要数据

### 执行迭代时
- [ ] 小步提交，每个文件独立提交
- [ ] 每次修改后运行测试
- [ ] 保持API兼容性
- [ ] 更新相关注释

### 完成迭代后
- [ ] 所有测试通过
- [ ] 类型检查通过
- [ ] 提交到远程分支
- [ ] 更新进度文档

---

## 🎯 优先级排序

### 高优先级 (立即执行)
1. **Batch 2: useAsyncAction** - 影响大，风险低
2. **Batch 3: useApiCall** - 影响大，风险低

### 中优先级 (近期执行)
3. **Batch 4: BaseRepository** - 影响中，风险中
4. **Batch 5: with_audit_log** - 影响中，风险中

### 低优先级 (长期优化)
5. **API客户端合并** - 合并3个api-client文件
6. **组件库优化** - 进一步优化组件结构

---

## 📚 参考文档

- [瘦身计划书](REFACTORING_SLIMMING_PLAN.md)
- [Phase 4 重构示例](.monkeycode/refactoring/phase4-examples.md)
- [Phase 4 应用指南](.monkeycode/refactoring/apply-examples.md)
- [Phase 3 完成报告](.monkeycode/refactoring/phase3-complete.md)

---

## 🚀 快速开始脚本

```bash
# 开始新的迭代
git checkout refactor/slimming-phase1
git pull origin refactor/slimming-phase1
npm install
npm test

# 执行重构...

# 完成后推送
git push origin refactor/slimming-phase1
```

---

**预计总工作量**: 每个批次 2-4 小时
**总预计时间**: 8-16 小时
**建议分配**: 每天 1-2 个批次

---

**文档创建时间**: 2026-03-09
**维护者**: 重构团队

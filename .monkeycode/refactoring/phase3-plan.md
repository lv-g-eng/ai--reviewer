# Phase 3: 提取与抽象方案

**开始时间**: 2026-03-09
**分支**: refactor/slimming-phase1
**状态**: 🔄 进行中

---

## 目标

从重复代码中提取通用工具函数和Hooks，减少约 **1,500行重复代码**。

---

## 任务清单

### 1. 前端 Hooks (优先级: 高)

- [ ] **useApiCall** - 统一API调用和错误处理
  - 影响: 10+ 文件，~150行
  - 位置: `frontend/src/hooks/useApiCall.ts`
  
- [ ] **useAsyncAction** - 异步操作状态管理
  - 影响: 15+ 文件，~200行
  - 位置: `frontend/src/hooks/useAsyncAction.ts`

- [ ] **Logger** - 统一日志工具
  - 影响: 20+ 文件，~100行
  - 位置: `frontend/src/lib/utils/logger.ts`

### 2. 后端基类 (优先级: 中)

- [ ] **BaseRepository** - 数据库操作基类
  - 影响: 8+ 文件，~200行
  - 位置: `backend/app/core/repository.py`

- [ ] **with_audit_log** - 审计日志装饰器
  - 影响: 10+ 文件，~150行
  - 位置: `backend/app/core/decorators.py`

---

## 执行顺序

1. 创建 Logger 工具 (最简单，影响最大)
2. 创建 useAsyncAction hook
3. 创建 useApiCall hook
4. 创建 BaseRepository 类
5. 创建 with_audit_log 装饰器

---

## 验证标准

- [ ] 所有新工具都有单元测试
- [ ] TypeScript类型完整
- [ ] 文档注释完善
- [ ] 至少1个组件/服务使用新工具

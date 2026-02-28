# Next.js 开发服务器启动检查清单

## ✅ 启动前检查

- [ ] Node.js 版本 >= 18.0.0 (`node --version`)
- [ ] npm 版本 >= 9.0.0 (`npm --version`)
- [ ] 端口 3000 未被占用
- [ ] 有足够的磁盘空间（至少 1GB）

## ✅ 清理步骤（如果遇到问题）

```powershell
# 1. 停止所有 Node 进程
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. 进入前端目录
cd frontend

# 3. 删除缓存和构建文件
Remove-Item -Recurse -Force .next, .swc -ErrorAction SilentlyContinue

# 4. （可选）重新安装依赖
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
npm install

# 5. 启动开发服务器
npm run dev
```

## ✅ 验证步骤

启动后，检查以下内容：

### 1. 终端输出
应该看到：
```
▲ Next.js 16.1.6
- Local:        http://localhost:3000
✓ Ready in X.Xs
```

### 2. 浏览器访问
- [ ] 打开 `http://localhost:3000`
- [ ] 页面正常加载（不是 404）
- [ ] 看到 AI Code Review Platform 主页
- [ ] 没有控制台错误

### 3. 文件系统
- [ ] `frontend/.next` 目录存在
- [ ] `frontend/.next/cache` 目录存在
- [ ] `frontend/node_modules` 目录存在

## ❌ 常见问题

### 问题 1: 404 Not Found - 静态资源
**症状：** 浏览器显示 404 错误，缺少 `/_next/static/...` 文件

**解决方案：**
```powershell
cd frontend
Remove-Item -Recurse -Force .next, .swc
npm run dev
```

### 问题 2: EADDRINUSE - 端口已占用
**症状：** `Error: listen EADDRINUSE: address already in use :::3000`

**解决方案：**
```powershell
# 查找占用端口的进程
netstat -ano | findstr :3000

# 终止进程（替换 <PID> 为实际进程 ID）
Stop-Process -Id <PID> -Force

# 或使用不同端口
npm run dev -- -p 3001
```

### 问题 3: Module not found
**症状：** `Error: Cannot find module 'next'` 或类似错误

**解决方案：**
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules, package-lock.json
npm install
npm run dev
```

### 问题 4: 页面空白
**症状：** 页面加载但显示空白

**可能原因：**
1. 后端 API 未运行（检查 `http://localhost:8000`）
2. 环境变量配置错误（检查 `.env.development`）
3. JavaScript 错误（打开浏览器控制台）

**解决方案：**
1. 启动后端服务器
2. 检查 `.env.development` 文件
3. 查看浏览器控制台错误

### 问题 5: 编译错误
**症状：** 终端显示 TypeScript 或 ESLint 错误

**解决方案：**
```powershell
# 检查类型错误
npm run type-check

# 修复 ESLint 错误
npm run lint:fix

# 如果错误持续，尝试清理
Remove-Item -Recurse -Force .next, tsconfig.tsbuildinfo
npm run dev
```

## 🔍 调试技巧

### 查看详细日志
```powershell
# 启动时显示详细日志
$env:DEBUG="*"
npm run dev
```

### 检查构建输出
```powershell
# 查看 .next 目录内容
Get-ChildItem -Recurse frontend/.next | Select-Object FullName
```

### 测试生产构建
```powershell
# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

## 📞 获取帮助

如果以上方法都无法解决问题：

1. 查看 `frontend/TROUBLESHOOTING.md` - 详细故障排除指南
2. 查看 `frontend/START_DEV_SERVER.md` - 启动服务器指南
3. 检查项目根目录的 `QUICK_START.md`
4. 查看 Next.js 官方文档：https://nextjs.org/docs

## ✨ 成功标志

当一切正常时，你应该：

- ✅ 终端显示 "Ready in X.Xs"
- ✅ 浏览器能访问 `http://localhost:3000`
- ✅ 看到完整的主页内容
- ✅ 热重载正常工作（修改文件后自动刷新）
- ✅ 没有控制台错误
- ✅ 可以导航到不同页面

恭喜！你的开发环境已经准备就绪！🎉

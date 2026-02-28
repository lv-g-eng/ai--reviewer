# Next.js 开发服务器故障排除

## 问题：404 错误 - 缺少静态资源

如果你看到类似以下的错误：
```
404 Not Found: /_next/static/chunks/fallback/main.js
404 Not Found: /_next/static/chunks/fallback/react-refresh.js
404 Not Found: /favicon.ico
```

这表明 Next.js 构建缓存已损坏或不完整。

## 快速修复方案

### 方案 1：使用自动修复脚本（推荐）

**Windows (PowerShell):**
```powershell
cd frontend
.\fix-nextjs.ps1
```

**Linux/Mac (Bash):**
```bash
cd frontend
chmod +x fix-nextjs.sh
./fix-nextjs.sh
```

### 方案 2：手动修复步骤

1. **停止开发服务器**
   - 按 `Ctrl+C` 停止正在运行的服务器
   - 或关闭运行服务器的终端窗口

2. **清理构建缓存**
   ```bash
   cd frontend
   rm -rf .next .swc node_modules/.cache
   ```
   
   Windows PowerShell:
   ```powershell
   cd frontend
   Remove-Item -Recurse -Force .next, .swc, node_modules/.cache -ErrorAction SilentlyContinue
   ```

3. **重新安装依赖（可选但推荐）**
   ```bash
   npm install
   ```

4. **重启开发服务器**
   ```bash
   npm run dev
   ```

## 常见原因

1. **不完整的构建** - 开发服务器在构建过程中被中断
2. **版本冲突** - Node.js 或 npm 版本与 Next.js 不兼容
3. **损坏的缓存** - `.next` 目录中的缓存文件损坏
4. **端口冲突** - 端口 3000 被其他进程占用

## 验证修复

修复后，你应该能够：

1. 访问 `http://localhost:3000` 而不出现 404 错误
2. 看到页面正常加载
3. 热重载（HMR）正常工作

## 如果问题仍然存在

### 检查 Node.js 版本
```bash
node --version  # 应该是 >= 18.0.0
npm --version   # 应该是 >= 9.0.0
```

### 检查端口占用
```bash
# Linux/Mac
lsof -i :3000

# Windows
netstat -ano | findstr :3000
```

### 完全重置（最后手段）
```bash
cd frontend
rm -rf node_modules package-lock.json .next .swc
npm install
npm run dev
```

## 预防措施

1. **优雅地停止服务器** - 始终使用 `Ctrl+C` 而不是强制关闭终端
2. **定期清理** - 每周运行一次 `rm -rf .next .swc`
3. **保持更新** - 定期更新 Next.js 和依赖项
4. **使用 Git** - 确保 `.next` 和 `.swc` 在 `.gitignore` 中

## 相关文件

- `package.json` - 依赖配置
- `next.config.mjs` - Next.js 配置
- `.next/` - 构建输出目录（自动生成）
- `.swc/` - SWC 编译器缓存（自动生成）

## 需要更多帮助？

如果以上方法都不起作用，请检查：
1. Next.js 官方文档：https://nextjs.org/docs
2. GitHub Issues：https://github.com/vercel/next.js/issues
3. 项目的 `package.json` 确保依赖版本兼容

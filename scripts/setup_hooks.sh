#!/bin/bash
# 设置Git Hooks脚本

echo "🔧 设置Git Hooks..."

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是Git仓库"
    exit 1
fi

# 创建hooks目录（如果不存在）
mkdir -p .git/hooks

# 复制pre-commit hook
if [ -f ".github/hooks/pre-commit" ]; then
    cp .github/hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook 已安装"
else
    echo "⚠️ Pre-commit hook 文件不存在"
fi

# 创建commit-msg hook（检查提交信息格式）
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# Commit message format checker

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# 检查提交信息格式
if [[ ! "$COMMIT_MSG" =~ ^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+ ]]; then
    echo "❌ 提交信息格式不正确"
    echo ""
    echo "正确格式: type(scope): description"
    echo ""
    echo "类型 (type):"
    echo "  feat:     新功能"
    echo "  fix:      修复bug"
    echo "  docs:     文档更新"
    echo "  style:    代码格式调整"
    echo "  refactor: 重构代码"
    echo "  test:     测试相关"
    echo "  chore:    构建/工具相关"
    echo ""
    echo "示例:"
    echo "  feat(auth): add user login validation"
    echo "  fix(api): resolve null pointer exception"
    echo "  docs: update README installation guide"
    echo ""
    exit 1
fi

# 检查提交信息长度
if [ ${#COMMIT_MSG} -gt 100 ]; then
    echo "⚠️ 提交信息过长 (${#COMMIT_MSG} 字符)，建议控制在100字符以内"
fi

exit 0
EOF

chmod +x .git/hooks/commit-msg
echo "✅ Commit-msg hook 已安装"

# 创建pre-push hook（运行完整质量检查）
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook for comprehensive quality checks

echo "🚀 运行推送前质量检查..."

# 检查是否有质量检查脚本
if [ -f "scripts/quality_check.sh" ]; then
    # 运行完整质量检查
    if ! bash scripts/quality_check.sh; then
        echo "❌ 质量检查失败，推送被阻止"
        echo "请修复问题后重新推送"
        exit 1
    fi
else
    echo "⚠️ 质量检查脚本不存在，跳过检查"
fi

echo "✅ 推送前检查通过"
exit 0
EOF

chmod +x .git/hooks/pre-push
echo "✅ Pre-push hook 已安装"

echo ""
echo "🎉 Git Hooks 设置完成！"
echo ""
echo "已安装的hooks:"
echo "  - pre-commit:  提交前快速检查"
echo "  - commit-msg:  提交信息格式检查"
echo "  - pre-push:    推送前完整质量检查"
echo ""
echo "💡 提示:"
echo "  - 如需跳过hooks，使用 git commit --no-verify"
echo "  - 建议在提交前运行 bash scripts/quality_check.sh"
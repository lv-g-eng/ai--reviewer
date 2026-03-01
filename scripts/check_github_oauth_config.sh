#!/bin/bash

# GitHub OAuth 配置检查脚本
# 用于诊断 GitHub OAuth 配置问题

echo "=================================="
echo "GitHub OAuth 配置检查"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. 检查根目录 .env 文件
echo "1. 检查根目录 .env 配置..."
if [ -f ".env" ]; then
    check_pass ".env 文件存在"
    
    # 检查 GITHUB_CLIENT_ID
    if grep -q "GITHUB_CLIENT_ID=" .env; then
        CLIENT_ID=$(grep "GITHUB_CLIENT_ID=" .env | cut -d '=' -f2)
        if [ -n "$CLIENT_ID" ] && [ "$CLIENT_ID" != "" ]; then
            check_pass "GITHUB_CLIENT_ID 已配置: $CLIENT_ID"
        else
            check_fail "GITHUB_CLIENT_ID 为空"
        fi
    else
        check_fail "GITHUB_CLIENT_ID 未配置"
    fi
    
    # 检查 GITHUB_CLIENT_SECRET
    if grep -q "GITHUB_CLIENT_SECRET=" .env; then
        SECRET=$(grep "GITHUB_CLIENT_SECRET=" .env | cut -d '=' -f2)
        if [ -n "$SECRET" ] && [ "$SECRET" != "" ]; then
            check_pass "GITHUB_CLIENT_SECRET 已配置 (长度: ${#SECRET})"
        else
            check_fail "GITHUB_CLIENT_SECRET 为空"
        fi
    else
        check_fail "GITHUB_CLIENT_SECRET 未配置"
    fi
else
    check_fail ".env 文件不存在"
fi

echo ""

# 2. 检查前端 .env.local 文件
echo "2. 检查前端 .env.local 配置..."
if [ -f "frontend/.env.local" ]; then
    check_pass "frontend/.env.local 文件存在"
    
    # 检查 NEXT_PUBLIC_GITHUB_CLIENT_ID
    if grep -q "NEXT_PUBLIC_GITHUB_CLIENT_ID=" frontend/.env.local; then
        FRONTEND_CLIENT_ID=$(grep "NEXT_PUBLIC_GITHUB_CLIENT_ID=" frontend/.env.local | cut -d '=' -f2)
        if [ -n "$FRONTEND_CLIENT_ID" ] && [ "$FRONTEND_CLIENT_ID" != "" ]; then
            check_pass "NEXT_PUBLIC_GITHUB_CLIENT_ID 已配置: $FRONTEND_CLIENT_ID"
            
            # 检查前后端 Client ID 是否一致
            if [ "$CLIENT_ID" = "$FRONTEND_CLIENT_ID" ]; then
                check_pass "前后端 Client ID 一致"
            else
                check_warn "前后端 Client ID 不一致！"
                echo "  后端: $CLIENT_ID"
                echo "  前端: $FRONTEND_CLIENT_ID"
            fi
        else
            check_fail "NEXT_PUBLIC_GITHUB_CLIENT_ID 为空"
        fi
    else
        check_fail "NEXT_PUBLIC_GITHUB_CLIENT_ID 未配置"
    fi
    
    # 检查 NEXT_PUBLIC_BACKEND_URL
    if grep -q "NEXT_PUBLIC_BACKEND_URL=" frontend/.env.local; then
        BACKEND_URL=$(grep "NEXT_PUBLIC_BACKEND_URL=" frontend/.env.local | cut -d '=' -f2)
        check_pass "NEXT_PUBLIC_BACKEND_URL: $BACKEND_URL"
    else
        check_warn "NEXT_PUBLIC_BACKEND_URL 未配置"
    fi
else
    check_fail "frontend/.env.local 文件不存在"
    echo "  请从 frontend/.env.example 复制并配置"
fi

echo ""

# 3. 检查后端 .env 文件
echo "3. 检查后端 .env 配置..."
if [ -f "backend/.env.development" ]; then
    check_pass "backend/.env.development 文件存在"
else
    check_warn "backend/.env.development 文件不存在（可选）"
fi

echo ""

# 4. 提供配置建议
echo "=================================="
echo "配置建议"
echo "=================================="
echo ""

if [ -n "$CLIENT_ID" ]; then
    echo "您的 GitHub OAuth 应用配置："
    echo ""
    echo "Client ID: $CLIENT_ID"
    echo ""
    echo "需要在 GitHub OAuth 应用中配置的回调 URL："
    echo ""
    echo "  开发环境："
    echo "    http://localhost:3000/api/github/callback"
    echo ""
    echo "  生产环境（根据实际域名修改）："
    echo "    https://your-domain.com/api/github/callback"
    echo ""
    echo "配置步骤："
    echo "  1. 访问: https://github.com/settings/developers"
    echo "  2. 找到 Client ID 为 $CLIENT_ID 的应用"
    echo "  3. 在 'Authorization callback URL' 中添加上述 URL"
    echo "  4. 保存更改"
    echo ""
fi

# 5. 检查服务运行状态
echo "=================================="
echo "服务运行状态检查"
echo "=================================="
echo ""

# 检查前端端口
if command -v lsof &> /dev/null; then
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        check_pass "前端服务运行在端口 3000"
    else
        check_warn "前端服务未在端口 3000 运行"
    fi
    
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        check_pass "后端服务运行在端口 8000"
    else
        check_warn "后端服务未在端口 8000 运行"
    fi
elif command -v netstat &> /dev/null; then
    if netstat -an | grep -q ":3000.*LISTEN"; then
        check_pass "前端服务运行在端口 3000"
    else
        check_warn "前端服务未在端口 3000 运行"
    fi
    
    if netstat -an | grep -q ":8000.*LISTEN"; then
        check_pass "后端服务运行在端口 8000"
    else
        check_warn "后端服务未在端口 8000 运行"
    fi
else
    check_warn "无法检查端口状态（lsof 和 netstat 都不可用）"
fi

echo ""
echo "=================================="
echo "检查完成"
echo "=================================="
echo ""
echo "如果仍有问题，请查看详细文档："
echo "  docs/GITHUB_OAUTH_SETUP.md"
echo ""

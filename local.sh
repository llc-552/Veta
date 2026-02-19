#!/bin/bash

################################################################################
# 🎓 智能教案与PPT生成系统 - 本地快速启动脚本
# Intelligent Lesson Plan and Teaching PPT Generation System
# Linux/Unix 版本
################################################################################

set -e  # 遇到错误立即退出

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 主程序开始
print_header "🎓 Veta 智能教案与PPT生成系统"
echo ""
print_success "检测到 Conda 环境已配置，开始启动服务..."
echo ""

# --- 第一步：创建必要的目录结构 ---
print_header "第一步：创建项目目录"
echo ""

DIRS=(
    "rag_data"
    "faiss_index"
    "generated_lessons"
    "generated_lessons/pptx"
    "generated_lessons/docx"
    "generated_lessons/json"
    "generated_lessons/markdown"
    "templates/ppt_templates"
    "logs"
)

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_success "目录创建: $dir"
    else
        print_success "目录已存在: $dir"
    fi
done

echo ""

# --- 第二步：检查并安装依赖 ---
print_header "第二步：检查并安装依赖"
echo ""

if [ -f "requirements.txt" ]; then
    print_warning "检查缺失的依赖..."
    conda run -n veta pip install -q -r requirements.txt
    print_success "依赖检查完成"
else
    print_error "未找到 requirements.txt 文件"
    exit 1
fi

echo ""

# --- 第三步：检查配置文件 ---
print_header "第三步：检查配置文件"
echo ""

if [ ! -f "config.yaml" ]; then
    if [ -f "config.example.yaml" ]; then
        print_warning "config.yaml 不存在，从 config.example.yaml 复制..."
        cp config.example.yaml config.yaml
        print_warning "请编辑 config.yaml 文件并填写您的 API 密钥:"
        echo "  - OpenAI API Key (或其他 LLM 服务)"
        echo "  - Redis 服务器地址和端口"
        echo ""
        read -p "按 Enter 键继续..."
    else
        print_error "config.yaml 和 config.example.yaml 都不存在"
        exit 1
    fi
else
    print_success "config.yaml 已存在"
fi

# --- 第三步：配置代理（可选）---
print_header "第三步：配置网络代理（可选）"
echo ""

# 统一代理格式：使用 HTTP 代理，兼容性最强
PROXY_HOST="${PROXY_HOST:-127.0.0.1}"
PROXY_PORT="${PROXY_PORT:-7897}"

if [ -n "$http_proxy" ]; then
    export http_proxy="http://${PROXY_HOST}:${PROXY_PORT}"
    export https_proxy="http://${PROXY_HOST}:${PROXY_PORT}"
    export all_proxy="http://${PROXY_HOST}:${PROXY_PORT}"
    print_success "代理已配置: http://${PROXY_HOST}:${PROXY_PORT}"
else
    print_warning "未配置代理"
fi

echo ""

# --- 第四步：启动应用服务 ---
print_header "第四步：启动 Veta 后端服务"
echo ""

PORT=${PORT:-3367}
HOST=${HOST:-0.0.0.0}

print_success "服务配置："
echo "  - 服务地址: http://localhost:$PORT"
echo "  - 绑定地址: $HOST"
echo "  - 模式: 开发模式（自动重载）"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 在 veta conda 环境中启动 Uvicorn
exec conda run -n veta uvicorn main.app:app --reload --host $HOST --port $PORT

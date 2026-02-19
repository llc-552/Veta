#!/bin/bash
# =====================================
# Veta 智能教案与PPT生成系统启动脚本
# =====================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印颜色输出
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 主函数
main() {
    print_header "🎓 Veta 智能教案与PPT生成系统启动"

    # 检查conda
    if ! command -v conda &> /dev/null; then
        print_error "Conda 未找到，请先安装 Anaconda 或 Miniconda"
        exit 1
    fi

    print_success "Conda 已检测到"

    # 获取conda路径
    CONDA_PATH=$(conda info --base)
    source "$CONDA_PATH/etc/profile.d/conda.sh"

    # 检查虚拟环境
    print_info "正在检查虚拟环境: veta"
    if conda env list | grep -q "veta"; then
        print_success "虚拟环境 veta 已存在"
    else
        print_error "虚拟环境 veta 不存在，请先创建"
        exit 1
    fi

    # 激活虚拟环境
    print_info "激活虚拟环境..."
    conda activate veta
    print_success "虚拟环境已激活"

    # 检查依赖
    print_info "检查依赖..."
    python -c "
import sys
required = ['fastapi', 'uvicorn', 'pydantic', 'langgraph', 'langchain', 'pptx', 'docx']
missing = []
for pkg in required:
    try:
        __import__(pkg.replace('-', '_'))
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'❌ 缺失依赖: {missing}')
    sys.exit(1)
else:
    print('✅ 所有依赖已安装')
" || {
        print_error "依赖检查失败"
        exit 1
    }

    # 检查配置文件
    print_info "检查配置文件..."
    if [ -f "config.yaml" ]; then
        print_success "配置文件已存在: config.yaml"
    else
        print_error "配置文件不存在: config.yaml"
        exit 1
    fi

    # 启动服务
    print_header "🚀 启动 FastAPI 服务器"
    echo ""
    echo "📍 服务地址: http://localhost:3367"
    echo "📍 前端地址: http://localhost:3367"
    echo ""
    echo "按 Ctrl+C 停止服务"
    echo ""

    python -m uvicorn main.app:app \
        --host 0.0.0.0 \
        --port 3367 \
        --reload \
        --reload-dir main
}

# 运行主函数
main "$@"


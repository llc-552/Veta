#!/bin/bash
# 启动服务脚本

echo "================================"
echo "🎓 Veta 智能教案与PPT生成系统"
echo "================================"
echo ""

# 检查环境
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found"
    exit 1
fi

# 获取conda的激活脚本路径
CONDA_PATH=$(conda info --base)
source "$CONDA_PATH/etc/profile.d/conda.sh"

# 激活虚拟环境
echo "📦 Activating Conda environment: veta"
conda activate veta

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate conda environment"
    exit 1
fi

echo "✅ Environment activated"
echo ""

# 启动服务
echo "🚀 Starting FastAPI server..."
echo "📍 Server will be available at: http://localhost:3367"
echo ""

python -m uvicorn main.app:app --host 0.0.0.0 --port 3367 --reload


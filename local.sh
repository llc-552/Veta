#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- 关键修正：统一代理格式 ---
# 将 socks 统一改为 http 或 socks5h (推荐用 http，兼容性最强)
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export all_proxy="http://127.0.0.1:7897"



# 启动 Uvicorn
echo "正在启动 Veta 后端服务 (端口 3367)..."
uvicorn main.app:app --reload --port 3367

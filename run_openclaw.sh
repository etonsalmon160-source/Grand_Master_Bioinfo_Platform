#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "[*] 首次运行：正在创建虚拟环境 venv 并安装依赖..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "[*] 正在校验依赖环境..."
pip install -r requirements.txt -q


echo "[*] 启动 OpenClaw 软件界面..."
exec streamlit run bioinfo_app.py --server.headless true

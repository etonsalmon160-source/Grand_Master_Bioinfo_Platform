#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "[*] 首次运行：正在创建虚拟环境 venv 并安装依赖..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -q
else
    source venv/bin/activate
fi

echo "[*] 启动 OpenClaw 软件界面..."
exec streamlit run openclaw_app.py --server.headless true

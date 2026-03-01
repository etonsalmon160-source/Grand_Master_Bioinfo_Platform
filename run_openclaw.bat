@echo off
chcp 65001 >nul
title OpenClaw 生信工作流
cd /d "%~dp0"

if not exist "venv" (
    echo [*] 首次运行：正在创建虚拟环境 venv 并安装依赖...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt -q
) else (
    call venv\Scripts\activate.bat
)

echo [*] 启动 OpenClaw 软件界面...
streamlit run openclaw_app.py --server.headless true
pause

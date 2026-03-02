@echo off
chcp 65001 >nul
title OpenClaw 生信工作流
cd /d "%~dp0"

if not exist "venv" (
    echo [*] 首次运行：正在创建虚拟环境 venv 并安装依赖...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [*] 正在校验依赖环境...
pip install -r requirements.txt -q


echo [*] 启动 OpenClaw 本地独立客户端架构 (Native Window)...
python openclaw_desktop.py
pause

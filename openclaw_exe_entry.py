import os
import sys


def main():
    """
    Windows EXE 入口：
    - 打包后双击 OpenClaw.exe 即可启动 Streamlit UI
    - 自动切换到项目根目录，确保相对路径（如 Run_GSE*_Results）正确
    """
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后的 exe 所在目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 源码运行时的当前文件所在目录
        base_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base_dir)

    # 以库方式调用 Streamlit，而不是依赖外部命令行
    try:
        from streamlit.web import cli as stcli  # 新版入口
    except ImportError:
        import streamlit.web.cli as stcli       # 旧版兼容

    # 构造等价于：streamlit run openclaw_app.py
    sys.argv = [
        "streamlit",
        "run",
        "openclaw_app.py",
        "--server.headless", "false",  # 允许自动打开浏览器
    ]
    stcli.main()


if __name__ == "__main__":
    main()


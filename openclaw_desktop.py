import os
import sys
import subprocess
import time
import requests
import webview

def launch_desktop():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # 1. Hide terminal window if starting on Windows (optional for purely console-less wrapper)
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass
    
    # 2. Start Streamlit via subprocess to isolate its signal handling
    python_exe = sys.executable
    print(f"Starting backend with {python_exe}...")
    
    # Inject an environment variable so the app knows it's running as a desktop native app
    env = os.environ.copy()
    env["OPENCLAW_IS_DESKTOP"] = "1"

    proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "bioinfo_app.py", "--server.headless", "true", "--server.port", "8503"],
        cwd=base_dir,
        env=env
    )


    url = "http://localhost:8503"
    print("Waiting for OpenClaw Core Engine to initialize...")
    
    # 3. Poll local server until it responds
    for _ in range(30):
        try:
            if requests.get(url, timeout=1).status_code == 200:
                print("Engine connected!")
                break
        except Exception:
            pass
        time.sleep(1)
        
    print("Launching Native Window...")
    # 4. Create an OS native window framing the local server
    window = webview.create_window('Grand Master | Precision Bioinfo', url, width=1440, height=900)
    
    # 5. Start the native messaging loop (blocks until window is closed)
    webview.start(private_mode=False)
    
    # 6. Once the native window is closed, gracefully kill the backend process
    proc.terminate()

if __name__ == '__main__':
    launch_desktop()

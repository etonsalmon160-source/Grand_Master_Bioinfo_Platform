import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import json
import requests
import threading
from master_bioinfo_suite import MasterBioinfoPipeline
from custom_geo_parser import fetch_real_geo_matrix_with_genes

# ==========================================
# 🚀 GRAND MASTER ULTIMATE SYSTICK (v2.6.2)
# ==========================================
st.set_page_config(
    page_title="Grand Master | Neural Bioinfo Engine",
    page_icon="🧬",
    layout="wide",
)

# --- FILE-BASED LIVE LOGGING (MOST ROBUST) ---
LOG_FILE = "openclaw_live.log"

def reset_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] [INFO] 🛡️ Neural Core Online. System Secure.\n")

def add_log(msg, status="INFO"):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] [{status}] {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    # Also print to black console
    print(line.strip())

def get_logs():
    if not os.path.exists(LOG_FILE): 
        reset_log()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []

if not os.path.exists(LOG_FILE):
    reset_log()

# --- STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    :root {
        --bg-main: #020617;
        --accent-glow: #38bdf8;
        --terminal-green: #4ade80;
    }
    .stApp { background: radial-gradient(circle at top right, #0f172a, #020617); color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
    .console-module {
        background-color: #000;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        padding: 1.2rem;
        height: 350px;
        overflow-y: auto;
        color: var(--terminal-green);
        box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
    }
    .console-line { margin-bottom: 4px; font-size: 0.85rem; line-height: 1.4; }
    .console-ts { color: #64748b; margin-right: 10px; }
    .premium-card { background: rgba(30,31,46,0.5); border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px); }
    </style>
""", unsafe_allow_html=True)

# --- CONFIG MANAGEMENT ---
_CONFIG_PATH = "openclaw_config.json"
def load_config():
    if os.path.exists(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r") as f: return json.load(f)
        except: pass
    return {"api_url": "", "api_key": ""}

# --- SESSION STATE ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analyzing" not in st.session_state: st.session_state.analyzing = False

def main():
    cfg = load_config()
    
    with st.sidebar:
        st.markdown("<h1 style='color: #fff; font-weight: 800; margin-bottom: 0;'>OpenClaw</h1>", unsafe_allow_html=True)
        st.caption("ULTIMATE BIOINFO AGENT • v2.6.2")
        st.divider()
        with st.expander("🛠️ API 配置 (Configuration)"):
            st.text_input("Endpoint", value=cfg.get("api_url", ""))
            st.text_input("API Key", type="password")
        st.markdown("---")
        if os.getenv("OPENCLAW_IS_DESKTOP"): st.success("💻 Local Desktop Node")
        else: st.info("☁️ Cloud Remote Node")

    st.markdown("## 🛰️ 综合指挥调度台 (Command Center)")
    
    t1, t2, t3 = st.tabs(["🚀 分析任务 (Jobs)", "📊 分析结果 (Results)", "🌐 社区 (Forum)"])
    
    with t1:
        col_main, col_console = st.columns([3, 2])
        
        with col_main:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("#### 📁 数据流注入 (Data Source)")
            geo_input = st.text_area("输入 GSE 编号 (多编号空格分隔)", placeholder="e.g. GSE31210 GSE30219", height=80)
            
            if st.button("🔥 启动全流程分析 (RUN ANALYSIS)", use_container_width=True):
                if not geo_input:
                    st.warning("⚠️ 请输入有效的 GSE 编号！")
                else:
                    st.session_state.analyzing = True
                    reset_log()
                    add_log(f"任务启动: {geo_input}")
                    
                    # ASYNC COMPUTATION THREAD
                    def background_analysis(gse_text):
                        try:
                            add_log("📡 探测分析意图: 正在调度数据节点...")
                            target_gse = gse_text.strip().split()[0]
                            add_log(f"📡 正在从 NCBI 数据库下载 {target_gse} (此步耗时由国际宽带决定)...")
                            
                            counts, meta = fetch_real_geo_matrix_with_genes(target_gse)
                            add_log(f"✅ 数据解析成功: {counts.shape[0]} 探针 x {counts.shape[1]} 样本")
                            
                            pipeline = MasterBioinfoPipeline(out_dir="Web_Analysis_Output")
                            add_log("🚀 启动自动化分析矩阵: 正在执行归一化与 PCA...")
                            pipeline.run_pre_processing(custom_counts=counts, custom_meta=meta)
                            
                            add_log("📊 执行差异表达分析 (DEA)...")
                            pipeline.run_dea()
                            
                            add_log("🔥 正在生成差异基因表达热图 (Heatmap)...")
                            pipeline.run_deg_heatmap()
                            
                            add_log("🧬 执行机器学习特征筛选 (Random Forest)...")
                            pipeline.run_advanced_ml()
                            
                            add_log("📈 拟合 Kaplan-Meier 临床生存曲线...")
                            pipeline.run_survival()
                            
                            add_log("🏁 任务大功告成。结果已进入可视化看板。")
                            st.session_state.analyzing = False
                        except Exception as e:
                            add_log(f"❌ 运行报错: {str(e)}", "ERROR")
                            st.session_state.analyzing = False

                    thread = threading.Thread(target=background_analysis, args=(geo_input,))
                    thread.daemon = True
                    thread.start()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.analyzing:
                st.markdown("<div style='text-align: center; margin-top:20px;'><div style='width: 40px; height: 40px; border: 4px solid #38bdf8; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px auto;'></div><span style='color: #38bdf8;'>OpenClaw 正在全力计算中...</span><style>@keyframes spin { to { transform: rotate(360deg); } }</style></div>", unsafe_allow_html=True)
                time.sleep(3) # Slower heartbeat to prevent flickering
                st.rerun()

        with col_console:
            st.markdown("#### 📟 实时控制面板 (Live Log)")
            # Log rendering from the file buffer
            lines = get_logs()
            console_html = "<div class='console-module'>"
            for line in reversed(lines[-25:]): # Show last 25 lines
                # Format: [HH:MM:SS] [LEVEL] MESSAGE
                try:
                    ts = line.split("]")[0].strip("[")
                    content = line.split("] ", 1)[1]
                    color = "#4ade80" if "INFO" in line else "#f87171"
                    console_html += f"<div class='console-line'><span class='console-ts'>[{ts}]</span> <span style='color:{color}'>{content}</span></div>"
                except:
                    console_html += f"<div class='console-line'>{line}</div>"
            console_html += "</div>"
            st.markdown(console_html, unsafe_allow_html=True)

            st.markdown("#### 🤖 交流官指令")
            u_input = st.chat_input("输入对话内容...")
            if u_input:
                st.session_state.chat_history.append({"role": "user", "content": u_input})
                st.rerun()

    with t2:
        out_dir = "Web_Analysis_Output"
        if os.path.exists(out_dir) and os.listdir(out_dir):
            files = sorted([f for f in os.listdir(out_dir) if f.endswith(".png")])
            for f in files: st.image(os.path.join(out_dir, f), caption=f)
        else: st.warning("暂无分析结果图，请在 Jobs 选项卡启动任务。")

    with t3:
        st.info("请访问 GitHub Discussions 参与讨论：[OpenClaw Community](https://github.com/etonsalmon160-source/Grand_Master_Bioinfo_Platform/discussions)")

if __name__ == "__main__":
    main()

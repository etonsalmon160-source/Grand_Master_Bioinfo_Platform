import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import json
import requests
from master_bioinfo_suite import MasterBioinfoPipeline

# ==========================================
# 💎 ULTIMATE ELITE UI CONFIG: CYBER-RESEARCH AESTHETIC
# ==========================================
st.set_page_config(
    page_title="Grand Master | Neural Bioinfo Engine",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS Injection - Dark Glassmorphism & High-Contrast CLI Accents
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --bg-main: #020617; /* Slate 950 */
        --bg-sidebar: #0f172a; /* Slate 900 */
        --card-bg: rgba(30, 41, 59, 0.7); /* Slate 800 with opacity */
        --border-color: rgba(51, 65, 85, 0.5); /* Slate 700 with opacity */
        --accent-glow: #38bdf8; /* Sky 400 */
        --terminal-green: #4ade80; /* Green 400 */
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    /* Global Base Styling */
    .stApp {
        background: radial-gradient(circle at top right, #0f172a, #020617);
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Hide Streamlit Native Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color);
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
    }
    
    /* Branding */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        background: linear-gradient(to bottom right, #fff, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    /* Console/Terminal Styling */
    .console-module {
        background-color: #000;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        padding: 1rem;
        color: var(--terminal-green);
        box-shadow: inset 0 0 20px rgba(74, 222, 128, 0.05);
        margin-bottom: 1rem;
        height: 300px;
        overflow-y: auto;
    }

    .console-line {
        margin-bottom: 2px;
        font-size: 0.8rem;
        opacity: 0.9;
        line-height: 1.2;
    }

    .console-timestamp {
        color: #64748b;
        margin-right: 8px;
    }

    /* Professional Card */
    .premium-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(12px);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }

    /* Tabs Layout */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-glow) !important;
        border-bottom: 2px solid var(--accent-glow) !important;
    }
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

def save_config(cfg):
    with open(_CONFIG_PATH, "w") as f: json.dump(cfg, f, indent=4)

# --- PERSISTENT LOG SYSTEM ---
# We use @st.cache_resource to ensure the log list object persists across script reruns
@st.cache_resource
def get_shared_logs():
    return [{"t": time.time(), "m": "🛡️ Neural Core Online. System Secure.", "s": "INFO"}]

SHARED_LOGS = get_shared_logs()

def add_log(msg, status="INFO"):
    SHARED_LOGS.append({"t": time.time(), "m": msg, "s": status})
    # Also print to target console (the black box) for double assurance
    print(f"[{status}] {msg}")

# Initialize Session State Variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analyzing" not in st.session_state:
    st.session_state.analyzing = False

def main():
    cfg = load_config()
    
    # --- SIDEBAR: CONTROL & CONFIG ---
    with st.sidebar:
        st.markdown("<h1 class='brand-title'>OpenClaw</h1>", unsafe_allow_html=True)
        st.caption("ULTIMATE BIOINFO AGENT • v2.6.0")
        
        st.markdown("---")
        with st.expander("🛠️ 系统配置 (API & Settings)", expanded=False):
            api_url = st.text_input("Interpretation API Endpoint", value=cfg.get("api_url", ""))
            api_key = st.text_input("API Access Key", value=cfg.get("api_key", ""), type="password")
            if st.button("保存并同步配置"):
                cfg["api_url"] = api_url
                cfg["api_key"] = api_key
                save_config(cfg)
                st.success("配置已写入内核文件")
        
        st.markdown("### 🔬 算法参数中心")
        p_thresh = st.slider("Significant P-value", 0.001, 0.1, 0.05, step=0.005)
        fc_thresh = st.slider("Fold Change (log2)", 0.5, 5.0, 1.0, step=0.1)
        
        st.markdown("---")
        IS_DESKTOP = os.getenv("OPENCLAW_IS_DESKTOP", "0") == "1"
        if IS_DESKTOP:
            st.success("💻 **本地终极版 (Native Core)**")
            st.caption("免鉴权模式，尊享最高算力权限。")
        else:
            st.info("☁️ **Cloud Remote Node**")
            
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-top:20px;'>
            <div style='font-size: 0.8rem; color: #64748b;'>DEVELOPER</div>
            <div style='font-weight: 600; color: #fff;'>Eto (eto10)</div>
            <div style='font-size: 0.7rem; color: #475569;'>Bioinformatics Automation Architect</div>
        </div>
        """, unsafe_allow_html=True)

    # --- MAIN UI LAYOUT ---
    st.markdown("## 🛰️ 综合指挥调度台 (Command Center)")
    
    tab_analysis, tab_results, tab_community = st.tabs(["🚀 任务调度 (Analysis)", "📊 分析结果 (Results)", "🌐 社区广场 (Forum)"])
    
    with tab_analysis:
        col_main, col_console = st.columns([3, 2])
        
        with col_main:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("#### 📁 数据流注入 (Data Stream)")
            
            # Smart Input Area
            geo_input = st.text_area("输入 GSE 编号或自然语言描述", placeholder="例如: GSE31210 GSE30219\n或者: 帮我找两个肺腺癌数据集并执行深度分析", height=100)
            
            st.markdown("---")
            c_file1, c_file2 = st.columns(2)
            with c_file1:
                exp_file = st.file_uploader("表达谱 (Expression Matrix)", type=["csv", "txt"])
            with c_file2:
                meta_file = st.file_uploader("元数据 (Clinical Metadata)", type=["csv", "txt"])
            
            if st.button("🔥 执行全量自动化流程 (RUN ANALYSIS)", use_container_width=True):
                if not geo_input and (not exp_file or not meta_file):
                    st.error("🚨 错误: 未检测到有效的 GSE ID 或本地数据流！")
                else:
                    st.session_state.analyzing = True
                    add_log(f"任务初始化成功: 路由匹配至 {geo_input[:15] if geo_input else 'Local Matrix'}")
                    
                    # ASYNCHRONOUS THREADED ENGINE
                    # This prevents the UI from freezing during long downloads or heavy calculations
                    import threading
                    from custom_geo_parser import fetch_real_geo_matrix_with_genes

                    def analysis_worker():
                        try:
                            add_log("📡 正在启动数据引擎...")
                            # 1. Fetching Data
                            if geo_input:
                                target_gse = geo_input.strip().split()[0]
                                add_log(f"📡 正在从 NCBI 数据库拉取 {target_gse} (大型数据集可能耗时 1-3 分钟)...")
                                counts, meta = fetch_real_geo_matrix_with_genes(target_gse)
                            else:
                                counts = pd.read_csv(exp_file, index_col=0)
                                meta = pd.read_csv(meta_file, index_col=0)
                            
                            add_log(f"✅ 数据解析就绪: {counts.shape[0]} 探针 x {counts.shape[1]} 样本")
                            
                            # 2. Pipeline Core
                            pipeline = MasterBioinfoPipeline(out_dir="Web_Analysis_Output")
                            add_log("🚀 启动自动化分析矩阵: 正在执行归一化与 PCA...")
                            pipeline.run_pre_processing(custom_counts=counts, custom_meta=meta)
                            
                            add_log("📊 执行差异表达分析 (DEA)...")
                            pipeline.run_dea()
                            
                            add_log("🧬 执行机器学习特征筛选 (Random Forest)...")
                            pipeline.run_ml_biomarkers()
                            
                            add_log("📈 正在拟合 Kaplan-Meier 临床生存曲线...")
                            pipeline.run_survival()
                            
                            add_log("🏁 任务全流程执行完毕。正在同步结果至看板...")
                            st.session_state.analyzing = False
                        except Exception as e:
                            add_log(f"❌ 运行报错: {str(e)}", "ERROR")
                            st.session_state.analyzing = False

                    # Start the thread
                    thread = threading.Thread(target=analysis_worker)
                    thread.daemon = True # Ensure thread dies if UI closes
                    thread.start()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # Results Preview placeholder
            if st.session_state.analyzing:
                st.markdown("""
                    <div style='text-align: center; padding: 20px; border: 1px dashed #38bdf8; border-radius:10px; background: rgba(56, 189, 248, 0.05);'>
                        <div style='width: 3rem; height: 3rem; margin: auto; border: 4px solid #38bdf8; border-top-color: transparent; border-radius: 50%; animation: spinner .8s linear infinite;'></div>
                        <p style='color: #38bdf8; margin-top: 15px; font-weight: 500; font-size: 1.1rem;'>📊 算力引擎正在疯狂运行中...<br><span style='font-size: 0.8rem; font-weight: 400; color: #64748b;'>请通过右侧实时日志监控后台进度，请勿刷新或关闭窗口</span></p>
                        <style>@keyframes spinner { to { transform: rotate(360deg); } }</style>
                    </div>
                """, unsafe_allow_html=True)
                
                # Use a slower but safer refresh to avoid flickering and "stuck" feeling
                time.sleep(3)
                st.rerun()
        
        with col_console:
            st.markdown("#### 📟 实时控制面板 (Live Console)")
            # Log Console Area - Reading from Persistent Shared Buffer
            log_html = "<div class='console-module'>"
            for l in SHARED_LOGS[::-1]: # Show newest first
                ts = time.strftime('%H:%M:%S', time.localtime(l['t']))
                color = "#4ade80" if l['s'] == "INFO" else "#f87171"
                log_html += f"<div class='console-line'><span class='console-timestamp'>[{ts}]</span> <span style='color:{color}'>{l['m']}</span></div>"
            log_html += "</div>"
            st.markdown(log_html, unsafe_allow_html=True)
            
            st.markdown("#### 🤖 指令通信官 (OpenClaw Agent)")
            # Chat interface for instructions
            for chat in st.session_state.chat_history[-3:]:
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])
            
            u_input = st.chat_input("输入科研指令交流...")
            if u_input:
                st.session_state.chat_history.append({"role": "user", "content": u_input})
                add_log(f"接收到用户指令: {u_input[:20]}...")
                # Simple logic for simulation
                if "肺腺癌" in u_input or "luad" in u_input:
                    ans = "🤖 意图识别: 肺腺癌 (LUAD)。系统已为您锁定训练集 GSE31210 与验证集 GSE30219。是否现在启动交叉验证？"
                else:
                    ans = f"🤖 已接收指令。正在解析 '{u_input}' 中的生信逻辑..."
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                st.rerun()

    with tab_results:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        out_dir = "Web_Analysis_Output"
        if not os.path.exists(out_dir) or not os.listdir(out_dir):
            st.warning("⚠️ 暂无分析记录。请在'任务调度'选项卡中启动分析任务。")
        else:
            # Dynamic Rendering System: Scans the output folder for generated PNGs
            files = os.listdir(out_dir)
            png_files = sorted([f for f in files if f.endswith(".png")])
            
            if not png_files:
                st.info("🔄 模型计算中... 尚未生成可视化图表。")
            else:
                res_tab_core, res_tab_ml, res_tab_surv = st.tabs(["🧬 核心图谱", "🤖 机器学习", "📈 临床预后"])
                
                with res_tab_core:
                    # PCA, Heatmap, Volcano
                    core_figs = [f for f in png_files if any(x in f.upper() for x in ["PCA", "HEATMAP", "VOLCANO", "DEA"])]
                    if core_figs:
                        for f in core_figs:
                            st.image(os.path.join(out_dir, f), caption=f.replace(".png", ""), use_container_width=True)
                    else: st.caption("尚未生成核心图谱。")

                with res_tab_ml:
                    # ML features, performance
                    ml_figs = [f for f in png_files if any(x in f.upper() for x in ["ML", "FEATURE", "RF", "IMPORTANCE"])]
                    if ml_figs:
                        for f in ml_figs:
                            st.image(os.path.join(out_dir, f), caption=f.replace(".png", ""), use_container_width=True)
                    else: st.caption("尚未生成机器学习评估图表。")

                with res_tab_surv:
                    # Survival curves
                    surv_figs = [f for f in png_files if any(x in f.upper() for x in ["SURVIVAL", "KM", "PROGNOSIS"])]
                    if surv_figs:
                        for f in surv_figs:
                            st.image(os.path.join(out_dir, f), caption=f.replace(".png", ""), use_container_width=True)
                    else: st.caption("尚未生成临床预后分析图表。")
                
                st.success(f"📊 成功加载 {len(png_files)} 个分析视窗。")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_community:
        st.markdown("<div class='premium-card' style='border-left: 4px solid var(--accent-glow);'>", unsafe_allow_html=True)
        st.markdown("### 🌐 Grand Master 开发者社区 (Developer Community)")
        st.markdown("""
            <p style='color: var(--text-secondary); margin-top: 5px; font-size: 0.95rem;'>
                为了保障最佳的交互体验与隐私安全，我们建议您前往原生的 GitHub Discussions 平台参与讨论。
                在这里，您可以：
            </p>
            <ul style='color: var(--text-secondary); font-size: 0.9rem;'>
                <li>✍️ 提交您的创新科研成果或分析案例</li>
                <li>🧬 申请新的生信分析模块或功能点</li>
                <li>🛠️ 获得开发者 Eto 对复杂报错的深度技术支持</li>
            </ul>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # High-End Action Buttons
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            st.markdown("""
                <div style='background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.2); padding: 20px; border-radius: 12px;'>
                    <div style='font-size: 1.1rem; font-weight: 600; color: #38bdf8; margin-bottom: 15px;'>✍️ 发起技术讨论</div>
                    <p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 20px;'>提出问题或分享您的生信分析流程心得。</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("前往 GitHub Discussions", "https://github.com/etonsalmon160-source/Grand_Master_Bioinfo_Platform/discussions/new/choose", use_container_width=True)
        
        with c_f2:
            st.markdown("""
                <div style='background: rgba(74, 222, 128, 0.05); border: 1px solid rgba(74, 222, 128, 0.2); padding: 20px; border-radius: 12px;'>
                    <div style='font-size: 1.1rem; font-weight: 600; color: #4ade80; margin-bottom: 15px;'>📢 浏览社区动态</div>
                    <p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 20px;'>查看全球研究者关于 OpenClaw 的最新讨论。</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("进入社区主页", "https://github.com/etonsalmon160-source/Grand_Master_Bioinfo_Platform/discussions", use_container_width=True)
        
        st.divider()
        st.info("💡 **提效建议**：您可以收藏该讨论链接，或在 GitHub 仓库点击 'Star' 以随时跟踪最新更新。")

if __name__ == "__main__":
    main()

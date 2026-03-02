import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import json
import requests
import threading
import streamlit.components.v1 as components
import re

from master_bioinfo_suite import MasterBioinfoPipeline
from custom_geo_parser import fetch_real_geo_matrix_with_genes

# GSE 编号正则
GSE_PATTERN = re.compile(r"GSE\d+", re.IGNORECASE)

def parse_gse_from_text(text: str, api_url: str = "", api_key: str = "") -> list[str]:
    if not text or not text.strip(): return []
    found = GSE_PATTERN.findall(text)
    
    if not found and api_url and api_key:
        try:
            add_log("🤖 正在调用 LLM 意图解析引擎... (API 请求中)")
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a bioinformatics assistant. Convert the disease/condition provided by the user into exactly ONE widely-used GEO GSE dataset ID (like GSE31210). Return ONLY the GSE ID string and nothing else. Ensure the dataset corresponds correctly."},
                    {"role": "user", "content": f"Find a high-quality human transcriptomic dataset for: {text}"}
                ]
            }
            resp = requests.post(f"{api_url}/chat/completions", headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                found = GSE_PATTERN.findall(content)
                if found:
                    add_log(f"🧠 LLM 推荐使用数据集: {found[0]}")
        except Exception as e:
            add_log(f"⚠️ NLP 推理受阻: {str(e)}", "WARNING")

    if not found:
        text_l = text.lower()
        if "肺腺癌" in text_l or "luad" in text_l or "lung adenocarcinoma" in text_l:
            if "一" in text_l or "1" in text_l: found = ["GSE31210"]
            elif "三" in text_l or "3" in text_l: found = ["GSE31210", "GSE30219", "GSE19188"]
            else: found = ["GSE31210", "GSE30219"]
        elif "鳞癌" in text_l or "lusc" in text_l: found = ["GSE73403"]
    
    seen = set()
    unique = []
    for g in found:
        g_upper = g.upper()
        if g_upper not in seen:
            seen.add(g_upper)
            unique.append(g_upper)
    return unique

# ==========================================
# 🚀 GRAND MASTER ULTIMATE SYSTICK (v2.6.6)
# ==========================================
st.set_page_config(
    page_title="Grand Master | Neural Bioinfo Engine",
    page_icon="🧬",
    layout="wide",
)

# --- FILE-BASED LIVE LOGGING ---
LOG_FILE = "openclaw_live.log"

def hard_reset_log():
    if os.path.exists(LOG_FILE):
        try: os.remove(LOG_FILE)
        except: pass
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] [INFO] 🛡️ Neural Core Online. System Secure.\n")

def add_log(msg, status="INFO"):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] [{status}] {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def get_logs():
    if not os.path.exists(LOG_FILE): 
        hard_reset_log()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []

if not os.path.exists(LOG_FILE):
    hard_reset_log()

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
    height: 400px;
    overflow-y: auto;
    color: var(--terminal-green);
    box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
}
.console-line { margin-bottom: 4px; font-size: 0.85rem; line-height: 1.4; }
.console-ts { color: #64748b; margin-right: 10px; }
.premium-card { background: rgba(30,31,46,0.5); border: 1px solid rgba(255,255,255,0.05); padding: 25px; border-radius: 12px; backdrop-filter: blur(10px); }
.custom-btn { display: inline-block; width: 100%; margin-top: 10px; }
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
        st.caption("ULTIMATE BIOINFO AGENT • GUI Edition")
        st.divider()
        with st.expander("🛠️ API 配置 (Configuration)"):
            api_url = st.text_input("Endpoint", value=cfg.get("api_url", "https://api.openai.com/v1"))
            api_key = st.text_input("API Key", type="password", value=cfg.get("api_key", ""))
            if st.button("💾 保存/更新配置", use_container_width=True):
                with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump({"api_url": api_url, "api_key": api_key}, f)
                st.success("配置已成功存入本地文件！")
        
        st.markdown("---")
        st.markdown("#### 💬 开发者专区")
        if st.button("🌐 访问开发者社区 (Forum)", use_container_width=True):
             st.info("请在右侧页面点击 '社区 (Forum)' 选项卡进行深度互动。")
        
        st.markdown("#### ⚙️ 差异分析设置 (DEA Settings)")
        p_val = st.slider("p-value 阈值", 0.0, 0.5, 0.05, 0.01)
        fc_val = st.slider("log2FC (倍数) 阈值", 0.0, 5.0, 1.0, 0.1)
        p_type = st.selectbox("p-value 类型", ["padj", "pvalue"], index=0, help="推荐使用 padj (FDR 校正后的 p 值)")
        
        st.markdown("---")
        if os.getenv("OPENCLAW_IS_DESKTOP"): st.success("💻 Local Desktop Node")
        else: st.info("☁️ Cloud Remote Node")

    st.markdown("## 🛰️ 综合指挥调度台 (Command Center)")
    
    t1, t2, t3 = st.tabs(["🚀 分析任务 (Jobs)", "📊 分析结果 (Results)", "🌐 社区 (Forum)"])
    
    with t1:
        # Changed columns ratio for a more balanced GUI lookup
        col_main, col_console = st.columns([1, 1])
        
        with col_main:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("#### 📁 数据流注入 (Data Source)")
            geo_input = st.text_area("输入 GSE 编号 (多编号空格分隔)", placeholder="e.g. GSE31210 GSE30219", height=80)
            
            def trigger_analysis(input_txt, is_nl=False, p_thresh=0.05, fc_thresh=1.0, p_type='padj'):
                st.session_state.analyzing = True
                hard_reset_log()
                add_log(f"任务启动指令收到: {input_txt}")
                
                out_dir = "Web_Analysis_Output"
                if os.path.exists(out_dir):
                    import shutil
                    try: shutil.rmtree(out_dir)
                    except: pass
                os.makedirs(out_dir, exist_ok=True)

                def background_analysis(text, is_natural_language, p_thresh, fc_thresh, p_type):
                    try:
                        target_gses = parse_gse_from_text(text, api_url=api_url, api_key=api_key) if is_natural_language else text.strip().split()
                        if not target_gses:
                            add_log("[ERROR] 未能在知识库或 LLM 中找到对应的 GSE 编号。任务中止。", "ERROR")
                            return

                        target_gse = target_gses[0]
                        add_log(f"📡 已锁定计算目标: {target_gse}")
                        add_log(f"📡 正在从 NCBI 数据库下载 {target_gse} (此步耗时由国际宽带决定)...")
                        
                        counts, meta = fetch_real_geo_matrix_with_genes(target_gse)
                        add_log(f"✅ 数据解析成功: {counts.shape[0]} 探针 x {counts.shape[1]} 样本")
                        
                        # 暴露数据为原始 CSV
                        add_log("📥 保存处理后的矩阵与临床打分表到本地...")
                        counts.to_csv(os.path.join(out_dir, "Expression_Matrix.csv"))
                        meta.to_csv(os.path.join(out_dir, "Clinical_Metadata.csv"))
                        
                        pipeline = MasterBioinfoPipeline(out_dir=out_dir)
                        add_log("🚀 启动自动化分析矩阵: 正在执行归一化与 PCA...")
                        pipeline.run_pre_processing(custom_counts=counts, custom_meta=meta)
                        
                        add_log(f"📊 执行差异表达分析 (DEA) [P<{p_thresh}, FC>{fc_thresh}]...")
                        pipeline.run_dea(p_thresh=p_thresh, fc_thresh=fc_thresh, p_type=p_type)
                        
                        add_log("🔥 正在生成差异基因表达热图 (Heatmap)...")
                        pipeline.run_deg_heatmap()
                        
                        add_log("🧬 执行机器学习特征筛选 (Random Forest)...")
                        pipeline.run_advanced_ml()
                        
                        add_log("📈 拟合 Kaplan-Meier 临床生存曲线...")
                        pipeline.run_survival()
                        
                        add_log("🧬 执行功能富集分析 (GO/KEGG)...")
                        pipeline.run_enrichment()
                        
                        add_log("📝 正在撰写自动化生信综合分析报告...")
                        pipeline.generate_report()
                        
                        add_log("[DONE] 任务大功告成。结果已进入可视化看板。")
                    except Exception as e:
                        add_log(f"[ERROR] 运行中断: {str(e)}", "ERROR")

                thread = threading.Thread(target=background_analysis, args=(input_txt, is_nl, p_thresh, fc_thresh, p_type))
                thread.daemon = True
                thread.start()

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔥 标准 GSE 启动", use_container_width=True, help="直接输入 GSE 号进行精准分析"):
                    if not geo_input: st.warning("⚠️ 请输入正确的 GSE 编号！")
                    else:
                        trigger_analysis(geo_input, is_nl=False, p_thresh=p_val, fc_thresh=fc_val, p_type=p_type)
                        st.rerun()
            with col_btn2:
                if st.button("🧠 语义分析启动", use_container_width=True, help="使用自然语言描述你的需求 (如: '帮我分析肺腺癌数据')"):
                    if not geo_input: st.warning("⚠️ 请输入你的分析需求！")
                    else:
                        trigger_analysis(geo_input, is_nl=True, p_thresh=p_val, fc_thresh=fc_val, p_type=p_type)
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True) 

            if st.session_state.analyzing:
                lines = get_logs()
                is_finished = any("[DONE]" in l or "[ERROR]" in l for l in lines)
                if is_finished:
                    st.session_state.analyzing = False
                    st.rerun()
                else:
                    st.markdown("<div style='text-align: center; margin-top:30px;'><div style='width: 50px; height: 50px; border: 4px solid #38bdf8; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px auto;'></div><span style='color: #38bdf8; font-size: 1.1rem; font-weight: 600;'>Neural Engine 正在高速运转...</span><style>@keyframes spin { to { transform: rotate(360deg); } }</style></div>", unsafe_allow_html=True)
                    time.sleep(2.5) 
                    st.rerun()

            # Result path notification
            out_dir = os.path.abspath("Web_Analysis_Output")
            if os.path.exists(out_dir) and not st.session_state.analyzing:
                st.info(f"📁 **结果已保存至本地：**\n`{out_dir}`")

        with col_console:
            st.markdown("#### 📟 实时控制面板 (Live Log)")
            lines = get_logs()
            console_html = "<div class='console-module'>"
            for line in reversed(lines[-30:]):
                try:
                    ts = line.split("]")[0].strip("[")
                    content = line.split("] ", 1)[1]
                    color = "#4ade80" if "INFO" in line else "#f87171"
                    if "[DONE]" in line: color = "#38bdf8"
                    console_html += f"<div class='console-line'><span class='console-ts'>[{ts}]</span> <span style='color:{color}'>{content}</span></div>"
                except:
                    console_html += f"<div class='console-line'>{line}</div>"
            console_html += "</div>"
            st.markdown(console_html, unsafe_allow_html=True)

            st.markdown("#### 🤖 疾病AI分析助手 (NL to Dataset)")
            u_input = st.chat_input("想研究什么疾病？(例如：lung adenocarcinoma)")
            if u_input:
                st.session_state.chat_history.append({"role": "user", "content": u_input})
                trigger_analysis(u_input, is_nl=True)
                st.rerun()

    with t2:
        out_dir = "Web_Analysis_Output"
        if os.path.exists(out_dir) and os.listdir(out_dir):
            files = sorted([f for f in os.listdir(out_dir) if f.endswith(".png")])
            for f in files: 
                col_img, col_btn = st.columns([5, 1])
                with col_img: st.image(os.path.join(out_dir, f), caption=f)
                with col_btn:
                    with open(os.path.join(out_dir, f), "rb") as file:
                        img_bytes = file.read()
                    st.download_button(label="📥 下载图片", data=img_bytes, file_name=f, mime="image/png", key=f"dl_img_{f}", use_container_width=True)
            
            # Also show markdown reports if any
            md_files = sorted([f for f in os.listdir(out_dir) if f.endswith(".md")])
            for f in md_files:
                st.markdown(f"**报告/文本: {f}**")
                with open(os.path.join(out_dir, f), "r", encoding="utf-8") as file:
                    md_text = file.read()
                st.download_button(label=f"📥 下载综合分析报告", data=md_text, file_name=f, mime="text/markdown", key=f"dl_md_{f}", use_container_width=True)
                
            # Offer CSV Matrix and Clinical info downloads
            csv_files = sorted([f for f in os.listdir(out_dir) if f.endswith(".csv")])
            for f in csv_files:
                st.markdown(f"**衍生数据矩阵: {f}**")
                with open(os.path.join(out_dir, f), "rb") as file:
                    csv_bytes = file.read()
                st.download_button(label=f"📥 下载原始表格流 ({f})", data=csv_bytes, file_name=f, mime="text/csv", key=f"dl_csv_{f}", use_container_width=True)

        else: st.warning("暂无分析结果图，请在 Jobs 选项卡启动任务。")

    with t3:
        st.info("💡 GitHub Discussions: 欢迎提出新问题或 Bug Report (登录 GitHub 参与互动)。")
        components.html(
            """
            <script src="https://giscus.app/client.js"
                data-repo="etonsalmon160-source/Grand_Master_Bioinfo_Platform"
                data-repo-id="R_kgDONzJIfg"
                data-category="Announcements"
                data-category-id="DIC_kwDONzJIfs4Cmosk"
                data-mapping="pathname"
                data-strict="0"
                data-reactions-enabled="1"
                data-emit-metadata="0"
                data-input-position="bottom"
                data-theme="dark"
                data-lang="zh-CN"
                data-loading="lazy"
                crossorigin="anonymous"
                async>
            </script>
            """,
            height=600,
            scrolling=True
        )

if __name__ == "__main__":
    main()

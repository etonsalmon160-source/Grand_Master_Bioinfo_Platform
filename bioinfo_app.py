import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from master_bioinfo_suite import MasterBioinfoPipeline

# ==========================================
# 💎 PREMIUM UI CONFIG & STYLING
# ==========================================
# ==========================================
# 💎 ULTIMATE PREMIUM UI CONFIG & STYLING (GLASSMORPHISM DARK)
# ==========================================
st.set_page_config(
    page_title="Grand Master | Elite Bioinfo Portal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS Injection - Advanced Medical/Tech Aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --accent-gradient: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --text-main: #f8fafc;
        --text-dim: #94a3b8;
    }

    /* Global Overrides */
    .stApp {
        background: radial-gradient(circle at 0% 0%, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, .main-header {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid var(--glass-border);
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 2rem;
    }

    /* Custom Header Style */
    .super-header {
        background: linear-gradient(to right, #fff 20%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem !important;
        letter-spacing: -2px;
        margin-bottom: 0.5rem;
    }

    .sub-glow {
        color: #60a5fa;
        text-shadow: 0 0 20px rgba(96, 165, 250, 0.5);
        font-weight: 500;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    /* Modern Card Container */
    .premium-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        padding: 2rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .premium-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        border-color: rgba(255,255,255,0.2);
    }

    /* Tab Styling Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 10px;
        color: var(--text-dim);
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255,255,255,0.1) !important;
        color: #fff !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Button Styling (Elite Level) */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 20px -10px rgba(59, 130, 246, 0.5);
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 20px 30px -10px rgba(59, 130, 246, 0.6);
        background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
    }

    /* Input Fields */
    .stTextInput input, .stFileUploader section {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--glass-border) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    /* Custom Footer */
    .glass-footer {
        padding: 2rem;
        text-align: center;
        color: var(--text-dim);
        font-size: 0.8rem;
        border-top: 1px solid var(--glass-border);
        margin-top: 4rem;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    # Utility to load local logo as base64
    def get_base64_logo(path):
        import base64
        import os
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""

    b64_logo = get_base64_logo("app_logo.png")
    logo_src = f"data:image/png;base64,{b64_logo}" if b64_logo else "https://img.icons8.com/3d-fluency/200/dna.png"

    # Sidebar Branding (Elite Layout)
    st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="display: inline-block; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px;">
                <img src="{logo_src}" width="120" style="filter: drop-shadow(0 0 15px rgba(96, 165, 250, 0.4)); filter: brightness(1.1);">
            </div>
            <h1 style='font-family: "Outfit", sans-serif; font-size: 2.2rem; margin:0; background: linear-gradient(to bottom, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Grand Master</h1>
            <div style='display: inline-block; background: linear-gradient(90deg, #B8860B, #FFD700); padding: 2px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; color: #1a1a1a; text-transform: uppercase; letter-spacing: 1px;'>
                v2.5.0 GOLD ELITE
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # User Declaration (Side)
    st.sidebar.info(f"""
    **🧪 指导与开发声明**  
    **负责人**: Eto (eto10)  
    **联系邮箱**: etonsalmon160@gmail.com  
    *Bioinformatics workflow automation expert.*
    """)
    
    # --- GITHUB OAUTH LOGIN ---
    import requests
    
    CLIENT_ID = st.secrets.get("GITHUB_CLIENT_ID")
    CLIENT_SECRET = st.secrets.get("GITHUB_CLIENT_SECRET")
    REDIRECT_URI = "https://grandmasterbioinfoplatform-dkdxqpknwocwqjskiwfwpn.streamlit.app/"

    if "user_info" not in st.session_state:
        st.session_state.user_info = None

    def get_login_url():
        return f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read:user"

    # Check for callback code in URL
    query_params = st.query_params
    if "code" in query_params and st.session_state.user_info is None:
        code = query_params["code"]
        # Exchange code for token
        token_res = requests.post(
            "https://github.com/login/oauth/access_token",
            data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code, "redirect_uri": REDIRECT_URI},
            headers={"Accept": "application/json"}
        ).json()
        
        if "access_token" in token_res:
            access_token = token_res["access_token"]
            # Get User Info
            user_data = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"}
            ).json()
            st.session_state.user_info = user_data
            st.query_params.clear()
            st.rerun()

    # Sidebar Login UI
    st.sidebar.markdown("---")
    if st.session_state.user_info:
        u = st.session_state.user_info
        cols = st.sidebar.columns([1, 4])
        cols[0].image(u.get("avatar_url"), width=40)
        cols[1].markdown(f"**欢迎, {u.get('login')}**")
        if st.sidebar.button("登出 (Logout)"):
            st.session_state.user_info = None
            st.rerun()
    else:
        if CLIENT_ID and CLIENT_SECRET:
            # Styled version (CSS can sometimes block this in iframes)
            st.sidebar.markdown(f'<a href="{get_login_url()}" target="_top" style="display:inline-block; background: linear-gradient(135deg, #2ea44f 0%, #22863a 100%); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; width: 100%; text-align: center; margin-bottom: 10px;">🚀 GitHub 账号登录</a>', unsafe_allow_html=True)
            
            # Standard Streamlit fallback (Most compatible)
            st.sidebar.link_button("💡 登录遇到困难? (备用入口)", get_login_url() if CLIENT_ID else "#", use_container_width=True)
            st.sidebar.caption("登录后可解锁实验记录同步")
        else:
            st.sidebar.warning("⚠️ GitHub API 未配置")
            with st.sidebar.expander("如何配置?"):
                st.markdown("""
                1. 在 GitHub Settings 创建 OAuth App。
                2. 设置 Callback 为当前网址。
                3. 在 Streamlit Cloud 的 Secrets 中填入 ID 和 Secret。
                """)

    st.sidebar.markdown("---")
    
    # Main Hero Section
    st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <div class='sub-glow'>Automated Multi-Omics Intelligence</div>
            <h1 class='super-header'>Grand Master</h1>
            <p style='color: var(--text-dim); font-size: 1.2rem; max-width: 600px;'>
                Elite-level bioinformatics workflow automation. 
                Integrating deep learning, statistical genetics, and clinical validation.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Global Navigation Tabs
    nav_tabs = st.tabs(["🚀 分析中心 (Analysis)", "💬 讨论广场 (Forum)", "📚 帮助指南 (Help)"])
    
    with nav_tabs[0]:
        with st.expander("📖 快速上手指南 (Quick Start)", expanded=False):
            st.info("""
            1. **输入数据**: 上传您的 CSV/TXT 矩阵，或直接输入 **NCBI GEO 编号**。
            2. **配置参数**: 在左侧面板调整基因筛选量与筛选开关。
            3. **启动引擎**: 点击下方蓝色按钮，等待全自动化流程跑完。
            """)

        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 数据导入 (Data Integration)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📁 1. 表达矩阵 (Expression)**")
            exp_file = st.file_uploader("Upload CSV/TXT/TSV", type=["csv", "txt", "tsv"], key="exp", label_visibility="collapsed")
            
        with col2:
            st.markdown("**📋 2. 临床元数据 (Metadata)**")
            meta_file = st.file_uploader("Include SampleID & Group", type=["csv", "txt", "tsv"], key="meta", label_visibility="collapsed")

        with col3:
            st.markdown("**🌍 3. 对接 GEO 数据 (NCBI)**")
            geo_id = st.text_input("GSE Number (e.g., GSE12345)", placeholder="GSExxxxx", label_visibility="collapsed")
            
            if geo_id.startswith("GSE"):
                geo_url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={geo_id}"
                st.markdown(f"🔗 [Series Page]({geo_url})")
            else:
                st.caption("Automatic fetching from NCBI Portal")
        st.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.subheader("🔬 科学筛选 (Screening)")
    p_type = st.sidebar.selectbox("显著性指标 (P-type)", ["FDR (padj)", "P-value"], index=0)
    p_thresh = st.sidebar.slider("显著性阈值 (P-thresh)", 0.001, 0.1, 0.05, format="%.3f")
    fc_thresh = st.sidebar.slider("差异倍数阈值 (log2FC)", 0.5, 5.0, 1.0, step=0.1)
    
    p_col_name = 'padj' if 'FDR' in p_type else 'pvalue'
    use_demo = st.sidebar.checkbox("使用演示数据 (Demo Data)")

    if st.button("🚀 开启全流程分析 (Execute Grand Master Flow)"):
        if not use_demo and (exp_file is None or meta_file is None):
            st.error("请先上传数据或选择'使用演示数据'！")
        else:
            msg_container = st.empty()
            progress_bar = st.progress(0)
            
            # Init Pipeline
            pipeline = MasterBioinfoPipeline(out_dir="Web_Analysis_Output")
            
            # 1. Load Data
            msg_container.info("🔄 正在加载并预处理数据...")
            custom_counts = None
            custom_meta = None
            
            if geo_id:
                try:
                    msg_container.info(f"📡 正在从 NCBI 下载 {geo_id}...")
                    custom_counts, custom_meta = pipeline.fetch_geo_data(geo_id)
                    st.success(f"成功获取 {geo_id} 数据！")
                except Exception as e:
                    st.error(f"GEO 下载失败: {str(e)}")
                    st.stop()
            elif not use_demo:
                try:
                    # Generic loader for CSV/TXT/TSV
                    sep = ',' if exp_file.name.endswith('.csv') else '\t'
                    custom_counts = pd.read_csv(exp_file, index_index=0, sep=sep)
                    custom_meta = pd.read_csv(meta_file, index_index=0, sep=sep)
                    
                    # Probe Conversion (e.g., GPL570)
                    custom_counts = pipeline.convert_probes_to_symbols(custom_counts)
                except Exception as e:
                    st.error(f"数据读取失败: {str(e)}")
                    st.stop()
            
            pipeline.run_pre_processing(n_genes=3000 if not geo_id and not use_demo else 5000, 
                                     custom_counts=custom_counts, 
                                     custom_meta=custom_meta)
            progress_bar.progress(20)
            
            msg_container.info("📊 正在探测样本差异 (DEA)...")
            pipeline.run_dea(p_thresh=p_thresh, fc_thresh=fc_thresh, p_type=p_col_name)
            progress_bar.progress(40)
            
            msg_container.info("🕸️ 正在构建共表达网络 (WGCNA)...")
            pipeline.run_wgcna_lite()
            progress_bar.progress(60)
            
            msg_container.info("💉 正在解析免疫微环境 (CIBERSORT)...")
            pipeline.run_cibersort_lite()
            progress_bar.progress(80)
            
            msg_container.info("🤖 正在启动双模型机器学习与生存验证...")
            if hasattr(pipeline, 'run_advanced_ml'):
                pipeline.run_advanced_ml()
            else:
                pipeline.run_ml_biomarkers()
            pipeline.run_survival()
            
            msg_container.info("🧬 正在执行 GO/KEGG 功能富集分析...")
            pipeline.run_enrichment()
            
            msg_container.info("📝 正在汇总中英文双语报告...")
            pipeline.generate_report()
            progress_bar.progress(100)
            
            msg_container.success("✅ 分析圆满完成！")
            
            # --- PUSHPLUS WECHAT NOTIFICATION ---
            try:
                push_token = "b5300e241cad4d73b36533b5c950e22d"
                push_title = "📊 生信分析任务已圆满完成"
                push_content = f"""
                ## 🚀 实验简报 (Grand Master Bioinfo)

                **任务状态**: ✅ 已完成
                **核心标志物**: {pipeline.top_gene}
                **分析时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

                > 您的生信私人实验室已完成全流程流水线（DEA, WGCNA, ML, Survival）。现已生成可视化报告，请返回 Web 界面查看详情。
                """
                requests.post("https://www.pushplus.plus/send", 
                             json={"token": push_token, "title": push_title, "content": push_content, "template": "markdown"},
                             timeout=5)
            except Exception as e:
                pass


            # --- DISPLAY RESULTS ---
            st.divider()
            st.success(f"核心标志物锁定: {pipeline.top_gene}")
            
            res_tabs = st.tabs(["核心概览", "机器学习", "功能富集", "免疫浸润", "生信报告"])
            
            with res_tabs[0]:
                c1, c2 = st.columns(2)
                with c1: st.image("Web_Analysis_Output/Fig1_PCA.png", caption="样本聚类视角")
                with c2: st.image("Web_Analysis_Output/Fig2_Volcano.png", caption="差异表达地图")
                st.image("Web_Analysis_Output/Fig6_Survival.png", caption="临床预后验证", width=600)

            with res_tabs[1]:
                # Dynamic check for ML files
                files = os.listdir("Web_Analysis_Output")
                if "Fig5d_ROC.png" in files:
                    st.image("Web_Analysis_Output/Fig5d_ROC.png", caption="多模型效能对比")
                    c3, c4 = st.columns(2)
                    with c3: st.image("Web_Analysis_Output/Fig5a_Lasso_CV.png", caption="LASSO 系数筛选")
                    with c4: st.image("Web_Analysis_Output/Fig5b_Lasso_Path.png", caption="LASSO 回归路径")
                    
                    # New RF diagnostic plots
                    c5, c6 = st.columns(2)
                    with c5: st.image("Web_Analysis_Output/Fig5c1_RF_Error.png", caption="随机森林收敛曲线")
                    with c6: st.image("Web_Analysis_Output/Fig5c2_RF_Imp.png", caption="特征重要性排列")
                else:
                    st.image("Web_Analysis_Output/Fig5_ML.png")

            with res_tabs[2]:
                st.image("Web_Analysis_Output/Fig7_Enrichment.png", caption="KEGG Pathway Enrichment Analysis")
                st.info("💡 提示: 气泡大小代表基因计数，颜色代表显著性水平 (-log10 P-value).")

            with res_tabs[3]:
                st.image("Web_Analysis_Output/Fig3_WGCNA.png", caption="WGCNA 调控模块")
                st.image("Web_Analysis_Output/Fig4_CIBERSORT.png", caption="免疫细胞含量全景")

            with res_tabs[4]:
                with open("Web_Analysis_Output/Analysis_Report.md", "r", encoding='utf-8') as f:
                    report_content = f.read()
                st.markdown(report_content)
                st.download_button("📥 下载完整报告与图表打包", 
                                   data=report_content, 
                                   file_name="Master_Bioinfo_Report.md")

    with nav_tabs[1]:
        st.markdown("""
            <div class='premium-card' style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%); border-left: 5px solid #3b82f6;'>
                <h2 style='margin:0; color: #fff;'>🧬 Grand Master 社区讨论广场</h2>
                <p style='color: var(--text-dim); margin-top: 5px;'>Elite Bioinformatics Interactive Space. Share, Ask, and Advance.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Guide Users to Post
        st.info("💡 **Quick Guide**: Use the buttons below to create new threads on GitHub, or scroll down to comment directly on this page.")
        
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            st.link_button("✍️ 发布新讨论 (前往 GitHub)", "https://github.com/etonsalmon160-source/Grand_Master_Bioinfo_Platform/discussions/new/choose", icon="🚀", use_container_width=True)
        with col_f2:
            st.link_button("📢 查看所有讨论主题", "https://github.com/etonsalmon160-source/Grand_Master_Bioinfo_Platform/discussions", icon="🔍", use_container_width=True)
        
        st.divider()
        
        # Giscus (GitHub Discussions) - Streamlit Optimized Sync
        # Mapping changed to 'specific' for more robust behavior in iframes
        giscus_html = f"""
        <div id="giscus-frame-container" style="background: rgba(15, 23, 42, 1); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 20px; min-height: 800px;">
            <script src="https://giscus.app/client.js"
                    data-repo="etonsalmon160-source/Grand_Master_Bioinfo_Platform"
                    data-repo-id="R_kgDORZS_Kw"
                    data-category="General"
                    data-category-id="DIC_kwDORZS_K84C3P-N"
                    data-mapping="specific"
                    data-term="GrandMasterBioinfoPortal"
                    data-strict="0"
                    data-reactions-enabled="1"
                    data-emit-metadata="1"
                    data-input-position="top"
                    data-theme="dark_dimmed"
                    data-lang="zh-CN"
                    crossorigin="anonymous"
                    async>
            </script>
        </div>
        """
        import streamlit.components.v1 as components
        components.html(giscus_html, height=1000, scrolling=True)



        
        # Enhanced Troubleshooting Section
        with st.expander("🛠️ 论坛无法加载? (Troubleshooting Forum)"):
            st.markdown("""
            若上方区域显示空白，请按以下步骤操作：
            1. **开启 Discussions**: 前往 [仓库设置](https://github.com/etonsalmon160-source/Grand_Master_Bioinfo_Platform/settings) 勾选 **Discussions** 选项。
            2. **安装 Giscus**: 确保已在 GitHub 上为该仓库安装并授权了 [giscus](https://github.com/apps/giscus) 应用。
            3. **网络检查**: 论坛依赖 GitHub API，如果您的网络环境受限，可能需要开启全局代理。
            4. **手动进入**: 您也可以直接点击上方按钮 **"查看所有讨论主题"** 在 GitHub 原生界面参与。
            """)


    with nav_tabs[2]:
        st.markdown("### 📚 平台指南与 FAQ")
        st.markdown("""
        - **如何导入 GEO?** 在分析中心输入 GSE 开头的编号即可。
        - **报错了怎么办?** 请在讨论广场贴出您的错误代码，Eto 会第一时间回复。
        """)

    # Professional Footer
    st.markdown(f"""
        <div class="glass-footer">
            <p><strong>Grand Master Bioinfo Platform</strong> | Elite Analytics Suite</p>
            <p style='color: var(--text-dim); margin-top: 10px;'>Architect: <strong>Eto (eto10)</strong> | 📧 etonsalmon160@gmail.com</p>
            <p style='font-size: 10px; color: #475569; margin-top: 20px;'>© 2026 Bioinformatics Automation. No placeholders, only real science.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

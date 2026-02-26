import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from master_bioinfo_suite import MasterBioinfoPipeline

# ==========================================
# 💎 PREMIUM UI CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="Grand Master Bioinfo Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High-End CSS Injection
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #fdfcfb 0%, #e2d1c3 100%);
    }

    /* Professional Header */
    .main-header {
        background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0px;
    }

    /* Cards & Containers */
    div.stButton > button {
        background: linear-gradient(to right, #FF512F 0%, #DD2476 51%, #FF512F 100%);
        border: none;
        color: white;
        font-weight: 700;
        text-transform: uppercase;
        transition: 0.5s;
        background-size: 200% auto;
        box-shadow: 0 4px 15px 0 rgba(236, 40, 111, 0.4);
        border-radius: 10px;
        height: 3.5rem;
    }
    div.stButton > button:hover {
        background-position: right center;
        transform: translateY(-2px);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff99;
        backdrop-filter: blur(10px);
        border-right: 1px solid #e0e0e0;
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #b21f1f;
        font-weight: 700;
    }

    /* Footer */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffffcc;
        color: #333;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        border-top: 1px solid #eee;
        backdrop-filter: blur(5px);
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Sidebar Credits & Branding
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 20px;">
            <img src="https://img.icons8.com/clouds/200/dna.png" width="80">
            <h2 style='color: #1a2a6c;'>Bioinfo Pro</h2>
            <p style='font-size: 0.8rem; color: #666;'>Version 2.5.0 Gold</p>
        </div>
    """, unsafe_allow_html=True)
    
    # User Declaration (Side)
    st.sidebar.info(f"""
    **🧪 指导与开发声明**  
    **负责人**: Eto (eto10)  
    **联系邮箱**: etonsalmon160@gmail.com  
    *Bioinformatics workflow automation expert.*
    """)
    
    st.sidebar.markdown("---")
    
    # Main Hero Section
    st.markdown("<h1 class='main-header'>Grand Master</h1>", unsafe_allow_html=True)
    st.markdown("### 🔬 一站式自动化生信挖掘平台 (Elite Edition)")
    st.markdown("---")
    
    with st.expander("📖 如何使用 (How to reuse)", expanded=False):
        st.info("""
        1. **上传数据**: 同时上传您的表达矩阵 (Counts) 和临床信息 (Metadata)。
        2. **启动引擎**: 点击 '开始全球分析'。
        3. **获取报告**: 分析完成后，直接在页面查看交互式结果并下载完整 Markdown 报告。
        """)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. 表达数据 (Expression)")
        exp_file = st.file_uploader("支持 .csv, .txt, .tsv", type=["csv", "txt", "tsv"], key="exp")
        
    with col2:
        st.subheader("2. 临床元数据 (Metadata)")
        meta_file = st.file_uploader("需包含 SampleID 和 Group", type=["csv", "txt", "tsv"], key="meta")

    with col3:
        st.subheader("3. 直接对接 GEO (NCBI)")
        geo_id = st.text_input("输入 GSE 编号 (例: GSE12345)", placeholder="GSExxxxx")
        
        if geo_id.startswith("GSE"):
            geo_url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={geo_id}"
            st.markdown(f"🔗 [前往该数据集官网 (Series Page)]({geo_url})")
            with st.expander("💡 手动下载指南 (Manual Guide)"):
                st.markdown(f"""
                - **表达矩阵**: 在页面底部寻找 `Series Matrix File(s)` 下载并解压。
                - **临床数据**: 在页面底部的 `Samples` 表格或 `Series Matrix` 的头部信息中可以提取。
                - **提示**: 若云端下载缓慢，建议手动下载后使用左侧【上传】功能。
                """)
        else:
            st.caption("输入后将自动下载矩阵与分组信息")

    st.sidebar.subheader("分析参数 (Parameters)")
    n_genes = st.sidebar.slider("基因筛选数量", 500, 10000, 3000)
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
            
            pipeline.run_pre_processing(n_genes=n_genes, 
                                     custom_counts=custom_counts, 
                                     custom_meta=custom_meta)
            progress_bar.progress(20)
            
            msg_container.info("📊 正在探测样本差异 (DEA)...")
            pipeline.run_dea()
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

            # --- DISPLAY RESULTS ---
            st.divider()
            st.success(f"核心标志物锁定: {pipeline.top_gene}")
            
            tabs = st.tabs(["核心概览", "机器学习", "功能富集", "免疫浸润", "讨论广场", "生信报告"])
            
            with tabs[0]:
                c1, c2 = st.columns(2)
                with c1: st.image("Web_Analysis_Output/Fig1_PCA.png", caption="样本聚类视角")
                with c2: st.image("Web_Analysis_Output/Fig2_Volcano.png", caption="差异表达地图")
                st.image("Web_Analysis_Output/Fig6_Survival.png", caption="临床预后验证", width=600)

            with tabs[1]:
                # Dynamic check for ML files
                files = os.listdir("Web_Analysis_Output")
                if "Fig5d_ROC.png" in files:
                    st.image("Web_Analysis_Output/Fig5d_ROC.png", caption="多模型效能对比")
                    c3, c4 = st.columns(2)
                    with c3: st.image("Web_Analysis_Output/Fig5a_Lasso_CV.png")
                    with c4: st.image("Web_Analysis_Output/Fig5b_Lasso_Path.png")
                else:
                    st.image("Web_Analysis_Output/Fig5_ML.png")

            with tabs[2]:
                st.image("Web_Analysis_Output/Fig7_Enrichment.png", caption="KEGG Pathway Enrichment Analysis")
                st.info("💡 提示: 气泡大小代表基因计数，颜色代表显著性水平 (-log10 P-value).")

            with tabs[3]:
                st.image("Web_Analysis_Output/Fig3_WGCNA.png", caption="WGCNA 调控模块")
                st.image("Web_Analysis_Output/Fig4_CIBERSORT.png", caption="免疫细胞含量全景")

            with tabs[4]:
                st.markdown("### 🧬 Grand Master 社区讨论广场")
                st.write("欢迎在下方分享您的发现、报错或算法改进建议。需登录 GitHub 即可参与讨论。")
                
                # Giscus (GitHub Discussions based commenting)
                # Note: The repo link should point to your repo
                giscus_html = """
                <script src="https://giscus.app/client.js"
                        data-repo="etonsalmon160-source/Grand_Master_Bioinfo_Platform"
                        data-repo-id="R_kgDONS4oWQ"
                        data-category="Announcements"
                        data-category-id="DIC_kwDONS4oWc4Ckk3b"
                        data-mapping="pathname"
                        data-strict="0"
                        data-reactions-enabled="1"
                        data-emit-metadata="0"
                        data-input-position="bottom"
                        data-theme="light"
                        data-lang="zh-CN"
                        crossorigin="anonymous"
                        async>
                </script>
                """
                import streamlit.components.v1 as components
                components.html(giscus_html, height=800, scrolling=True)

            with tabs[5]:
                with open("Web_Analysis_Output/Analysis_Report.md", "r", encoding='utf-8') as f:
                    report_content = f.read()
                st.markdown(report_content)
                st.download_button("📥 下载完整报告与图表打包", 
                                   data=report_content, 
                                   file_name="Master_Bioinfo_Report.md")

    # Professional Footer
    st.markdown(f"""
        <div class="footer">
            <p><strong>Grand Master Bioinfo Platform</strong> | Optimized by <strong>Eto (eto10)</strong> | 📧 etonsalmon160@gmail.com</p>
            <p style='font-size: 10px; color: #999;'>© 2026 Bioinformatics Automation Suite. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

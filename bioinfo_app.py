import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from master_bioinfo_suite import MasterBioinfoPipeline

# ==========================================
# 💎 PREMIMUM UI CONFIG
# ==========================================
st.set_page_config(
    page_title="Grand Master Bioinfo Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #E64B35;
        color: white;
        font-weight: bold;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.sidebar.image("https://img.icons8.com/clouds/200/dna.png", width=100)
    st.sidebar.title("Bioinfo Engine v2.0")
    st.sidebar.markdown("---")
    
    st.title("🧪 Grand Master 生信云分析平台")
    st.markdown("##### CNS 级别的一站式自动化生信分析工作流")
    
    with st.expander("📖 如何使用 (How to reuse)", expanded=False):
        st.info("""
        1. **上传数据**: 同时上传您的表达矩阵 (Counts) 和临床信息 (Metadata)。
        2. **启动引擎**: 点击 '开始全球分析'。
        3. **获取报告**: 分析完成后，直接在页面查看交互式结果并下载完整 Markdown 报告。
        """)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. 表达数据 (Expression Matrix)")
        exp_file = st.file_uploader("支持 .csv, .txt, .tsv", type=["csv", "txt", "tsv"], key="exp")
        
    with col2:
        st.subheader("2. 临床元数据 (Clinical Metadata)")
        meta_file = st.file_uploader("需包含 SampleID 和 Group 列", type=["csv", "txt", "tsv"], key="meta")

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
            
            if not use_demo:
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
            
            msg_container.info("📝 正在汇总中英文双语报告...")
            pipeline.generate_report()
            progress_bar.progress(100)
            
            msg_container.success("✅ 分析圆满完成！")

            # --- DISPLAY RESULTS ---
            st.divider()
            st.success(f"核心标志物锁定: {pipeline.top_gene}")
            
            tabs = st.tabs(["核心概览", "机器学习", "免疫浸润", "生信报告"])
            
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
                st.image("Web_Analysis_Output/Fig3_WGCNA.png", caption="WGCNA 调控模块")
                st.image("Web_Analysis_Output/Fig4_CIBERSORT.png", caption="免疫细胞含量全景")

            with tabs[3]:
                with open("Web_Analysis_Output/Analysis_Report.md", "r", encoding='utf-8') as f:
                    report_content = f.read()
                st.markdown(report_content)
                st.download_button("📥 下载完整报告与图表打包", 
                                   data=report_content, 
                                   file_name="Master_Bioinfo_Report.md")

    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by OpenClaw AI | 2026")

if __name__ == "__main__":
    main()

# 🧬 Grand Master Bioinfo Platform (v2.8.0)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Streamlit-FF4B4B.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

> **The ultimate automated workflow for CNS-grade bioinformatics discovery.**
Developed and optimized by **Eto (eto10)**.

---

## 🌟 Key Features

- **Clinical Miner Engine**: Automatically extracts OS/DFS survival time and status from GEO metadata for clinical validation.
- **Semantic Intent Analysis**: Supports natural language queries (e.g., "Find and analyze LUAD studies") via LLM integration.
- **Multi-Algorithm Marker Discovery**: Integrated LASSO (L1-Logistic) regression and Random Forest feature selection.
- **Deep Mechanism Mining**: Automated GO and KEGG enrichment analysis with high-fidelity bubble plots.
- **Stable Heatmap (Exploratory Mode)**: Publication-quality Heatmap that gracefully falls back to high-variance genes if DEGs are scarce.
- **Immune Profiling**: CIBERSORT-based immune infiltration estimation.
- **WGCNA Integration**: Identification of gene co-expression modules and hub genes.
- **Clinical Validation**: Automated Kaplan-Meier survival curves and ROC performance metrics.
- **Raw Data Export**: Direct export of processed Expression Matrices and Clinical Metadata in CSV format.

---

## 🚀 Quick Start (快速入门)

### Option A: Local Web App (推荐：网页交互版)

如果您想在本地运行可视化界面：

1. **克隆/下载仓库** 并进入目录。
2. **一键启动 (Windows)**:
    双击运行 `run_openclaw.bat`。它会自动创建虚拟环境并安装所有依赖。
3. **手动启动**:

    ```bash
    pip install -r requirements.txt
    streamlit run bioinfo_app.py
    ```

### Option B: Command Line (CLI 极客版)

如果您喜欢命令行操作：

```bash
python launcher.py "GSE31210" --simple
```

---

## 📦 Packaging & Installation (安装引导)

### 1. 环境准备

确保您的电脑已安装 **Python 3.10+** 或 **Anaconda**。

### 2. 依赖安装

```bash
pip install -r requirements.txt
```

*主要依赖包括：gseapy, streamlit, scikit-learn, lifelines, pandas, matplotlib-venn 等。*

### 3. 使用 Conda (可选)

```bash
conda env create -f environment.yml
conda activate openclaw
```

---

## 📂 Project Structure

- `bioinfo_app.py`: 核心 Streamlit UI，提供极致的科研交互体验。
- `master_bioinfo_suite.py`: 生信分析引擎（包含 DEA, WGCNA, ML, Survival, Enrichment）。
- `launcher.py`: 命令行启动工具，支持灵活的分析模式。
- `run_openclaw.bat`: Windows 用户一键环境部署与启动脚本。

---

## 🛡️ License & Contact

This project is licensed under the **MIT License**.
**Eto (eto10)**: [etonsalmon160@gmail.com](mailto:etonsalmon160@gmail.com)
*Powered by Antigravity Bioinfo Master Suite*

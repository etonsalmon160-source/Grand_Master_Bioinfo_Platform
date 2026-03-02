# 🧪 Grand Master 生信云分析平台 (部署与复用指南)

感谢您使用 OpenClaw 构建的自动化生信平台。以下是将其**部署为网站**或**分享给他人复用**的说明。

## 1. 本地网页版启动 (Local Web Launch)

如果您想在自己的电脑上以网页形式运行：

1. 打开终端或 PowerShell。
2. 运行以下命令：

   ```bash
   streamlit run bioinfo_app.py
   ```

3. 浏览器会自动弹出 `http://localhost:8501`，即可进入可视化交互界面。

## 2. 封装与复用 (Reusability for Others)

为了让您的同事或协作者直接使用，请打包分享以下文件：

* `master_bioinfo_suite.py` (核心引擎)
* `bioinfo_app.py` (网页界面)
* `requirements.txt` (环境依赖)

**他人如何运行？**
只需三步：

1. 安装 Python 环境。
2. 安装依赖：`pip install -r requirements.txt`
3. 启动网页：`streamlit run bioinfo_app.py`

## 3. 部署到公网 (Cloud Deployment)

如果您希望成为一个真正的公共网站，推荐以下方案：

* **Streamlit Cloud (最快)**: 将代码上传到 GitHub，直接在 Streamlit 官网一键绑定，即可获得一个公网 URL (例如 `https://yourname-bioinfo.streamlit.app`)。
* **Docker 部署**: 我们可以生成 Docker 镜像，在服务器上一键启动。

---

## ✨ 平台核心优势

* **零代码交互**: 所有的复杂分析已经封装在后端，前端只需上传 CSV 即可。
* **模块化引擎**: 以后只要更新 `master_bioinfo_suite.py` 中的算法，网页端会自动升级功能。
* **导出即论文**: 报告直接以 Markdown 形式导出，图表符合顶级期刊标准。

---
*Powered by Antigravity Bioinfo Master Suite*

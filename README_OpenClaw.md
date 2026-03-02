# 🦞 OpenClaw 生信工作流

可更新、环境可封装的生信分析软件：支持 **GSE 编号** 与 **自然语言描述** 启动，一键运行从 GEO 下载到报告生成的全流程。

---

## ✨ 功能概览

- **双模式启动**：直接输入 GSE 号（如 `GSE31210`）或自然语言（如「分析肺腺癌 GSE31210 和 GSE30219」），自动解析并依次运行。
- **统一软件界面**：Streamlit UI（`openclaw_app.py`）集成启动器与工作流，可选简化流程（本地结果）或完整流程（D 盘归档 + 通知）。
- **可更新**：界面内「检查更新」从 GitHub Releases 获取最新版本；发布新版本时打 tag（如 `v1.0.1`）即可。
- **环境封装**：提供 `requirements.txt`、`environment.yml` 与一键运行脚本，便于复现与分发。

---

## 🚀 快速开始

### 方式一：一键运行（推荐，自动创建 venv）

- **Windows**：双击 `run_openclaw.bat`，或在项目目录下执行：
  ```bat
  run_openclaw.bat
  ```
- **Linux / macOS**：
  ```bash
  chmod +x run_openclaw.sh
  ./run_openclaw.sh
  ```
  首次运行会自动创建 `venv` 并安装依赖，然后打开浏览器进入 OpenClaw 界面。

### 方式二：已有 Python 环境

```bash
cd /path/to/openclaw-bioinfo
pip install -r requirements.txt
streamlit run openclaw_app.py
```

### 方式三：Conda 环境（环境与代码一起封装）

```bash
conda env create -f environment.yml
conda activate openclaw
streamlit run openclaw_app.py
```

### 命令行启动器（无 UI）

```bash
# 传统 GSE
python launcher.py GSE31210
python launcher.py GSE31210 GSE30219

# 自然语言
python launcher.py "分析 GSE31210 和 GSE30219"

# 简化流程 + 不通知
python launcher.py --simple --no-notify GSE31210
```

---

## 🔄 更新与版本

- 当前版本写在项目根目录的 **`VERSION`** 文件中（如 `1.0.0`）。
- 在软件界面侧边栏点击 **「检查更新」** 会请求 GitHub 仓库的 `releases/latest`，若有新 tag 会提示并给出下载链接。
- 若仓库不是默认的 `YOUR_USERNAME/openclaw-bioinfo`，可设置环境变量：
  ```bash
  set OPENCLAW_GITHUB_REPO=你的用户名/你的仓库名
  ```
  再启动 `openclaw_app.py`。

---

## 📂 项目结构（与封装相关）

| 文件/目录           | 说明 |
|--------------------|------|
| `openclaw_app.py`  | 统一软件入口（Streamlit UI，GSE/自然语言 + 工作流） |
| `launcher.py`      | 命令行启动器（解析 GSE/自然语言，调用简化或完整流程） |
| `VERSION`         | 当前版本号，用于界面显示与更新检查 |
| `requirements.txt`| Pip 依赖，用于 venv / 一键脚本 |
| `environment.yml` | Conda 环境，便于环境与代码一起封装 |
| `run_openclaw.bat`| Windows 一键运行（自动 venv + streamlit） |
| `run_openclaw.sh` | Linux/macOS 一键运行 |
| `master_bioinfo_suite.py` | 分析引擎（DEA、WGCNA、ML、生存、富集等） |
| `custom_geo_parser.py`    | GEO 数据下载与解析 |
| `auto_agent_workflow.py`  | 完整流程（D 盘临时目录、归档、可选通知） |

---

## 📤 上传到 GitHub（可更新 + 环境封装）

1. **在 GitHub 创建仓库**（如 `openclaw-bioinfo`），不要勾选 “Add a README”（若本地已有完整项目）。

2. **本地已初始化 git 时**，添加远程并推送：
   ```bash
   git remote add origin https://github.com/你的用户名/openclaw-bioinfo.git
   git branch -M main
   git add .
   git commit -m "OpenClaw 生信工作流：UI + 启动器 + 环境封装"
   git push -u origin main
   ```
   使用 **Personal Access Token** 时，在推送时用 token 代替密码：
   ```bash
   git push https://你的用户名:你的TOKEN@github.com/你的用户名/openclaw-bioinfo.git main
   ```
   或配置 Git 凭据存储后直接 `git push origin main`。

3. **发布新版本（可更新）**：在 GitHub 仓库页面 → Releases → Create a new release，填写 tag（如 `v1.0.0`）、标题和说明。用户点击「检查更新」时会收到该版本提示。

4. **环境一起封装**：将 `requirements.txt`、`environment.yml`、`run_openclaw.bat`、`run_openclaw.sh` 一并提交到仓库，他人 clone 后即可按 README 一键安装环境并运行。

---

## 📜 许可证与致谢

- 本仓库在原有 Grand Master 生信流程基础上整合 OpenClaw 启动器与统一 UI。
- 开发：Eto (eto10) | etonsalmon160@gmail.com

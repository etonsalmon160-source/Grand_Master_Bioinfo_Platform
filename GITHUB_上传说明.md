# 上传到 GitHub 的步骤（含令牌使用）

## 1. 在 GitHub 创建新仓库

- 登录 GitHub → New repository
- 仓库名建议：`openclaw-bioinfo`（或任意名称）
- 不要勾选 “Add a README” / “Add .gitignore”（本地已有）
- 创建后记下仓库地址，例如：`https://github.com/你的用户名/openclaw-bioinfo`

## 2. 本地已存在 Git 仓库时

在项目根目录（与 `openclaw_app.py` 同级）打开终端：

```bash
# 添加远程（把下面的 你的用户名 和 仓库名 换成你的）
git remote add origin https://github.com/你的用户名/openclaw-bioinfo.git

# 若之前已有 origin 且地址不对，可先删除再添加：
# git remote remove origin
# git remote add origin https://github.com/你的用户名/openclaw-bioinfo.git

git branch -M main
git add .
git status
git commit -m "OpenClaw 生信工作流：UI + 启动器 + 环境封装"
```

## 3. 使用令牌 (Token) 推送

**重要**：不要把令牌写进任何代码或提交到仓库。

- 在 GitHub：Settings → Developer settings → Personal access tokens → 生成 token（勾选 `repo` 等所需权限）
- 推送时用令牌代替密码：

```bash
# 方式 A：推送时在 URL 里带 token（仅本次，不会保存）
git push https://你的用户名:你的TOKEN@github.com/你的用户名/openclaw-bioinfo.git main

# 方式 B：先设置远程地址（含 token），再 push（注意：会保存在 git config 里，勿提交）
# git remote set-url origin https://你的用户名:你的TOKEN@github.com/你的用户名/openclaw-bioinfo.git
# git push -u origin main
```

推荐用 **方式 A**，或使用 Git 凭据管理器保存令牌（不写在命令里）。

## 4. 启用「检查更新」功能

- 在仓库 → Releases → Create a new release
- Tag 填版本号，如 `v1.0.0`（与 `VERSION` 文件一致或更新）
- 发布后，软件里「检查更新」会读取该 tag 并提示新版本

## 5. 环境一起封装

仓库中已包含：

- `requirements.txt`、`environment.yml`：他人可用 `pip install -r requirements.txt` 或 `conda env create -f environment.yml` 复现环境
- `run_openclaw.bat` / `run_openclaw.sh`：一键创建 venv 并启动界面

用户 clone 后按 `README_OpenClaw.md` 操作即可完成「环境+代码」的封装使用。

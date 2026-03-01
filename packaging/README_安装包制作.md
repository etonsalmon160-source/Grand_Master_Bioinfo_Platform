# OpenClaw 安装包制作说明

用 **PyInstaller** 打出 exe，再用 **Inno Setup** 做成「下一步 → 下一步 → 完成」的安装向导。

---

## 1. 安装 Inno Setup

- 官网：https://jrsoftware.org/isinfo.php  
- 下载并安装 **Inno Setup 6**（免费）。  
- 安装时勾选“中文”可得到中文向导界面。

---

## 2. 打出 OpenClaw.exe（PyInstaller）

在项目根目录（与 `openclaw_app.py` 同级）打开终端，建议用**单独的小环境**，避免把整个 Anaconda 打进去：

```powershell
conda create -n openclaw_build python=3.11 -y
conda activate openclaw_build

cd "C:\Users\eto10\Desktop\open claw初尝试"
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --noconsole --name OpenClaw openclaw_exe_entry.py
```

完成后会得到：

- `dist\OpenClaw\OpenClaw.exe`  
- 以及同目录下的一批依赖文件（DLL、库等）。

**可选**：若希望安装后不再依赖项目里的 `.py` 文件，可在 `OpenClaw.spec` 的 `Analysis(datas=...)` 中加入：

```python
datas=[
    ('openclaw_app.py', '.'),
    ('launcher.py', '.'),
    ('master_bioinfo_suite.py', '.'),
    ('custom_geo_parser.py', '.'),
    ('auto_agent_workflow.py', '.'),
    ('VERSION', '.'),
],
```

然后执行：`pyinstaller --noconfirm OpenClaw.spec`。  
不做这一步也可以：当前 Inno 脚本会在安装时自动把上述脚本复制进安装目录。

---

## 3. 用 Inno Setup 生成安装程序

1. 打开 **Inno Setup Compiler**。  
2. 菜单：**文件 → 打开**，选择项目下的：
   ```
   packaging\OpenClawSetup.iss
   ```
3. 菜单：**构建 → 编译**（或按 Ctrl+F9）。  
4. 编译成功后，安装包在：
   ```
   项目根目录\installer_output\OpenClaw_Setup_1.0.0.exe
   ```

将该 exe 发给用户，对方双击即可进入安装向导，选择安装路径、是否创建桌面/开始菜单快捷方式，安装完成后可从开始菜单或桌面启动 **OpenClaw 生信工作流**。

---

## 4. 修改版本号与名称

- **版本号**：在 `OpenClawSetup.iss` 顶部改 `#define MyAppVersion "1.0.0"`，并与根目录 `VERSION` 文件保持一致（可选）。  
- **名称/网址**：修改同一文件中的 `MyAppNameZh`、`MyAppPublisher`、`MyAppURL` 等即可。

---

## 5. 常见问题

- **编译时提示找不到 `..\dist\OpenClaw\*`**  
  先完成第 2 步，确保已生成 `dist\OpenClaw\` 且其中有 `OpenClaw.exe`。

- **安装后双击 exe 没反应或报错**  
  多数是 PyInstaller 未把运行所需文件打全。可用「可选」里的 `datas` 把 `openclaw_app.py` 等一并打进 exe，或保持现状依赖 Inno 脚本复制到安装目录。

- **想换安装程序图标**  
  在 `OpenClawSetup.iss` 的 `[Setup]` 中设置：
  `SetupIconFile=..\你的图标.ico`
  并取消该行前面的分号。

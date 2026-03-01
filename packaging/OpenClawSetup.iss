; OpenClaw 生信工作流 — Inno Setup 安装脚本
; 用法：先在本机用 PyInstaller 打出 dist\OpenClaw，再在 Inno Setup 中打开此文件并编译

#define MyAppName "OpenClaw"
#define MyAppNameZh "OpenClaw 生信工作流"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "OpenClaw"
#define MyAppURL "https://github.com/your-username/openclaw-bioinfo"
#define MyAppExeName "OpenClaw.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppNameZh}
AppVersion={#MyAppVersion}
AppVerName={#MyAppNameZh} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppNameZh}
AllowNoIcons=yes
OutputDir=..\installer_output
OutputBaseFilename=OpenClaw_Setup_{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "创建快速启动栏快捷方式"; GroupDescription: "附加图标:"; Flags: unchecked

[Files]
; PyInstaller 输出的 exe 及依赖（先执行 pyinstaller 生成 dist\OpenClaw 后再编译本脚本）
Source: "..\dist\OpenClaw\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 以下脚本与配置：若未通过 PyInstaller 打进 exe，则从项目根目录复制到安装目录
Source: "..\openclaw_app.py"; DestDir: "{app}"; Flags: ignoreversion; Check: NeedAppScripts
Source: "..\launcher.py"; DestDir: "{app}"; Flags: ignoreversion; Check: NeedAppScripts
Source: "..\master_bioinfo_suite.py"; DestDir: "{app}"; Flags: ignoreversion; Check: NeedAppScripts
Source: "..\custom_geo_parser.py"; DestDir: "{app}"; Flags: ignoreversion; Check: NeedAppScripts
Source: "..\auto_agent_workflow.py"; DestDir: "{app}"; Flags: ignoreversion; Check: NeedAppScripts
Source: "..\VERSION"; DestDir: "{app}"; Flags: ignoreversion; Check: NeedAppScripts
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Check: NeedAppScripts

[Icons]
Name: "{group}\{#MyAppNameZh}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppNameZh}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppNameZh}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppNameZh}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行 {#MyAppNameZh}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\Run_*_Results"
Type: filesandordirs; Name: "{app}\*.json"

[Code]
function NeedAppScripts: Boolean;
begin
  Result := not FileExists(ExpandConstant('{app}\openclaw_app.py'));
end;

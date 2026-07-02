; EADC Text Crypt - Inno Setup installer script
; Installs to C:\Program Files\EADC Text Crypt
;
; Build order:
;   1. Run build_exe.bat first. This creates: dist\EADC_Text_Crypt.exe
;   2. Open this .iss file with Inno Setup Compiler
;   3. Compile

#define MyAppName "EADC Text Crypt"
#define MyAppVersion "1.2.1"
#define MyAppPublisher "N4EAC"
#define MyAppExeName "EADC_Text_Crypt.exe"

[Setup]
AppId={{8A2B5F57-8F9B-4C38-B3D5-4A5A4D3EADC}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/N4EAC/text-cryptography
AppSupportURL=https://github.com/N4EAC/text-cryptography
AppUpdatesURL=https://github.com/N4EAC/text-cryptography
DefaultDirName={commonpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=EADC_Text_Crypt_v{#MyAppVersion}_Setup
SetupIconFile=eadc_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "eadc_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "eadc_icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\eadc_icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\eadc_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

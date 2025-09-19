; Inno Setup Script for LJK Scanner

[Setup]
AppName=LJK Scanner
AppVersion=1.0
DefaultDirName={pf}\LJK Scanner
DefaultGroupName=LJK Scanner
OutputBaseFilename=LJK_Scanner_Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico     
UninstallDisplayIcon={app}\ljk_scanner.exe
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Files]
Source: "dist\ljk_scanner.exe"; DestDir: "{app}"; Flags: ignoreversion
; Tambahkan file lain jika perlu, contoh:
; Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LJK Scanner"; Filename: "{app}\ljk_scanner.exe"
Name: "{group}\Uninstall LJK Scanner"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\ljk_scanner.exe"; Description: "Jalankan LJK Scanner"; Flags: nowait postinstall skipifsilent

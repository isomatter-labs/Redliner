[Setup]
AppName=Redliner
AppVersion=0.3.3
DefaultDirName={pf}\redliner
DefaultGroupName=Redliner
OutputDir=..\dist\installer
OutputBaseFilename=redliner_installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\onedirectory\redliner\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Redliner"; Filename: "{app}\redliner.exe"
Name: "{group}\Uninstall Redliner"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Redliner"; Filename: "{app}\redliner.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

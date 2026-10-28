[Setup]
AppName=DIMA Accounting
AppVersion=1.0
AppPublisher=Omid-Rezapour
DefaultDirName={userpf}\DIMA Accounting
DefaultGroupName=DIMA Accounting
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=DIMA_Accounting_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\DIMA_Accounting.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DIMA Accounting"; Filename: "{app}\DIMA_Accounting.exe"
Name: "{autodesktop}\DIMA Accounting"; Filename: "{app}\DIMA_Accounting.exe"

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchFile = Join-Path $ProjectPath "start_jay.bat"
$ShortcutPath = Join-Path $DesktopPath "Jay - Auction Analyzer.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $BatchFile
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.Description = "Jay - BringATrailer Auction Analyzer"
$Shortcut.IconLocation = "C:\Windows\System32\cmd.exe,0"
$Shortcut.Save()

Write-Host "Desktop shortcut created: $ShortcutPath"
Write-Host "You can now double-click 'Jay - Auction Analyzer' on your desktop to start the app!"

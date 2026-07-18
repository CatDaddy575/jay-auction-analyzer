Set objShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strPath

' Open browser first
objShell.Run "start http://localhost:8501", 0, False

' Wait a moment then start streamlit silently
WScript.Sleep 1000
objShell.Run "cmd /c streamlit run app.py", 0, False

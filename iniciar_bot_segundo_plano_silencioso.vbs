Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\mega-drive-cloner"
WshShell.Run "pythonw.exe D:\mega-drive-cloner\bot_telegram_local.py", 0, False

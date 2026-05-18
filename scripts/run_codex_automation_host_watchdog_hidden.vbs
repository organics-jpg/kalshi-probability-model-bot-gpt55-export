Set shell = CreateObject("WScript.Shell")
command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\Users\organ\Desktop\KALSHI + TRUFFLE BOT\scripts\ensure_codex_automation_host.ps1"""
shell.Run command, 0, False

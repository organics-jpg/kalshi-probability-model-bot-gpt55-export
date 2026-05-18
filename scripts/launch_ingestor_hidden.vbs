Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT" && C:\Python312\python.exe research_ingestor.py --dataset live_mushroom_v21_size2 --watch --interval-seconds 300", 0, False

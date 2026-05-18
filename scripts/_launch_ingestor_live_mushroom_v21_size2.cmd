@echo off
cd /d "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT"
".\venv\Scripts\python.exe" ".\research_ingestor.py" --dataset live_mushroom_v21_size2 --watch --interval-seconds 300 1>> "logs\launcher\mushroom_v21_ingestor_restart_20260430_195007.out.log" 2>> "logs\launcher\mushroom_v21_ingestor_restart_20260430_195007.err.log"

@echo off
cd /d "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\run_probability_lab_ingestor_watch.ps1" -DatasetTag live_mushroom_v21_size2 -IntervalSeconds 300 1>> "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\launcher\mushroom_v21_ingestor_restart_20260430_195225.out.log" 2>> "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\launcher\mushroom_v21_ingestor_restart_20260430_195225.err.log"

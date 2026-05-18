@echo off
setlocal
cd /d "%~dp0.."
set "PYTHON_EXE=C:\Python312\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
set "STDOUT_LOG=%CD%\logs\edge_research\live_liquidity_dwell_size2_log_backfill_watcher.stdout.log"
set "STDERR_LOG=%CD%\logs\edge_research\live_liquidity_dwell_size2_log_backfill_watcher.stderr.log"
"%PYTHON_EXE%" ".\research_live_bot_log_backfill.py" --dataset "live_liquidity_dwell_size2" --storage-tag "live_liquidity_dwell_size2" --watch --interval-seconds 30 >> "%STDOUT_LOG%" 2>> "%STDERR_LOG%"

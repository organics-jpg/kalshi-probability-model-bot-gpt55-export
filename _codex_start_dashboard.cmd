@echo off
cd /d "%~dp0"
set "PY=%~dp0venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" -c "import streamlit" >nul 2>nul
if errorlevel 1 (
  echo Streamlit is not available. Run setup_dashboard.ps1 first.
  exit /b 1
)
"%PY%" -m streamlit run "%~dp0dashboard.py" --server.address 127.0.0.1 --server.port 8501

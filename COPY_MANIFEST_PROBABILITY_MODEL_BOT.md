# KALSHI PROBABILITY MODEL BOT Copy Manifest

Created: 2026-04-29 20:45:43 -04:00
Source: C:\Users\organ\Desktop\KALSHI + TRUFFLE BOT
Target: C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT

Included:
- Top-level runnable/research files: Python scripts, PowerShell/CMD launchers, docs/config examples, requirements, README files, and related root files
- .streamlit
- docs
- logs
- research_data
- scripts
- stats
- Empty state directory placeholder

Excluded intentionally:
- .git
- venv
- __pycache__
- _archive
- .vscode
- secrets
- live state contents
- .env
- detached dashboard stdout/stderr log files at repo root
- reserved/stray root file nul

Notes:
- This copy is meant for research, dashboard use, replay, and backtests.
- Live trading credentials/state were intentionally not copied.
- To configure live credentials later, start from .env.example and review all behavior manually first.
- Research Lab metadata preserves the original capture provenance paths from the source repo.
- Dashboard launchers were adjusted in this copy to use .\venv when present, or python from PATH otherwise.
- Run .\setup_dashboard.ps1 in this folder to create a fresh local dashboard virtual environment.

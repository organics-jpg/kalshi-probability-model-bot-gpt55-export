# Project Tree Guide

This repo has a few different kinds of files mixed together. The important guardrail is that live bot code and research scripts may assume they live in the repo root, so most Python and PowerShell files are intentionally left in place unless their imports/path assumptions are checked first.

## Keep In Root

- `kalshi_btc15m_bot_ws.py`: main live bot.
- `dashboard.py`: main dashboard.
- `score_bot_log.py`: log scoring utility.
- `hourly_truffle_edge_research.py`: hourly Codex edge-search runner used by automation.
- `truffle_*.py`: Truffle integration/replay modules.
- `truffle_*_prompt.txt`: prompt files loaded by live/probe code from root-relative paths.
- `run_*.ps1`, `setup_*.ps1`, `tail_*.ps1`: operator scripts and launch helpers.

## Organized Folders

- `docs/research/`: research notes and integration specs.
- `logs/`: active bot, dashboard, Truffle, and research output logs.
- `logs/edge_research/`: hourly edge-search reports, ledgers, charts, and strategy memory.
- `_archive/root_logs/YYYY-MM-DD/`: old top-level launch logs moved out of the root.
- `research_data/`, `stats/`, `state/`: local datasets and bot state.
- `secrets/`: local secret material.
- `venv/`: Python virtual environment.

## One-Off Research Scripts

Files like `probe_*.py`, `analyze_*.py`, `evaluate_*.py`, `validate_*.py`, `stress_*.py`, `research_*.py`, and `export_*.py` are research scratch/probe scripts. They are intentionally not moved yet because many may rely on `Path(__file__).parent` resolving to the repo root.

For a cleaner editor view, `.vscode/settings.json` hides those files from the VS Code explorer while leaving them on disk and runnable.

The same noisy research/probe files are also marked with the Windows `Hidden` attribute. A manifest lives at `docs/research/hidden_tree_files.txt`.

To show them in PowerShell, use:

```powershell
Get-ChildItem -Force
```

To unhide them later:

```powershell
Get-Content .\docs\research\hidden_tree_files.txt | ForEach-Object { attrib -h $_ }
```

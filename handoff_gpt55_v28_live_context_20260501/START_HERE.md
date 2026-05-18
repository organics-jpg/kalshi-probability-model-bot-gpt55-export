# GPT-5.5 Handoff: BTC Mushroom v28 Live Bot Context

Generated: 2026-05-01 06:35:10 UTC-04:00.

This folder is a sanitized work bundle for another model or engineer. It is meant to explain how the existing Kalshi BTC 15m bot actually behaves live, because v28 was created mostly as a standalone fair-value engine.

## Start Here

1. Read `PROMPT_FOR_GPT_5_5.md`.
2. Read `BOT_ARCHITECTURE_CONTEXT.md`.
3. Read `OVERNIGHT_PERFORMANCE_SUMMARY.md` and `KNOWN_ISSUES_AND_HYPOTHESES.md`.
4. Use `LIVE_CONFIG_SANITIZED.md` plus the files in `data/` and `logs/` to reason from real behavior.
5. Use `code_context/KEY_FUNCTION_LOCATIONS.md` and `code_context/RELEVANT_CODE_EXCERPTS.md` before editing `kalshi_btc15m_bot_ws.py`.

## Important Safety Notes

- This bundle intentionally does not include `.env`, `secrets/`, private keys, tokens, or API keys.
- Order IDs/client IDs were removed or replaced.
- PnL in this bundle is gross before fees unless explicitly stated.
- Inferred settlement outcomes come from late orderbook heartbeats, not from a canonical settlement API.

## Core Files In The Repo

- `kalshi_btc15m_bot_ws.py`: monolithic live bot, orderbook, state, entry/exit execution.
- `btc_mushroom_forecaster_v28_fast.py`: v28 fair-value model.
- `btc_mushroom_live_fv_worker_v28.py`: live worker wrapper for v28.
- `scripts/run_probability_lab_bot_live_size2.ps1`: current live launcher/config.
- `logs/live_mushroom_v28_size2/`: source live logs.
- `state/live_mushroom_v28_size2/bot_state.json`: live state file.

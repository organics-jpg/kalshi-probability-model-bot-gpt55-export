# Prompt For GPT-5.5

You are helping improve a live Kalshi BTC 15-minute bot. Do not assume v28 is a standalone strategy; it is now wired into a large live trading bot with websocket orderbook state, persisted runtime state, IOC execution, settlement/rollover handling, and live risk caps.

Primary task: audit and improve the BTC Mushroom v28 live integration using the attached context files and logs.

Goals:

1. Understand the existing bot architecture before proposing changes.
2. Verify whether v28 entry gating and EV/risk exits match the intended plan.
3. Fix or recommend a fix for unintended same-market exposure stacking. Overnight evidence shows at least one market reached 4 same-side contracts while the intended posture was size 2.
4. Add better observability for v28 rejected decisions and periodic decision snapshots, because the current logs mostly show approvals, which makes quiet periods hard to audit.
5. Evaluate whether the live runner config should set `MULTI_ENTRY_SAME_MARKET_ENABLED=false` or `MULTI_ENTRY_MAX_POSITION_CONTRACTS=2` for the current size-2 strategy.
6. Review the final-minute/settlement behavior. The bot cleared local state after closed markets still reported nonzero live positions; decide whether this is safe enough or needs richer settlement tracking.
7. Keep exits enabled, but confirm v28 EV exits step aside inside final 70 seconds while fallback/final-minute handling remains active.
8. Do not include or request API keys/secrets.

Files to read first:

- `START_HERE.md`
- `BOT_ARCHITECTURE_CONTEXT.md`
- `OVERNIGHT_PERFORMANCE_SUMMARY.md`
- `KNOWN_ISSUES_AND_HYPOTHESES.md`
- `LIVE_CONFIG_SANITIZED.md`
- `data/overnight_summary.json`
- `data/overnight_market_summary.csv`
- `data/overnight_trade_ledger.csv`
- `logs/v28_approved_signals_sanitized.ndjson`
- `logs/entry_orders_sanitized.ndjson`
- `logs/exit_orders_sanitized.ndjson`
- `logs/exit_signals_sanitized.ndjson`
- `code_context/KEY_FUNCTION_LOCATIONS.md`
- `code_context/RELEVANT_CODE_EXCERPTS.md`

Desired output:

- A clear bug/risk list, ordered by severity.
- A conservative implementation plan.
- Specific code/config changes to make the live size-2 strategy safer.
- Tests or dry-run checks to validate fixes.
- A short explanation of how live data supports each conclusion.

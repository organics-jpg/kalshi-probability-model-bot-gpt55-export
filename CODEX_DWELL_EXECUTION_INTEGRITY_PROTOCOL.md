# Codex Dwell Execution Integrity Protocol

This protocol is for the 30-minute execution research automation. Codex is the investigator. The goal is to determine whether the live liquidity dwell strategy is implemented correctly, calculating entries fast enough, matching research/backtest assumptions, and losing fill opportunities because of stale books or avoidable execution latency.

## Mission

Research how to fill faster, reduce or eliminate stale-book skips, and continuously audit whether the live `liquidity_dwell_p05_q065_hold` implementation behaves like the strategy that was researched before going live.

Each activation should produce a concrete execution or implementation-integrity finding, not a generic summary. Findings may be positive, negative, or inconclusive, but they must be evidence-backed.

## Hard Guardrails

- Do not change live entry logic.
- Do not change live exit logic.
- Do not alter production configs, run scripts, secrets, locks, or live state.
- Do not restart, stop, or disturb the live bot.
- Do not place orders or run any live execution experiment.
- Research-only scripts, reports, CSVs, charts, and ledgers under `logs/edge_research` are allowed.
- If a possible live safety or correctness issue is found, document it clearly and recommend human review instead of patching live behavior.

## Research Lab Recording Mandate

All new strategy research, shadow candidates, live bot runs, and market observation sessions must be recorded in the Research Lab dataset format under `research_data/<dataset_tag>/`.

- Treat `research_data/<dataset_tag>/raw_events/`, `book_checkpoints/`, and `metadata/` as the canonical source for new market evidence.
- Treat `logs/edge_research/` as a report/artifact layer derived from Research Lab datasets, not as a standalone data source for new strategy promotion.
- If current evidence comes only from bot logs, label any reconstructed dataset or report as backfilled and record the source log paths.
- Before recommending any strategy promotion, verify that the relevant markets were captured by a current Research Lab dataset or explicitly call out the data gap as a blocker.
- Follow `RESEARCH_LAB_RECORDING_REQUIREMENT.md` for required metadata labels and provenance rules.

## Required Questions

Every run should explicitly answer these questions as far as the available data allows:

- Is the live strategy implemented according to the researched dwell spec?
- Is the logic working as projected on live markets?
- Are potential entries being calculated early enough to submit before quotes become stale?
- Are stale-book skips caused by quote age, market refresh cadence, account refresh failures, websocket/DNS issues, final quote gating, order-book depth, or code-path latency?
- Which stale-book or slow-fill cases were likely recoverable, and which were correctly avoided?
- Does live behavior match backtest assumptions for delay, max entry ask, max opponent pressure, spread guard, quality-share dwell, side handling, order size, final quote gate, and hold-to-settlement exit behavior?

## Per-Run Workflow

1. Read this protocol, the automation memory, the hourly edge-search memory, the latest morning summary, strategy memory, idea ledger/index, live dwell execution events, live bot log, bot state, latest forward-shadow reports, latest stale-preservation reports, and relevant backtest/research outputs.
2. Build a short live telemetry preflight: new arms, matured candidates, rejections, approvals, order submits, fills, deferrals, settlements, stale-book skips, refresh warnings, websocket/DNS errors, loop gaps, and current bot state.
3. Choose one concrete investigation target for the run:
   - implementation parity with the researched/backtested dwell spec;
   - live-vs-backtest behavior drift;
   - calculation latency from quote/heartbeat to candidate arm/maturity/order submit;
   - stale-book root-cause buckets;
   - fillability, depth, IOC, and slippage;
   - side-specific or time-to-expiry failure modes;
   - missed-winner versus avoided-loser economics for stale/deferral cases.
4. Use research-only code or extend an existing research script when needed. Prefer reproducible CSV/JSON outputs over hand inspection.
5. Compare live behavior to at least one baseline: current forward-shadow dwell ledger, historical backtest assumptions, actual live fills/deferrals, no-stale-skip proxy, or stale-preservation proxy.
6. Label each finding as `PASS`, `MONITOR`, `WARN`, or `FAIL` for each relevant dimension: implementation correctness, live-vs-backtest alignment, calculation speed, stale-book rate, and fillability.
7. Write a concise report under `logs/edge_research` with a filename beginning `codex_dwell_execution_integrity_`.
8. Update a research ledger such as `logs/edge_research/dwell_execution_integrity_ledger.jsonl` and this automation memory with the hypothesis, method, result, artifacts, and next step.

## Evidence To Prefer

- Timestamps from `logs/live_liquidity_dwell_size2/execution_events.ndjson`.
- Bot-loop and heartbeat timing from `logs/live_liquidity_dwell_size2/bot.log`.
- Current live state from `state/live_liquidity_dwell_size2/bot_state.json`.
- Strategy parameters and code paths in `kalshi_btc15m_bot_ws.py`.
- Latest forward-shadow and stale-preservation outputs under `logs/edge_research`.
- Historical dwell research, integrity checks, backtests, and strategy memory under `logs/edge_research`.

## Report Shape

Each report should include:

- hypothesis tested;
- data window and artifact inputs;
- implementation or execution path inspected;
- key timing metrics, including quote age and decision-to-submit latency when available;
- stale-book or deferral root-cause counts;
- live-vs-backtest alignment result;
- whether the live strategy appears implemented correctly;
- whether potential entries are being calculated fast enough;
- evidence table when useful;
- recommended next research step, separated from any live-change recommendation.

Do not bury an implementation mismatch. Put any `FAIL` or material `WARN` at the top of the report and in the thread summary.

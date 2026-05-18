# v28 Lead Exit Policy Completion Gap - 2026-05-07

Research-only. No live bot changes, process control, or orders.

## Lead Candidate

The current lead existing candidate is an exit-policy repair layered onto the current live v28 entry and sizing policy:

- Entry: current v28 live gate from `scripts/run_probability_lab_bot_live_size2.ps1`.
  - `MUSHROOM_V28_DECISION_ENGINE_ENABLED=true`
  - `MUSHROOM_V28_MIN_P_SIDE=0.85`
  - `MUSHROOM_V28_MIN_EDGE_CENTS_15M=2.0`
  - `MUSHROOM_V28_MAX_ASK_CENTS=90`
  - `MUSHROOM_V28_MIN_SECONDS_TO_CLOSE=70`
  - `MUSHROOM_V28_MAX_SECONDS_TO_CLOSE=900`
  - fee/slippage guard uses `MUSHROOM_V28_MODEL_BUFFER_CENTS=1.0` and `MUSHROOM_V28_SLIPPAGE_CENTS=1.0`
- Sizing: current live size-2 policy.
  - `POSITION_SIZE=2`
  - same-market multi-entry enabled
  - `MULTI_ENTRY_MAX_POSITION_CONTRACTS=10`
  - `MULTI_ENTRY_MIN_SECONDS_BETWEEN_ENTRIES=120`
- Candidate exit: `book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0`.
  - Suppress `value_over_hold` exits when held-side `p_hold - exit_bid >= 0.00`.
  - Also suppress `value_over_hold` exits when `p_hold >= 0.85` and `fair_drawdown_cents >= -5.0`.
  - Also suppress `value_over_hold` exits when `p_hold >= 0.95`, even if book gap is slightly negative.
  - Suppress `probability_reduce` exits only when `p_hold >= 0.79` and `p_hold - exit_bid >= 0.00`.
  - Keep collapse exits unchanged.
- Risk/kill rule: current v28 risk stop remains active. Promotion is blocked while control loss-count churn is unresolved.
- Accounting/PnL rule: use raw `logs/live_mushroom_v28_size2/execution_events.ndjson` via `score_bot_log.py`/candidate probes, not only `recent_market_outcomes.json`.
- Live-test rule: do not live-test until live-readiness artifact passes and a single-process coordinator exists if a candidate must run beside another live lane.
- Iteration rule: judge only rows after each candidate freeze clock; no pre-freeze diagnostic rows count as promotion evidence.

## Refreshed Evidence

Generated/refreshed around 2026-05-07 20:59 UTC:

- Current live-only v28 baseline: `1361c` / `$13.61` from `stats/live_mushroom_v28_size2/summary.json`.
- Control risk stop: active by loss count, not drawdown.
  - Control window: `173` scored trades, `823c` gross, `75` losses.
  - Main failure classes: `exit_policy_cost=-1029c`, `fv_or_entry_timing_error=-784c`.
- Exit watch dashboard:
  - `book_gap_loss_guard`: `59` settled, `17` suppressions, `+242c`, `0c` loss-control cost, blocker `suppressed_decisions_lt_30`.
  - `book_gap_loss_guard_v2`: `58` settled, `5` suppressions, `+152c`, `0c` loss-control cost, blocker `suppressed_decisions_lt_30`.
  - `book_gap_loss_guard_v3`: `46` settled, `9` suppressions, `+166c`, `0c` loss-control cost, cushion `6`, blocker `suppressed_decisions_lt_30`.
  - `common_clock_strict_forward_v1`: `59` settled, `17` suppressions, `+242c`, `0c` loss-control cost, blocker `suppressed_decisions_lt_30`.
  - `common_clock_strict_forward_v2`: `58` settled, `17` suppressions, `+242c`, `0c` loss-control cost, blocker `suppressed_decisions_lt_30`.
  - `common_clock_strict_forward_v3`: `46` settled, `13` suppressions, `+214c`, `0c` loss-control cost, blocker `suppressed_decisions_lt_30`.
- V3 strict rows: `9/0` suppressed W/L, `+166c`, no observed loss-control cost.
- V3 diagnostic rows: `39/0` suppressed W/L, `+811c`, no observed loss-control cost.

## Promotion Gap

This is not complete yet.

Missing gates:

- Suppressed-decision density: v3 needs `21` more strict suppressions to reach 30; common-clock v3 needs `17` more.
- Live readiness: `logs/edge_research/v28_live_trade_readiness_latest.md` still says `Any live-ready candidate: False`.
- Risk stop: control loss-count stop remains active.
- Full end-to-end proof: current evidence is strongest on exit repair, but the full entry+exit+sizing+risk policy has not passed a live-test gate.
- Live-test isolation: simultaneous live testing is blocked without a single-process coordinator and separate accounting.

## Next Action

Keep this as the lead existing candidate family. Do not start a new broad entry family yet.

Concrete next step:

1. Continue collecting strict post-freeze exit rows.
2. Re-run:
   - `python .\probe_v28_exit_policy_watch_dashboard.py`
   - `python .\probe_v28_exit_policy_common_clock_watch.py`
   - `python .\probe_v28_frozen_exit_book_gap_loss_guard_v3.py`
   - `python .\probe_v28_objective_gap_checklist.py`
3. If v3 or common-clock v3 reaches at least 30 suppressions with positive delta, zero loss-control cost, and cushion >=3, run a full policy readiness audit against current v28 entry/sizing/risk and refreshed live-only baseline.
4. Only after readiness passes, design the controlled live-test/coordinator path.

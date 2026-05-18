# Bot Architecture Context

This is a live Kalshi BTC 15m trading bot, not just a model runner.

## Main Loop Shape

The bot watches one BTC 15m Kalshi market at a time. It maintains:

- Kalshi orderbook websocket state.
- Current market ticker, strike, close time.
- Persisted runtime state: pending order, open position, exit confirmation, traded markets.
- BTC fair-value model state, now with Mushroom v28.
- Live account state / balance / positions checks.

## Entry Flow

High-level path:

1. `maybe_check_entry()` decides whether entry evaluation can run.
2. `detect_entry_signal()` delegates to v28 when `MUSHROOM_V28_DECISION_ENGINE_ENABLED=true`.
3. `detect_mushroom_v28_entry_signal()` evaluates YES and NO candidates.
4. `build_mushroom_v28_decision_fields()` calculates p-side, fair values, net edge, freshness, risk, ask caps, balance, and block reason.
5. If approved, an `EntrySignal` becomes an `ExecutionPlan`.
6. `execute_entry()` submits IOC order(s), reconciles fills, writes `state.position`, emits telemetry, and marks market traded.

Important: entry safety is split across model gates, `entry_block_reason()`, `v28_allowed_entry_count()`, execution policy, and persisted state. A model-only view will miss important live behavior.

## Exit Flow

High-level path:

1. `maybe_check_exit()` runs when `state.position` exists.
2. `detect_exit_signal()` includes fallback stops and v28 live exit logic.
3. `detect_mushroom_v28_exit_signal()` compares executable exit value against model hold value and probability/fair-value deterioration.
4. Exit execution uses protected IOC/sliced logic and reconciliation.
5. Inside final 70 seconds, v28 EV exits are supposed to step aside; fallback/final-minute behavior remains.

## State And Settlement

`state/live_mushroom_v28_size2/bot_state.json` is the live persisted state. Closed markets can still report nonzero positions briefly after settlement. The bot currently has a pathway that clears local state and advances if it considers the position settlement-only. This worked overnight but should be reviewed.

## Why v28 Needs Bot Context

v28 only produces fair values/probabilities. The live bot adds:

- Orderbook freshness and sequence trust.
- BTC tick freshness and fallback feeds.
- Balance/risk sizing.
- IOC fill/retry behavior.
- Same-market re-entry controls.
- Settlement and rollover behavior.
- Telemetry and persistence.

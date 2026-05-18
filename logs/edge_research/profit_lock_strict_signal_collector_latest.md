# Profit Lock Strict Signal Collector

Generated UTC: `20260505_031943Z`

## Scope

- Research-only collector; no orders are submitted and no bot files or live processes are touched.
- Runs strict pre-resolution monitors so future evidence is registered before outcomes are known.
- Denominator is recurring BTC 15-minute markets, not fills or selected heartbeat rows.

- Iteration: 614
- Failed steps: 0
- Main monitor new records: 0
- Path monitor new records: 0
- Strict registered coverage failures: 13

## Command Results

| step | return code | stdout tail | stderr tail |
|---|---:|---|---|
| `pending_signal_monitor` | 0 | Profit lock pending signal monitor complete<br>new_records=0 registered=3040<br>removed_post_close_records=0<br>report=logs\edge_research\profit_lock_pending_signal_monitor_latest.md |  |
| `path_pending_monitor` | 0 | Kinetic path-confirmation pending monitor complete<br>new_records=0 registered=119<br>removed_post_close_records=0<br>report=logs\edge_research\kinetic_path_confirmation_pending_monitor_latest.md |  |
| `market_denominator_audit` | 0 | Profit lock market-denominator audit complete<br>locks=34<br>coverage_fail=13<br>report=logs\edge_research\profit_lock_market_denominator_audit_latest.md |  |
| `registered_signal_readiness` | 0 | Profit lock registered-signal readiness complete<br>ready_count=0<br>report=logs\edge_research\profit_lock_registered_signal_readiness_latest.md |  |
| `registered_signal_delta` | 0 | Profit lock registered-signal delta complete<br>changed=0<br>report=logs\edge_research\profit_lock_registered_signal_delta_latest.md |  |

## Top Registered Coverage Rows

| lock | registered/resolved/pending | registered coverage | resolved coverage | net P&L | ready |
|---|---:|---:|---:|---:|---|
| book_hour04_v2_switch | 86/86/0 | 0.9555555555555556 | 0.9772727272727273 | -375.0c | False |
| frontier_v2_continuous | 107/107/0 | 0.9553571428571429 | 0.9727272727272728 | -177.0c | False |
| book_margin | 106/106/0 | 0.954954954954955 | 0.9724770642201835 | 71.0c | False |
| book_margin_early | 102/102/0 | 0.9532710280373832 | 0.9714285714285714 | 41.0c | False |
| logit_blend_edge10 | 76/76/0 | 0.9382716049382716 | 0.9620253164556962 | 178.0c | False |

## Read

- Collector iteration completed; strict evidence was refreshed without changing live trading code.

# v28 Successor Live P&L Policy Forward Loop

Research-only bounded loop for freezing live policy rows, labeling settled rows, scoring paired baselines, and rerunning the strict profit-goal audit.

## Summary

- Generated UTC: `2026-05-14T01:02:49Z`
- Loop status: `completed_iterations`
- Collect mode: `none`
- Collection scope: `nearest_close`
- Iterations run: `1` / `1`
- Profit goal complete: `True`
- Promotion allowed: `False`
- Controlled live test authorized: `False`

## Final State

- cycle_status: `profit_goal_candidate_forward_ready`
- policy_id: `v28s_live_pnl_midband_no_fade_yes_v019`
- policy_hash: `5bf8d66dbe2b31e01d38abe8a0238e68`
- registry_rows: `16302`
- primary_policy_rows_after_hash: `314`
- joined_primary_rows: `313`
- joined_primary_markets: `11`
- primary_entered_rows: `3`
- primary_net_pnl_cents: `70.0`
- primary_delta_vs_v28_cents: `762.3`
- overall_status: `complete`
- test_status: `pass`

## Iterations

| iteration | cycle status | primary policy rows | joined rows | joined markets | entries | net cents | delta vs v28 | audit |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `profit_goal_candidate_forward_ready` | 314 | 313 | 11 | 3 | 70.0 | 762.3 | `complete` |

## Guardrails

- does not start or stop live bot processes
- does not read or write secrets
- does not place orders
- does not mutate live thresholds, order logic, state, or sizing
- uses public/recorded sidecar artifacts only
- keeps pre-policy-hash rows diagnostic only
- keeps controlled live authorization false unless the strict audit eventually passes

## Read

- This loop is an evidence collector and auditor, not a promotion path.
- A skipped policy row can still count as a primary observed opportunity; P&L proof requires settled joined rows and positive same-row economics.
- Use `--collect-mode public-rest` only when public pre-resolution capture is intended.

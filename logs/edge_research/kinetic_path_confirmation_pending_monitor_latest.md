# Kinetic Path-Confirmation Pending Monitor

Generated UTC: `20260505_032000Z`

## Scope

- Research-only pre-resolution registry; no orders are submitted and no bot files or live processes are touched.
- Applies the frozen delayed same-side confirmation policy to raw heartbeat rows, including unresolved markets.
- Registers a signal only after the confirmation condition appears in the log, before outcome is known.

- Confirmation: `same_side_for>=60s AND confirm_score>=0.6`
- Effective entry boundary: `2026-05-03 04:15:00+00:00`
- New records registered this run: 0
- Post-close/non-causal registry records removed this run: 0

## Registry Summary

| registered | pending | resolved | wins/losses | acc | resolved net P&L | first pending |
|---:|---:|---:|---:|---:|---:|---|
| 119 | 0 | 119 | 89/30 | 74.79% | -85.0c | `` |

## Read

- No unresolved path-confirmation signal is currently pending.

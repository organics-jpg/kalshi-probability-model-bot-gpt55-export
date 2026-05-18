# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T12:05:04.050955+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T08:22:49.551119+00:00`
- Model defined UTC: `2026-05-05T08:22:49.551119+00:00`
- Policy: `v57_v55_bookanchor_hold15_prob52_edge0_p65_stc0_600`

## Registry

- Registered shadow entries: 14
- New entries this run: 0
- Finalized / open: 14 / 0
- Exited / settled: 3 / 11
- Observed candidate markets after lock: 14
- Resolved / pending candidate markets after lock: 14 / 0

## Finalized Performance

- Settlement W/L for settled rows: 11/0
- Gross P&L: $0.32
- Fee-adjusted P&L: $-0.10
- Fee-adjusted with 1c entry haircut: $-0.38
- Fee-adjusted ROI on entry cost: -0.42%

## Read

- Too few strict-forward finalized rows for a model decision.

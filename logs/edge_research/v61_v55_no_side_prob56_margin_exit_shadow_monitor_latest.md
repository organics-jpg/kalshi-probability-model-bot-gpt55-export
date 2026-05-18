# v61 v55 NO-Side Prob56 Margin Exit Shadow Monitor

Generated UTC: `2026-05-05T12:05:03.514880+00:00`

## Scope

- Strict-forward shadow validation of the v61 v55 FV prob56 NO-side YES-axis margin-gated exit candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T11:00:45.760125+00:00`
- Model defined UTC: `2026-05-05T11:00:45.760125+00:00`
- Policy: `v61_v55_bookanchor_hold15_prob56_noside_marginlte0p25_edge0_p65_stc0_600`

## Registry

- Registered shadow entries: 4
- New entries this run: 0
- Finalized / open: 4 / 0
- Exited / settled: 0 / 4
- Observed candidate markets after lock: 4
- Resolved / pending candidate markets after lock: 4 / 0

## Finalized Performance

- Settlement W/L for settled rows: 3/1
- Gross P&L: $-0.08
- Fee-adjusted P&L: $-0.20
- Fee-adjusted with 1c entry haircut: $-0.28
- Fee-adjusted ROI on entry cost: -3.29%

## Read

- Too few strict-forward finalized rows for a model decision.

# v60 v55 NO-Side Margin Exit Shadow Monitor

Generated UTC: `2026-05-05T12:05:01.899178+00:00`

## Scope

- Strict-forward shadow validation of the v60 v55 FV NO-side YES-axis margin-gated exit candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T10:49:23.268424+00:00`
- Model defined UTC: `2026-05-05T10:49:23.268424+00:00`
- Policy: `v60_v55_bookanchor_hold15_prob52_noside_marginlte0p25_edge0_p65_stc0_600`

## Registry

- Registered shadow entries: 5
- New entries this run: 0
- Finalized / open: 5 / 0
- Exited / settled: 1 / 4
- Observed candidate markets after lock: 5
- Resolved / pending candidate markets after lock: 5 / 0

## Finalized Performance

- Settlement W/L for settled rows: 3/1
- Gross P&L: $-1.12
- Fee-adjusted P&L: $-1.29
- Fee-adjusted with 1c entry haircut: $-1.39
- Fee-adjusted ROI on entry cost: -16.08%

## Read

- Too few strict-forward finalized rows for a model decision.

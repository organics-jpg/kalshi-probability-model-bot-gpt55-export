# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T09:57:26.439826+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T08:00:25.016813+00:00`
- Model defined UTC: `2026-05-05T08:00:25.016813+00:00`
- Policy: `v55_bookanchor_m10_v20_g05_book_plus2_edge0_p65_stc0_600_prob52`

## Registry

- Registered shadow entries: 8
- New entries this run: 1
- Finalized / open: 8 / 0
- Exited / settled: 1 / 7
- Observed candidate markets after lock: 8
- Resolved / pending candidate markets after lock: 7 / 1

## Finalized Performance

- Settlement W/L for settled rows: 7/0
- Gross P&L: $2.32
- Fee-adjusted P&L: $2.05
- Fee-adjusted with 1c entry haircut: $1.89
- Fee-adjusted ROI on entry cost: 16.35%

## Read

- Too few strict-forward finalized rows for a model decision.

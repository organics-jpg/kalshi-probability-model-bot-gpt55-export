# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T07:17:17.176844+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T04:06:03.978229+00:00`
- Model defined UTC: `2026-05-05T04:06:03.978229+00:00`
- Policy: `v42_latent_hole_book_edge0_p64_stc0_600_prob52`

## Registry

- Registered shadow entries: 12
- New entries this run: 7
- Finalized / open: 12 / 0
- Exited / settled: 5 / 7
- Observed candidate markets after lock: 12
- Resolved / pending candidate markets after lock: 12 / 0

## Finalized Performance

- Settlement W/L for settled rows: 6/1
- Gross P&L: $-4.04
- Fee-adjusted P&L: $-4.50
- Fee-adjusted with 1c entry haircut: $-4.74
- Fee-adjusted ROI on entry cost: -23.58%

## Read

- Too few strict-forward finalized rows for a model decision.

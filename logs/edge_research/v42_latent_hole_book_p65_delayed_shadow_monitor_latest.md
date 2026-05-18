# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T07:20:04.522628+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T05:33:33.135107+00:00`
- Model defined UTC: `2026-05-05T05:33:33.135107+00:00`
- Policy: `v42_latent_hole_book_edge0_p65_stc120_600_prob52`

## Registry

- Registered shadow entries: 6
- New entries this run: 6
- Finalized / open: 6 / 0
- Exited / settled: 2 / 4
- Observed candidate markets after lock: 6
- Resolved / pending candidate markets after lock: 6 / 0

## Finalized Performance

- Settlement W/L for settled rows: 4/0
- Gross P&L: $-0.38
- Fee-adjusted P&L: $-0.60
- Fee-adjusted with 1c entry haircut: $-0.72
- Fee-adjusted ROI on entry cost: -6.20%

## Read

- Too few strict-forward finalized rows for a model decision.

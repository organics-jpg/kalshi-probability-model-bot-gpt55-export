# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T07:26:56.152255+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T05:37:39.666426+00:00`
- Model defined UTC: `2026-05-05T05:37:39.666426+00:00`
- Policy: `v45_latent_disagree_book_else_blend90_edge0_p65_stc0_600_prob54`

## Registry

- Registered shadow entries: 7
- New entries this run: 1
- Finalized / open: 6 / 1
- Exited / settled: 2 / 4
- Observed candidate markets after lock: 7
- Resolved / pending candidate markets after lock: 6 / 1

## Finalized Performance

- Settlement W/L for settled rows: 4/0
- Gross P&L: $-0.10
- Fee-adjusted P&L: $-0.33
- Fee-adjusted with 1c entry haircut: $-0.45
- Fee-adjusted ROI on entry cost: -3.51%

## Read

- Too few strict-forward finalized rows for a model decision.

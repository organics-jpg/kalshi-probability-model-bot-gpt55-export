# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T12:32:09.436360+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T06:45:56.595204+00:00`
- Model defined UTC: `2026-05-05T06:45:56.595204+00:00`
- Policy: `v50_thinedge_ask90_edge1_stc450_cap75_edge0_p65_stc0_600_prob54`

## Registry

- Registered shadow entries: 23
- New entries this run: 10
- Finalized / open: 23 / 0
- Exited / settled: 5 / 18
- Observed candidate markets after lock: 23
- Resolved / pending candidate markets after lock: 23 / 0

## Finalized Performance

- Settlement W/L for settled rows: 18/0
- Gross P&L: $2.86
- Fee-adjusted P&L: $2.08
- Fee-adjusted with 1c entry haircut: $1.62
- Fee-adjusted ROI on entry cost: 5.69%

## Read

- Too few strict-forward finalized rows for a model decision.

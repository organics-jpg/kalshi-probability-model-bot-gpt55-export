# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T12:35:40.108877+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T07:36:31.104711+00:00`
- Model defined UTC: `2026-05-05T07:36:31.104711+00:00`
- Policy: `v53_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75_edge0_p65_stc0_600_prob54`

## Registry

- Registered shadow entries: 20
- New entries this run: 9
- Finalized / open: 20 / 0
- Exited / settled: 4 / 16
- Observed candidate markets after lock: 20
- Resolved / pending candidate markets after lock: 20 / 0

## Finalized Performance

- Settlement W/L for settled rows: 16/0
- Gross P&L: $3.24
- Fee-adjusted P&L: $2.56
- Fee-adjusted with 1c entry haircut: $2.16
- Fee-adjusted ROI on entry cost: 8.03%

## Read

- Too few strict-forward finalized rows for a model decision.

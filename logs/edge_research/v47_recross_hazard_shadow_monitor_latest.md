# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T12:29:09.120892+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T06:19:27.463102+00:00`
- Model defined UTC: `2026-05-05T06:19:27.463102+00:00`
- Policy: `v47_recross_sigma1_v3cap68_edge0_p65_stc0_600_prob54`

## Registry

- Registered shadow entries: 25
- New entries this run: 10
- Finalized / open: 24 / 1
- Exited / settled: 6 / 18
- Observed candidate markets after lock: 25
- Resolved / pending candidate markets after lock: 24 / 1

## Finalized Performance

- Settlement W/L for settled rows: 18/0
- Gross P&L: $2.46
- Fee-adjusted P&L: $1.62
- Fee-adjusted with 1c entry haircut: $1.14
- Fee-adjusted ROI on entry cost: 4.27%

## Read

- Too few strict-forward finalized rows for a model decision.

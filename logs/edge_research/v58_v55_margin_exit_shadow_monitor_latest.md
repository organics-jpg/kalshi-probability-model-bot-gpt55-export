# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T10:35:25.786490+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T10:22:10.853096+00:00`
- Model defined UTC: `2026-05-05T10:22:10.853096+00:00`
- Policy: `v58_v55_bookanchor_hold15_prob52_marginlte0p25_edge0_p65_stc0_600`

## Registry

- Registered shadow entries: 1
- New entries this run: 1
- Finalized / open: 1 / 0
- Exited / settled: 0 / 1
- Observed candidate markets after lock: 1
- Resolved / pending candidate markets after lock: 1 / 0

## Finalized Performance

- Settlement W/L for settled rows: 1/0
- Gross P&L: $0.72
- Fee-adjusted P&L: $0.68
- Fee-adjusted with 1c entry haircut: $0.66
- Fee-adjusted ROI on entry cost: 53.12%

## Read

- Too few strict-forward finalized rows for a model decision.

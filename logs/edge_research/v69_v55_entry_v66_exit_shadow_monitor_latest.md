# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T12:21:24.205895+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T12:20:19.781679+00:00`
- Model defined UTC: `2026-05-05T12:20:19.781679+00:00`
- Policy: `v69_v55_entry_v66_exit_hold15_prob52_edge0_p65_stc0_600`

## Registry

- Registered shadow entries: 0
- New entries this run: 0
- Finalized / open: 0 / 0
- Exited / settled: 0 / 0
- Observed candidate markets after lock: 0
- Resolved / pending candidate markets after lock: 0 / 0

## Finalized Performance

- Settlement W/L for settled rows: 0/0
- Gross P&L: $0.00
- Fee-adjusted P&L: $0.00
- Fee-adjusted with 1c entry haircut: $0.00
- Fee-adjusted ROI on entry cost: NA

## Read

- Too few strict-forward finalized rows for a model decision.

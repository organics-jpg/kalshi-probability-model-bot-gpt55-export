# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T03:56:02.705368+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T03:51:25.040846+00:00`
- Model defined UTC: `2026-05-05T03:51:25.040846+00:00`
- Policy: `v38_edgehole80_allday_block_first_8_20_edge-2_p65_stc60_600_prob54`

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

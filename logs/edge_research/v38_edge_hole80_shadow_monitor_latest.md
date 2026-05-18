# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T07:17:16.564478+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T02:46:23.374949+00:00`
- Model defined UTC: `2026-05-05T02:46:23.374949+00:00`
- Policy: `v38_edgehole80_block_first_10_20_p65_prob54`

## Registry

- Registered shadow entries: 17
- New entries this run: 10
- Finalized / open: 17 / 0
- Exited / settled: 6 / 11
- Observed candidate markets after lock: 17
- Resolved / pending candidate markets after lock: 17 / 0

## Finalized Performance

- Settlement W/L for settled rows: 10/1
- Gross P&L: $-4.64
- Fee-adjusted P&L: $-5.21
- Fee-adjusted with 1c entry haircut: $-5.55
- Fee-adjusted ROI on entry cost: -18.66%

## Read

- Too few strict-forward finalized rows for a model decision.

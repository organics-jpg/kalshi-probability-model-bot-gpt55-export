# v38 Edge-Hole Shadow Monitor

Generated UTC: `2026-05-05T03:56:01.991838+00:00`

## Scope

- Strict-forward shadow validation of the v38 edge-hole candidate.
- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.
- No live bot code/process/orders are touched.

## Lock

- Created UTC: `2026-05-05T00:51:32.357578+00:00`
- Model defined UTC: `2026-05-05T00:51:32.357578+00:00`
- Policy: `v38_edgehole_block_first_8_20_p65_prob52`

## Registry

- Registered shadow entries: 10
- New entries this run: 1
- Finalized / open: 9 / 1
- Exited / settled: 3 / 6
- Observed candidate markets after lock: 10
- Resolved / pending candidate markets after lock: 8 / 2

## Finalized Performance

- Settlement W/L for settled rows: 6/0
- Gross P&L: $0.02
- Fee-adjusted P&L: $-0.29
- Fee-adjusted with 1c entry haircut: $-0.47
- Fee-adjusted ROI on entry cost: -1.95%

## Read

- Too few strict-forward finalized rows for a model decision.

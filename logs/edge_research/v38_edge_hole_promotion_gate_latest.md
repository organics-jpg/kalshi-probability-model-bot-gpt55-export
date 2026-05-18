# v38 Edge-Hole Promotion Gate

Generated UTC: `2026-05-05T03:57:24.389339+00:00`
Candidate: `block_market_first_edge_8_20`

## Result

- Overall pass: `False`
- Retrospective pass: `True`
- Temporal pass: `True`
- Leave-one-day-out pass: `True`
- Strict-forward pass: `False`

## Strict Forward

- Registered rows: 10
- Finalized rows: 9 / required 50
- Registered markets: 10 / required 50
- Forward days: 1 / required 2
- Forward coverage vs post-lock observed markets: 76.92% / required 75.00%
- Forward denominator source: `forward_denominator`
- Fee-adjusted P&L: $-0.29
- Fee-adjusted P&L with 1c entry haircut: $-0.47
- Fee-adjusted ROI: -1.95%

## Read

- Candidate does not pass promotion gate. The current blocker is strict-forward sample size/coverage.

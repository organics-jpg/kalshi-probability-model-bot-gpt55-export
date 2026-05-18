# v28 Feature-Gate Pending Resolution Audit

Research-only linkage audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T06:43:14.738140+00:00`
- Candidate: `post_feature_freeze_entry_raw05_recross60_abs085`
- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This audit is linkage-only: it does not change the official frozen candidate score.
- 0/0 pending selected rows have finalized market results in the refreshed live scorer artifacts.
- If those results are linked back into the research surface, selected net would be about 275.0c before any new coverage rows.
- Coverage still needs 4 additional selected denominator rows because the pending rows were already counted as entries.
- Source share is unchanged by resolving pending rows, so the source-quality gate still fails.

## Summary

- Pending rows: `0`
- Pending resolved in market-results artifact: `0`
- Current selected settled/net: `33` / `275.000000c`
- Projected selected settled/net if linked: `33` / `275.000000c`
- Projected cushion cents still needed: `25.000000`
- Reconstructed share unchanged: `0.363636`
- Source gate unchanged: `False`
- Coverage entries needed unchanged: `4`
- Recent-outcome live PnL across pending markets: `$0.000000`

## Rows

| market | side | result | won | est entry net c | live outcome | live pnl $ | trades | ask | edge | recross | abs d |
|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|

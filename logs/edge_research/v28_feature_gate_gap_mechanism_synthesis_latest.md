# v28 Feature-Gate Gap Mechanism Synthesis

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T17:39:10.699753+00:00`
- Raw05 bridge: entries/settled `47/41`, coverage `65.28%`, net `350c ($3.50)`, source `0.277`, live-snapshot gap `983c ($9.83)`
- Raw03 bridge: entries/settled `54/48`, coverage `75.00%`, net `283c ($2.83)`, source `0.370`, live-snapshot gap `1050c ($10.50)`
- Raw05 loss classes: `{'entry_or_fv_failure_exit_helped': 3, 'no_exit_observation': 10}`
- Raw05 loss sources: `{'approved_entry': 3, 'rejected_actionable': 10}`
- Exit-state frontier best: `baseline_live` delta-live `0c ($0.00)`
- Blockers: `research_only, not_promotion_evidence, raw05_losses_mostly_no_exit_observation, approved_losses_exit_helped_vs_hold, raw05_bridge_coverage_gap, raw03_bridge_source_gap, fresh_v28_live_collection_unhealthy`

## Conclusion

Do not repair the current feature-gate gap with broad exit suppression. The raw05 bridge is cleaner but under-covered; its losing rows are mostly no-exit-observation/source rows, and the approved losing rows were helped by exits versus holding. Raw03 restores coverage by admitting risky rows and still fails source/cushion gates.

## Next

- Treat raw05 as a clean-core coverage/source wait, not an exit-suppression repair.
- Do not relax to raw03 for coverage; raw03 marginal rows are source-risk and negative/weak.
- When v28 collection is healthy again, watch for clean raw05-eligible rows or a separately frozen continuous size/source-quality proxy.

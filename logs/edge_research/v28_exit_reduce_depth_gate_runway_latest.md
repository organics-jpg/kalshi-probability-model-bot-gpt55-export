# v28 Exit Reduce Depth-Gate Runway

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:14:20.311485+00:00`
- Depth-gate freeze UTC: `2026-05-06T20:19:43.176664+00:00`

## Interpretation

- This is a runway report only; diagnostic rows are mechanism evidence, not promotion evidence.
- Diagnostic best diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 has settled 132, suppressed 8, delta 397.0c, and full-loss cushion 3.
- Post-birth best post_depth_gate_birth_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 has settled 60, suppressed 2, delta 94.0c, full-loss cushion 0, and blockers ['full_loss_cushion_lt_3'].
- Post-birth still needs 0 settled rows, 3 suppressed exits, and 206.0c of net cushion before this exit repair is promotion-reviewable.

## Runway

| lane | candidate | settled | suppressed | harmful suppressed | delta c | cushion | rows needed | suppressed needed | cushion c needed | absorbable losses | ready | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| diagnostic | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 | 132 | 8 | 0 | 397.000000 | 3 | 0 | 0 | 0.000000 | 3 | True | none |
| post_birth | post_depth_gate_birth_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 | 60 | 2 | 0 | 94.000000 | 0 | 0 | 3 | 206.000000 | 0 | False | full_loss_cushion_lt_3 |

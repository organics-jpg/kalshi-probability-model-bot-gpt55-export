# v28 Exit Reduce Blocker Decision

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T05:16:58.852930+00:00`
- Decision: `watch_child_repairs_do_not_promote_blanket`

## Interpretation

- Blanket p_hold>=0.75 suppression is not promotable: it has positive delta, but at least one suppressed loser turned a controlled reduce exit into a large loss.
- Best clean diagnostic guard is diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_stc_lte_596 with 499.0c delta, 9 suppressions, and no loss-control cost.
- Strict child watches have not yet produced enough post-freeze suppressed decisions to judge the repair.
- Action: keep the cleaner child watches collecting; do not promote blanket reduce suppression while loss-control cost or suppressed-loser blockers remain.

## Blanket Reduce Suppression

- Candidate: `suppress_reduce_p_hold_ge_075`
- Freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Settled: `62`
- Delta vs current exits: `212.000c`
- Suppressed exits: `8`
- Winner recovery / loss-control cost: `372.000c / -160.000c`
- Helpful/harmful suppressed rows: `7/1`
- Blockers: `['suppressed_loss_control_cost_negative']`
- Invalidators now: `['suppressed_loss_control_cost_negative', 'robustness_shadow_interest_false']`

## Child Watch Summary

| source | candidate | strict | settled | suppressed | sup W/L | delta c | loss cost c | cushion | blockers | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| depth_gate_diagnostic | diagnostic_from_reduce_freeze_reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5 | False | 98 | 6 | 6/0 | 319.000 | 0.000 | 3 | none | none |
| depth_gate_strict | post_depth_gate_birth_reduce_suppress_p_hold_ge_079_entry_depth_lte_384 | True | 26 | 0 | 0/0 | 0.000 | 0.000 | 0 | settled_lt_30, no_suppressed_exits_yet, delta_not_positive, full_loss_cushion_lt_3 | settled+4, suppressed+30, positive_delta, cushion+3 |
| observable_loss_control_diagnostic | diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_stc_lte_596 | False | 99 | 9 | 9/0 | 499.000 | 0.000 | 4 | suppressed_decisions_lt_30 | none |
| observable_loss_control_strict | post_observable_birth_reduce_suppress_p75_entry_stc_lte_596 | True | 21 | 0 | 0/0 | 0.000 | 0.000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 | settled+9, suppressed+30, positive_delta, cushion+3 |
| side_geometry_diagnostic | side_geometry_or_no_deep_loss20_suppress_reduce_p_hold_ge_075 | False | 62 | 6 | 6/0 | 318.000 | 0.000 | 3 | none | none |
| side_geometry_strict | base_suppress_reduce_p_hold_ge_075 | True | 6 | 0 | 0/0 | 0.000 | 0.000 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 | settled+24, suppressed+30, positive_delta, cushion+3 |

## Harmful Blanket Rows

| market | side/result | p_hold | drawdown | exit | current c | hold c | delta c | worst mark |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060700-00 | no/yes | 0.800 | 4.040 | 80 | -8.000 | -168.000 | -160.000 | 10 |

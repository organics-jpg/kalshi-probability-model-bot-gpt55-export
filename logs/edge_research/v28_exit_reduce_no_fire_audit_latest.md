# v28 Exit Reduce No-Fire Audit

Research-only no-fire audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T08:24:37.057987+00:00`

## Interpretation

- Research-only no-fire audit; no live bot changes or orders.
- The reduce branch is not currently a leading repair because post-freeze probability-reduce opportunities are too sparse.
- Depth gate saw 1 probability-reduce row in 27 post-birth rows; strict p_hold>=0.79 fires 0 times.
- A looser depth rule would fire 1 time for -120.0c, so widening would currently add loss-control harm.
- Geometry saw 2 probability-reduce rows and 2 base p-hold candidates, but 0 geometry suppressions; the rejected base opportunity was -74.0c.
- Every post-refinement variant has zero suppressions, so refinement cannot be judged until new probability-reduce opportunities arrive.
- Actionable read: keep reduce watches running, but prioritize exit watches with active denominator and clean suppression evidence over widening reduce rules.

## Depth Gate

- Post-birth rows: `27`
- Probability-reduce rows: `1`
- Strict would-suppress rows: `0`
- Loose would-suppress rows/delta: `1` / `-120.00c`
- Strict fail reasons: `{'not_probability_reduce': 26, 'p_hold_below_floor': 1}`

## Geometry

- Post-freeze rows: `37`
- Probability-reduce rows: `2`
- Base p-hold candidates: `2`
- Geometry would-suppress rows: `0`
- Rejected base opportunity delta: `-74.00c`
- Reason counts: `{'fair_drawdown_missing': 6, 'no_positive_drawdown_reject': 10, 'not_probability_reduce': 35, 'p_hold_below_floor': 16, 'p_hold_missing': 6, 'yes_negative_drawdown_reject': 5}`

## Refinement

| candidate | settled | suppressed | delta c | blockers |
|---|---:|---:|---:|---|
| `post_refinement_birth_reduce_suppress_p_hold_ge_079` | 27 | 0 | 0.00 | settled_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `post_refinement_birth_reduce_suppress_p_hold_ge_075_drawdown_lte_2p5` | 27 | 0 | 0.00 | settled_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `post_refinement_birth_reduce_suppress_p_hold_ge_079_or_drawdown_lte_2p5` | 27 | 0 | 0.00 | settled_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| `post_refinement_birth_reduce_suppress_p_hold_ge_075_fair_drawdown_lte_0` | 27 | 0 | 0.00 | settled_lt_30, delta_not_positive, full_loss_cushion_lt_3 |

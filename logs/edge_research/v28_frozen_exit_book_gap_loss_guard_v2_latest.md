# v28 Frozen Exit Book-Gap Loss Guard V2

Research-only frozen watch. No live bot changes or orders.

- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Candidate: `book_gap_loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0`
- Live ready: `False`
- Blockers: `suppressed_decisions_lt_30`

## Post-Freeze Summary

| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 58 | 41/17 | 426c ($4.26) | 578c ($5.78) | 152c ($1.52) | 5 | 152c ($1.52) | 0c ($0.00) |

## Discovery Sample

This is diagnostic only; the forward clock starts at the freeze above.

| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 173 | 109/64 | 823c ($8.23) | 1574c ($15.74) | 751c ($7.51) | 18 | 751c ($7.51) | 0c ($0.00) |

## Comparable Book-Gap Freeze Window

This uses the earlier book-gap freeze timestamp for diagnostic comparison only.

| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 120 | 78/42 | 727c ($7.27) | 1266c ($12.66) | 539c ($5.39) | 13 | 539c ($5.39) | 0c ($0.00) |

## Rule

Suppress value-over-hold exits when p_hold - exit_bid >= 0.00, or when p_hold >= 0.85 and fair_drawdown_cents >= -5.0. Suppress probability_reduce exits only when p_hold >= 0.79 and p_hold - exit_bid >= 0.00. Keep collapse exits unchanged.

## Interpretation

- Frozen v2 loss guard has 58 settled rows after its own freeze.
- Post-freeze delta versus current v28 exits is 152.0c.
- On the full diagnostic exit sample, v2 scored 1574.0c with 109/64 W/L, 751.0c winner recovery, and 0c suppressed-loss cost.
- On the comparable book-gap freeze window, v2 scored 1266.0c with 539.0c winner recovery and 0c suppressed-loss cost.

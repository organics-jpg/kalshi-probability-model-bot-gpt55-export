# v28 Frozen Exit Book-Gap Loss Guard

Research-only frozen watch. No live bot changes or orders.

- Freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- Candidate: `book_gap_loss_guard_value_p85_reduce_p79_gap0`
- Live ready: `False`
- Blockers: `suppressed_decisions_lt_30`

## Post-Freeze Summary

| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 59 | 41/18 | 340c ($3.40) | 582c ($5.82) | 242c ($2.42) | 17 | 242c ($2.42) | 0c ($0.00) |

## Discovery Sample

This is diagnostic only; the forward clock starts at the freeze above.

| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 173 | 108/65 | 823c ($8.23) | 1632c ($16.32) | 809c ($8.09) | 56 | 995c ($9.95) | -186c ($-1.86) |

## Comparable Book-Gap Freeze Window

This uses the earlier book-gap freeze timestamp for apples-to-apples diagnostic comparison.

| settled | W/L | current | candidate | delta | suppressed | winner recovery | loss cost |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 120 | 78/42 | 727c ($7.27) | 1442c ($14.42) | 715c ($7.15) | 38 | 715c ($7.15) | 0c ($0.00) |

## Rule

Suppress value-over-hold soft exits when p_hold >= 0.85 or p_hold - exit_bid >= 0.00. Suppress probability_reduce exits only when p_hold >= 0.79 and p_hold - exit_bid >= 0.00. Keep collapse exits unchanged.

## Interpretation

- Frozen loss-guarded book-gap candidate has 59 settled rows after its own freeze.
- Post-freeze delta versus current v28 exits is 242.0c.
- Discovery sample before this freeze scored 1632.0c with 108/65 W/L, 995.0c winner recovery, and -186.0c suppressed-loss cost.
- On the comparable book-gap freeze window, the same rule scored 1442.0c with 715.0c winner recovery and 0c suppressed-loss cost.

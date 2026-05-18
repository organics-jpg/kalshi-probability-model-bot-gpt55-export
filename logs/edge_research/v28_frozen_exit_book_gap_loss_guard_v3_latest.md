# v28 Frozen Exit Book-Gap Loss Guard V3

Research-only. No live bot changes or orders.

- Candidate: `book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0`
- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Live ready: `False`
- Blockers: `['suppressed_decisions_lt_30']`

## Rule

- Suppress value-over-hold exits when p_hold - exit_bid >= 0.00; or when p_hold >= 0.85 and fair_drawdown_cents >= -5.0; or when p_hold >= 0.95 even if book gap is slightly negative. Suppress probability_reduce exits only when p_hold >= 0.79 and p_hold - exit_bid >= 0.00. Keep collapse exits unchanged.
- Physics: A rich negative-gap exit should usually be accepted, unless the held-side probability is extreme enough that the exit is likely clipping a near-certain winner. This keeps the v2 loss guard while testing whether v1-only high-p recoveries are durable.

## Score

| window | settled | W/L | current | candidate | delta | suppressed | suppressed W/L | loss cost | cushion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| strict_post_v3_freeze | 46 | 33/13 | 478c ($4.78) | 644c ($6.44) | 166c ($1.66) | 9 | 9/0 | 0c ($0.00) | 6 |
| all_exit_diagnostic | 173 | 109/64 | 823c ($8.23) | 1634c ($16.34) | 811c ($8.11) | 39 | 39/0 | 0c ($0.00) | 16 |
| book_gap_freeze_comparable | 120 | 78/42 | 727c ($7.27) | 1316c ($13.16) | 589c ($5.89) | 28 | 28/0 | 0c ($0.00) | 13 |

## Strict Rows

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | side won |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982461 | -0.007538999999999962 | -10.246054 | 99 | 2c ($0.02) | True |
| KXBTC15M-26MAY062215-15 | no/no | mushroom_v28_exit_value_over_hold | 0.860673 | -0.029326999999999992 | -2.067333 | 89 | 22c ($0.22) | True |
| KXBTC15M-26MAY070815-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.890464 | -0.019535999999999998 | -1.046434 | 91 | 18c ($0.18) | True |
| KXBTC15M-26MAY070930-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.969995 | -0.01000499999999993 | -13.999536 | 97 | 6c ($0.06) | True |
| KXBTC15M-26MAY071115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.888844 | -0.021156000000000064 | -4.884431 | 91 | 18c ($0.18) | True |
| KXBTC15M-26MAY071145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982146 | -0.007854000000000028 | -17.214598 | 99 | 2c ($0.02) | True |
| KXBTC15M-26MAY071200-00 | no/no | mushroom_v28_exit_value_over_hold | 0.961165 | -0.018834999999999935 | -19.116535 | 98 | 4c ($0.04) | True |
| KXBTC15M-26MAY071215-15 | no/no | mushroom_v28_probability_reduce | 0.797661 | 0.037660999999999945 | 4.233856 | 76 | 48c ($0.48) | True |
| KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_probability_reduce | 0.798341 | 0.02834099999999995 | -0.834147 | 77 | 46c ($0.46) | True |

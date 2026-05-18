# v28 Exit Reduce Observable Loss-Control Opportunity

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:44:55.406806+00:00`
- Freeze UTC: `2026-05-07T00:08:36.297681+00:00`

## Interpretation

- This report only explains opportunity availability for the frozen observable loss-control watch.
- reduce_suppress_p75_entry_stc_lte_596: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 6, delta if suppressed -110.0c, fail reasons {'entry_seconds_to_close_above_gate': 3, 'not_probability_reduce': 44, 'p_hold_below_gate': 1}.
- reduce_suppress_p75_duration_lte_52: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 5, delta if suppressed -142.0c, fail reasons {'not_probability_reduce': 44, 'p_hold_below_gate': 1, 'trade_duration_sec_above_gate': 4}.
- reduce_suppress_p75_entry_book_age_gte_672: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 1, delta if suppressed -146.0c, fail reasons {'entry_book_age_ms_below_gate': 8, 'not_probability_reduce': 44, 'p_hold_below_gate': 1}.
- reduce_suppress_p75_exit_sigma_gte_110: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 3, delta if suppressed -242.0c, fail reasons {'exit_sigma_t_dollars_below_gate': 6, 'not_probability_reduce': 44, 'p_hold_below_gate': 1}.
- reduce_suppress_p75_exit_cents_lte_72: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 2, delta if suppressed -58.0c, fail reasons {'exit_cents_above_gate': 7, 'not_probability_reduce': 44, 'p_hold_below_gate': 1}.
- reduce_suppress_p75_entry_volshock_gte_0468: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 2, delta if suppressed -304.0c, fail reasons {'entry_volshock_below_gate': 7, 'not_probability_reduce': 44, 'p_hold_below_gate': 1}.
- reduce_suppress_p75_depth_lte384_or_duration_lte52: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 9, delta if suppressed -126.0c, fail reasons {'not_probability_reduce': 44, 'p_hold_below_gate': 1}.
- reduce_suppress_p75_depth_lte384_and_duration_lte75: post-birth rows 54, probability-reduce rows 10, p_hold candidates 9, would-suppress rows 5, delta if suppressed -142.0c, fail reasons {'entry_depth_above_gate': 1, 'not_probability_reduce': 44, 'p_hold_below_gate': 1, 'trade_duration_sec_above_gate': 3}.

## Rules

| candidate | rows | reduce rows | p-hold candidates | would suppress | delta if suppressed | fail reasons |
|---|---:|---:|---:|---:|---:|---|
| `reduce_suppress_p75_entry_stc_lte_596` | 54 | 10 | 9 | 6 | -110.000000 | {'entry_seconds_to_close_above_gate': 3, 'not_probability_reduce': 44, 'p_hold_below_gate': 1} |
| `reduce_suppress_p75_duration_lte_52` | 54 | 10 | 9 | 5 | -142.000000 | {'not_probability_reduce': 44, 'p_hold_below_gate': 1, 'trade_duration_sec_above_gate': 4} |
| `reduce_suppress_p75_entry_book_age_gte_672` | 54 | 10 | 9 | 1 | -146.000000 | {'entry_book_age_ms_below_gate': 8, 'not_probability_reduce': 44, 'p_hold_below_gate': 1} |
| `reduce_suppress_p75_exit_sigma_gte_110` | 54 | 10 | 9 | 3 | -242.000000 | {'exit_sigma_t_dollars_below_gate': 6, 'not_probability_reduce': 44, 'p_hold_below_gate': 1} |
| `reduce_suppress_p75_exit_cents_lte_72` | 54 | 10 | 9 | 2 | -58.000000 | {'exit_cents_above_gate': 7, 'not_probability_reduce': 44, 'p_hold_below_gate': 1} |
| `reduce_suppress_p75_entry_volshock_gte_0468` | 54 | 10 | 9 | 2 | -304.000000 | {'entry_volshock_below_gate': 7, 'not_probability_reduce': 44, 'p_hold_below_gate': 1} |
| `reduce_suppress_p75_depth_lte384_or_duration_lte52` | 54 | 10 | 9 | 9 | -126.000000 | {'not_probability_reduce': 44, 'p_hold_below_gate': 1} |
| `reduce_suppress_p75_depth_lte384_and_duration_lte75` | 54 | 10 | 9 | 5 | -142.000000 | {'entry_depth_above_gate': 1, 'not_probability_reduce': 44, 'p_hold_below_gate': 1, 'trade_duration_sec_above_gate': 3} |

## First-Rule Near Misses

| market | side | result | reason | entry | exit | p_hold | depth | stc | dur | book age | sigma | volshock | delta if suppressed | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | no | yes | mushroom_v28_probability_reduce | 76 | 60 | 0.768407 | 24.000000 | 628.084000 | 245.683692 | 297.000000 | 76.542004 | 0.060341 | -120.000000 | entry_seconds_to_close_above_gate |
| KXBTC15M-26MAY071000-00 | no | no | mushroom_v28_probability_reduce | 71 | 79 | 0.781361 | 21.000000 | 777.523000 | 618.463568 | 438.000000 | 69.298788 | 0.019548 | 42.000000 | entry_seconds_to_close_above_gate |
| KXBTC15M-26MAY071045-45 | no | no | mushroom_v28_probability_reduce | 74 | 69 | 0.760529 | 225.990000 | 822.403000 | 35.479669 | 437.000000 | 137.454980 | 0.288890 | 62.000000 | entry_seconds_to_close_above_gate |
| KXBTC15M-26MAY071230-30 | yes | yes | mushroom_v28_probability_reduce | 77 | 72 | 0.749378 | 20.000000 | 413.948000 | 31.849329 | 125.000000 | 101.284840 | 0.632754 | 56.000000 | p_hold_below_gate |

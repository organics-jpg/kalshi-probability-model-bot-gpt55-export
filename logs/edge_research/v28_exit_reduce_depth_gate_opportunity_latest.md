# v28 Exit Reduce Depth-Gate Opportunity Denominator

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:14:22.347603+00:00`
- Depth-gate freeze UTC: `2026-05-06T20:19:43.176664+00:00`

## Interpretation

- This report only explains opportunity availability for the frozen depth gate; it does not change exit behavior.
- reduce_suppress_p_hold_ge_075_entry_depth_lte_384: post-birth rows 60, probability-reduce rows 10, p_hold candidates 9, depth candidates 8, would-suppress rows 8, fail reasons {'entry_depth_above_gate': 1, 'not_probability_reduce': 50, 'p_hold_below_floor': 1}.
- reduce_suppress_p_hold_ge_075_entry_depth_lte_295: post-birth rows 60, probability-reduce rows 10, p_hold candidates 9, depth candidates 8, would-suppress rows 8, fail reasons {'entry_depth_above_gate': 1, 'not_probability_reduce': 50, 'p_hold_below_floor': 1}.
- reduce_suppress_p_hold_ge_079_entry_depth_lte_384: post-birth rows 60, probability-reduce rows 10, p_hold candidates 2, depth candidates 2, would-suppress rows 2, fail reasons {'entry_depth_above_gate': 1, 'not_probability_reduce': 50, 'p_hold_below_floor': 8}.
- reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5: post-birth rows 60, probability-reduce rows 10, p_hold candidates 9, depth candidates 8, would-suppress rows 3, fail reasons {'entry_depth_above_gate': 1, 'fair_drawdown_above_gate': 6, 'not_probability_reduce': 50, 'p_hold_below_floor': 1}.

## Rules

| candidate | rows | reduce rows | p-hold candidates | depth candidates | would suppress | fail reasons |
|---|---:|---:|---:|---:|---:|---|
| reduce_suppress_p_hold_ge_075_entry_depth_lte_384 | 60 | 10 | 9 | 8 | 8 | {'entry_depth_above_gate': 1, 'not_probability_reduce': 50, 'p_hold_below_floor': 1} |
| reduce_suppress_p_hold_ge_075_entry_depth_lte_295 | 60 | 10 | 9 | 8 | 8 | {'entry_depth_above_gate': 1, 'not_probability_reduce': 50, 'p_hold_below_floor': 1} |
| reduce_suppress_p_hold_ge_079_entry_depth_lte_384 | 60 | 10 | 2 | 2 | 2 | {'entry_depth_above_gate': 1, 'not_probability_reduce': 50, 'p_hold_below_floor': 8} |
| reduce_suppress_p_hold_ge_075_entry_depth_lte_384_drawdown_lte_2p5 | 60 | 10 | 9 | 8 | 3 | {'entry_depth_above_gate': 1, 'fair_drawdown_above_gate': 6, 'not_probability_reduce': 50, 'p_hold_below_floor': 1} |

## First-Rule Near Misses

| market | side | result | reason | entry | exit | p_hold | depth | current c | hold c | delta if suppressed | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071215-15 | no | no | mushroom_v28_probability_reduce | 80 | 76 | 0.765822 | 1329.710000 | -8.000000 | 40.000000 | 48.000000 | entry_depth_above_gate |
| KXBTC15M-26MAY071230-30 | yes | yes | mushroom_v28_probability_reduce | 77 | 72 | 0.749378 | 20.000000 | -10.000000 | 46.000000 | 56.000000 | p_hold_below_floor |

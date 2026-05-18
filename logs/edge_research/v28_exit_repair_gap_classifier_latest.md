# v28 Exit Repair Gap Classifier

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T16:44:22.404823+00:00`
- Loss rows: `73`
- Unresolved rows: `56` / `76.712329%`
- No exit-repair observation: `19`
- No-observation pre/post first exit-repair freeze: `19/0`
- First exit-repair freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Matched but unchanged: `37`
- Repair flips loss: `15`
- Repair would worsen: `2`
- Observable post-birth probability-reduce/would-suppress: `8/7`
- Observable post-birth worst suppress delta: `-304c`

## Interpretation

- Research-only diagnostic; this does not create or promote an exit rule.
- 56 of 73 losing control rows remain unresolved by the current frozen exit repair family.
- 19 losses have no matching frozen exit observation; 19 of them predate the first frozen exit-repair window, so they are historical context rather than a current denominator miss.
- 37 losses are matched but unchanged; these are mostly true collapse/value-exit or low-p_hold states where broad suppressions risk holding losers.
- The observable loss-control watch has only 8 post-birth probability-reduce row(s), 7 would-suppress row(s), and worst delta -304.0c, so it remains watch-only.

## Escape Classes

| class | rows | actual loss c | best repair delta c | known hold | hold helpful | hold harmful | hold unknown |
|---|---:|---:|---:|---:|---:|---:|---:|
| loss_escapes_current_exit_repairs | 37 | -1122c | 0c | 35 | 25 | 8 | 2 |
| no_exit_repair_observation | 19 | -464c | 0c | 19 | 9 | 10 | 0 |
| repair_flips_loss | 15 | -189c | 807c | 15 | 15 | 0 | 0 |
| repair_would_worsen | 2 | -18c | -306c | 2 | 0 | 2 | 0 |

## Unresolved Failure Classes

| failure class | rows | actual loss c | known hold | hold helpful | hold harmful | hold unknown |
|---|---:|---:|---:|---:|---:|---:|
| exit_policy_cost | 34 | -772c | 34 | 34 | 0 | 0 |
| exited_unsettled | 2 | -48c | 0 | 0 | 0 | 2 |
| fv_or_entry_timing_error | 20 | -766c | 20 | 0 | 18 | 0 |

## Unresolved Tag Combos

| tags | rows | actual loss c | hold helpful | hold harmful | hold unknown |
|---|---:|---:|---:|---:|---:|
| exit_policy_cost+near_boundary+recross_hazard_high | 7 | -140c | 7 | 0 | 0 |
| exit_policy_cost+near_boundary | 7 | -170c | 7 | 0 | 0 |
| fv_or_entry_timing_error+near_boundary+recross_hazard_high+thin_raw_edge | 5 | -122c | 0 | 5 | 0 |
| fv_or_entry_timing_error+near_boundary | 5 | -308c | 0 | 4 | 0 |
| exit_policy_cost+near_boundary+recross_hazard_high+thin_raw_edge | 5 | -78c | 5 | 0 | 0 |
| fv_or_entry_timing_error+near_boundary+recross_hazard_high+thin_touch_depth | 3 | -72c | 0 | 3 | 0 |
| fv_or_entry_timing_error | 3 | -46c | 0 | 2 | 0 |
| exit_policy_cost+rich_entry | 3 | -62c | 3 | 0 | 0 |
| exit_policy_cost+near_boundary+thin_raw_edge+rich_entry | 2 | -50c | 2 | 0 | 0 |
| exit_policy_cost+crowded_depth | 2 | -66c | 2 | 0 | 0 |

## Unresolved Exit Reasons

| reason | rows | actual loss c |
|---|---:|---:|
| exit_trigger | 54 | -1434c |
| unknown | 2 | -152c |

## Largest No-Observation Losses

| market | side | loss c | exit | hold c | tags |
|---|---|---:|---|---:|---|
| KXBTC15M-26MAY051830-30 | no | -92c | exit_trigger@34 | -160c | large_50_99c, fv_or_entry_timing_error, rich_entry, near_boundary |
| KXBTC15M-26MAY051715-15 | yes | -48c | exit_trigger@45 | -138c | medium_25_49c, fv_or_entry_timing_error, near_boundary |
| KXBTC15M-26MAY052315-15 | yes | -38c | exit_trigger@62 | 38c | medium_25_49c, exit_policy_cost, exit_policy_clip_vs_hold, rich_entry |
| KXBTC15M-26MAY052100-00 | no | -30c | exit_trigger@64 | -158c | medium_25_49c, fv_or_entry_timing_error, recross_hazard_high, thin_raw_edge, near_boundary |
| KXBTC15M-26MAY051715-15 | yes | -28c | exit_trigger@68 | -164c | medium_25_49c, fv_or_entry_timing_error, recross_hazard_high, thin_raw_edge, rich_entry, near_boundary |

## Largest Matched-Unchanged Losses

| market | side | loss c | best policy | p_hold | exit | hold c | tags |
|---|---|---:|---|---:|---|---:|---|
| KXBTC15M-26MAY062015-15 | yes | -134c | exit_reduce | None | @None | -134c | full_loss_ge_100c, fv_or_entry_timing_error, near_boundary |
| KXBTC15M-26MAY061800-00 | no | -86c | exit_reduce | 0.552607 | exit_trigger@24 | 66c | large_50_99c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold |
| KXBTC15M-26MAY060900-00 | yes | -76c | exit_reduce | 0.397320 | exit_trigger@40 | -156c | large_50_99c, fv_or_entry_timing_error, recross_hazard_high, near_boundary |
| KXBTC15M-26MAY060745-45 | yes | -70c | exit_reduce | 0.563569 | exit_trigger@43 | -156c | large_50_99c, fv_or_entry_timing_error, near_boundary |
| KXBTC15M-26MAY062015-15 | no | -60c | exit_reduce | 0.268932 | exit_trigger@12 | 116c | large_50_99c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary |

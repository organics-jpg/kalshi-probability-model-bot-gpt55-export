# v28 Feature-Gate Exit Watch Alignment Audit

Research-only alignment report. No live bot changes, no orders, no new candidate rule.

- Generated UTC: `2026-05-07T08:38:26.788208+00:00`
- Mismatch markets: `7`
- Settlement theory / live selected-side / swing: `161c` / `-456c` / `617c`
- Value-watch catches: `2`
- High-bid watch catches: `7`
- Delayed-recheck watch catches: `6`
- Broad loss-control risk rows among catches: `5`
- Reason groups: `{'value_over_hold': 2, 'probability_reduce': 4, 'probability_collapse': 1}`

## Strict Watch Status

| watch | freeze UTC | strict rows | suppressed | net | blockers |
|---|---|---:|---:|---:|---|
| exit_bid_watch | `2026-05-07T07:32:00.852069+00:00` | 0 | 0 | 0c | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| delayed_recheck_watch | `2026-05-07T07:54:52.452489+00:00` | 0 | 0 | 0c | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, full_loss_cushion_lt_3 |
| value_exit_watch | `2026-05-07T07:36:17.925386+00:00` | 0 | 0 | 0c | settled_lt_30, net_not_positive, full_loss_cushion_lt_3, selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |

## Mismatch Alignment

| market | reason group | theory | live selected | swing | value | high bid | delayed | bid min | p_hold avg | recheck bid | drop | risk |
|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | value_over_hold | 15c | -164c | 179c | yes | yes | yes | 63.0 | 0.7844025 | 73.0 | -3.0 |  |
| KXBTC15M-26MAY062315-15 | probability_reduce | 15c | -104c | 119c |  | yes | yes | 67.0 | 0.7811086 | 76.0 | 0.0 | reduce/collapse |
| KXBTC15M-26MAY062215-15 | probability_collapse | 33c | -62c | 95c |  | yes | yes | 65.0 | 0.713473 | 64.0 | 5.0 | reduce/collapse |
| KXBTC15M-26MAY062015-15 | probability_reduce | 56c | -60c | 116c |  | yes |  | 60.0 | 0.68996675 | 53.0 | -1.0 | reduce/collapse |
| KXBTC15M-26MAY062045-45 | probability_reduce | 18c | -38c | 56c |  | yes | yes | 64.0 | 0.767832 | 82.0 | 1.0 | reduce/collapse |
| KXBTC15M-26MAY061400-00 | value_over_hold | 10c | -20c | 30c | yes | yes | yes | 84.0 | 0.7422999999999998 | 92.0 | 3.0 |  |
| KXBTC15M-26MAY061815-15 | probability_reduce | 14c | -8c | 22c |  | yes | yes | 66.0 | 0.750076 | 86.0 | -4.0 | reduce/collapse |

## Interpretation

- All joined rows are diagnostic/prefreeze for these exit watches; strict post-freeze watch rows remain the promotion denominator.
- Value-only catches fewer observed selected-side winner clips but is narrower and closer to preserving reduce/collapse loss-control behavior.
- High-bid and delayed-recheck watch shapes cover more observed clips, including reduce/collapse exits, so they need strict forward proof that they do not suppress true loss-control exits.

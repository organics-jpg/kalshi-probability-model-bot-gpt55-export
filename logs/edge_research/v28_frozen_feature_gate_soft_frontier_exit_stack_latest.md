# v28 Frozen Feature-Gate Soft-Frontier + Guarded Exit Stack

Research-only frozen forward watch. No live bot changes.

- Generated UTC: `2026-05-11T03:42:23.214631+00:00`
- Freeze timestamp UTC: `2026-05-07T01:24:41.529764+00:00`
- Candidate family: `feature_gate_soft_frontier_exit_stack`
- Exit rows available after freeze: `{'book_gap': 42, 'loss_guard_v1': 42, 'loss_guard_v2': 42, 'loss_guard_v3': 42}`
- Any live-ready variant: `False`

## Interpretation

- post_soft_stack_entry book_gap best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 386.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_soft_stack_bridge book_gap best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 386.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_soft_stack_entry loss_guard_v1 best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 500.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_soft_stack_bridge loss_guard_v1 best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 500.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_soft_stack_entry loss_guard_v2 best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 464.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_soft_stack_bridge loss_guard_v2 best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 464.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_soft_stack_entry loss_guard_v3 best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 476.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_soft_stack_bridge loss_guard_v3 best soft_raw03_recross50_abs65_ask35 has entry settled 39, coverage 76.47058823529412%, entry net 24.0c, joined exit rows 19, joined exit net 476.0c, blockers ['entry_reconstructed_share_gt_35pct', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].

## post_soft_stack_entry / book_gap

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 386.000000 | -42.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 386.000000 | -42.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 386.000000 | -42.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_soft_stack_bridge / book_gap

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 386.000000 | -42.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 386.000000 | -42.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 386.000000 | -42.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_soft_stack_entry / loss_guard_v1

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 500.000000 | 72.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 500.000000 | 72.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 500.000000 | 72.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_soft_stack_bridge / loss_guard_v1

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 500.000000 | 72.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 500.000000 | 72.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 500.000000 | 72.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_soft_stack_entry / loss_guard_v2

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 464.000000 | 36.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 464.000000 | 36.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 464.000000 | 36.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_soft_stack_bridge / loss_guard_v2

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 464.000000 | 36.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 464.000000 | 36.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 464.000000 | 36.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_soft_stack_entry / loss_guard_v3

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 476.000000 | 48.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 476.000000 | 48.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 476.000000 | 48.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_soft_stack_bridge / loss_guard_v3

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `soft_raw03_recross50_abs65_ask35` | 39 | 32/7 | 76.470588 | 24.000000 | 0.358974 | 19 | 476.000000 | 48.000000 | 12 | 8 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `soft_raw03_recross50_abs50_ask35` | 42 | 33/9 | 82.352941 | -36.000000 | 0.428571 | 19 | 476.000000 | 48.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `soft_raw03_recross50_abs50_ask50` | 42 | 33/9 | 82.352941 | -57.000000 | 0.428571 | 19 | 476.000000 | 48.000000 | 15 | 8 | entry_net_not_positive, entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

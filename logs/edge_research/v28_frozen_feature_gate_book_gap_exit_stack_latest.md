# v28 Frozen Feature-Gate + Guarded Exit Stack

Research-only frozen forward watch. No live bot changes.

- Generated UTC: `2026-05-11T03:46:38.358325+00:00`
- Freeze timestamp UTC: `2026-05-06T21:20:30.347830+00:00`
- Candidate family: `feature_gate_book_gap_exit_stack`
- Exit rows available after freeze: `{'book_gap': 59, 'loss_guard_v1': 59, 'loss_guard_v2': 58, 'loss_guard_v3': 46}`
- Any live-ready variant: `False`

## Interpretation

- post_stack_entry book_gap best raw05_recross60_abs085_ask65 has entry settled 41, coverage 61.19402985074627%, entry net 271.0c, joined exit rows 27, joined exit net 320.0c, blockers ['entry_coverage_too_low', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_stack_bridge book_gap best raw05_recross60_abs085_ask65 has entry settled 41, coverage 61.19402985074627%, entry net 271.0c, joined exit rows 27, joined exit net 320.0c, blockers ['entry_coverage_too_low', 'entry_full_loss_cushion_lt_3', 'joined_exit_rows_lt_30'].
- post_stack_entry loss_guard_v1 best raw05_recross60_abs085 has entry settled 44, coverage 65.67164179104478%, entry net 309.0c, joined exit rows 24, joined exit net 416.0c, blockers ['entry_coverage_too_low', 'joined_exit_rows_lt_30'].
- post_stack_bridge loss_guard_v1 best raw05_recross60_abs085 has entry settled 44, coverage 65.67164179104478%, entry net 309.0c, joined exit rows 24, joined exit net 416.0c, blockers ['entry_coverage_too_low', 'joined_exit_rows_lt_30'].
- post_stack_entry loss_guard_v2 best raw05_recross60_abs085 has entry settled 44, coverage 65.67164179104478%, entry net 309.0c, joined exit rows 23, joined exit net 440.0c, blockers ['entry_coverage_too_low', 'joined_exit_rows_lt_30'].
- post_stack_bridge loss_guard_v2 best raw05_recross60_abs085 has entry settled 44, coverage 65.67164179104478%, entry net 309.0c, joined exit rows 23, joined exit net 440.0c, blockers ['entry_coverage_too_low', 'joined_exit_rows_lt_30'].
- post_stack_entry loss_guard_v3 best raw05_recross60_abs085 has entry settled 44, coverage 65.67164179104478%, entry net 309.0c, joined exit rows 17, joined exit net 388.0c, blockers ['entry_coverage_too_low', 'joined_exit_rows_lt_30'].
- post_stack_bridge loss_guard_v3 best raw05_recross60_abs085 has entry settled 44, coverage 65.67164179104478%, entry net 309.0c, joined exit rows 17, joined exit net 388.0c, blockers ['entry_coverage_too_low', 'joined_exit_rows_lt_30'].

## post_stack_entry / book_gap

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 27 | 320.000000 | -134.000000 | 2 | 12 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 17 | 212.000000 | -10.000000 | 4 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |
| 3 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 24 | 182.000000 | -154.000000 | 9 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |
| 4 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 24 | 182.000000 | -154.000000 | 19 | 10 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |

## post_stack_bridge / book_gap

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 27 | 320.000000 | -134.000000 | 2 | 12 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 2 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 17 | 212.000000 | -10.000000 | 4 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |
| 3 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 24 | 182.000000 | -154.000000 | 9 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |
| 4 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 24 | 182.000000 | -154.000000 | 19 | 10 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |

## post_stack_entry / loss_guard_v1

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 24 | 416.000000 | 80.000000 | 9 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 2 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 27 | 554.000000 | 100.000000 | 2 | 12 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 24 | 416.000000 | 80.000000 | 19 | 10 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 4 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 17 | 276.000000 | 54.000000 | 4 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |

## post_stack_bridge / loss_guard_v1

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 24 | 416.000000 | 80.000000 | 9 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 2 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 27 | 554.000000 | 100.000000 | 2 | 12 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 24 | 416.000000 | 80.000000 | 19 | 10 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 4 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 17 | 276.000000 | 54.000000 | 4 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |

## post_stack_entry / loss_guard_v2

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 23 | 440.000000 | 18.000000 | 10 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 2 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 16 | 308.000000 | 0.000000 | 5 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 3 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 26 | 576.000000 | 36.000000 | 3 | 12 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 4 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 23 | 440.000000 | 18.000000 | 20 | 10 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_stack_bridge / loss_guard_v2

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 23 | 440.000000 | 18.000000 | 10 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 2 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 16 | 308.000000 | 0.000000 | 5 | 11 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 3 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 26 | 576.000000 | 36.000000 | 3 | 12 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 4 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 23 | 440.000000 | 18.000000 | 20 | 10 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |

## post_stack_entry / loss_guard_v3

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 17 | 388.000000 | 30.000000 | 17 | 10 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 2 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 20 | 444.000000 | 48.000000 | 11 | 10 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 17 | 388.000000 | 30.000000 | 27 | 9 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 4 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 12 | 294.000000 | 6.000000 | 10 | 10 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |

## post_stack_bridge / loss_guard_v3

| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw05_recross60_abs085` | 44 | 33/11 | 65.671642 | 309.000000 | 0.204545 | 17 | 388.000000 | 30.000000 | 17 | 10 | entry_coverage_too_low, joined_exit_rows_lt_30 |
| 2 | `raw05_recross60_abs085_ask65` | 41 | 36/5 | 61.194030 | 271.000000 | 0.048780 | 20 | 444.000000 | 48.000000 | 11 | 10 | entry_coverage_too_low, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 3 | `raw03_recross70_abs075` | 53 | 36/17 | 79.104478 | 171.000000 | 0.358491 | 17 | 388.000000 | 30.000000 | 27 | 9 | entry_reconstructed_share_gt_35pct, entry_full_loss_cushion_lt_3, joined_exit_rows_lt_30 |
| 4 | `raw07_recross60_abs085` | 32 | 26/6 | 47.761194 | 338.000000 | 0.125000 | 12 | 294.000000 | 6.000000 | 10 | 10 | entry_coverage_too_low, joined_exit_rows_lt_30, joined_exit_full_loss_cushion_lt_3 |

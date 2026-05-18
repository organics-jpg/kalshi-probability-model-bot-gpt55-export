# v28 Feature-Gate Guarded Coverage Repair Scan

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:37:23.801272+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Live baseline: `821c`

## Interpretation

- Research-only guarded coverage repair scan; no live bot changes or orders.
- The scan starts from the raw03 feature-gate lane plus the high-ask-over-cheap side guard.
- After the current denominator update, one-row observable repairs reach only 74.58% coverage; at least 3 added markets are required for the 75% gate.
- The two-row relaxation frontier reaches 76.27% nominal coverage, but remains a post-hoc diagnostic unless it gets its own frozen birth.
- The three-row relaxation frontier reaches 77.97% nominal coverage; use it as a source-quality stress test, not as a promotion candidate.
- The best one-row additions remain source-fragile diagnostics; they are selected by relaxed predicates after seeing the frozen sample and do not clear source/live gates.

## post_feature_freeze_entry

- Future denominator: `59`
- Base guarded raw03: `42` entries, `71.19%` coverage, `314c`, W/L `30/12`, recon `0.357`, cushion `3`, blockers `coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline`.

### Best One-Row Repairs

| rank | repair | added market | source | net | miss reasons | coverage | total net | delta live | recon | cushion | blockers |
|---:|---|---|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY061715-15` `no` | `rejected_actionable` | 93c | raw_edge_below_min | 72.88% | 407c | -414c | 0.372 | 4 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `absd65_keep_raw03_recross70` | `KXBTC15M-26MAY061945-45` `no` | `rejected_actionable` | 51c | abs_d_below_min | 72.88% | 365c | -456c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 3 | `absd50_keep_raw03_recross70` | `KXBTC15M-26MAY061945-45` `no` | `rejected_actionable` | 51c | abs_d_below_min | 72.88% | 365c | -456c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `ask35_absd65_raw03_recross70` | `KXBTC15M-26MAY061945-45` `no` | `rejected_actionable` | 51c | abs_d_below_min | 72.88% | 365c | -456c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `absd50_keep_raw03_recross70` | `KXBTC15M-26MAY062000-00` `yes` | `rejected_actionable` | 48c | abs_d_below_min | 72.88% | 362c | -459c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `absd65_keep_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 72.88% | 342c | -479c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 7 | `absd50_keep_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 72.88% | 342c | -479c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 8 | `ask35_absd65_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 72.88% | 342c | -479c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 9 | `ask50_absd65_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 72.88% | 342c | -479c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 10 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY061500-00` `no` | `rejected_actionable` | 15c | raw_edge_below_min | 72.88% | 329c | -492c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 11 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 6c | raw_edge_below_min | 72.88% | 320c | -501c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 12 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY070630-30` `no` | `rejected_actionable` | 0c | raw_edge_below_min | 72.88% | 314c | -507c | 0.372 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

### Best Two-Row Repairs

| rank | added markets | sources | added net | coverage | total net | delta live | recon | cushion | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable | 37c | 74.58% | 351c | -470c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes` | rejected_actionable, rejected_actionable | 36c | 74.58% | 350c | -471c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 3 | `KXBTC15M-26MAY061715-15` `no`; `KXBTC15M-26MAY061945-45` `no` | rejected_actionable, rejected_actionable | 30c | 74.58% | 344c | -477c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `yes` | rejected_actionable, rejected_actionable | 30c | 74.58% | 344c | -477c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070630-30` `no` | rejected_actionable, rejected_actionable | 30c | 74.58% | 344c | -477c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061715-15` `yes` | rejected_actionable, rejected_actionable | 28c | 74.58% | 342c | -479c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 7 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `no` | rejected_actionable, rejected_actionable | 28c | 74.58% | 342c | -479c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 8 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061745-45` `no` | rejected_actionable, rejected_actionable | 28c | 74.58% | 342c | -479c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 9 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061515-15` `yes` | rejected_actionable, rejected_actionable | 28c | 74.58% | 342c | -479c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 10 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070630-30` `yes` | rejected_actionable, rejected_actionable | 28c | 74.58% | 342c | -479c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 11 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070730-30` `yes` | rejected_actionable, rejected_actionable | 27c | 74.58% | 341c | -480c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 12 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070100-00` `no` | rejected_actionable, rejected_actionable | 26c | 74.58% | 340c | -481c | 0.386 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

### Best Three-Row Repairs

| rank | added markets | sources | added net | coverage | total net | delta live | recon | cushion | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 43c | 76.27% | 357c | -464c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `KXBTC15M-26MAY061715-15` `no`; `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 37c | 76.27% | 351c | -470c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 3 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `yes`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 37c | 76.27% | 351c | -470c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY070630-30` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 37c | 76.27% | 351c | -470c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `KXBTC15M-26MAY061715-15` `no`; `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 36c | 76.27% | 350c | -471c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `yes`; `KXBTC15M-26MAY070600-00` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 36c | 76.27% | 350c | -471c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 7 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes`; `KXBTC15M-26MAY070630-30` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 36c | 76.27% | 350c | -471c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 8 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY061715-15` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 76.27% | 349c | -472c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 9 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY062000-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 76.27% | 349c | -472c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 10 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY061745-45` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 76.27% | 349c | -472c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 11 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY061515-15` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 76.27% | 349c | -472c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 12 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY070630-30` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 76.27% | 349c | -472c | 0.400 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

## post_feature_freeze_bridge

- Future denominator: `59`
- Base guarded raw03: `43` entries, `72.88%` coverage, `314c`, W/L `30/12`, recon `0.349`, cushion `3`, blockers `coverage_too_low, does_not_beat_refreshed_live_baseline`.

### Best One-Row Repairs

| rank | repair | added market | source | net | miss reasons | coverage | total net | delta live | recon | cushion | blockers |
|---:|---|---|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY061715-15` `no` | `rejected_actionable` | 93c | raw_edge_below_min | 74.58% | 407c | -414c | 0.364 | 4 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `absd65_keep_raw03_recross70` | `KXBTC15M-26MAY061945-45` `no` | `rejected_actionable` | 51c | abs_d_below_min | 74.58% | 365c | -456c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 3 | `absd50_keep_raw03_recross70` | `KXBTC15M-26MAY061945-45` `no` | `rejected_actionable` | 51c | abs_d_below_min | 74.58% | 365c | -456c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `ask35_absd65_raw03_recross70` | `KXBTC15M-26MAY061945-45` `no` | `rejected_actionable` | 51c | abs_d_below_min | 74.58% | 365c | -456c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `absd50_keep_raw03_recross70` | `KXBTC15M-26MAY062000-00` `yes` | `rejected_actionable` | 48c | abs_d_below_min | 74.58% | 362c | -459c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `absd65_keep_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 74.58% | 342c | -479c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 7 | `absd50_keep_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 74.58% | 342c | -479c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 8 | `ask35_absd65_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 74.58% | 342c | -479c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 9 | `ask50_absd65_raw03_recross70` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 28c | abs_d_below_min | 74.58% | 342c | -479c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 10 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY061500-00` `no` | `rejected_actionable` | 15c | raw_edge_below_min | 74.58% | 329c | -492c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 11 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY070600-00` `yes` | `rejected_actionable` | 6c | raw_edge_below_min | 74.58% | 320c | -501c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 12 | `raw00_keep_recross70_abs075` | `KXBTC15M-26MAY070630-30` `no` | `rejected_actionable` | 0c | raw_edge_below_min | 74.58% | 314c | -507c | 0.364 | 3 | coverage_too_low, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

### Best Two-Row Repairs

| rank | added markets | sources | added net | coverage | total net | delta live | recon | cushion | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable | 37c | 76.27% | 351c | -470c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes` | rejected_actionable, rejected_actionable | 36c | 76.27% | 350c | -471c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 3 | `KXBTC15M-26MAY061715-15` `no`; `KXBTC15M-26MAY061945-45` `no` | rejected_actionable, rejected_actionable | 30c | 76.27% | 344c | -477c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `yes` | rejected_actionable, rejected_actionable | 30c | 76.27% | 344c | -477c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070630-30` `no` | rejected_actionable, rejected_actionable | 30c | 76.27% | 344c | -477c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061715-15` `yes` | rejected_actionable, rejected_actionable | 28c | 76.27% | 342c | -479c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 7 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `no` | rejected_actionable, rejected_actionable | 28c | 76.27% | 342c | -479c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 8 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061745-45` `no` | rejected_actionable, rejected_actionable | 28c | 76.27% | 342c | -479c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 9 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061515-15` `yes` | rejected_actionable, rejected_actionable | 28c | 76.27% | 342c | -479c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 10 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070630-30` `yes` | rejected_actionable, rejected_actionable | 28c | 76.27% | 342c | -479c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 11 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070730-30` `yes` | rejected_actionable, rejected_actionable | 27c | 76.27% | 341c | -480c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 12 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070100-00` `no` | rejected_actionable, rejected_actionable | 26c | 76.27% | 340c | -481c | 0.378 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

### Best Three-Row Repairs

| rank | added markets | sources | added net | coverage | total net | delta live | recon | cushion | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 43c | 77.97% | 357c | -464c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 2 | `KXBTC15M-26MAY061715-15` `no`; `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 37c | 77.97% | 351c | -470c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 3 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `yes`; `KXBTC15M-26MAY061500-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 37c | 77.97% | 351c | -470c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY070630-30` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 37c | 77.97% | 351c | -470c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `KXBTC15M-26MAY061715-15` `no`; `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 36c | 77.97% | 350c | -471c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY062000-00` `yes`; `KXBTC15M-26MAY070600-00` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 36c | 77.97% | 350c | -471c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 7 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY070600-00` `yes`; `KXBTC15M-26MAY070630-30` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 36c | 77.97% | 350c | -471c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 8 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY061715-15` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 77.97% | 349c | -472c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 9 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY062000-00` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 77.97% | 349c | -472c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 10 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY061745-45` `no` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 77.97% | 349c | -472c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 11 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY061515-15` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 77.97% | 349c | -472c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 12 | `KXBTC15M-26MAY061945-45` `no`; `KXBTC15M-26MAY061500-00` `no`; `KXBTC15M-26MAY070630-30` `yes` | rejected_actionable, rejected_actionable, rejected_actionable | 35c | 77.97% | 349c | -472c | 0.391 | 3 | reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

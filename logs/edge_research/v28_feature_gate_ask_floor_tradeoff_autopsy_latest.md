# v28 Feature-Gate Ask-Floor Tradeoff Autopsy

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:31:58.037603+00:00`
- Candidate source UTC: `2026-05-07T11:17:29.409489+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Live baseline: `821c`

## Interpretation

- Research-only ask-floor tradeoff autopsy; no live bot changes or orders.
- Live baseline for deltas is 821c from the refreshed live-only score.
- The ask65 lane remains the cleanest source-quality core but is far below broad-entry coverage and sample/cushion gates.
- The raw05 lane adds coverage while staying near the 35% source gate, but it still misses 75% coverage and does not beat live.
- The raw03 lane is the broadest current post-freeze feature-gate lane, but the extra coverage comes with too much rejected/reconstructed share and weak cushion.

## post_feature_freeze_entry

- Future denominator: `57`

| variant | entries | settled | W/L | coverage | net | delta live | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `ask65_clean_core` | 29 | 27 | 24/3 | 50.88% | 157c | -664c | 0.069 | 1 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| `raw05_source_cleaner_coverage` | 36 | 35 | 23/12 | 63.16% | 299c | -522c | 0.361 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `raw03_broad_coverage` | 42 | 40 | 25/15 | 73.68% | 306c | -515c | 0.452 | 3 | coverage_too_low, reconstructed_share_gt_35pct |

### Added/Omitted Row Buckets

| bucket | rows | displaced | new markets | W/L/F | net | recon | avg ask | avg abs d | avg recross | top tags |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `raw05_added_vs_ask65` | 12 | 5 | 7 | 2/10/0 | 106c | 0.917 | 0.067 | 0.994 | 0.086 | below_ask65:12, cheap_touch_lt50:12, source_quality_error:11, realized_loss:10, thin_raw_edge_lt07:4, realized_win:2 |
| `raw03_added_vs_raw05` | 6 | 0 | 6 | 2/3/1 | -9c | 1.000 | 0.443 | 1.364 | 0.102 | source_quality_error:6, thin_raw_edge_lt07:5, below_ask65:4, cheap_touch_lt50:3, realized_loss:3, expensive_touch_gte85:2 |
| `raw03_added_vs_ask65` | 18 | 5 | 13 | 4/13/1 | 92c | 0.944 | 0.195 | 1.099 | 0.093 | source_quality_error:17, below_ask65:16, cheap_touch_lt50:15, realized_loss:13, thin_raw_edge_lt07:8, realized_win:4 |
| `ask65_rows_not_in_raw05` | 5 | 5 | 0 | 3/1/1 | -36c | 0.000 | 0.834 | 1.252 | 0.135 | expensive_touch_gte85:4, realized_win:3, thin_raw_edge_lt07:3, flat:1, large_raw_edge_false_positive:1, realized_loss:1 |

## post_feature_freeze_bridge

- Future denominator: `58`

| variant | entries | settled | W/L | coverage | net | delta live | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `ask65_clean_core` | 29 | 29 | 26/3 | 50.00% | 182c | -639c | 0.069 | 1 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| `raw05_source_cleaner_coverage` | 36 | 36 | 24/12 | 62.07% | 315c | -506c | 0.361 | 3 | coverage_too_low, reconstructed_share_gt_35pct |
| `raw03_broad_coverage` | 42 | 42 | 26/16 | 72.41% | 254c | -567c | 0.452 | 2 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Added/Omitted Row Buckets

| bucket | rows | displaced | new markets | W/L/F | net | recon | avg ask | avg abs d | avg recross | top tags |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `raw05_added_vs_ask65` | 12 | 5 | 7 | 2/10/0 | 106c | 0.917 | 0.067 | 0.994 | 0.086 | below_ask65:12, cheap_touch_lt50:12, source_quality_error:11, realized_loss:10, thin_raw_edge_lt07:4, realized_win:2 |
| `raw03_added_vs_raw05` | 6 | 0 | 6 | 2/4/0 | -77c | 1.000 | 0.443 | 1.364 | 0.102 | source_quality_error:6, thin_raw_edge_lt07:5, below_ask65:4, realized_loss:4, cheap_touch_lt50:3, expensive_touch_gte85:2 |
| `raw03_added_vs_ask65` | 18 | 5 | 13 | 4/14/0 | 24c | 0.944 | 0.195 | 1.099 | 0.093 | source_quality_error:17, below_ask65:16, cheap_touch_lt50:15, realized_loss:14, thin_raw_edge_lt07:8, realized_win:4 |
| `ask65_rows_not_in_raw05` | 5 | 5 | 0 | 4/1/0 | -27c | 0.000 | 0.834 | 1.252 | 0.135 | expensive_touch_gte85:4, realized_win:4, thin_raw_edge_lt07:3, large_raw_edge_false_positive:1, realized_loss:1 |

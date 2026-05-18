# v28 Dual-Lane Overlay Filter Frontier

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:11.028829+00:00`
- Same-window compare UTC: `2026-05-11T03:47:01.196227+00:00`
- Promotion use: `diagnostic_only_filter_design`
- Rows available / denominator: `16` / `18`
- Rules tested: `74`
- Viable diagnostic rules: `0`

## Read

- This is not promotion evidence; it is a filter-design audit over a tiny same-window sample.
- A useful deployable overlay needs an observable filter, then a separate own-freeze watch.
- If top filters require hindsight-like separation or tiny coverage, dual-lane is not yet live-ready as an overlay.

## Best Diagnostic Rule

- Label: `yes_recross_le0.3`
- Rows/coverage: `4` / `22.22%`
- Candidate/live/delta: `87c ($0.87)` / `-43c ($-0.43)` / `130c ($1.30)`
- Helpful/harmful/share: `3` / `1` / `75.00%`
- Blockers: `diagnostic_coverage_lt_25pct`
- Selected markets: `['KXBTC15M-26MAY071300-00', 'KXBTC15M-26MAY071230-30', 'KXBTC15M-26MAY071115-15', 'KXBTC15M-26MAY071315-15']`

## Top Rules

| rank | rule | rows | coverage | cand net | live net | delta | helpful | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `yes_recross_le0.3` | 4 | 22.22% | 87c ($0.87) | -43c ($-0.43) | 130c ($1.30) | 75.00% | diagnostic_coverage_lt_25pct |
| 2 | `raw0.05_recross_le0.3_abs0.85` | 6 | 33.33% | 170c ($1.70) | 50c ($0.50) | 120c ($1.20) | 66.67% | helpful_share_lt_70pct |
| 3 | `no_recross_le0.4` | 5 | 27.78% | 106c ($1.06) | 90c ($0.90) | 16c ($0.16) | 40.00% | helpful_share_lt_70pct |
| 4 | `raw0.08_recross_le0.3_abs0.85` | 3 | 16.67% | 87c ($0.87) | 34c ($0.34) | 53c ($0.53) | 66.67% | diagnostic_coverage_lt_25pct, helpful_share_lt_70pct |
| 5 | `raw0.08_recross_le0.4_abs0.85` | 3 | 16.67% | 87c ($0.87) | 34c ($0.34) | 53c ($0.53) | 66.67% | diagnostic_coverage_lt_25pct, helpful_share_lt_70pct |
| 6 | `no_recross_le0.3` | 4 | 22.22% | 93c ($0.93) | 48c ($0.48) | 45c ($0.45) | 50.00% | diagnostic_coverage_lt_25pct, helpful_share_lt_70pct |
| 7 | `raw0.05_recross_le0.3_abs0.9` | 4 | 22.22% | 105c ($1.05) | 80c ($0.80) | 25c ($0.25) | 50.00% | diagnostic_coverage_lt_25pct, helpful_share_lt_70pct |
| 8 | `recross_ge0.25_ask_le0.82` | 8 | 44.44% | 47c ($0.47) | 56c ($0.56) | -9c ($-0.09) | 50.00% | delta_not_positive, helpful_share_lt_70pct |
| 9 | `raw0.05_recross_le0.4_abs0.85` | 9 | 50.00% | 57c ($0.57) | 84c ($0.84) | -27c ($-0.27) | 55.56% | delta_not_positive, helpful_share_lt_70pct |
| 10 | `yes_side_only` | 7 | 38.89% | 7c ($0.07) | 55c ($0.55) | -48c ($-0.48) | 57.14% | delta_not_positive, helpful_share_lt_70pct |
| 11 | `yes_recross_le0.4` | 7 | 38.89% | 7c ($0.07) | 55c ($0.55) | -48c ($-0.48) | 57.14% | delta_not_positive, helpful_share_lt_70pct |
| 12 | `yes_recross_le0.5` | 7 | 38.89% | 7c ($0.07) | 55c ($0.55) | -48c ($-0.48) | 57.14% | delta_not_positive, helpful_share_lt_70pct |
| 13 | `yes_recross_le0.6` | 7 | 38.89% | 7c ($0.07) | 55c ($0.55) | -48c ($-0.48) | 57.14% | delta_not_positive, helpful_share_lt_70pct |
| 14 | `high_cost_low_edge_raw_le0.12_ask_ge0.75` | 5 | 27.78% | 83c ($0.83) | 136c ($1.36) | -53c ($-0.53) | 20.00% | delta_not_positive, helpful_share_lt_70pct |
| 15 | `high_cost_low_edge_raw_le0.15_ask_ge0.75` | 5 | 27.78% | 83c ($0.83) | 136c ($1.36) | -53c ($-0.53) | 20.00% | delta_not_positive, helpful_share_lt_70pct |
| 16 | `recross_ge0.25_ask_le0.78` | 7 | 38.89% | 7c ($0.07) | 84c ($0.84) | -77c ($-0.77) | 42.86% | delta_not_positive, helpful_share_lt_70pct |
| 17 | `approved_only` | 13 | 72.22% | 16c ($0.16) | 97c ($0.97) | -81c ($-0.81) | 53.85% | delta_not_positive, helpful_share_lt_70pct |
| 18 | `raw0.08_recross_le0.5_abs0.85` | 7 | 38.89% | 33c ($0.33) | 129c ($1.29) | -96c ($-0.96) | 42.86% | delta_not_positive, helpful_share_lt_70pct |
| 19 | `raw0.08_recross_le0.6_abs0.85` | 7 | 38.89% | 33c ($0.33) | 129c ($1.29) | -96c ($-0.96) | 42.86% | delta_not_positive, helpful_share_lt_70pct |
| 20 | `no_side_only` | 9 | 50.00% | 52c ($0.52) | 185c ($1.85) | -133c ($-1.33) | 33.33% | delta_not_positive, helpful_share_lt_70pct |

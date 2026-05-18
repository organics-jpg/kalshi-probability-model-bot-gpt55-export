# v28 Feature-Gate Core/Expansion Mix

Research-only mix/match probe. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:55:01.187412+00:00`
- Source generated UTC: `2026-05-07T18:14:31.766018+00:00`
- Lane: `post_feature_freeze_bridge`
- Core: `post_feature_freeze_bridge_raw05_recross60_abs085_ask65`
- Broad expansion parent: `post_feature_freeze_bridge_raw03_recross70_abs075`
- Any live-ready mix row: `False`
- Best policy: `approved_expansion_full_reconstructed_quarter`

## Mix Rows

| rank | policy | entries | settled | W/L | coverage | weighted net | row source | exposure source | cushion | rows needed | live ready | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `approved_expansion_full_reconstructed_quarter` | 64 | 64 | 42/22 | 78.0% | 386.5c ($3.87) | 39.1% | 16.6% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct |
| 2 | `continuous_quality_scaled_expansion` | 64 | 64 | 42/22 | 78.0% | 363.9c ($3.64) | 39.1% | 10.9% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct |
| 3 | `source_or_cheap_quarter_else_half` | 64 | 64 | 42/22 | 78.0% | 358.5c ($3.58) | 39.1% | 16.8% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct |
| 4 | `core_only` | 40 | 40 | 36/4 | 48.8% | 357.0c ($3.57) | 5.0% | 5.0% | 3 | cov 22/settle 0/clean 0/cushion 0.0c | False | coverage_outside_target |
| 5 | `skip_thin_cheap_else_half` | 60 | 60 | 42/18 | 73.2% | 345.0c ($3.45) | 35.0% | 23.0% | 3 | cov 2/settle 0/clean 0/cushion 0.0c | False | coverage_outside_target |
| 6 | `skip_source_thin_cheap_else_half` | 60 | 60 | 42/18 | 73.2% | 345.0c ($3.45) | 35.0% | 23.0% | 3 | cov 2/settle 0/clean 0/cushion 0.0c | False | coverage_outside_target |
| 7 | `expansion_quarter` | 64 | 64 | 42/22 | 78.0% | 344.5c ($3.44) | 39.1% | 16.8% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct |
| 8 | `expansion_half` | 64 | 64 | 42/22 | 78.0% | 332.0c ($3.32) | 39.1% | 26.0% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct |
| 9 | `cheap_tail_quarter_else_half` | 64 | 64 | 42/22 | 78.0% | 331.5c ($3.31) | 39.1% | 19.4% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct |
| 10 | `continuous_ask_scaled_expansion` | 64 | 64 | 42/22 | 78.0% | 321.8c ($3.22) | 39.1% | 14.9% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct |
| 11 | `broad_full_control` | 64 | 64 | 42/22 | 78.0% | 307.0c ($3.07) | 39.1% | 39.1% | 3 | cov 0/settle 0/clean 8/cushion 0.0c | False | row_source_share_gt_35pct, exposure_source_share_gt_35pct |

## Best Policy Class Attribution

- Policy: `approved_expansion_full_reconstructed_quarter`
- Class counts: `{'core': 40, 'source_fragile+cheap_tail': 13, 'source_fragile+cheap_tail+thin_raw_edge': 4, 'approved_expansion': 1, 'source_fragile+thin_raw_edge': 3, 'source_fragile': 1, 'source_fragile+recross_risk': 1, 'source_fragile+thin_raw_edge+recross_risk': 1}`
- Class weights: `{'core': 40.0, 'source_fragile+cheap_tail': 3.25, 'source_fragile+cheap_tail+thin_raw_edge': 1.0, 'approved_expansion': 1.0, 'source_fragile+thin_raw_edge': 0.75, 'source_fragile': 0.25, 'source_fragile+recross_risk': 0.25, 'source_fragile+thin_raw_edge+recross_risk': 0.25}`
- Class weighted net: `{'core': 357.0, 'source_fragile+cheap_tail': 7.0, 'source_fragile+cheap_tail+thin_raw_edge': -6.5, 'approved_expansion': 56.0, 'source_fragile+thin_raw_edge': 4.75, 'source_fragile': -17.0, 'source_fragile+recross_risk': -18.75, 'source_fragile+thin_raw_edge+recross_risk': 4.0}`

## Interpretation

- Full-size broad coverage now has enough settled rows, but source share and full-loss cushion still block promotion.
- Fractional expansion can reduce notional/source exposure, but official promotion still needs row-source quality unless the gate is explicitly changed.
- Treat any live_ready=False row as watch-only, even if weighted net improves.

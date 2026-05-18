# v28 Feature-Gate High-Gap Shrink Diagnostic

Research-only diagnostic; no live bot changes or orders.

- Input report: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_boundary_clock_feature_gate_candidate_latest.json`
- Live baseline net: `1157.000000c`
- Evaluated lane/variant rows: `6`
- Promotion-ready rows: `0`

## Interpretation

- This is a diagnostic notional-shrink replay on existing feature-gate rows, not a new frozen candidate.
- Live baseline used for naive comparison is 1157.0c.
- Best shrink delta is no_shrink_control on diagnostic_entry_raw03_recross70_abs075: 0.0c versus control, weighted net 726.0c, blockers ['does_not_beat_refreshed_live_baseline', 'diagnostic_not_independently_frozen_candidate'].
- Rows with large positive raw/book gaps include tail winners, so any useful repair must track winner cost explicitly.

## diagnostic_entry / diagnostic_entry_raw03_recross70_abs075

- Future denominator: `104`
- Base reconstructed share: `0.325301`

| rank | policy | settled | W/L | coverage | weighted net | delta vs control | delta vs live | row recon | weighted recon | high-gap W/L/net | winner cost | loser saved | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `no_shrink_control` | 82 | 59/23 | 79.807692 | 726.000000 | 0.000000 | -431.000000 | 0.325301 | 0.325301 | 1/1/45.000000 | 0.000000 | 0.000000 | 7 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 2 | `gap30_mild_75` | 82 | 59/23 | 79.807692 | 714.750000 | -11.250000 | -442.250000 | 0.325301 | 0.327273 | 1/1/45.000000 | 14.000000 | 2.750000 | 7 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 3 | `gap30_linear_floor25` | 82 | 59/23 | 79.807692 | 713.022920 | -12.977080 | -443.977080 | 0.325301 | 0.329787 | 1/1/45.000000 | 21.227080 | 8.250000 | 7 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 4 | `gap30_half` | 82 | 59/23 | 79.807692 | 703.500000 | -22.500000 | -453.500000 | 0.325301 | 0.329268 | 1/1/45.000000 | 28.000000 | 5.500000 | 7 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 5 | `gap30_quarter` | 82 | 59/23 | 79.807692 | 692.250000 | -33.750000 | -464.750000 | 0.325301 | 0.331288 | 1/1/45.000000 | 42.000000 | 8.250000 | 6 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |

### High-Gap Rows For Best Policy

| market | source | side | won | net c | gap | weight | weighted c | ask | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY060330-30` | `approved_entry` | `no` | False | -11.000000 | 0.909788 | 1.000000 | -11.000000 | 0.090000 | 0.002807 | 3.991247 |
| `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 56.000000 | 0.451622 | 1.000000 | 56.000000 | 0.420000 | 0.094396 | 0.916460 |

## diagnostic_bridge / diagnostic_bridge_raw03_recross70_abs075

- Future denominator: `102`
- Base reconstructed share: `0.333333`

| rank | policy | settled | W/L | coverage | weighted net | delta vs control | delta vs live | row recon | weighted recon | high-gap W/L/net | winner cost | loser saved | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `no_shrink_control` | 80 | 58/22 | 79.411765 | 718.000000 | 0.000000 | -439.000000 | 0.333333 | 0.333333 | 1/0/56.000000 | 0.000000 | 0.000000 | 7 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 2 | `gap30_mild_75` | 80 | 58/22 | 79.411765 | 704.000000 | -14.000000 | -453.000000 | 0.333333 | 0.334365 | 1/0/56.000000 | 14.000000 | 0.000000 | 7 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 3 | `gap30_linear_floor25` | 80 | 58/22 | 79.411765 | 696.772920 | -21.227080 | -460.227080 | 0.333333 | 0.334901 | 1/0/56.000000 | 21.227080 | 0.000000 | 6 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 4 | `gap30_half` | 80 | 58/22 | 79.411765 | 690.000000 | -28.000000 | -467.000000 | 0.333333 | 0.335404 | 1/0/56.000000 | 28.000000 | 0.000000 | 6 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 5 | `gap30_quarter` | 80 | 58/22 | 79.411765 | 676.000000 | -42.000000 | -481.000000 | 0.333333 | 0.336449 | 1/0/56.000000 | 42.000000 | 0.000000 | 6 | does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |

### High-Gap Rows For Best Policy

| market | source | side | won | net c | gap | weight | weighted c | ask | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 56.000000 | 0.451622 | 1.000000 | 56.000000 | 0.420000 | 0.094396 | 0.916460 |

## post_feature_freeze_entry / post_feature_freeze_entry_raw05_recross60_abs085

- Future denominator: `65`
- Base reconstructed share: `0.325000`

| rank | policy | settled | W/L | coverage | weighted net | delta vs control | delta vs live | row recon | weighted recon | high-gap W/L/net | winner cost | loser saved | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `no_shrink_control` | 30 | 19/11 | 61.538462 | 279.000000 | 0.000000 | -878.000000 | 0.325000 | 0.325000 | 1/0/56.000000 | 0.000000 | 0.000000 | 2 | coverage_too_low, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 2 | `gap30_mild_75` | 30 | 19/11 | 61.538462 | 265.000000 | -14.000000 | -892.000000 | 0.325000 | 0.327044 | 1/0/56.000000 | 14.000000 | 0.000000 | 2 | coverage_too_low, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 3 | `gap30_linear_floor25` | 30 | 19/11 | 61.538462 | 257.772920 | -21.227080 | -899.227080 | 0.325000 | 0.328109 | 1/0/56.000000 | 21.227080 | 0.000000 | 2 | coverage_too_low, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 4 | `gap30_half` | 30 | 19/11 | 61.538462 | 251.000000 | -28.000000 | -906.000000 | 0.325000 | 0.329114 | 1/0/56.000000 | 28.000000 | 0.000000 | 2 | coverage_too_low, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 5 | `gap30_quarter` | 30 | 19/11 | 61.538462 | 237.000000 | -42.000000 | -920.000000 | 0.325000 | 0.331210 | 1/0/56.000000 | 42.000000 | 0.000000 | 2 | coverage_too_low, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |

### High-Gap Rows For Best Policy

| market | source | side | won | net c | gap | weight | weighted c | ask | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 56.000000 | 0.451622 | 1.000000 | 56.000000 | 0.420000 | 0.094396 | 0.916460 |

## post_feature_freeze_entry / post_feature_freeze_entry_raw03_recross70_abs075

- Future denominator: `65`
- Base reconstructed share: `0.425532`

| rank | policy | settled | W/L | coverage | weighted net | delta vs control | delta vs live | row recon | weighted recon | high-gap W/L/net | winner cost | loser saved | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `no_shrink_control` | 37 | 22/15 | 72.307692 | 296.000000 | 0.000000 | -861.000000 | 0.425532 | 0.425532 | 1/0/56.000000 | 0.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 2 | `gap30_mild_75` | 37 | 22/15 | 72.307692 | 282.000000 | -14.000000 | -875.000000 | 0.425532 | 0.427807 | 1/0/56.000000 | 14.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 3 | `gap30_linear_floor25` | 37 | 22/15 | 72.307692 | 274.772920 | -21.227080 | -882.227080 | 0.425532 | 0.428992 | 1/0/56.000000 | 21.227080 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 4 | `gap30_half` | 37 | 22/15 | 72.307692 | 268.000000 | -28.000000 | -889.000000 | 0.425532 | 0.430108 | 1/0/56.000000 | 28.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 5 | `gap30_quarter` | 37 | 22/15 | 72.307692 | 254.000000 | -42.000000 | -903.000000 | 0.425532 | 0.432432 | 1/0/56.000000 | 42.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |

### High-Gap Rows For Best Policy

| market | source | side | won | net c | gap | weight | weighted c | ask | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 56.000000 | 0.451622 | 1.000000 | 56.000000 | 0.420000 | 0.094396 | 0.916460 |

## post_feature_freeze_bridge / post_feature_freeze_bridge_raw05_recross60_abs085

- Future denominator: `66`
- Base reconstructed share: `0.325000`

| rank | policy | settled | W/L | coverage | weighted net | delta vs control | delta vs live | row recon | weighted recon | high-gap W/L/net | winner cost | loser saved | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `no_shrink_control` | 31 | 20/11 | 60.606061 | 333.000000 | 0.000000 | -824.000000 | 0.325000 | 0.325000 | 1/0/56.000000 | 0.000000 | 0.000000 | 3 | coverage_too_low, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 2 | `gap30_mild_75` | 31 | 20/11 | 60.606061 | 319.000000 | -14.000000 | -838.000000 | 0.325000 | 0.327044 | 1/0/56.000000 | 14.000000 | 0.000000 | 3 | coverage_too_low, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 3 | `gap30_linear_floor25` | 31 | 20/11 | 60.606061 | 311.772920 | -21.227080 | -845.227080 | 0.325000 | 0.328109 | 1/0/56.000000 | 21.227080 | 0.000000 | 3 | coverage_too_low, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 4 | `gap30_half` | 31 | 20/11 | 60.606061 | 305.000000 | -28.000000 | -852.000000 | 0.325000 | 0.329114 | 1/0/56.000000 | 28.000000 | 0.000000 | 3 | coverage_too_low, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 5 | `gap30_quarter` | 31 | 20/11 | 60.606061 | 291.000000 | -42.000000 | -866.000000 | 0.325000 | 0.331210 | 1/0/56.000000 | 42.000000 | 0.000000 | 2 | coverage_too_low, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |

### High-Gap Rows For Best Policy

| market | source | side | won | net c | gap | weight | weighted c | ask | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 56.000000 | 0.451622 | 1.000000 | 56.000000 | 0.420000 | 0.094396 | 0.916460 |

## post_feature_freeze_bridge / post_feature_freeze_bridge_raw03_recross70_abs075

- Future denominator: `66`
- Base reconstructed share: `0.425532`

| rank | policy | settled | W/L | coverage | weighted net | delta vs control | delta vs live | row recon | weighted recon | high-gap W/L/net | winner cost | loser saved | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `no_shrink_control` | 38 | 22/16 | 71.212121 | 266.000000 | 0.000000 | -891.000000 | 0.425532 | 0.425532 | 1/0/56.000000 | 0.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 2 | `gap30_mild_75` | 38 | 22/16 | 71.212121 | 252.000000 | -14.000000 | -905.000000 | 0.425532 | 0.427807 | 1/0/56.000000 | 14.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 3 | `gap30_linear_floor25` | 38 | 22/16 | 71.212121 | 244.772920 | -21.227080 | -912.227080 | 0.425532 | 0.428992 | 1/0/56.000000 | 21.227080 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 4 | `gap30_half` | 38 | 22/16 | 71.212121 | 238.000000 | -28.000000 | -919.000000 | 0.425532 | 0.430108 | 1/0/56.000000 | 28.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |
| 5 | `gap30_quarter` | 38 | 22/16 | 71.212121 | 224.000000 | -42.000000 | -933.000000 | 0.425532 | 0.432432 | 1/0/56.000000 | 42.000000 | 0.000000 | 2 | coverage_too_low, row_reconstructed_share_gt_35pct, weighted_reconstructed_share_gt_35pct, weighted_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, diagnostic_not_independently_frozen_candidate |

### High-Gap Rows For Best Policy

| market | source | side | won | net c | gap | weight | weighted c | ask | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 56.000000 | 0.451622 | 1.000000 | 56.000000 | 0.420000 | 0.094396 | 0.916460 |

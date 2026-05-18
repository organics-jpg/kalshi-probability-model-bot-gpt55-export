# Profit Lock Registry/Recompute Divergence Audit

Generated UTC: `20260504_131712Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Compares pre-registered resolved first signals with recomputed fresh selected rows.
- Any divergence means recomputed fresh metrics are diagnostic, not promotion evidence, for that market.

## Summary

| lock | registered | recomputed | common | mismatches | entry | side | win | registry-only | selected-only | net delta sel-reg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| challenger | 81 | 114 | 61 | 81 | 8 | 2 | 2 | 20 | 53 | -10.0c |
| touch_hazard | 93 | 119 | 72 | 69 | 0 | 1 | 1 | 21 | 47 | -99.0c |
| touch_overlay | 86 | 108 | 66 | 63 | 1 | 1 | 1 | 20 | 42 | -101.0c |
| kinetic_touch | 84 | 112 | 63 | 74 | 4 | 1 | 1 | 21 | 49 | -111.0c |
| hazard_mean_touch80 | 23 | 14 | 14 | 11 | 2 | 1 | 1 | 9 | 0 | 101.0c |
| logit_blend_edge10 | 24 | 3 | 3 | 22 | 1 | 0 | 0 | 21 | 0 | 1.0c |
| logit_blend_thresh55_edge15 | 21 | 1 | 1 | 21 | 1 | 0 | 0 | 20 | 0 | -3.0c |
| hazard_fallback_logit55 | 20 | 10 | 10 | 12 | 2 | 1 | 1 | 10 | 0 | 111.0c |
| hazard_fallback_logit55_wait8 | 15 | 6 | 6 | 10 | 1 | 1 | 1 | 9 | 0 | 105.0c |
| hazard_fallback_score60 | 16 | 5 | 5 | 12 | 1 | 1 | 1 | 11 | 0 | 111.0c |
| kinetic_guard | 78 | 111 | 57 | 79 | 4 | 1 | 1 | 21 | 54 | 71.0c |
| kinetic_price_guard | 66 | 96 | 48 | 72 | 6 | 1 | 1 | 18 | 48 | -83.0c |
| kinetic_combo_price_guard | 60 | 68 | 42 | 48 | 4 | 1 | 1 | 18 | 26 | 100.0c |

## Material Differences

- challenger KXBTC15M-26MAY021800-00: selected_only registry= nanc win=None net=nanc; recomputed=yes 73.0c win=False net=-75.0c.
- challenger KXBTC15M-26MAY021900-00: selected_only registry= nanc win=None net=nanc; recomputed=yes 63.0c win=True net=35.0c.
- challenger KXBTC15M-26MAY021915-15: selected_only registry= nanc win=None net=nanc; recomputed=no 73.0c win=True net=25.0c.
- challenger KXBTC15M-26MAY021930-30: selected_only registry= nanc win=None net=nanc; recomputed=no 59.0c win=False net=-61.0c.
- challenger KXBTC15M-26MAY021945-45: selected_only registry= nanc win=None net=nanc; recomputed=yes 54.0c win=False net=-56.0c.
- challenger KXBTC15M-26MAY022000-00: selected_only registry= nanc win=None net=nanc; recomputed=no 65.0c win=True net=33.0c.
- challenger KXBTC15M-26MAY030000-00: selected_only registry= nanc win=None net=nanc; recomputed=yes 61.0c win=True net=37.0c.
- challenger KXBTC15M-26MAY030030-30: selected_only registry= nanc win=None net=nanc; recomputed=yes 68.0c win=True net=30.0c.
- challenger KXBTC15M-26MAY030045-45: selected_only registry= nanc win=None net=nanc; recomputed=no 75.0c win=True net=23.0c.
- challenger KXBTC15M-26MAY030100-00: selected_only registry= nanc win=None net=nanc; recomputed=no 53.0c win=True net=45.0c.
- challenger KXBTC15M-26MAY030115-15: selected_only registry= nanc win=None net=nanc; recomputed=yes 68.0c win=True net=30.0c.
- challenger KXBTC15M-26MAY030130-30: selected_only registry= nanc win=None net=nanc; recomputed=yes 53.0c win=False net=-55.0c.
- challenger KXBTC15M-26MAY030145-45: selected_only registry= nanc win=None net=nanc; recomputed=no 60.0c win=True net=38.0c.
- challenger KXBTC15M-26MAY030200-00: selected_only registry= nanc win=None net=nanc; recomputed=yes 71.0c win=True net=27.0c.
- challenger KXBTC15M-26MAY030215-15: selected_only registry= nanc win=None net=nanc; recomputed=no 76.0c win=True net=22.0c.
- challenger KXBTC15M-26MAY030230-30: selected_only registry= nanc win=None net=nanc; recomputed=no 50.0c win=True net=48.0c.
- challenger KXBTC15M-26MAY030300-00: selected_only registry= nanc win=None net=nanc; recomputed=yes 58.0c win=True net=40.0c.
- challenger KXBTC15M-26MAY030315-15: selected_only registry= nanc win=None net=nanc; recomputed=yes 69.0c win=True net=29.0c.
- challenger KXBTC15M-26MAY030330-30: selected_only registry= nanc win=None net=nanc; recomputed=no 61.0c win=False net=-63.0c.
- challenger KXBTC15M-26MAY030345-45: selected_only registry= nanc win=None net=nanc; recomputed=yes 66.0c win=True net=32.0c.
- challenger KXBTC15M-26MAY030400-00: selected_only registry= nanc win=None net=nanc; recomputed=no 55.0c win=True net=43.0c.
- challenger KXBTC15M-26MAY030415-15: selected_only registry= nanc win=None net=nanc; recomputed=yes 65.0c win=True net=33.0c.
- challenger KXBTC15M-26MAY030430-30: selected_only registry= nanc win=None net=nanc; recomputed=yes 65.0c win=False net=-67.0c.
- challenger KXBTC15M-26MAY030445-45: selected_only registry= nanc win=None net=nanc; recomputed=no 66.0c win=False net=-68.0c.
- challenger KXBTC15M-26MAY030500-00: selected_only registry= nanc win=None net=nanc; recomputed=yes 59.0c win=False net=-61.0c.
- challenger KXBTC15M-26MAY030515-15: selected_only registry= nanc win=None net=nanc; recomputed=no 54.0c win=False net=-56.0c.
- challenger KXBTC15M-26MAY030530-30: selected_only registry= nanc win=None net=nanc; recomputed=yes 68.0c win=True net=30.0c.
- challenger KXBTC15M-26MAY030615-15: selected_only registry= nanc win=None net=nanc; recomputed=no 70.0c win=True net=28.0c.
- challenger KXBTC15M-26MAY030630-30: selected_only registry= nanc win=None net=nanc; recomputed=no 58.0c win=True net=40.0c.
- challenger KXBTC15M-26MAY030945-45: selected_only registry= nanc win=None net=nanc; recomputed=yes 73.0c win=False net=-75.0c.

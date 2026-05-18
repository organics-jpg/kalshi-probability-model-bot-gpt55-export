# Profit Lock Pending Signal Monitor

Generated UTC: `20260505_032157Z`

## Scope

- Research-only pre-resolution registry; no orders are submitted and no bot files or live processes are touched.
- Applies existing locked EV policies to raw heartbeat rows, including unresolved markets.
- Registers the first eligible post-lock signal per market before outcome is available; later runs only update outcomes.

- New records registered this run: 32
- Post-close/non-causal registry records removed this run: 0

## Registry Summary

| lock | registered | pending | resolved | wins/losses | acc | resolved net P&L | first pending |
|---|---:|---:|---:|---:|---:|---:|---|
| book_early_score_gap020_wait | 90 | 1 | 89 | 61/28 | 68.54% | -298.0c | `KXBTC15M-26MAY042330-30` |
| book_hour04_v2_switch | 87 | 1 | 86 | 52/34 | 60.47% | -375.0c | `KXBTC15M-26MAY042330-30` |
| book_margin | 107 | 1 | 106 | 73/33 | 68.87% | 71.0c | `KXBTC15M-26MAY042330-30` |
| book_margin_adverse100 | 70 | 0 | 70 | 46/24 | 65.71% | -136.0c | `` |
| book_margin_delayed_adv100_brownian55 | 83 | 1 | 82 | 55/27 | 67.07% | -325.0c | `KXBTC15M-26MAY042330-30` |
| book_margin_early | 103 | 1 | 102 | 70/32 | 68.63% | 41.0c | `KXBTC15M-26MAY042330-30` |
| book_margin_gap015 | 91 | 1 | 90 | 61/29 | 67.78% | 45.0c | `KXBTC15M-26MAY042330-30` |
| book_p80_ask90_frontier | 42 | 1 | 41 | 34/7 | 82.93% | -75.0c | `KXBTC15M-26MAY042330-30` |
| book_p80_profit_frontier | 43 | 1 | 42 | 34/8 | 80.95% | -169.0c | `KXBTC15M-26MAY042330-30` |
| book_refmargin_score_switch | 80 | 1 | 79 | 55/24 | 69.62% | -179.0c | `KXBTC15M-26MAY042330-30` |
| book_score_gap020_wait | 87 | 1 | 86 | 58/28 | 67.44% | -379.0c | `KXBTC15M-26MAY042330-30` |
| challenger | 130 | 1 | 129 | 87/42 | 67.44% | 78.0c | `KXBTC15M-26MAY042330-30` |
| frontier_v2 | 117 | 1 | 116 | 72/44 | 62.07% | -130.0c | `KXBTC15M-26MAY042330-30` |
| frontier_v2_continuous | 108 | 1 | 107 | 66/41 | 61.68% | -177.0c | `KXBTC15M-26MAY042330-30` |
| hazard_fallback_logit55 | 70 | 1 | 69 | 48/21 | 69.57% | -134.0c | `KXBTC15M-26MAY042330-30` |
| hazard_fallback_logit55_wait8 | 63 | 1 | 62 | 42/20 | 67.74% | -292.0c | `KXBTC15M-26MAY042330-30` |
| hazard_fallback_score60 | 66 | 1 | 65 | 46/19 | 70.77% | -80.0c | `KXBTC15M-26MAY042330-30` |
| hazard_mean_touch80 | 71 | 1 | 70 | 50/20 | 71.43% | -72.0c | `KXBTC15M-26MAY042330-30` |
| hazard_mean_touch80_ask76 | 55 | 1 | 54 | 37/17 | 68.52% | -174.0c | `KXBTC15M-26MAY042330-30` |
| impulse_reversal_book_margin_fade | 60 | 1 | 59 | 33/26 | 55.93% | 19.0c | `KXBTC15M-26MAY042330-30` |
| kinetic_combo_price_guard | 102 | 1 | 101 | 67/34 | 66.34% | 128.0c | `KXBTC15M-26MAY042330-30` |
| kinetic_guard | 128 | 1 | 127 | 89/38 | 70.08% | 8.0c | `KXBTC15M-26MAY042330-30` |
| kinetic_price_guard | 109 | 1 | 108 | 69/39 | 63.89% | -53.0c | `KXBTC15M-26MAY042330-30` |
| kinetic_touch | 136 | 1 | 135 | 89/46 | 65.93% | -349.0c | `KXBTC15M-26MAY042330-30` |
| logit_blend_edge10 | 77 | 1 | 76 | 49/27 | 64.47% | 178.0c | `KXBTC15M-26MAY042330-30` |
| logit_blend_thresh55_edge15 | 71 | 1 | 70 | 49/21 | 70.00% | -107.0c | `KXBTC15M-26MAY042330-30` |
| original | 139 | 1 | 138 | 92/46 | 66.67% | 44.0c | `KXBTC15M-26MAY042330-30` |
| score_min60 | 104 | 1 | 103 | 72/31 | 69.90% | -248.0c | `KXBTC15M-26MAY042330-30` |
| score_min60_gap020 | 93 | 1 | 92 | 64/28 | 69.57% | -244.0c | `KXBTC15M-26MAY042330-30` |
| touch_hazard | 148 | 1 | 147 | 88/59 | 59.86% | -59.0c | `KXBTC15M-26MAY042330-30` |
| touch_overlay | 140 | 1 | 139 | 85/54 | 61.15% | 158.0c | `KXBTC15M-26MAY042330-30` |
| v2_wait_score_min60_brownian70_early | 99 | 1 | 98 | 69/29 | 70.41% | -171.0c | `KXBTC15M-26MAY042330-30` |
| v2_wait_score_min60_early | 103 | 1 | 102 | 71/31 | 69.61% | -259.0c | `KXBTC15M-26MAY042330-30` |

## Read

- At least one lock has pre-registered unresolved market signals waiting for settlement.

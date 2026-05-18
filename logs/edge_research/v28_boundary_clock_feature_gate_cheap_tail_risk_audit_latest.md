# v28 Boundary-Clock Feature-Gate Cheap-Tail Risk Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T04:59:33.256457+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a failure-mode audit, not a promotion candidate.
- Selection policies below use only observable ask price; source labels are used only to audit whether cheap-tail rows explain the source-quality blocker.
- post_feature_freeze_entry broad raw03_recross70_abs075 has 33 settled, coverage 73.33333333333333%, net 277.0c, reconstructed share 0.3939393939393939.
- post_feature_freeze_entry cheap added rows versus strict ask-floor are 6 row(s), net 74.0c, W/L {'wins': 1, 'losses': 5, 'flats': 0}, source counts {'rejected_actionable': 6}.
- post_feature_freeze_entry reconstructed rows net 53.0c; without the top reconstructed win the reconstructed slice is -43.0c.
- post_feature_freeze_entry cheap_lt10_half keeps coverage 73.33333333333333% with weighted net 248.0c; cheap_lt10_skip coverage is 51.11111111111111%.
- post_feature_freeze_bridge broad raw03_recross70_abs075 has 33 settled, coverage 73.33333333333333%, net 277.0c, reconstructed share 0.3939393939393939.
- post_feature_freeze_bridge cheap added rows versus strict ask-floor are 6 row(s), net 74.0c, W/L {'wins': 1, 'losses': 5, 'flats': 0}, source counts {'rejected_actionable': 6}.
- post_feature_freeze_bridge reconstructed rows net 53.0c; without the top reconstructed win the reconstructed slice is -43.0c.
- post_feature_freeze_bridge cheap_lt10_half keeps coverage 73.33333333333333% with weighted net 248.0c; cheap_lt10_skip coverage is 51.11111111111111%.

## post_feature_freeze_entry

- Broad rule: `raw03_recross70_abs075`
- Strict clean rule: `raw05_recross60_abs085_ask65`
- Broad settled/coverage/net/recon: `33/73.33333333333333/277.0c/0.3939393939393939`
- Strict settled/coverage/net/recon: `25/55.55555555555556/126.0c/0.04`
- Added rows versus strict: `8` rows, `63.0c`, W/L `{'wins': 2, 'losses': 6, 'flats': 0}`, sources `{'rejected_actionable': 8}`
- Cheap added rows versus strict: `6` rows, `74.0c`, W/L `{'wins': 1, 'losses': 5, 'flats': 0}`, sources `{'rejected_actionable': 6}`
- Reconstructed rows net/top-win/net-without-top-win: `53.0/96.0/-43.0c`

### Tail Buckets

| bucket | rows | net c | W/L | recon share | avg ask | avg edge | avg recross | avg abs d |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| ask_05_10 | 2 | -13.000000 | 0/2 | 1.000000 | 0.055000 | 0.082015 | 0.101248 | 0.894473 |
| ask_10_15 | 1 | -15.000000 | 0/1 | 1.000000 | 0.130000 | 0.041601 | 0.132257 | 0.784861 |
| ask_gt_90 | 2 | 10.000000 | 2/0 | 1.000000 | 0.935000 | 0.048418 | 0.030804 | 2.070678 |
| ask_lt_05 | 8 | 71.000000 | 1/7 | 1.000000 | 0.026250 | 0.075388 | 0.079250 | 1.080900 |
| mid_ask | 20 | 224.000000 | 18/2 | 0.000000 | 0.767500 | 0.146113 | 0.194607 | 1.193193 |

### Observable Notional Policies

| policy | participating | coverage | weight | weighted net c | cushion | recon share | target cov |
|---|---:|---:|---:|---:|---:|---:|---|
| no_shrink | 33 | 73.333333 | 33.000000 | 277.000000 | 2 | 0.393939 | False |
| cheap_lt10_half | 33 | 73.333333 | 28.000000 | 248.000000 | 2 | 0.393939 | False |
| cheap_lt10_quarter | 33 | 73.333333 | 25.500000 | 233.500000 | 2 | 0.393939 | False |
| cheap_lt15_half | 33 | 73.333333 | 27.500000 | 255.500000 | 2 | 0.393939 | False |
| cheap_lt15_quarter | 33 | 73.333333 | 24.750000 | 244.750000 | 2 | 0.393939 | False |
| cheap_lt10_skip | 23 | 51.111111 | 23.000000 | 219.000000 | 2 | 0.130435 | False |
| cheap_lt15_skip | 22 | 48.888889 | 22.000000 | 234.000000 | 2 | 0.090909 | False |

### Added Rows Versus Strict Ask-Floor

| market | source | side | won | net c | edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 |

## post_feature_freeze_bridge

- Broad rule: `raw03_recross70_abs075`
- Strict clean rule: `raw05_recross60_abs085_ask65`
- Broad settled/coverage/net/recon: `33/73.33333333333333/277.0c/0.3939393939393939`
- Strict settled/coverage/net/recon: `25/55.55555555555556/126.0c/0.04`
- Added rows versus strict: `8` rows, `63.0c`, W/L `{'wins': 2, 'losses': 6, 'flats': 0}`, sources `{'rejected_actionable': 8}`
- Cheap added rows versus strict: `6` rows, `74.0c`, W/L `{'wins': 1, 'losses': 5, 'flats': 0}`, sources `{'rejected_actionable': 6}`
- Reconstructed rows net/top-win/net-without-top-win: `53.0/96.0/-43.0c`

### Tail Buckets

| bucket | rows | net c | W/L | recon share | avg ask | avg edge | avg recross | avg abs d |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| ask_05_10 | 2 | -13.000000 | 0/2 | 1.000000 | 0.055000 | 0.082015 | 0.101248 | 0.894473 |
| ask_10_15 | 1 | -15.000000 | 0/1 | 1.000000 | 0.130000 | 0.041601 | 0.132257 | 0.784861 |
| ask_gt_90 | 2 | 10.000000 | 2/0 | 1.000000 | 0.935000 | 0.048418 | 0.030804 | 2.070678 |
| ask_lt_05 | 8 | 71.000000 | 1/7 | 1.000000 | 0.026250 | 0.075388 | 0.079250 | 1.080900 |
| mid_ask | 20 | 224.000000 | 18/2 | 0.000000 | 0.767500 | 0.146113 | 0.194607 | 1.193193 |

### Observable Notional Policies

| policy | participating | coverage | weight | weighted net c | cushion | recon share | target cov |
|---|---:|---:|---:|---:|---:|---:|---|
| no_shrink | 33 | 73.333333 | 33.000000 | 277.000000 | 2 | 0.393939 | False |
| cheap_lt10_half | 33 | 73.333333 | 28.000000 | 248.000000 | 2 | 0.393939 | False |
| cheap_lt10_quarter | 33 | 73.333333 | 25.500000 | 233.500000 | 2 | 0.393939 | False |
| cheap_lt15_half | 33 | 73.333333 | 27.500000 | 255.500000 | 2 | 0.393939 | False |
| cheap_lt15_quarter | 33 | 73.333333 | 24.750000 | 244.750000 | 2 | 0.393939 | False |
| cheap_lt10_skip | 23 | 51.111111 | 23.000000 | 219.000000 | 2 | 0.130435 | False |
| cheap_lt15_skip | 22 | 48.888889 | 22.000000 | 234.000000 | 2 | 0.090909 | False |

### Added Rows Versus Strict Ask-Floor

| market | source | side | won | net c | edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 |

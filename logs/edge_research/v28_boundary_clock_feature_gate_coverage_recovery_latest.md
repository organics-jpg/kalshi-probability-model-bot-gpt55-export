# v28 Boundary-Clock Feature-Gate Coverage Recovery

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T12:04:52.019162+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a post-freeze mechanism audit, not a promotion candidate.
- The strict ask-floor rule is clean but under-covered; broader rules are judged by source mix, added/replaced row PnL, and runway to 75% coverage.
- post_feature_freeze_entry strict raw05_recross60_abs085_ask65 has 30 settled, coverage 49.18032786885246%, net 212.0c, recon share 0.06666666666666667, blockers ['coverage_too_low', 'full_loss_cushion_lt_3'].
- post_feature_freeze_entry best broader rule raw05_recross60_abs085 has coverage 60.65573770491803%, net 345.0c, recon share 0.35135135135135137, adds 7 markets for 66.0c and needs 9 more selected rows for 75% coverage.
- post_feature_freeze_bridge strict raw05_recross60_abs085_ask65 has 30 settled, coverage 49.18032786885246%, net 212.0c, recon share 0.06666666666666667, blockers ['coverage_too_low', 'full_loss_cushion_lt_3'].
- post_feature_freeze_bridge best broader rule raw05_recross60_abs085 has coverage 60.65573770491803%, net 345.0c, recon share 0.35135135135135137, adds 7 markets for 66.0c and needs 9 more selected rows for 75% coverage.

## post_feature_freeze_entry

| rule | selected/den | settled | W/L | coverage | net c | recon share | cushion | delta vs strict | added markets/net | rows to 75% | clean rows to source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| raw05_recross60_abs085 | 37/61 | 37 | 25/12 | 60.655738 | 345.000000 | 0.351351 | 3 | 133.000000 | 7/66.000000 | 9 | 1 | coverage_too_low, reconstructed_share_gt_35pct |
| raw05_recross60_abs085_ask65 | 30/61 | 30 | 27/3 | 49.180328 | 212.000000 | 0.066667 | 2 | 0.000000 | 0/0 | 16 | 0 | coverage_too_low, full_loss_cushion_lt_3 |
| raw03_recross70_abs075 | 43/61 | 43 | 27/16 | 70.491803 | 284.000000 | 0.441860 | 2 | 72.000000 | 13/-16.000000 | 3 | 12 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw07_recross60_abs085 | 26/61 | 26 | 18/8 | 42.622951 | 292.000000 | 0.307692 | 2 | 174.000000 | 5/78.000000 | 20 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |

### Added Rows Versus Strict Ask-Floor

| rule | market | source | side | side won | net c | edge | recross | abs d | ask |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| raw05_recross60_abs085 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070145-45 | rejected_actionable | yes | False | -3.000000 | 0.043906 | 0.028894 | 1.241798 | 0.020000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -11.000000 | 0.086934 | 0.122242 | 0.758696 | 0.090000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.047387 | 0.085902 | 1.454914 | 0.910000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 0.200931 | 0.253348 | 0.819952 | 0.640000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 |

## post_feature_freeze_bridge

| rule | selected/den | settled | W/L | coverage | net c | recon share | cushion | delta vs strict | added markets/net | rows to 75% | clean rows to source | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| raw05_recross60_abs085 | 37/61 | 37 | 25/12 | 60.655738 | 345.000000 | 0.351351 | 3 | 133.000000 | 7/66.000000 | 9 | 1 | coverage_too_low, reconstructed_share_gt_35pct |
| raw05_recross60_abs085_ask65 | 30/61 | 30 | 27/3 | 49.180328 | 212.000000 | 0.066667 | 2 | 0.000000 | 0/0 | 16 | 0 | coverage_too_low, full_loss_cushion_lt_3 |
| raw03_recross70_abs075 | 43/61 | 43 | 27/16 | 70.491803 | 284.000000 | 0.441860 | 2 | 72.000000 | 13/-16.000000 | 3 | 12 | coverage_too_low, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw07_recross60_abs085 | 26/61 | 26 | 18/8 | 42.622951 | 292.000000 | 0.307692 | 2 | 174.000000 | 5/78.000000 | 20 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |

### Added Rows Versus Strict Ask-Floor

| rule | market | source | side | side won | net c | edge | recross | abs d | ask |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| raw05_recross60_abs085 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 |
| raw05_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070145-45 | rejected_actionable | yes | False | -3.000000 | 0.043906 | 0.028894 | 1.241798 | 0.020000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -11.000000 | 0.086934 | 0.122242 | 0.758696 | 0.090000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.047387 | 0.085902 | 1.454914 | 0.910000 |
| raw03_recross70_abs075 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 0.200931 | 0.253348 | 0.819952 | 0.640000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 |
| raw07_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 |

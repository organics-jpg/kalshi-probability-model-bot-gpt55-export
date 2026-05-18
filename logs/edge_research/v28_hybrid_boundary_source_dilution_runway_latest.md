# v28 Hybrid/Boundary Source Dilution Runway

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T00:49:16.259638+00:00`
- Stack freeze UTC: `2026-05-06T15:37:04.750154+00:00`

## Interpretation

- Best diagnostic stack needs 49 additional clean approved selected rows to dilute reconstructed share to <=35%; it can absorb 8 full-loss rows before net turns non-positive.
- Even the diagnostic source frontier needs 53 clean approved selected rows unless coverage is allowed to fall below target.
- Post-freeze stack evidence is still tiny: settled 66 with 66 entries of denominator 87, reconstructed share 0.6666666666666666; it needs 60 future clean approved settled rows to satisfy the sample/source gate together.
- This is a runway estimate, not promotion evidence; future rows must actually settle and stay profitable.

## Diagnostic Stack Runway

| rank | candidate | settled/entries/den | cov | net c | W/L | recon share | approved | recon | clean rows to <=35% | future rows to gate | max full losses positive | avg c needed for cushion3 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 114/114/152 | 75.000000 | 803.000000 | 83/31 | 0.500000 | 57 | 57 | 49 | 49 | 8 | -10.265306 | reconstructed_share_gt_35pct |
| 2 | 114/114/152 | 75.000000 | 769.000000 | 83/31 | 0.500000 | 57 | 57 | 49 | 49 | 7 | -9.571429 | reconstructed_share_gt_35pct |
| 3 | 114/114/152 | 75.000000 | 731.000000 | 82/32 | 0.526316 | 54 | 60 | 58 | 58 | 7 | -7.431034 | reconstructed_share_gt_35pct |
| 4 | 114/114/152 | 75.000000 | 697.000000 | 82/32 | 0.526316 | 54 | 60 | 58 | 58 | 6 | -6.844828 | reconstructed_share_gt_35pct |
| 5 | 114/114/152 | 75.000000 | 641.000000 | 82/32 | 0.508772 | 56 | 58 | 52 | 52 | 6 | -6.557692 | reconstructed_share_gt_35pct |
| 6 | 114/114/152 | 75.000000 | 607.000000 | 82/32 | 0.508772 | 56 | 58 | 52 | 52 | 6 | -5.903846 | reconstructed_share_gt_35pct |
| 7 | 114/114/152 | 75.000000 | 596.000000 | 82/32 | 0.517544 | 55 | 59 | 55 | 55 | 5 | -5.381818 | reconstructed_share_gt_35pct |
| 8 | 114/114/152 | 75.000000 | 567.000000 | 82/32 | 0.526316 | 54 | 60 | 58 | 58 | 5 | -4.603448 | reconstructed_share_gt_35pct |

## Post-Freeze Stack Runway

| rank | candidate | settled/entries/den | cov | net c | W/L | recon share | approved | recon | clean rows to <=35% | future rows to gate | max full losses positive | avg c needed for cushion3 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 66/66/87 | 75.862069 | 173.000000 | 42/24 | 0.666667 | 22 | 44 | 60 | 60 | 1 | 2.116667 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 2 | 66/66/87 | 75.862069 | 173.000000 | 42/24 | 0.666667 | 22 | 44 | 60 | 60 | 1 | 2.116667 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 3 | 66/66/87 | 75.862069 | 95.000000 | 41/25 | 0.666667 | 22 | 44 | 60 | 60 | 0 | 3.416667 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 4 | 66/66/87 | 75.862069 | 95.000000 | 41/25 | 0.666667 | 22 | 44 | 60 | 60 | 0 | 3.416667 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 5 | 66/66/87 | 75.862069 | 88.000000 | 42/24 | 0.636364 | 24 | 42 | 55 | 55 | 0 | 3.854545 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 6 | 66/66/87 | 75.862069 | 88.000000 | 42/24 | 0.636364 | 24 | 42 | 55 | 55 | 0 | 3.854545 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 7 | 66/66/87 | 75.862069 | 10.000000 | 41/25 | 0.636364 | 24 | 42 | 55 | 55 | 0 | 5.272727 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| 8 | 66/66/87 | 75.862069 | 10.000000 | 41/25 | 0.636364 | 24 | 42 | 55 | 55 | 0 | 5.272727 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## Diagnostic Frontier Runway

| rank | candidate | settled/entries/den | cov | net c | W/L | recon share | approved | recon | clean rows to <=35% | future rows to gate | max full losses positive | avg c needed for cushion3 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 96/96/128 | 75.000000 | 1980.000000 | 79/17 | 0.541667 | 44 | 52 | 53 | 53 | 19 | -31.698113 | reconstructed_share_gt_35pct |
| 2 | 96/96/128 | 75.000000 | 1961.000000 | 78/18 | 0.593750 | 39 | 57 | 67 | 67 | 19 | -24.791045 | reconstructed_share_gt_35pct |
| 3 | 96/96/128 | 75.000000 | 1957.000000 | 78/18 | 0.552083 | 43 | 53 | 56 | 56 | 19 | -29.589286 | reconstructed_share_gt_35pct |
| 4 | 96/96/128 | 75.000000 | 1942.000000 | 79/17 | 0.531250 | 45 | 51 | 50 | 50 | 19 | -32.840000 | reconstructed_share_gt_35pct |
| 5 | 96/96/128 | 75.000000 | 1837.000000 | 78/18 | 0.541667 | 44 | 52 | 53 | 53 | 18 | -29.000000 | reconstructed_share_gt_35pct |

## Post-Freeze Frontier Runway

| rank | candidate | settled/entries/den | cov | net c | W/L | recon share | approved | recon | clean rows to <=35% | future rows to gate | max full losses positive | avg c needed for cushion3 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 48/48/63 | 76.190476 | 681.000000 | 32/16 | 0.791667 | 10 | 38 | 61 | 61 | 6 | -6.245902 | reconstructed_share_gt_35pct |
| 2 | 48/48/63 | 76.190476 | 568.000000 | 32/16 | 0.750000 | 12 | 36 | 55 | 55 | 5 | -4.872727 | reconstructed_share_gt_35pct |
| 3 | 48/48/63 | 76.190476 | 556.000000 | 32/16 | 0.750000 | 12 | 36 | 55 | 55 | 5 | -4.654545 | reconstructed_share_gt_35pct |
| 4 | 48/48/63 | 76.190476 | 444.000000 | 31/17 | 0.770833 | 11 | 37 | 58 | 58 | 4 | -2.482759 | reconstructed_share_gt_35pct |
| 5 | 48/48/63 | 76.190476 | 444.000000 | 31/17 | 0.770833 | 11 | 37 | 58 | 58 | 4 | -2.482759 | reconstructed_share_gt_35pct |

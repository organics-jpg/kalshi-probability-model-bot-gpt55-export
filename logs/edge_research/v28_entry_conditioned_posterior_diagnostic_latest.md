# v28 Entry-Conditioned Posterior Diagnostic

Fixed entry selector: raw v28 p50 edge0. Tests whether posterior lift improves calibration across physical buckets.

- Selected entries: `172`
- Settled entries: `172`

| bucket | rows | settled | W/L | net c | best overlay | best brier | plus05 brier delta | plus05 logloss delta |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| all | 172 | 172 | 101/71 | -81.000000 | book_probability | 0.217446 | 0.006406 | 0.011122 |
| early_markets | 86 | 86 | 54/32 | 330.000000 | noise_shrink_light_probability | 0.224976 | 0.002481 | 0.004143 |
| late_markets | 86 | 86 | 47/39 | -411.000000 | book_probability | 0.207805 | 0.010331 | 0.018102 |
| approved_entries | 10 | 10 | 10/0 | 133.000000 | entry_conditioned_plus05_probability | 0.003762 | -0.007807 | -0.051943 |
| shadow_rejected_actionable | 162 | 162 | 91/71 | -214.000000 | book_probability | 0.228479 | 0.007283 | 0.015015 |
| near_strike_abs_d_lte_025 | 92 | 92 | 47/45 | 23.000000 | book_probability | 0.242314 | 0.006122 | 0.012510 |
| away_from_strike_abs_d_gt_025 | 80 | 80 | 54/26 | -104.000000 | book_probability | 0.188848 | 0.006733 | 0.009527 |
| high_recross | 165 | 165 | 94/71 | -144.000000 | book_probability | 0.225007 | 0.006995 | 0.013748 |
| lower_recross | 7 | 7 | 7/0 | 63.000000 | entry_conditioned_plus05_probability | 0.003996 | -0.007483 | -0.050778 |
| spectral_dominant_factor | 168 | 168 | 99/69 | 92.000000 | book_probability | 0.219352 | 0.006038 | 0.010756 |
| insufficient_or_other_spectral | 4 | 4 | 2/2 | -173.000000 | entry_conditioned_logit125_p60_only_probability | 0.135606 | 0.021873 | 0.026498 |
| raw_p_50_60 | 87 | 87 | 46/41 | 419.000000 | book_probability | 0.240217 | 0.003928 | 0.007814 |
| raw_p_60_plus | 85 | 85 | 55/30 | -500.000000 | book_probability | 0.194139 | 0.008942 | 0.014509 |
| ask_lte_60 | 119 | 119 | 58/61 | -657.000000 | book_probability | 0.246024 | 0.010444 | 0.022620 |
| ask_gt_60 | 53 | 53 | 43/10 | 576.000000 | entry_conditioned_plus05_probability | 0.140569 | -0.002660 | -0.014694 |

## Interpretation

- Buckets where +5pp failed to improve Brier with at least 5 settled rows:
  - `all` settled `172`, delta `0.006406`
  - `early_markets` settled `86`, delta `0.002481`
  - `late_markets` settled `86`, delta `0.010331`
  - `shadow_rejected_actionable` settled `162`, delta `0.007283`
  - `near_strike_abs_d_lte_025` settled `92`, delta `0.006122`
  - `away_from_strike_abs_d_gt_025` settled `80`, delta `0.006733`
  - `high_recross` settled `165`, delta `0.006995`
  - `spectral_dominant_factor` settled `168`, delta `0.006038`
  - `raw_p_50_60` settled `87`, delta `0.003928`
  - `raw_p_60_plus` settled `85`, delta `0.008942`
  - `ask_lte_60` settled `119`, delta `0.010444`
- This remains discovery-only until the frozen forward validator accumulates sample.

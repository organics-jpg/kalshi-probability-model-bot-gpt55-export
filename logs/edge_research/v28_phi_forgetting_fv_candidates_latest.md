# v28 Phi-Forgetting FV Candidates

Frozen forward validator for phi-decay catastrophic-forgetting overlays.

- Freeze timestamp UTC: `2026-05-06T15:08:04.481035+00:00`
- Entry policy: `raw_v28_p50_edge0_fixed_selection`
- Forward denominator: `89`
- Phi: `1.618033988749895`
- Hypothesis: Phi decay is a compressible forgetting schedule: each independent noise/turbulence warning divides retained FV adjustment by phi. Durable geometry can restore one half-step, but selection cannot change.

## Forward Ranking

| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | raw_probability | 88 | 88 | 49/39 | 98.876404 | 0.221305 | 0.000000 | 0.625296 | 0.000000 | 0.623808 | 0.556818 | -247.000000 | none |
| 2 | phi_half_shrink_to50 | 88 | 88 | 49/39 | 98.876404 | 0.221651 | 0.000346 | 0.627322 | 0.002026 | 0.599143 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 3 | phi_forget_logit125 | 88 | 88 | 49/39 | 98.876404 | 0.222163 | 0.000858 | 0.624718 | -0.000577 | 0.638560 | 0.556818 | -247.000000 | brier_not_better_than_raw |
| 4 | phi_shrink_to50 | 88 | 88 | 49/39 | 98.876404 | 0.223117 | 0.001812 | 0.631021 | 0.005726 | 0.584934 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 5 | phi_forget_plus03 | 88 | 88 | 49/39 | 98.876404 | 0.223175 | 0.001870 | 0.627380 | 0.002084 | 0.637842 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 6 | phi_forget_plus05 | 88 | 88 | 49/39 | 98.876404 | 0.224746 | 0.003441 | 0.629670 | 0.004374 | 0.646999 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |

## Discovery Context

Not promotion evidence. The phi schedule must earn forward rows after its own freeze timestamp.

| rank | overlay | entries | settled | W/L | brier | d brier | logloss | d logloss | avg p | win rate | net c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | phi_half_shrink_to50 | 172 | 172 | 101/71 | 0.223828 | -0.000167 | 0.632222 | 0.000325 | 0.599665 | 0.587209 | -81.000000 |
| 2 | raw_probability | 172 | 172 | 101/71 | 0.223995 | 0.000000 | 0.631897 | 0.000000 | 0.626302 | 0.587209 | -81.000000 |
| 3 | phi_shrink_to50 | 172 | 172 | 101/71 | 0.224932 | 0.000937 | 0.635003 | 0.003106 | 0.584493 | 0.587209 | -81.000000 |
| 4 | phi_forget_logit125 | 172 | 172 | 101/71 | 0.225350 | 0.001356 | 0.632604 | 0.000707 | 0.640982 | 0.587209 | -81.000000 |
| 5 | phi_forget_plus03 | 172 | 172 | 101/71 | 0.225722 | 0.001728 | 0.633976 | 0.002080 | 0.639694 | 0.587209 | -81.000000 |
| 6 | phi_forget_plus05 | 172 | 172 | 101/71 | 0.227181 | 0.003187 | 0.636161 | 0.004265 | 0.648521 | 0.587209 | -81.000000 |

## Forward Buckets

| bucket | entries | settled | W/L | avg phi penalty | avg retention | net c | raw brier | phi shrink | phi half shrink | phi +3 | phi +5 | phi logit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 88 | 88 | 49/39 | 2.193182 | 0.469191 | -247.000000 | 0.221305 | 0.223117 | 0.221651 | 0.223175 | 0.224746 | 0.222163 |
| away_from_strike | 41 | 41 | 28/13 | 0.634146 | 0.771885 | 146.000000 | 0.186935 | 0.192043 | 0.188820 | 0.188901 | 0.190846 | 0.188329 |
| edge_ge_4pp | 45 | 45 | 25/20 | 1.555556 | 0.604399 | 235.000000 | 0.220546 | 0.220768 | 0.220997 | 0.224076 | 0.226918 | 0.223103 |
| edge_lt_4pp | 43 | 43 | 24/19 | 2.860465 | 0.327695 | -482.000000 | 0.222099 | 0.225575 | 0.222335 | 0.222232 | 0.222472 | 0.221179 |
| high_recross | 50 | 50 | 24/26 | 3.250000 | 0.263254 | -676.000000 | 0.260878 | 0.256497 | 0.257845 | 0.263808 | 0.265870 | 0.263787 |
| lower_recross | 38 | 38 | 25/13 | 0.802632 | 0.740161 | 429.000000 | 0.169235 | 0.179195 | 0.174027 | 0.169709 | 0.170635 | 0.167395 |
| near_strike | 47 | 47 | 21/26 | 3.553191 | 0.205139 | -393.000000 | 0.251287 | 0.250224 | 0.250290 | 0.253073 | 0.254318 | 0.251678 |
| phi_forget_heavy | 45 | 45 | 20/25 | 3.644444 | 0.192663 | -347.000000 | 0.250680 | 0.250039 | 0.249949 | 0.252396 | 0.253587 | 0.250946 |
| phi_remember_high | 22 | 22 | 14/8 | 0.068182 | 0.970839 | -8.000000 | 0.196082 | 0.191293 | 0.193516 | 0.201160 | 0.205470 | 0.201183 |
| raw_p_50_60 | 44 | 44 | 20/24 | 3.681818 | 0.188360 | -249.000000 | 0.248004 | 0.249074 | 0.248346 | 0.249441 | 0.250442 | 0.248004 |
| raw_p_60_plus | 44 | 44 | 29/15 | 0.704545 | 0.750022 | 2.000000 | 0.194605 | 0.197160 | 0.194956 | 0.196909 | 0.199049 | 0.196322 |

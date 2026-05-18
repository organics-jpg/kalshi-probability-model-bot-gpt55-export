# v28 Raw p52 Book-Disagreement Skip

Discovery diagnostic only. The rule is frozen separately before forward validation.

- Base policy: `v28_raw_p52_edge0`
- Candidate: `raw_p52_skip_v28_minus_book_gt15pp`
- Rule: `Start from v28_raw_p52_edge0 and skip rows where p_eff - executable ask probability > 15pp.`
- Watched markets: `181`
- Delta vs base: `-28.000000c`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg p-book | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 169 | 169 | 104/65 | 93.370166 | 0.615385 | 0.644300 | 0.586036 | 0.058265 | 71.000000 | 12/157 |
| candidate_summary | 155 | 155 | 98/57 | 85.635359 | 0.632258 | 0.644811 | 0.603742 | 0.041069 | 43.000000 | 11/144 |
| skipped_summary | 14 | 14 | 6/8 | 7.734807 | 0.428571 | 0.638640 | 0.390000 | 0.248640 | 28.000000 | 1/13 |

## Skipped Rows

| market | side | source | p | ask | p-book | won | net c |
|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY051830-30 | yes | rejected_actionable | 0.581240 | 0.310000 | 0.271240 | True | 135.000000 |
| KXBTC15M-26MAY060445-45 | no | rejected_actionable | 0.636374 | 0.450000 | 0.186374 | False | -94.000000 |
| KXBTC15M-26MAY060545-45 | no | rejected_actionable | 0.626642 | 0.440000 | 0.186642 | False | -92.000000 |
| KXBTC15M-26MAY060945-45 | no | rejected_actionable | 0.761891 | 0.500000 | 0.261891 | True | 96.000000 |
| KXBTC15M-26MAY061830-30 | yes | rejected_actionable | 0.553162 | 0.230000 | 0.323162 | False | -49.000000 |
| KXBTC15M-26MAY061900-00 | no | rejected_actionable | 0.661389 | 0.450000 | 0.211389 | False | -94.000000 |
| KXBTC15M-26MAY062030-30 | yes | rejected_actionable | 0.544418 | 0.320000 | 0.224418 | False | -68.000000 |
| KXBTC15M-26MAY062100-00 | no | rejected_actionable | 0.615588 | 0.220000 | 0.395588 | False | -47.000000 |
| KXBTC15M-26MAY062130-30 | yes | rejected_actionable | 0.586142 | 0.410000 | 0.176142 | True | 114.000000 |
| KXBTC15M-26MAY062200-00 | no | rejected_actionable | 0.617816 | 0.460000 | 0.157816 | True | 104.000000 |
| KXBTC15M-26MAY062230-30 | yes | rejected_actionable | 0.718015 | 0.380000 | 0.338015 | False | -80.000000 |
| KXBTC15M-26MAY070030-30 | no | rejected_actionable | 0.523605 | 0.330000 | 0.193605 | False | -70.000000 |
| KXBTC15M-26MAY070615-15 | no | rejected_actionable | 0.610872 | 0.280000 | 0.330872 | True | 141.000000 |
| KXBTC15M-26MAY070745-45 | yes | approved_entry | 0.903807 | 0.680000 | 0.223807 | True | 32.000000 |

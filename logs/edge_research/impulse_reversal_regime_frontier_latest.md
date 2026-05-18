# Impulse Reversal Regime Frontier

Generated UTC: `20260504_100050Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether short-horizon favorable impulse larger than distance-to-strike is an overreaction state.
- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 307
- V21 markets: 221
- Candidate specs: 205
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 cov | current/v21 net | current/v21 acc | min block+ rate | worst block | fades current/v21 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `fade; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=60; impulse_3_5m-margin>=20; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 4141.0c | 1837.0c | 97.78% | 99.35%/99.10% | 2337.0c/1804.0c | 70.82%/71.23% | 0.667 | -311.0c | 44/41 |
| `fade; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=60; signed_move_5m-margin>=20; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 3591.0c | 1702.0c | 97.78% | 99.35%/99.10% | 2194.0c/1397.0c | 70.82%/71.23% | 0.667 | -311.0c | 39/29 |
| `fade; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=60; impulse_3_5m-margin>=40; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 3359.0c | 1629.0c | 97.78% | 99.35%/99.10% | 2133.0c/1226.0c | 70.82%/71.23% | 0.667 | -332.0c | 38/25 |
| `fade; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=60; signed_move_5m-margin>=40; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 3062.0c | 1450.0c | 97.78% | 99.35%/99.10% | 1946.0c/1116.0c | 70.82%/71.23% | 0.600 | -332.0c | 31/21 |
| `fade; base=min55; choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; sec_to_close>=120; impulse_3_5m>=60; impulse_3_5m-margin>=20; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 3880.0c | 1326.0c | 97.78% | 99.35%/99.10% | 1956.0c/1924.0c | 67.87%/69.86% | 0.667 | -269.0c | 47/39 |
| `fade; base=min55; choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; sec_to_close>=120; signed_move_5m>=60; signed_move_5m-margin>=20; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 3467.0c | 1257.0c | 97.78% | 99.35%/99.10% | 1824.0c/1643.0c | 67.87%/69.86% | 0.667 | -269.0c | 41/29 |
| `fade; base=min55; choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; sec_to_close>=120; impulse_3_5m>=60; impulse_3_5m-margin>=40; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 3150.0c | 1026.0c | 97.78% | 99.35%/99.10% | 1571.0c/1579.0c | 67.87%/69.86% | 0.667 | -289.0c | 36/28 |
| `fade; base=min55; choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; sec_to_close>=120; signed_move_5m>=60; signed_move_5m-margin>=40; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 2943.0c | 935.0c | 97.78% | 99.35%/99.10% | 1452.0c/1491.0c | 67.87%/69.86% | 0.600 | -289.0c | 30/24 |
| `baseline; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=10000; impulse_3_5m-margin>=10000; sec>=120; margin_sigma<=10000; score<=1; fade_ask<=45` | False | 1376.0c | 853.0c | 97.78% | 99.35%/99.10% | 951.0c/425.0c | 70.82%/71.23% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=80; impulse_3_5m-margin>=0; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 1318.0c | 812.0c | 97.78% | 99.35%/99.10% | 833.0c/485.0c | 70.82%/72.15% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=60; impulse_3_5m-margin>=0; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1068.0c | 795.0c | 97.78% | 99.35%/99.10% | 723.0c/345.0c | 70.49%/71.69% | 0.600 | -342.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=60; impulse_3_5m-margin>=0; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 1022.0c | 792.0c | 97.78% | 99.35%/99.10% | 689.0c/333.0c | 70.49%/71.69% | 0.600 | -342.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=80; impulse_3_5m-margin>=20; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 1334.0c | 770.0c | 97.78% | 99.35%/99.10% | 836.0c/498.0c | 70.82%/72.15% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=40; impulse_3_5m-margin>=0; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 485.0c | 748.0c | 97.78% | 99.35%/99.10% | 470.0c/15.0c | 70.16%/71.23% | 0.467 | -365.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=80; signed_move_5m-margin>=0; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1256.0c | 739.0c | 97.78% | 99.35%/99.10% | 867.0c/389.0c | 70.82%/71.69% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=80; signed_move_5m-margin>=0; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 1274.0c | 738.0c | 97.78% | 99.35%/99.10% | 863.0c/411.0c | 70.82%/71.69% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=80; signed_move_5m-margin>=40; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1223.0c | 729.0c | 97.78% | 99.35%/99.10% | 889.0c/334.0c | 70.82%/71.23% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=60; signed_move_5m-margin>=40; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1101.0c | 724.0c | 97.78% | 99.35%/99.10% | 774.0c/327.0c | 70.49%/71.23% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=80; signed_move_5m-margin>=20; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1286.0c | 722.0c | 97.78% | 99.35%/99.10% | 882.0c/404.0c | 70.82%/71.69% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=80; signed_move_5m-margin>=20; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 1307.0c | 721.0c | 97.78% | 99.35%/99.10% | 878.0c/429.0c | 70.82%/71.69% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=80; impulse_3_5m-margin>=0; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1134.0c | 721.0c | 97.78% | 99.35%/99.10% | 758.0c/376.0c | 70.49%/71.69% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=80; signed_move_5m-margin>=40; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 1220.0c | 718.0c | 97.78% | 99.35%/99.10% | 878.0c/342.0c | 70.82%/71.23% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=60; signed_move_5m-margin>=40; sec>=600; margin_sigma<=0.75; score<=0.82; fade_ask<=45` | False | 1097.0c | 712.0c | 97.78% | 99.35%/99.10% | 762.0c/335.0c | 70.49%/71.23% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=60; signed_move_5m-margin>=0; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 990.0c | 702.0c | 97.78% | 99.35%/99.10% | 632.0c/358.0c | 70.16%/71.69% | 0.600 | -342.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=40; signed_move_5m-margin>=0; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 499.0c | 696.0c | 97.78% | 99.35%/99.10% | 423.0c/76.0c | 69.84%/71.23% | 0.467 | -362.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=80; impulse_3_5m-margin>=40; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1091.0c | 693.0c | 97.78% | 99.35%/99.10% | 763.0c/328.0c | 70.49%/71.23% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=80; impulse_3_5m-margin>=20; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1145.0c | 690.0c | 97.78% | 99.35%/99.10% | 759.0c/386.0c | 70.49%/71.69% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_5m>=60; signed_move_5m-margin>=20; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 1122.0c | 685.0c | 97.78% | 99.35%/99.10% | 741.0c/381.0c | 70.49%/71.69% | 0.600 | -342.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=60; impulse_3_5m-margin>=40; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 940.0c | 681.0c | 97.78% | 99.35%/99.10% | 621.0c/319.0c | 70.16%/71.23% | 0.600 | -332.0c | 0/0 |
| `veto; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=40; impulse_3_5m-margin>=20; sec>=600; margin_sigma<=0.5; score<=0.82; fade_ask<=45` | False | 460.0c | 677.0c | 97.78% | 99.35%/99.10% | 428.0c/32.0c | 69.84%/70.78% | 0.533 | -362.0c | 0/0 |

## Baselines

| policy | combined all net | combined OOS net | min split cov | current/v21 cov | current/v21 net | current/v21 acc |
|---|---:|---:|---:|---:|---:|---:|
| `baseline; base=book_margin; choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=10000; impulse_3_5m-margin>=10000; sec>=120; margin_sigma<=10000; score<=1; fade_ask<=45` | 1376.0c | 853.0c | 97.78% | 99.35%/99.10% | 951.0c/425.0c | 70.82%/71.23% |
| `baseline; base=min55; choose=score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; sec_to_close>=120; impulse_3_5m>=10000; impulse_3_5m-margin>=10000; sec>=120; margin_sigma<=10000; score<=1; fade_ask<=45` | 1250.0c | 251.0c | 97.78% | 99.35%/99.10% | 418.0c/832.0c | 67.87%/69.86% |
| `baseline; base=book55_margin; choose=book_p_side; book_p_side>=0.55; ask<=95; sec_to_close>=120; margin_rv15>=0; impulse_3_5m>=10000; impulse_3_5m-margin>=10000; sec>=120; margin_sigma<=10000; score<=1; fade_ask<=45` | 724.0c | -281.0c | 97.78% | 99.35%/99.10% | 224.0c/500.0c | 64.92%/67.12% |
| `baseline; base=mean55; choose=score_mean_book_rv15; score_mean_book_rv15>=0.55; ask<=95; sec_to_close>=120; impulse_3_5m>=10000; impulse_3_5m-margin>=10000; sec>=120; margin_sigma<=10000; score<=1; fade_ask<=45` | 335.0c | -119.0c | 97.78% | 99.35%/99.10% | -415.0c/750.0c | 62.30%/67.58% |
| `baseline; base=regime55; choose=score_regime_blend; score_regime_blend>=0.55; ask<=95; sec_to_close>=120; impulse_3_5m>=10000; impulse_3_5m-margin>=10000; sec>=120; margin_sigma<=10000; score<=1; fade_ask<=45` | -1680.0c | -1137.0c | 97.78% | 99.35%/99.10% | -2312.0c/632.0c | 52.13%/62.10% |

## Read

- No impulse reversal overlay clears the full strict gate. Do not promote any row from this scan.

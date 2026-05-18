# v28 Forward Calibration

- Scope: settled v28 approved entries plus actionable settled rejects.
- Purpose: judge FV probability calibration before using P&L as a model selector.

## Overall

- Observations: `795`
- Avg p_side: `0.7129118490566038`
- Win rate: `0.7144654088050314`
- Calibration error win_rate_minus_avg_p: `0.0015535597484276353`
- Avg Brier: `0.16330634137287547`
- Gross cents proxy: `472.0`

## By Probability Bucket

| bucket | count | avg p | win rate | error | brier | gross c |
|---|---:|---:|---:|---:|---:|---:|
| 00_50 | 177 | 0.4108281355932203 | 0.4180790960451977 | 0.0072509604519774284 | 0.23527528576268927 | -966.0 |
| 50_60 | 118 | 0.542476406779661 | 0.6101694915254238 | 0.06769308474576274 | 0.23699001927608473 | 1400.0 |
| 60_70 | 44 | 0.6364080227272727 | 0.5 | -0.1364080227272727 | 0.2628138595200682 | -1198.0 |
| 70_80 | 29 | 0.7490259310344827 | 0.8620689655172413 | 0.11304303448275865 | 0.129748059684 | 186.0 |
| 80_85 | 22 | 0.8281605909090909 | 0.8636363636363636 | 0.03547577272727276 | 0.11706820331777273 | -236.0 |
| 85_90 | 259 | 0.8670064208494209 | 0.8494208494208494 | -0.017585571428571534 | 0.12724123696964093 | 413.0 |
| 90_95 | 91 | 0.9233148461538462 | 0.9230769230769231 | -0.00023792307692305226 | 0.07113284506517582 | 561.0 |
| 95_100 | 55 | 0.9730285818181817 | 0.9454545454545454 | -0.02757403636363631 | 0.05253491341970909 | 312.0 |

## By Source

| source | count | avg p | win rate | error | brier | gross c |
|---|---:|---:|---:|---:|---:|---:|
| entry | 173 | 0.8838875953757226 | 0.8439306358381503 | -0.03995695953757228 | 0.13363403471027746 | 823.0 |
| rejected_actionable | 622 | 0.6653575016077171 | 0.6784565916398714 | 0.01309909003215426 | 0.17155924981761736 | -351.0 |

## Latest Observations

| source | market | side | reason | bucket | p_side | outcome | brier | gross c |
|---|---|---|---|---|---:|---:|---:|---:|
| rejected_actionable | KXBTC15M-26MAY071230-30 | yes | edge_below_floor | 85_90 | 0.857838 | 1.0 | 0.020210034244000002 | 38 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | no | p_below_floor | 00_50 | 0.440021 | 1.0 | 0.313576480441 | 108 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | no | edge_below_floor | 85_90 | 0.853317 | 1.0 | 0.021515902489000004 | 32 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | no | ask_too_high | 90_95 | 0.921072 | 1.0 | 0.006229629184 | 18 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | yes | p_below_floor | 50_60 | 0.559979 | 0.0 | 0.313576480441 | -110 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | no | p_below_floor | 00_50 | 0.36396 | 1.0 | 0.4045468815999999 | 116 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | no | ask_too_high | 80_85 | 0.835792 | 1.0 | 0.026964267264000006 | 18 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | no | edge_below_floor | 90_95 | 0.938084 | 1.0 | 0.003833591055999996 | 20 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | yes | p_below_floor | 60_70 | 0.63604 | 0.0 | 0.4045468816000001 | -118 |
| entry | KXBTC15M-26MAY071315-15 | yes | approved_entry | 85_90 | 0.860278 | 1.0 | 0.019522237284000002 | -6 |
| entry | KXBTC15M-26MAY071315-15 | yes | approved_entry | 85_90 | 0.865868 | 1.0 | 0.017991393424000007 | -14 |
| entry | KXBTC15M-26MAY071315-15 | yes | approved_entry | 85_90 | 0.850827 | 1.0 | 0.022252583929 | 32 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | no | p_below_floor | 00_50 | 0.466558 | 0.0 | 0.21767636736399998 | -100 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | yes | p_below_floor | 50_60 | 0.533442 | 1.0 | 0.21767636736400003 | 98 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | yes | edge_below_floor | 85_90 | 0.850666 | 1.0 | 0.02230064355599999 | 40 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | yes | ask_too_high | 95_100 | 0.955633 | 1.0 | 0.001968430689000004 | 14 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | no | p_below_floor | 50_60 | 0.576763 | 1.0 | 0.17912955816899997 | 80 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | no | edge_below_floor | 85_90 | 0.86478 | 1.0 | 0.0182844484 | 18 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | no | ask_too_high | 90_95 | 0.921226 | 1.0 | 0.006205343076000002 | 16 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | yes | p_below_floor | 00_50 | 0.423237 | 0.0 | 0.17912955816899997 | -82 |

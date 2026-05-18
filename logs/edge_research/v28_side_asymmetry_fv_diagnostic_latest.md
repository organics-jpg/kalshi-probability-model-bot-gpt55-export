# v28 Side-Asymmetry FV Diagnostic

Research-only: no live bot changes and no orders.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Entries/settled: `112/112`
- Min bucket settled: `3`

## Interpretation

- Target surface has 112 entries over 152 forward markets.
- Buckets are predeclared by side, p-range, distance, recross, time, source, and boundary-clock state.
- Top suspicious bucket is side:no|p60_70 with settled=27, net=-888.0c, avg_p=0.632525037037037, win_rate=0.4074074074074074.
- This is diagnostic only; promote nothing until a frozen future registry validates the bucket.

## Suspicious Buckets

| bucket | rows | settled | W/L | avg p | win rate | cal gap | net c | shrink50 brier delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| side:no|p60_70 | 27 | 27 | 11/16 | 0.632525 | 0.407407 | 0.225118 | -888.000000 | -1.104351 |
| side:no|p60_70|mid_boundary | 14 | 14 | 5/9 | 0.649386 | 0.357143 | 0.292244 | -615.000000 | -0.881936 |
| side:no|p60_70|mid_boundary|mid_recross | 10 | 10 | 3/7 | 0.646175 | 0.300000 | 0.346175 | -499.000000 | -0.788991 |
| side:no|p60_70|near_boundary|early | 7 | 7 | 2/5 | 0.614681 | 0.285714 | 0.328967 | -446.000000 | -0.388953 |
| side:yes|p60_70|near_boundary|clock:True | 7 | 7 | 2/5 | 0.612740 | 0.285714 | 0.327025 | -416.000000 | -0.441733 |
| side:no|p60_70|near_boundary|clock:True | 5 | 5 | 1/4 | 0.607024 | 0.200000 | 0.407024 | -398.000000 | -0.359006 |
| side:no|p60_70|mid_boundary|early | 10 | 10 | 4/6 | 0.650739 | 0.400000 | 0.250739 | -390.000000 | -0.542095 |
| side:yes|source:rejected_actionable | 56 | 56 | 30/26 | 0.623173 | 0.535714 | 0.087459 | -355.000000 | 0.448954 |
| side:no|p60_70|mid_boundary|clock:False | 12 | 12 | 5/7 | 0.646270 | 0.416667 | 0.229603 | -345.000000 | -0.489152 |
| side:no|source:rejected_actionable | 49 | 49 | 27/22 | 0.652237 | 0.551020 | 0.101217 | -334.000000 | 1.030484 |
| side:no|p60_70|near_boundary|high_recross | 6 | 6 | 2/4 | 0.611981 | 0.333333 | 0.278648 | -328.000000 | -0.240944 |
| side:no | 52 | 52 | 30/22 | 0.667703 | 0.576923 | 0.090780 | -323.000000 | 1.755406 |
| side:yes | 60 | 60 | 34/26 | 0.641681 | 0.566667 | 0.075014 | -303.000000 | 1.408968 |
| side:yes|p70_80 | 8 | 8 | 4/4 | 0.749082 | 0.500000 | 0.249082 | -301.000000 | -0.442738 |
| side:no|p60_70|near_boundary | 13 | 13 | 6/7 | 0.614367 | 0.461538 | 0.152828 | -273.000000 | -0.222415 |
| side:yes|p60_70|near_boundary|high_recross | 9 | 9 | 4/5 | 0.616996 | 0.444444 | 0.172552 | -268.000000 | -0.213113 |
| side:yes|p60_70|near_boundary|early | 9 | 9 | 4/5 | 0.616996 | 0.444444 | 0.172552 | -268.000000 | -0.213113 |
| side:no|p50_60|near_boundary|middle | 4 | 4 | 0/4 | 0.521575 | 0.000000 | 0.521575 | -249.000000 | -0.089227 |
| side:no|p60_70|mid_boundary|middle | 4 | 4 | 1/3 | 0.646004 | 0.250000 | 0.396004 | -225.000000 | -0.339841 |
| side:yes|p60_70 | 18 | 18 | 10/8 | 0.637545 | 0.555556 | 0.081990 | -206.000000 | 0.042291 |

## Worst Rows From Top Bucket

| market | source | side | won | net c | p | ask | edge | stc | abs d | recross | clock |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060630-30 | rejected_actionable | no | False | -136.000000 | 0.675344 | 0.660000 | 0.015344 | 868.927000 | 0.393798 | 0.762043 | True |
| KXBTC15M-26MAY060245-45 | rejected_actionable | no | False | -134.000000 | 0.660829 | 0.650000 | 0.010829 | 868.740000 | 0.346255 | 0.663720 | True |
| KXBTC15M-26MAY052330-30 | rejected_actionable | no | False | -130.000000 | 0.659176 | 0.630000 | 0.029176 | 654.661000 | 0.369967 | 0.572942 | False |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | False | -128.000000 | 0.635838 | 0.620000 | 0.015838 | 843.330000 | 0.346131 | 0.982771 | False |
| KXBTC15M-26MAY060500-00 | rejected_actionable | no | False | -126.000000 | 0.674136 | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 | False |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -124.000000 | 0.610883 | 0.600000 | 0.010883 | 717.804000 | 0.229994 | 0.723320 | False |
| KXBTC15M-26MAY071015-15 | rejected_actionable | no | False | -124.000000 | 0.609894 | 0.600000 | 0.009894 | 864.225000 | 0.287274 | 1.102864 | True |
| KXBTC15M-26MAY060830-30 | rejected_actionable | no | False | -122.000000 | 0.600730 | 0.590000 | 0.010730 | 884.233000 | 0.286154 | 0.943700 | True |
| KXBTC15M-26MAY052245-45 | rejected_actionable | no | False | -118.000000 | 0.643789 | 0.570000 | 0.073789 | 752.490000 | 0.362082 | 0.663374 | False |
| KXBTC15M-26MAY060330-30 | rejected_actionable | no | False | -118.000000 | 0.630880 | 0.570000 | 0.060880 | 884.146000 | 0.287388 | 0.689280 | False |
| KXBTC15M-26MAY061045-45 | rejected_actionable | no | False | -118.000000 | 0.601767 | 0.570000 | 0.031767 | 868.842000 | 0.212683 | 1.191443 | True |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -112.000000 | 0.605951 | 0.540000 | 0.065951 | 841.408000 | 0.278629 | 0.786584 | True |

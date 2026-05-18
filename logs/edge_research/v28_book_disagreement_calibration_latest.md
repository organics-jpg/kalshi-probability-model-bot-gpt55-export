# v28 Book Disagreement Calibration

- Physics prior: executable book price is a noisy market-implied probability.
- Question: when v28 disagrees with that prior, is v28 better calibrated after settlement?

## Overall

- Observations: `795`
- Avg v28 p: `0.7129118490566038`
- Avg ask probability: `0.7014591194968554`
- Avg v28 minus ask probability: `0.011452729559748425`
- Win rate: `0.7144654088050314`
- Avg v28 Brier: `0.16330634137287547`
- Avg book Brier: `0.1559896855345912`
- Avg v28 minus book Brier: `0.007316655838284272`

## By Disagreement Bucket

| bucket | count | avg v28 p | avg ask p | win rate | v28-book p | v28 brier | book brier | v28-book brier | gross c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v28_below_book | 139 | 0.5875153956834532 | 0.7225179856115108 | 0.7194244604316546 | -0.13500258992805755 | 0.18342929165192806 | 0.15705971223021584 | 0.026369579421712218 | -125.0 |
| slightly_below_book | 180 | 0.6421632555555555 | 0.6636111111111112 | 0.6333333333333333 | -0.021447855555555558 | 0.16655990654233332 | 0.16708055555555557 | -0.0005206490132222305 | -1099.0 |
| near_book | 141 | 0.716946170212766 | 0.7031914893617022 | 0.75177304964539 | 0.01375468085106383 | 0.16723888417557448 | 0.168568085106383 | -0.001329200930808513 | 1356.0 |
| v28_plus_03_08 | 215 | 0.8182310046511628 | 0.7664651162790698 | 0.7674418604651163 | 0.05176588837209302 | 0.14275293015054885 | 0.14023116279069767 | 0.002521767359851161 | 235.0 |
| v28_plus_08_15 | 79 | 0.7716471265822785 | 0.6665822784810127 | 0.759493670886076 | 0.10506484810126582 | 0.12398216783127848 | 0.1314354430379747 | -0.007453275206696207 | 405.0 |
| v28_plus_15 | 41 | 0.7693096341463415 | 0.5165853658536586 | 0.5609756097560976 | 0.2527242682926829 | 0.25082762840007317 | 0.19036097560975607 | 0.06046665279031708 | -300.0 |

## Observations

| source | market | side | bucket | p_side | ask p | outcome | v28-book brier | gross c |
|---|---|---|---|---:|---:|---:|---:|---:|
| rejected_actionable | KXBTC15M-26MAY071230-30 | yes | v28_plus_03_08 | 0.857838 | 0.81 | 1.0 | -0.015889965755999977 | 38.0 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | no | slightly_below_book | 0.440021 | 0.46 | 1.0 | 0.02197648044099998 | 108.0 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | no | near_book | 0.853317 | 0.84 | 1.0 | -0.004084097511000008 | 32.0 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | no | near_book | 0.921072 | 0.91 | 1.0 | -0.0018703708159999947 | 18.0 |
| rejected_actionable | KXBTC15M-26MAY071245-45 | yes | near_book | 0.559979 | 0.55 | 0.0 | 0.011076480440999958 | -110.0 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | no | v28_below_book | 0.36396 | 0.42 | 1.0 | 0.06814688159999982 | 116.0 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | no | v28_below_book | 0.835792 | 0.91 | 1.0 | 0.018864267264000013 | 18.0 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | no | v28_plus_03_08 | 0.938084 | 0.9 | 1.0 | -0.006166408943999999 | 20.0 |
| rejected_actionable | KXBTC15M-26MAY071300-00 | yes | v28_plus_03_08 | 0.63604 | 0.59 | 0.0 | 0.05644688160000011 | -118.0 |
| entry | KXBTC15M-26MAY071315-15 | yes | v28_plus_03_08 | 0.860278 | 0.8 | 1.0 | -0.020477762715999978 | -6.0 |
| entry | KXBTC15M-26MAY071315-15 | yes | v28_plus_03_08 | 0.865868 | 0.81 | 1.0 | -0.018108606575999973 | -14.0 |
| entry | KXBTC15M-26MAY071315-15 | yes | v28_plus_03_08 | 0.850827 | 0.78 | 1.0 | -0.02614741607099999 | 32.0 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | no | slightly_below_book | 0.466558 | 0.5 | 0.0 | -0.03232363263600002 | -100.0 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | yes | near_book | 0.533442 | 0.51 | 1.0 | -0.022423632635999946 | 98.0 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | yes | v28_plus_03_08 | 0.850666 | 0.8 | 1.0 | -0.01769935644399999 | 40.0 |
| rejected_actionable | KXBTC15M-26MAY071315-15 | yes | near_book | 0.955633 | 0.93 | 1.0 | -0.002931569310999989 | 14.0 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | no | slightly_below_book | 0.576763 | 0.6 | 1.0 | 0.019129558168999944 | 80.0 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | no | v28_plus_03_08 | 0.86478 | 0.82 | 1.0 | -0.014115551600000019 | 18.0 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | no | near_book | 0.921226 | 0.92 | 1.0 | -0.00019465692399999162 | 16.0 |
| rejected_actionable | KXBTC15M-26MAY071330-30 | yes | near_book | 0.423237 | 0.41 | 0.0 | 0.011029558169000003 | -82.0 |

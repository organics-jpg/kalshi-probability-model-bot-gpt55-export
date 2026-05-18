# v28 Raw p52 Confirmation Path

- Base policy: `v28_raw_p50_edge0`
- Confirmation policy: `v28_raw_p52_edge0`

## Summary

- Changed paths: `23`
- Resolved changed paths: `23`
- Base W/net: `13/443.0c`
- Confirm W/net: `17/544.0c`
- Confirm minus base: `101.000000c`
- Avg delay seconds: `104.718533`
- Avg Brier base/confirm: `0.249188/0.194780`

## By Path Type

| path type | count | resolved | base W | confirm W | base net | confirm net | delta | avg delay | brier base/confirm |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| minor_wait | 3 | 3 | 3 | 3 | 294.000000 | 286.000000 | -8.000000 | 105.255461 | 0.232916/0.227156 |
| pay_up_for_probability_confirmation | 11 | 11 | 8 | 8 | 486.000000 | 223.000000 | -263.000000 | 76.202867 | 0.247173/0.196744 |
| pay_up_without_probability_confirmation | 1 | 1 | 0 | 0 | -102.000000 | -108.000000 | -6.000000 | 200.106081 | 0.263728/0.280870 |
| side_flip_confirmation | 8 | 8 | 2 | 6 | -235.000000 | 143.000000 | 378.000000 | 131.802781 | 0.256242/0.169176 |

## Changed Rows

| market | type | base side | confirm side | delay | base p | confirm p | base ask | confirm ask | base net | confirm net | delta | base won | confirm won |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY051430-30 | side_flip_confirmation | yes | no | 199.999103 | 0.501306 | 0.541007 | 0.470000 | 0.520000 | -98.000000 | 92.000000 | 190.000000 | False | True |
| KXBTC15M-26MAY051500-00 | pay_up_without_probability_confirmation | yes | yes | 200.106081 | 0.513545 | 0.529972 | 0.490000 | 0.520000 | -102.000000 | -108.000000 | -6.000000 | False | False |
| KXBTC15M-26MAY051530-30 | minor_wait | yes | yes | 19.993813 | 0.514168 | 0.527782 | 0.490000 | 0.500000 | 98.000000 | 96.000000 | -2.000000 | True | True |
| KXBTC15M-26MAY051645-45 | pay_up_for_probability_confirmation | yes | yes | 93.048183 | 0.516843 | 0.546658 | 0.500000 | 0.540000 | 96.000000 | 88.000000 | -8.000000 | True | True |
| KXBTC15M-26MAY051730-30 | pay_up_for_probability_confirmation | no | no | 105.534075 | 0.502782 | 0.681429 | 0.480000 | 0.670000 | 100.000000 | 62.000000 | -38.000000 | True | True |
| KXBTC15M-26MAY060115-15 | pay_up_for_probability_confirmation | no | no | 19.994434 | 0.513971 | 0.577382 | 0.510000 | 0.560000 | 94.000000 | 84.000000 | -10.000000 | True | True |
| KXBTC15M-26MAY060315-15 | pay_up_for_probability_confirmation | yes | yes | 99.996802 | 0.512365 | 0.616640 | 0.500000 | 0.610000 | 96.000000 | 74.000000 | -22.000000 | True | True |
| KXBTC15M-26MAY060345-45 | side_flip_confirmation | yes | no | 120.589387 | 0.515105 | 0.702712 | 0.380000 | 0.660000 | -80.000000 | 64.000000 | 144.000000 | False | True |
| KXBTC15M-26MAY060715-15 | pay_up_for_probability_confirmation | yes | yes | 39.989685 | 0.501801 | 0.539914 | 0.490000 | 0.530000 | 98.000000 | 90.000000 | -8.000000 | True | True |
| KXBTC15M-26MAY060815-15 | pay_up_for_probability_confirmation | no | no | 60.015858 | 0.505085 | 0.540349 | 0.490000 | 0.540000 | 98.000000 | 88.000000 | -10.000000 | True | True |
| KXBTC15M-26MAY060845-45 | side_flip_confirmation | yes | no | 20.058176 | 0.506183 | 0.528543 | 0.500000 | 0.520000 | -104.000000 | 92.000000 | 196.000000 | False | True |
| KXBTC15M-26MAY061000-00 | pay_up_for_probability_confirmation | no | no | 19.995984 | 0.513222 | 0.661616 | 0.500000 | 0.540000 | 96.000000 | 88.000000 | -8.000000 | True | True |
| KXBTC15M-26MAY061145-45 | side_flip_confirmation | no | yes | 41.933152 | 0.502076 | 0.544366 | 0.490000 | 0.510000 | 98.000000 | -106.000000 | -204.000000 | True | False |
| KXBTC15M-26MAY061415-15 | minor_wait | no | no | 60.053315 | 0.519091 | 0.521166 | 0.480000 | 0.490000 | 100.000000 | 98.000000 | -2.000000 | True | True |
| KXBTC15M-26MAY061515-15 | minor_wait | no | no | 235.719254 | 0.518915 | 0.521257 | 0.500000 | 0.520000 | 96.000000 | 92.000000 | -4.000000 | True | True |
| KXBTC15M-26MAY061545-45 | pay_up_for_probability_confirmation | no | no | 57.363246 | 0.513617 | 0.599662 | 0.490000 | 0.590000 | -102.000000 | -122.000000 | -20.000000 | False | False |
| KXBTC15M-26MAY061745-45 | side_flip_confirmation | no | yes | 2.376566 | 0.510383 | 0.872414 | 0.140000 | 0.870000 | -30.000000 | 24.000000 | 54.000000 | False | True |
| KXBTC15M-26MAY061900-00 | side_flip_confirmation | yes | no | 199.557428 | 0.501794 | 0.661389 | 0.340000 | 0.450000 | 128.000000 | -94.000000 | -222.000000 | True | False |
| KXBTC15M-26MAY070200-00 | side_flip_confirmation | yes | no | 227.522202 | 0.505710 | 0.741860 | 0.300000 | 0.710000 | -63.000000 | 55.000000 | 118.000000 | False | True |
| KXBTC15M-26MAY070815-15 | pay_up_for_probability_confirmation | yes | yes | 282.282708 | 0.501147 | 0.950799 | 0.440000 | 0.900000 | 108.000000 | 1.000000 | -107.000000 | True | True |
| KXBTC15M-26MAY070830-30 | side_flip_confirmation | yes | no | 242.386234 | 0.514492 | 0.875926 | 0.410000 | 0.820000 | -86.000000 | 16.000000 | 102.000000 | False | True |
| KXBTC15M-26MAY070930-30 | pay_up_for_probability_confirmation | no | no | 20.007701 | 0.511849 | 0.580081 | 0.480000 | 0.580000 | -100.000000 | -120.000000 | -20.000000 | False | False |
| KXBTC15M-26MAY071215-15 | pay_up_for_probability_confirmation | yes | yes | 40.002863 | 0.509397 | 0.543727 | 0.470000 | 0.530000 | -98.000000 | -110.000000 | -12.000000 | False | False |

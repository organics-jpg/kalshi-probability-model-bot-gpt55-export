# v28 Frozen Approved-Entry Book-Edge Gate

Research-only; no live bot changes or orders.

- Candidate: `skip_discount15_book_edge_lt_5pp`
- Freeze timestamp UTC: `2026-05-06T13:10:59.879402+00:00`
- Future actual-approved entries: `88`
- Candidate live-ready: `True`
- Blockers: `none`

## Current Read

- Frozen candidate has 88 future actual-approved entries and 71 retained settled rows.
- Control net 631.0c; retained net 783.0c; delta 152.0c.
- Retained coverage 80.68181818181819; skipped rows 14/3 for -152.0c.
- Promotion blockers: none.
- This validator starts after its own freeze timestamp; earlier actionability results are discovery only.

## Scorecard

| surface | entries | settled | W/L | coverage | net c | book brier d | book logloss d |
|---|---:|---:|---:|---:|---:|---:|---:|
| keep_all_control | 88 | 88 | 79/9 | 100.000000 | 631.000000 | 0.015379 | 0.037568 |
| retained_candidate | 71 | 71 | 65/6 | 80.681818 | 783.000000 | 0.012262 | 0.043968 |
| skipped_rows | 17 | 17 | 14/3 | 19.318182 | -152.000000 | 0.028399 | 0.010836 |

## Full-Loss Runway

| added full losses | stressed settled | stressed net c | still positive | sample gate met |
|---:|---:|---:|---:|---:|
| 1 | 72 | 683.000000 | True | True |
| 2 | 73 | 583.000000 | True | True |
| 3 | 74 | 483.000000 | True | True |
| 4 | 75 | 383.000000 | True | True |
| 5 | 76 | 283.000000 | True | True |

## Skipped Rows

| market | side | won | gross c | raw | book | ask | discount | book edge |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY060945-45` | no | True | -16 | 0.854149 | 0.590000 | 0.590000 | 0.264149 | 0.000000 |
| `KXBTC15M-26MAY060945-45` | no | True | -16 | 0.850231 | 0.700000 | 0.700000 | 0.150231 | 0.000000 |
| `KXBTC15M-26MAY060945-45` | no | True | -12 | 0.861162 | 0.710000 | 0.710000 | 0.151162 | 0.000000 |
| `KXBTC15M-26MAY061000-00` | no | True | 70 | 0.854748 | 0.650000 | 0.650000 | 0.204748 | 0.000000 |
| `KXBTC15M-26MAY061015-15` | no | True | -6 | 0.859312 | 0.680000 | 0.680000 | 0.179312 | 0.000000 |
| `KXBTC15M-26MAY061015-15` | no | True | 0 | 0.855860 | 0.700000 | 0.700000 | 0.155860 | 0.000000 |
| `KXBTC15M-26MAY061800-00` | no | True | -86 | 0.897587 | 0.670000 | 0.670000 | 0.227587 | 0.000000 |
| `KXBTC15M-26MAY062015-15` | no | True | -60 | 0.871622 | 0.420000 | 0.420000 | 0.451622 | 0.000000 |
| `KXBTC15M-26MAY062015-15` | yes | False | -134 | 0.885657 | 0.670000 | 0.670000 | 0.215657 | 0.000000 |
| `KXBTC15M-26MAY062030-30` | no | True | 32 | 0.874426 | 0.670000 | 0.670000 | 0.204426 | 0.000000 |
| `KXBTC15M-26MAY062100-00` | yes | True | 14 | 0.852359 | 0.610000 | 0.610000 | 0.242359 | 0.000000 |
| `KXBTC15M-26MAY062115-15` | yes | True | -12 | 0.942571 | 0.730000 | 0.730000 | 0.212571 | 0.000000 |
| `KXBTC15M-26MAY062115-15` | no | False | -34 | 0.860865 | 0.690000 | 0.690000 | 0.170865 | 0.000000 |
| `KXBTC15M-26MAY062215-15` | no | True | 14 | 0.889241 | 0.650000 | 0.650000 | 0.239241 | 0.000000 |
| `KXBTC15M-26MAY070015-15` | no | False | -2 | 0.963659 | 0.700000 | 0.700000 | 0.263659 | 0.000000 |
| `KXBTC15M-26MAY070745-45` | yes | True | 34 | 0.903807 | 0.680000 | 0.680000 | 0.223807 | 0.000000 |
| `KXBTC15M-26MAY070945-45` | no | True | 62 | 0.853699 | 0.690000 | 0.690000 | 0.163699 | 0.000000 |

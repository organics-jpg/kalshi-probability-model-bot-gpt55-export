# v61 Exit Robustness Audit

Generated UTC: `2026-05-05T10:58:54.228483+00:00`

## Scope

- Research-only comparison of v57 baseline, v60 max-upside NO-side margin gate, a prob56 NO-side compromise, and a symmetric held-side margin row.
- Same v55 entry/FV surface across policies.
- Live bot untouched.

## Policy Slices

| policy | slice | value | trades | fee+1c | exits | settled | wins | losses |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `hold15_prob52` | `all` | `all` | 333 | $13.60 | 78 | 255 | 277 | 56 |
| `hold15_prob52` | `side` | `no` | 162 | $4.47 | 42 | 120 | 135 | 27 |
| `hold15_prob52` | `side` | `yes` | 171 | $9.13 | 36 | 135 | 142 | 29 |
| `hold15_prob52` | `split` | `holdout` | 61 | $0.93 | 16 | 45 | 49 | 12 |
| `hold15_prob52` | `split` | `train` | 205 | $7.45 | 47 | 158 | 174 | 31 |
| `hold15_prob52` | `split` | `validation` | 67 | $5.22 | 15 | 52 | 54 | 13 |
| `hold15_prob52_noside_marginlte0p25` | `all` | `all` | 333 | $21.26 | 68 | 265 | 277 | 56 |
| `hold15_prob52_noside_marginlte0p25` | `side` | `no` | 162 | $12.13 | 32 | 130 | 135 | 27 |
| `hold15_prob52_noside_marginlte0p25` | `side` | `yes` | 171 | $9.13 | 36 | 135 | 142 | 29 |
| `hold15_prob52_noside_marginlte0p25` | `split` | `holdout` | 61 | $0.87 | 15 | 46 | 49 | 12 |
| `hold15_prob52_noside_marginlte0p25` | `split` | `train` | 205 | $12.71 | 41 | 164 | 174 | 31 |
| `hold15_prob52_noside_marginlte0p25` | `split` | `validation` | 67 | $7.68 | 12 | 55 | 54 | 13 |
| `hold15_prob56_noside_marginlte0p25` | `all` | `all` | 333 | $16.37 | 79 | 254 | 277 | 56 |
| `hold15_prob56_noside_marginlte0p25` | `side` | `no` | 162 | $6.86 | 40 | 122 | 135 | 27 |
| `hold15_prob56_noside_marginlte0p25` | `side` | `yes` | 171 | $9.51 | 39 | 132 | 142 | 29 |
| `hold15_prob56_noside_marginlte0p25` | `split` | `holdout` | 61 | $0.99 | 17 | 44 | 49 | 12 |
| `hold15_prob56_noside_marginlte0p25` | `split` | `train` | 205 | $10.40 | 46 | 159 | 174 | 31 |
| `hold15_prob56_noside_marginlte0p25` | `split` | `validation` | 67 | $4.98 | 16 | 51 | 54 | 13 |
| `hold15_prob54_heldmarginlte0p5` | `all` | `all` | 333 | $13.14 | 79 | 254 | 277 | 56 |
| `hold15_prob54_heldmarginlte0p5` | `side` | `no` | 162 | $2.95 | 43 | 119 | 135 | 27 |
| `hold15_prob54_heldmarginlte0p5` | `side` | `yes` | 171 | $10.19 | 36 | 135 | 142 | 29 |
| `hold15_prob54_heldmarginlte0p5` | `split` | `holdout` | 61 | $1.07 | 16 | 45 | 49 | 12 |
| `hold15_prob54_heldmarginlte0p5` | `split` | `train` | 205 | $6.95 | 48 | 157 | 174 | 31 |
| `hold15_prob54_heldmarginlte0p5` | `split` | `validation` | 67 | $5.12 | 15 | 52 | 54 | 13 |

## Delta Concentration Vs Baseline

| candidate | delta | pos/neg markets | top5 positive | top5 share | worst negative |
|---|---:|---:|---:|---:|---:|
| `hold15_prob52_noside_marginlte0p25` | $7.66 | 7/6 | $7.67 | 100.1% | $-0.45 |
| `hold15_prob56_noside_marginlte0p25` | $2.77 | 21/18 | $6.52 | 235.4% | $-1.02 |
| `hold15_prob54_heldmarginlte0p5` | $-0.46 | 8/6 | $1.28 | NA | $-0.86 |

## Largest Positive Deltas

| candidate | market | side | split | base fee+1c | candidate fee+1c | delta | base exit | candidate exit |
|---|---|---|---|---:|---:|---:|---|---|
| `hold15_prob56_noside_marginlte0p25` | `KXBTC15M-26MAY022330-30` | `no` | `train` | $-0.68 | $1.04 | $1.72 | `probability_reduce` | `settlement_win` |
| `hold15_prob52_noside_marginlte0p25` | `KXBTC15M-26MAY022330-30` | `no` | `train` | $-0.68 | $1.04 | $1.72 | `probability_reduce` | `settlement_win` |
| `hold15_prob52_noside_marginlte0p25` | `KXBTC15M-26MAY031515-15` | `no` | `validation` | $-0.95 | $0.64 | $1.59 | `probability_reduce` | `settlement_win` |
| `hold15_prob52_noside_marginlte0p25` | `KXBTC15M-26MAY012300-00` | `no` | `train` | $-0.18 | $1.41 | $1.59 | `probability_reduce` | `settlement_win` |
| `hold15_prob56_noside_marginlte0p25` | `KXBTC15M-26MAY011230-30` | `no` | `train` | $-0.98 | $0.47 | $1.45 | `probability_reduce` | `settlement_win` |
| `hold15_prob52_noside_marginlte0p25` | `KXBTC15M-26MAY011230-30` | `no` | `train` | $-0.98 | $0.47 | $1.45 | `probability_reduce` | `settlement_win` |
| `hold15_prob56_noside_marginlte0p25` | `KXBTC15M-26MAY031945-45` | `no` | `validation` | $-0.85 | $0.47 | $1.32 | `probability_reduce` | `settlement_win` |
| `hold15_prob52_noside_marginlte0p25` | `KXBTC15M-26MAY031945-45` | `no` | `validation` | $-0.85 | $0.47 | $1.32 | `probability_reduce` | `settlement_win` |
| `hold15_prob56_noside_marginlte0p25` | `KXBTC15M-26MAY011300-00` | `no` | `train` | $-0.83 | $0.41 | $1.24 | `probability_reduce` | `settlement_win` |
| `hold15_prob52_noside_marginlte0p25` | `KXBTC15M-26MAY011300-00` | `no` | `train` | $-0.83 | $0.41 | $1.24 | `probability_reduce` | `settlement_win` |
| `hold15_prob56_noside_marginlte0p25` | `KXBTC15M-26MAY040500-00` | `no` | `holdout` | $-1.30 | $-0.51 | $0.79 | `probability_reduce` | `probability_reduce` |
| `hold15_prob56_noside_marginlte0p25` | `KXBTC15M-26MAY022015-15` | `yes` | `train` | $-1.09 | $-0.32 | $0.77 | `probability_reduce` | `probability_reduce` |
| `hold15_prob54_heldmarginlte0p5` | `KXBTC15M-26MAY040600-00` | `yes` | `holdout` | $-0.70 | $-0.24 | $0.46 | `probability_reduce` | `probability_reduce` |
| `hold15_prob54_heldmarginlte0p5` | `KXBTC15M-26MAY010945-45` | `yes` | `train` | $-0.97 | $-0.69 | $0.28 | `probability_reduce` | `probability_reduce` |
| `hold15_prob54_heldmarginlte0p5` | `KXBTC15M-26MAY021030-30` | `yes` | `train` | $-0.51 | $-0.31 | $0.20 | `probability_reduce` | `probability_reduce` |
| `hold15_prob54_heldmarginlte0p5` | `KXBTC15M-26MAY030800-00` | `yes` | `train` | $-0.58 | $-0.38 | $0.20 | `probability_reduce` | `probability_reduce` |
| `hold15_prob54_heldmarginlte0p5` | `KXBTC15M-26MAY012230-30` | `yes` | `train` | $-0.34 | $-0.20 | $0.14 | `probability_reduce` | `probability_reduce` |
| `hold15_prob54_heldmarginlte0p5` | `KXBTC15M-26MAY020545-45` | `yes` | `train` | $-0.91 | $-0.83 | $0.08 | `probability_reduce` | `probability_reduce` |

## Read

- The prob56 NO-side margin compromise is the main robustness challenger: lower all-market PnL than v60, but a better min/holdout cushion than v57 in the current sweep.
- It still needs its own concentration and strict-forward behavior to justify promotion; this audit is retrospective only.

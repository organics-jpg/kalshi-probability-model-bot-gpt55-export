# v59 v58 Asymmetry Audit

Generated UTC: `2026-05-05T10:42:05.533396+00:00`

## Scope

- Research-only overfit/concentration audit for the v58 NO-side YES-axis margin-gated exit.
- Compares v58 against v57-style `hold15_prob52` and the best symmetric held-side margin row.
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
| `hold15_prob54_heldmarginlte0p5` | `all` | `all` | 333 | $13.14 | 79 | 254 | 277 | 56 |
| `hold15_prob54_heldmarginlte0p5` | `side` | `no` | 162 | $2.95 | 43 | 119 | 135 | 27 |
| `hold15_prob54_heldmarginlte0p5` | `side` | `yes` | 171 | $10.19 | 36 | 135 | 142 | 29 |
| `hold15_prob54_heldmarginlte0p5` | `split` | `holdout` | 61 | $1.07 | 16 | 45 | 49 | 12 |
| `hold15_prob54_heldmarginlte0p5` | `split` | `train` | 205 | $6.95 | 48 | 157 | 174 | 31 |
| `hold15_prob54_heldmarginlte0p5` | `split` | `validation` | 67 | $5.12 | 15 | 52 | 54 | 13 |

## Delta Concentration

- Total v58-v57 fee+1c delta: $7.66
- Positive / negative delta markets: 7 / 6
- Top 5 positive-delta markets: $7.67 (100.1% of total delta)
- Top 10 positive-delta markets: $8.99 (117.4% of total delta)
- Worst single negative delta: $-0.45

## Largest Positive Deltas

| market | side | split | base fee+1c | v58 fee+1c | delta | base exit | v58 exit |
|---|---|---|---:|---:|---:|---|---|
| `KXBTC15M-26MAY022330-30` | `no` | `train` | $-0.68 | $1.04 | $1.72 | `probability_reduce` | `settlement_win` |
| `KXBTC15M-26MAY012300-00` | `no` | `train` | $-0.18 | $1.41 | $1.59 | `probability_reduce` | `settlement_win` |
| `KXBTC15M-26MAY031515-15` | `no` | `validation` | $-0.95 | $0.64 | $1.59 | `probability_reduce` | `settlement_win` |
| `KXBTC15M-26MAY011230-30` | `no` | `train` | $-0.98 | $0.47 | $1.45 | `probability_reduce` | `settlement_win` |
| `KXBTC15M-26MAY031945-45` | `no` | `validation` | $-0.85 | $0.47 | $1.32 | `probability_reduce` | `settlement_win` |
| `KXBTC15M-26MAY011300-00` | `no` | `train` | $-0.83 | $0.41 | $1.24 | `probability_reduce` | `settlement_win` |
| `KXBTC15M-26MAY040500-00` | `no` | `holdout` | $-1.30 | $-1.22 | $0.08 | `probability_reduce` | `probability_reduce` |
| `KXBTC15M-26APR302245-45` | `no` | `train` | $-0.89 | $-0.89 | $0.00 | `probability_reduce` | `probability_reduce` |
| `KXBTC15M-26APR302300-00` | `no` | `train` | $0.47 | $0.47 | $0.00 | `settlement_win` | `settlement_win` |
| `KXBTC15M-26MAY042315-15` | `no` | `holdout` | $-0.31 | $-0.31 | $0.00 | `probability_reduce` | `probability_reduce` |
| `KXBTC15M-26MAY041900-00` | `yes` | `holdout` | $-0.28 | $-0.28 | $0.00 | `probability_reduce` | `probability_reduce` |
| `KXBTC15M-26MAY041330-30` | `yes` | `holdout` | $0.41 | $0.41 | $0.00 | `settlement_win` | `settlement_win` |

## Read

- The v58 improvement is highly concentrated; treat it as overfit-prone until forward data confirms it.
- The symmetric held-side margin row improves robustness less than v58 and does not beat v57 on all-market PnL.

# v64 Forward Loss Analog Audit

Generated UTC: `2026-05-05T11:34:21.220580+00:00`

## Scope

- Research-only historical analog audit for the fresh 97c NO forward loss.
- Replays v55 entry with v57-style hold15/prob52 exit.
- Live bot untouched.

## Slices

| slice | trades | fee+1c | avg c | exits | settled | wins | losses | NO/YES | avg ask | avg edge | avg p | avg stc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `all_v57_style` | 333 | $13.60 | 4.1 | 78 | 255 | 277 | 56 | 162/171 | 80.9 | 3.13 | 0.840 | 437.2 |
| `ask>=95_edge<=2_stc120_600` | 40 | $1.06 | 2.6 | 0 | 40 | 40 | 0 | 19/21 | 97.2 | 0.87 | 0.980 | 348.7 |
| `ask>=95_edge<=2_p>=95_stc120_600` | 40 | $1.06 | 2.6 | 0 | 40 | 40 | 0 | 19/21 | 97.2 | 0.87 | 0.980 | 348.7 |
| `NO_ask>=95_edge<=2_p>=95_stc120_600` | 19 | $0.53 | 2.8 | 0 | 19 | 19 | 0 | 19/0 | 97.1 | 0.84 | 0.979 | 308.2 |
| `NO_ask>=95_edge<=2_p>=95_stc120_450` | 18 | $0.46 | 2.6 | 0 | 18 | 18 | 0 | 18/0 | 97.2 | 0.81 | 0.980 | 298.9 |
| `NO_ask>=97_edge<=1p5_p>=98_stc120_450` | 10 | $0.06 | 0.6 | 0 | 10 | 10 | 0 | 10/0 | 98.2 | 0.72 | 0.989 | 293.7 |
| `YES_ask>=95_edge<=2_p>=95_stc120_600` | 21 | $0.53 | 2.5 | 0 | 21 | 21 | 0 | 0/21 | 97.2 | 0.90 | 0.981 | 385.3 |
| `ask>=97_edge<=1p5_stc120_450` | 20 | $0.16 | 0.8 | 0 | 20 | 20 | 0 | 11/9 | 98.1 | 0.54 | 0.986 | 301.4 |

## Exact Analog Rows

| market | split | side | ask | edge | p_side | stc | exit | fee+1c | outcome |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| `KXBTC15M-26MAY012315-15` | `train` | `no` | 99 | 0.58 | 0.996 | 226.4 | `settlement_win` | $-0.01 | `no` |
| `KXBTC15M-26MAY030230-30` | `train` | `no` | 99 | 0.18 | 0.992 | 129.3 | `settlement_win` | $-0.01 | `no` |
| `KXBTC15M-26MAY040615-15` | `holdout` | `no` | 99 | 1.00 | 1.000 | 446.7 | `settlement_win` | $-0.01 | `no` |
| `KXBTC15M-26MAY041530-30` | `holdout` | `no` | 99 | 0.33 | 0.993 | 159.4 | `settlement_win` | $-0.01 | `no` |
| `KXBTC15M-26MAY030015-15` | `train` | `no` | 98 | 0.98 | 0.990 | 262.7 | `settlement_win` | $0.01 | `no` |
| `KXBTC15M-26MAY031445-45` | `validation` | `no` | 98 | 0.70 | 0.987 | 299.9 | `settlement_win` | $0.01 | `no` |
| `KXBTC15M-26MAY041945-45` | `holdout` | `no` | 98 | 0.06 | 0.981 | 408.5 | `settlement_win` | $0.01 | `no` |
| `KXBTC15M-26MAY010645-45` | `train` | `no` | 98 | 0.67 | 0.987 | 299.4 | `settlement_win` | $0.01 | `no` |
| `KXBTC15M-26MAY040030-30` | `validation` | `no` | 97 | 0.41 | 0.974 | 297.9 | `settlement_win` | $0.03 | `no` |
| `KXBTC15M-26MAY030215-15` | `train` | `no` | 97 | 1.60 | 0.986 | 281.1 | `settlement_win` | $0.03 | `no` |
| `KXBTC15M-26MAY011700-00` | `train` | `no` | 97 | 1.36 | 0.984 | 412.6 | `settlement_win` | $0.03 | `no` |
| `KXBTC15M-26MAY010245-45` | `train` | `no` | 97 | 1.37 | 0.984 | 292.6 | `settlement_win` | $0.03 | `no` |
| `KXBTC15M-26MAY020630-30` | `train` | `no` | 96 | 1.62 | 0.976 | 413.3 | `settlement_win` | $0.05 | `no` |
| `KXBTC15M-26MAY011630-30` | `train` | `no` | 96 | 1.78 | 0.978 | 445.3 | `settlement_win` | $0.05 | `no` |
| `KXBTC15M-26APR302345-45` | `train` | `no` | 96 | 0.00 | 0.960 | 294.1 | `settlement_win` | $0.05 | `no` |
| `KXBTC15M-26MAY011045-45` | `train` | `no` | 96 | 0.00 | 0.960 | 174.8 | `settlement_win` | $0.05 | `no` |
| `KXBTC15M-26MAY040430-30` | `holdout` | `no` | 95 | 1.86 | 0.969 | 305.9 | `settlement_win` | $0.07 | `no` |
| `KXBTC15M-26MAY020115-15` | `train` | `no` | 95 | 0.00 | 0.950 | 230.4 | `settlement_win` | $0.07 | `no` |

## Read

- Exact NO-side analogs are not historically negative enough to justify a narrow veto from this audit alone.
- Any follow-up should preserve the 75-80% coverage requirement and be strict-forward validated.

# v28 Frozen Exit Reduce Geometry Relaxed Watch

Research-only; frozen watch, no live logic changes or orders.

- Generated UTC: `2026-05-11T03:14:30.270728+00:00`
- Freeze UTC: `2026-05-07T01:18:56.563250+00:00`
- Candidate: `side_geometry_or_no_deep_loss20_suppress_reduce_p_hold_ge_075`
- Rule: `Suppress mushroom_v28_probability_reduce when p_hold >= 0.75 and fair_drawdown sign agrees with the held side; additionally, for NO side only, allow sign-disagree suppression if current_cents <= -20.`
- Strict settled/suppressed/delta: `43/4/-164.000c`
- Strict blockers: `suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, full_loss_cushion_lt_3`

## Interpretation

- Research-only frozen watch; no live logic changes or orders.
- Diagnostic best is side_geometry_suppress_reduce_p_hold_ge_075 with 625.0c delta and 14/1 suppressed W/L.
- Strict post-freeze candidate has 43 settled rows, 4 suppressed decisions, -164.0c delta, blockers ['suppressed_decisions_lt_30', 'delta_not_positive', 'suppressed_losers_present', 'full_loss_cushion_lt_3'].

## Diagnostic Comparison

| policy | settled | candidate c | delta c | W/L | suppressed | suppressed W/L | recovery c | loss cost c | cushion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `side_geometry_suppress_reduce_p_hold_ge_075` | 132 | 1346.000 | 625.000 | 86/46 | 15 | 14/1 | 783.000 | -158.000 | 6 |
| `side_geometry_or_no_deep_loss20_suppress_reduce_p_hold_ge_075` | 132 | 1272.000 | 551.000 | 87/45 | 17 | 15/2 | 829.000 | -278.000 | 5 |
| `base_suppress_reduce_p_hold_ge_075` | 132 | 1058.000 | 337.000 | 91/41 | 25 | 20/5 | 1067.000 | -730.000 | 3 |

## Strict Post-Freeze Comparison

| policy | settled | candidate c | delta c | W/L | suppressed | suppressed W/L | recovery c | loss cost c | cushion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `side_geometry_suppress_reduce_p_hold_ge_075` | 43 | 458.000 | -44.000 | 30/13 | 3 | 2/1 | 114.000 | -158.000 | 0 |
| `base_suppress_reduce_p_hold_ge_075` | 43 | 376.000 | -126.000 | 33/10 | 9 | 6/3 | 298.000 | -424.000 | 0 |
| `side_geometry_or_no_deep_loss20_suppress_reduce_p_hold_ge_075` | 43 | 338.000 | -164.000 | 30/13 | 4 | 2/2 | 114.000 | -278.000 | 0 |

## Diagnostic Best Suppressed Rows

| market | side | result | exit | p_hold | drawdown | current c | hold c | delta c | won |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY060245-45` | `yes` | `yes` | 76 | 0.793 | 2.667 | -8.000 | 40.000 | 48.000 | True |
| `KXBTC15M-26MAY060300-00` | `yes` | `yes` | 74 | 0.780 | 2.960 | -14.000 | 38.000 | 52.000 | True |
| `KXBTC15M-26MAY060300-00` | `yes` | `yes` | 69 | 0.753 | 4.684 | -22.000 | 40.000 | 62.000 | True |
| `KXBTC15M-26MAY060630-30` | `yes` | `yes` | 73 | 0.778 | 1.223 | -12.000 | 42.000 | 54.000 | True |
| `KXBTC15M-26MAY060645-45` | `yes` | `yes` | 74 | 0.799 | 2.065 | -16.000 | 36.000 | 52.000 | True |
| `KXBTC15M-26MAY060645-45` | `yes` | `yes` | 72 | 0.780 | 0.021 | -12.000 | 44.000 | 56.000 | True |
| `KXBTC15M-26MAY060915-15` | `no` | `no` | 70 | 0.794 | -9.376 | 0.000 | 60.000 | 60.000 | True |
| `KXBTC15M-26MAY060930-30` | `no` | `no` | 69 | 0.788 | -2.761 | -14.000 | 48.000 | 62.000 | True |
| `KXBTC15M-26MAY060930-30` | `no` | `no` | 72 | 0.799 | -6.918 | -3.000 | 54.000 | 57.000 | True |
| `KXBTC15M-26MAY061015-15` | `no` | `no` | 70 | 0.800 | -9.998 | 0.000 | 60.000 | 60.000 | True |
| `KXBTC15M-26MAY061030-30` | `yes` | `yes` | 70 | 0.753 | 2.726 | -16.000 | 44.000 | 60.000 | True |
| `KXBTC15M-26MAY061045-45` | `yes` | `yes` | 77 | 0.797 | 0.305 | -6.000 | 40.000 | 46.000 | True |
| `KXBTC15M-26MAY071015-15` | `no` | `yes` | 79 | 0.789 | -0.913 | 2.000 | -156.000 | -158.000 | False |
| `KXBTC15M-26MAY071045-45` | `no` | `no` | 69 | 0.761 | -2.053 | -10.000 | 52.000 | 62.000 | True |
| `KXBTC15M-26MAY071315-15` | `yes` | `yes` | 74 | 0.784 | 2.583 | -14.000 | 38.000 | 52.000 | True |
